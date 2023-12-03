import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt


def visualize_room_occupancy(schedule_file_path):
    # Load the data
    schedule_df = pd.read_excel(schedule_file_path)

    # Function to fix time slots missing 'am'/'pm' designations
    def fix_time_format(time_slot):
        parts = time_slot.split(" - ")
        if len(parts) == 2:
            start_time, end_time = parts
            # If 'am'/'pm' is missing in start time, but present in end time, add it to start time
            if ("am" in end_time or "pm" in end_time) and (
                "am" not in start_time and "pm" not in start_time
            ):
                am_pm = "am" if "am" in end_time else "pm"
                start_time += am_pm
            return f"{start_time} - {end_time}"
        return time_slot

    # Apply the fix to the "Time Slot" column
    schedule_df["Time Slot"] = (
        schedule_df["Time Slot"].str.strip().apply(fix_time_format)
    )

    # Adjusted function to parse the 'Time Slot' column and extract days and times
    def parse_time_slot(time_slot):
        parts = time_slot.split(" - ")
        if len(parts) == 2:
            day_time, end_time = parts
            day_time_parts = day_time.split(" ")
            days = day_time_parts[0]
            start_time = " ".join(day_time_parts[1:])
            if "am" in start_time or "pm" in start_time:
                start_time = start_time.replace("am", " am").replace("pm", " pm")
            return days, start_time, end_time
        return [None, None, None]

    # Parse the Time Slot column
    schedule_df[["Days", "Start Time", "End Time"]] = schedule_df["Time Slot"].apply(
        lambda x: pd.Series(parse_time_slot(x))
    )

    # Function to convert time to 24-hour format
    def convert_to_24h(time_str):
        if ":" not in time_str:
            time_str += ":00"
        if "pm" in time_str.lower():
            time_str = time_str.lower().replace("pm", "").strip()
            hours, minutes = map(int, time_str.split(":"))
            hours += 0 if hours == 12 else 12
        else:
            time_str = time_str.lower().replace("am", "").strip()
            hours, minutes = map(int, time_str.split(":"))
            hours = 0 if hours == 12 else hours
        return f"{hours:02d}:{minutes:02d}"

    # Convert start and end times to 24-hour format
    schedule_df["Start Time"] = schedule_df["Start Time"].apply(convert_to_24h)
    schedule_df["End Time"] = schedule_df["End Time"].apply(convert_to_24h)

    # Function to expand times into 30-minute blocks
    def expand_into_time_blocks(start_time, end_time, interval_minutes=30):
        start_hour, start_minute = map(int, start_time.split(":"))
        end_hour, end_minute = map(int, end_time.split(":"))
        start = start_hour * 60 + start_minute
        end = end_hour * 60 + end_minute
        return np.arange(start, end, interval_minutes)

    # Define the 24-hour time range
    time_range = [
        f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in [0, 30]
    ]

    # Generate colors for each course
    unique_courses = schedule_df["Course ID"].unique()
    colors = list(mcolors.TABLEAU_COLORS.keys())  # Predefined set of colors

    # Sort the room numbers
    sorted_room_numbers = sorted(schedule_df["Room"].unique())

    # Create a figure
    plt.figure(figsize=(15, 10))

    # Initialize a combined heatmap data array
    combined_heatmap_data = np.zeros(
        (len(sorted_room_numbers), len(time_range) * len("MTWRF")), dtype=float
    )

    # Plot each course's schedule as a layer in the heatmap
    for course_id in unique_courses:
        # Initialize a schedule array for this course
        course_schedule_array = np.zeros(
            (len(sorted_room_numbers), len(time_range) * len("MTWRF")), dtype=float
        )

        # Populate the array for this course
        course_schedule = schedule_df[schedule_df["Course ID"] == course_id]
        for _, row in course_schedule.iterrows():
            room_index = sorted_room_numbers.index(row["Room"])
            for day in row["Days"]:
                day_index = "MTWRF".index(day)
                time_blocks = expand_into_time_blocks(
                    row["Start Time"], row["End Time"]
                )
                for block in time_blocks:
                    time_block_index = day_index * len(time_range) + (block // 30)
                    course_schedule_array[
                        room_index, time_block_index
                    ] = 1  # Mark as occupied

        # Overlay this course's schedule on the combined heatmap
        combined_heatmap_data += course_schedule_array * (
            unique_courses.tolist().index(course_id) + 1
        )

    # Define the tick labels for the x-axis to be more readable
    readable_x_ticks_labels = [
        f"{day}\n{time}" for day in "MTWRF" for time in time_range[::8]
    ]
    readable_x_ticks_positions = np.arange(0, len(time_range) * len("MTWRF"), 8)

    # Create the heatmap with sorted rooms and more readable time labels
    ax = sns.heatmap(
        combined_heatmap_data,
        cmap=mcolors.ListedColormap(colors[: len(unique_courses)]),
        cbar=False,
    )

    # Set the y-axis labels to the sorted room numbers
    ax.set_yticks(np.arange(len(sorted_room_numbers)))
    ax.set_yticklabels(sorted_room_numbers)

    # Set the x-axis labels to the readable time labels
    ax.set_xticks(readable_x_ticks_positions)
    ax.set_xticklabels(readable_x_ticks_labels, rotation=90)

    # Set the labels and title
    plt.xlabel("Day of the Week and Time")
    plt.ylabel("Room Number")
    plt.title("Weekly Room Occupancy Schedule by Course ID")
    plt.tight_layout()

    # Show the heatmap
    plt.show()

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages


def visualize_room_occupancy(schedule_file_path):
    # Load the data
    schedule_df = pd.read_excel(schedule_file_path)

    # Function to fix time slots missing 'am'/'pm' designations and to parse them

    def fix_and_parse_time_slot(time_slot):
        if pd.isna(time_slot):
            return [None, None, None]
        parts = time_slot.split(" - ")
        if len(parts) == 2:
            day_time, end_time = parts
            # Correctly append ':00' for hour-only times
            if "am" in day_time or "pm" in day_time:
                if ":" not in day_time:
                    day_time = day_time.replace("am", ":00am").replace("pm", ":00pm")
            if "am" in end_time or "pm" in end_time:
                if ":" not in end_time:
                    end_time = end_time.replace("am", ":00am").replace("pm", ":00pm")
            # Append AM/PM to start time if missing
            if ("am" in end_time or "pm" in end_time) and (
                "am" not in day_time and "pm" not in day_time
            ):
                am_pm = "am" if "am" in end_time else "pm"
                day_time += am_pm
            day_time_parts = day_time.split(" ")
            days, start_time = day_time_parts[0], " ".join(day_time_parts[1:])
            return days, start_time, end_time
        return [None, None, None]

    def convert_to_24h(time_str):
        if time_str is None:
            return None
        # Check if the time string contains 'am' or 'pm'
        if "am" in time_str or "pm" in time_str:
            # Correctly format the time string for parsing
            formatted_time_str = time_str
            if ":" not in time_str:
                formatted_time_str = time_str[:-2] + ":00" + time_str[-2:]
            return datetime.strptime(formatted_time_str, "%I:%M%p").strftime("%H:%M")
        else:
            # If no 'am' or 'pm', return the time string as is
            return time_str

    def time_to_datetime(time_str):
        return datetime.strptime(time_str, "%H:%M")

    # Apply the parsing and fixing functions to the schedule
    schedule_df[["Days", "Start Time", "End Time"]] = schedule_df["Time Slot"].apply(
        lambda x: pd.Series(fix_and_parse_time_slot(x))
    )
    schedule_df["Start Time"] = schedule_df["Start Time"].apply(convert_to_24h)
    schedule_df["End Time"] = schedule_df["End Time"].apply(convert_to_24h)

    # Generate unique colors for each course
    unique_courses = schedule_df["Course ID"].unique()
    colors = plt.cm.get_cmap("hsv", len(unique_courses) + 1)
    course_color_map = {course: colors(i) for i, course in enumerate(unique_courses)}

    def plot_room_schedule(room_schedule, room_number, ax):
        days = ["M", "T", "W", "R", "F"]
        day_to_num = {day: i for i, day in enumerate(days)}

        start_time = time_to_datetime("08:00")
        end_time = time_to_datetime("22:00")

        ax.yaxis_date()
        ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.yaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax.set_ylim(start_time, end_time)

        for _, row in room_schedule.iterrows():
            if row["Days"] is not None:  # Check if 'Days' is not None
                for day in row["Days"]:
                    if day in day_to_num:
                        x = day_to_num[day]
                        y_start = time_to_datetime(row["Start Time"])
                        y_end = time_to_datetime(row["End Time"])

                        course_color = course_color_map[row["Course ID"]]
                        rect = plt.Rectangle(
                            (x - 0.4, mdates.date2num(y_start)),
                            0.8,
                            mdates.date2num(y_end) - mdates.date2num(y_start),
                            color=course_color,
                            alpha=0.5,
                        )
                        ax.add_patch(rect)

        ax.set_xlim(-0.5, len(days) - 0.5)
        ax.set_xticks(range(len(days)))
        ax.set_xticklabels(days)
        ax.set_title(f"Room {room_number} Schedule")

        # Create a legend specific to this room
        unique_courses_in_room = room_schedule["Course ID"].unique()
        legend_handles = []
        legend_labels = []
        for course in unique_courses_in_room:
            color = course_color_map[course]
            teacher_id = room_schedule[room_schedule["Course ID"] == course][
                "Teacher ID"
            ].iloc[0]
            legend_label = f"TID: {teacher_id}\nCS: {course}"
            legend_handles.append(plt.Rectangle((0, 0), 1, 1, color=color, alpha=0.5))
            legend_labels.append(legend_label)

        ax.legend(
            legend_handles, legend_labels, loc="upper left", bbox_to_anchor=(1, 1)
        )

    unique_rooms = schedule_df["Room"].unique()

    # Create a PDF file
    with PdfPages("docs/Room_Schedules.pdf") as pdf:
        for room in sorted(unique_rooms):
            fig, ax = plt.subplots(figsize=(12, 6))
            room_schedule = schedule_df[schedule_df["Room"] == room]
            plot_room_schedule(room_schedule, room, ax)

            pdf.savefig(fig)
            plt.close(fig)

    print("Final schedule successfully exported to 'docs/Room_Schedules'.")


# Call the function with the path to your schedule file
# visualize_room_occupancy("path_to_your_file.xlsx")

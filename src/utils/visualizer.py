import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
from src.utils.time_slot_parser import TimeSlotParser


def extract_start_end_time(time_slots):
    if not time_slots:
        return [None, None, None]
    try:
        first_slot = time_slots[0]
        days = first_slot[:-4]
        start_time = first_slot[-4:]
        last_slot = time_slots[-1]
        end_time = last_slot[-4:]

        start_time_formatted = (
            f"{start_time[:2]}:{start_time[2:]}" if len(start_time) == 4 else start_time
        )
        end_time_formatted = (
            f"{end_time[:2]}:{end_time[2:]}" if len(end_time) == 4 else end_time
        )

        return [days, start_time_formatted, end_time_formatted]
    except ValueError as e:
        print(e)  # Or log to a file
        return [None, None, None]  # Skip invalid time slots


def visualize_room_occupancy(schedule_file_path):
    schedule_df = pd.read_excel(schedule_file_path)

    # Process time slots to extract days, start time, and end time
    schedule_df[["Days", "Start Time", "End Time"]] = schedule_df["Time Slot"].apply(
        lambda x: pd.Series(extract_start_end_time(TimeSlotParser.parse_time_slot(x)))
    )

    # Convert times to datetime objects
    schedule_df["Start Time"] = pd.to_datetime(
        schedule_df["Start Time"], format="%H:%M"
    )
    schedule_df["End Time"] = pd.to_datetime(schedule_df["End Time"], format="%H:%M")

    # Generate unique colors for each course
    unique_courses = schedule_df["Course ID"].unique()
    colors = plt.cm.get_cmap("hsv", len(unique_courses) + 1)
    course_color_map = {course: colors(i) for i, course in enumerate(unique_courses)}

    def plot_room_schedule(room_schedule, room_number, ax):
        days = ["M", "T", "W", "R", "F"]
        day_to_num = {day: i for i, day in enumerate(days)}

        start_time = datetime.strptime("08:00", "%H:%M")
        end_time = datetime.strptime("22:00", "%H:%M")

        ax.yaxis_date()
        ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.yaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax.set_ylim(start_time, end_time)

        for _, row in room_schedule.iterrows():
            if row["Days"] is not None:  # Check if 'Days' is not None
                for day in row["Days"]:
                    if day in day_to_num:
                        x = day_to_num[day]
                        y_start = row["Start Time"]
                        y_end = row["End Time"]

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


# Example usage
# visualize_room_occupancy("path_to_your_schedule_file.xlsx")

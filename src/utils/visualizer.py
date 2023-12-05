import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
from src.utils.time_slot_parser import TimeSlotParser


def plot_room_schedule(room_schedule, room_number, ax, day_to_num, course_color_map):
    """
    Plot schedule for a single room.
    """
    for _, row in room_schedule.iterrows():
        for day in row["Days"]:
            if day in day_to_num:
                x = day_to_num[day]
                y_start = mdates.date2num(row["Start Time"])
                y_end = mdates.date2num(row["End Time"])

                course_color = course_color_map[row["Course ID"]]
                rect = plt.Rectangle(
                    (x - 0.4, y_start),
                    0.8,
                    y_end - y_start,
                    color=course_color,
                    alpha=0.5,
                )
                ax.add_patch(rect)

    ax.set_xlim(-0.5, len(day_to_num) - 0.5)
    ax.set_xticks(range(len(day_to_num)))
    ax.set_xticklabels(day_to_num.keys())
    ax.set_ylim(
        mdates.date2num(datetime.strptime("00:00", "%H:%M")),
        mdates.date2num(datetime.strptime("23:59", "%H:%M")),
    )
    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.yaxis.set_major_locator(mdates.HourLocator(interval=1))
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

    ax.legend(legend_handles, legend_labels, loc="upper left", bbox_to_anchor=(1, 1))


def visualize_room_occupancy(schedule_file_path):
    schedule_df = pd.read_excel(schedule_file_path)

    # Extract days, start time, and end time in a vectorized manner
    (
        schedule_df["Days"],
        schedule_df["Start Time"],
        schedule_df["End Time"],
    ) = TimeSlotParser.parse_time_slots(schedule_df["Time Slot"])

    # Convert times to datetime objects with error handling
    try:
        schedule_df["Start Time"] = pd.to_datetime(
            schedule_df["Start Time"], format="%H:%M", errors="coerce"
        )
        schedule_df["End Time"] = pd.to_datetime(
            schedule_df["End Time"], format="%H:%M", errors="coerce"
        )
    except Exception as e:
        print("Error converting times: ", e)
        return

    # Check for any NaT values that indicate failed conversions
    if schedule_df["Start Time"].isna().any() or schedule_df["End Time"].isna().any():  # type: ignore
        print("Some time values could not be converted. Please check the input data.")
        return

    # Global settings
    days = ["M", "T", "W", "R", "F"]
    day_to_num = {day: i for i, day in enumerate(days)}

    # Generate a global unique color map for each course
    unique_courses = schedule_df["Course ID"].unique()
    colors = plt.cm.get_cmap("hsv", len(unique_courses) + 1)
    global_course_color_map = {
        course: colors(i) for i, course in enumerate(unique_courses)
    }

    # Create a PDF file
    with PdfPages("docs/Room_Schedules.pdf") as pdf:
        for room in sorted(schedule_df["Room"].unique()):
            fig, ax = plt.subplots(figsize=(12, 6))
            room_schedule = schedule_df[schedule_df["Room"] == room]

            # Call with correct number of arguments
            plot_room_schedule(
                room_schedule,
                room,
                ax,
                day_to_num,
                global_course_color_map,
            )

            pdf.savefig(fig, bbox_inches="tight")  # Adjust for tight layout
            plt.close(fig)

    print("Final schedule successfully exported to 'docs/Room_Schedules'.")

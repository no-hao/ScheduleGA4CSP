import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


def visualize_room_occupancy(schedule_file_path):
    # Load the data
    schedule_df = pd.read_excel(schedule_file_path)

    # Function to fix time slots missing 'am'/'pm' designations and to parse them
    def fix_and_parse_time_slot(time_slot):
        parts = time_slot.split(" - ")
        if len(parts) == 2:
            day_time, end_time = parts
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

    def time_to_datetime(time_str):
        return datetime.strptime(time_str, "%H:%M")

    # Apply the parsing and fixing functions to the schedule
    schedule_df[["Days", "Start Time", "End Time"]] = schedule_df["Time Slot"].apply(
        lambda x: pd.Series(fix_and_parse_time_slot(x))
    )
    schedule_df["Start Time"] = schedule_df["Start Time"].apply(convert_to_24h)
    schedule_df["End Time"] = schedule_df["End Time"].apply(convert_to_24h)

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
            for day in row["Days"]:
                if day in day_to_num:
                    x = day_to_num[day]
                    y_start = time_to_datetime(row["Start Time"])
                    y_end = time_to_datetime(row["End Time"])

                    # Draw a rectangle for the time slot
                    rect = plt.Rectangle(
                        (x - 0.4, mdates.date2num(y_start)),
                        0.8,
                        mdates.date2num(y_end) - mdates.date2num(y_start),
                        color=np.random.rand(
                            3,
                        ),
                        alpha=0.5,
                    )
                    ax.add_patch(rect)

        ax.set_xlim(-0.5, len(days) - 0.5)
        ax.set_xticks(range(len(days)))
        ax.set_xticklabels(days)
        ax.set_title(f"Room {room_number} Schedule")

    # Create a figure with a subplot for each room
    unique_rooms = schedule_df["Room"].unique()
    # Figure variable 'fig' is created for plotting purposes but not directly used
    fig, axes = plt.subplots(
        nrows=len(unique_rooms), ncols=1, figsize=(12, 20), constrained_layout=True
    )

    # Plot schedule for each room
    for i, room in enumerate(sorted(unique_rooms)):
        room_schedule = schedule_df[schedule_df["Room"] == room]
        plot_room_schedule(
            room_schedule, room, axes[i] if len(unique_rooms) > 1 else axes
        )

    plt.show()

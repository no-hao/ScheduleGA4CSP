import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def parse_time(time_str):
    # Add ':00' if it's a single digit hour (e.g., '7' to '7:00')
    if re.match(r"^\d$", time_str):
        time_str += ":00"

    # Add 'am' or 'pm' if missing, with default to 'am'
    if not re.search(r"am|pm", time_str, re.IGNORECASE):
        time_str += "am"

    return time_str


def parse_time_slot_string(time_slot_str):
    parts = time_slot_str.split(" ")
    day_part = parts[0]
    time_part = " ".join(parts[1:])

    if " - " in time_part:
        start_time_str, end_time_str = time_part.split(" - ")
    else:
        # Handle cases where the time part is not in 'start - end' format
        # You might want to define a default end time or handle it some other way
        start_time_str = time_part
        end_time_str = "11:59pm"  # Default or calculated end time

    start_time_str = parse_time(start_time_str)
    end_time_str = parse_time(end_time_str)

    return day_part, start_time_str, end_time_str


def get_day_and_time(time_slot_id, time_slot_details):
    time_slot_str = time_slot_details[time_slot_id]
    day_part, start_time_str, end_time_str = parse_time_slot_string(time_slot_str)

    # Map the day part to a full day name if needed
    day_mapping = {
        "M": "Monday",
        "T": "Tuesday",
        "W": "Wednesday",
        "R": "Thursday",
        "F": "Friday",
        # Add more mappings if there are other abbreviations used
    }

    # Extract the full day names based on abbreviations, assuming no overlapping days
    days = [day_mapping[day] for day in day_part]
    day = " & ".join(days)  # Combine days for display (e.g., "Tuesday & Thursday")

    return day, start_time_str, end_time_str


def convert_to_coordinates(
    day_str, start_time_str, end_time_str, start_hour=8, end_hour=20
):
    try:
        start_time = datetime.strptime(start_time_str, "%I:%M%p")
        end_time = datetime.strptime(end_time_str, "%I:%M%p")
    except ValueError as e:
        print(f"Error parsing time: {e}")
        return []  # Return an empty list in case of error

    day_mapping = {
        "M": "Monday",
        "T": "Tuesday",
        "W": "Wednesday",
        "R": "Thursday",
        "F": "Friday",
    }

    # Convert days to x coordinates
    coordinates = []
    for day in day_str:
        if day in day_mapping:
            x = list(day_mapping.keys()).index(day)
            y_start = start_time.hour + start_time.minute / 60.0 - start_hour
            y_end = end_time.hour + end_time.minute / 60.0 - start_hour
            height = y_end - y_start  # Height of the rectangle
            width = 0.8  # Width is set to 0.8 for visual separation between days
            coordinates.append((x, y_start, width, height))

    return coordinates


def visualize_schedule(chromosome, time_slot_details, days_of_week, output_path):
    start_hour = 8  # Define the start hour
    end_hour = 20  # Define the end hour

    fig, ax = plt.subplots(figsize=(15, 8))

    for gene in chromosome.genes:
        course_id = gene[0]["Course Section ID"]
        room = gene[1]["Room Number"]
        time_slot_id = gene[2]["Time Slot ID"]
        day_str, start_time_str, end_time_str = parse_time_slot_string(
            time_slot_details[time_slot_id]
        )

        coordinates = convert_to_coordinates(day_str, start_time_str, end_time_str)
        for x, y, width, height in coordinates:
            rect = patches.Rectangle(
                (x, y),
                width,
                height,
                linewidth=1,
                edgecolor="black",
                facecolor="skyblue",
                alpha=0.3,
            )
            ax.add_patch(rect)
            plt.text(
                x + width / 2,
                y + height / 2,
                f"{course_id}\nRoom {room}",
                fontsize=8,
                va="center",
                ha="center",
            )

    ax.set_xlim(-0.5, len(days_of_week) - 0.5)
    ax.set_ylim(0, 12)  # Assuming 12-hour day starting at 8AM

    ax.set_xticks(range(len(days_of_week)))
    ax.set_xticklabels(days_of_week)
    ax.set_yticks(range(13))  # Assuming 12-hour day with hourly ticks
    ax.set_yticklabels([f"{hour}:00" for hour in range(start_hour, end_hour + 1)])
    ax.grid(True)

    ax.set_yticklabels([f"{hour}:00" for hour in range(start_hour, end_hour + 1)])
    plt.savefig(output_path)
    plt.show()

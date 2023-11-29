import pandas as pd


class TimeSlotParser:
    @staticmethod
    def to_string(parsed_slots):
        # Converts a list of parsed time slots into a single string, separated by newlines.
        return "\n".join(parsed_slots)

    @staticmethod
    def normalize_time_str(time_str):
        # Normalizes a time string to ensure it includes minutes and AM/PM.
        # This is especially useful for time formats that only specify the hour.
        if "am" not in time_str and "pm" not in time_str:
            if "-" in time_str:  # Checks if it's a time range.
                start, end = time_str.split("-")
                start, end = start.strip(), end.strip()
                # Append ":00" to indicate minutes if they are missing.
                start += ":00" if ":" not in start else ""
                end += ":00" if ":" not in end else ""
                # Add "pm" to the end time if necessary, based on 12-hour format rules.
                if int(start.split(":")[0]) < int(end.split(":")[0]):
                    end += "pm"
                return f"{start} - {end}"
            else:
                # Append ":00" for single time instances lacking minutes.
                time_str += ":00"
        return time_str

    @staticmethod
    def convert_to_24h(time_str):
        # Converts time strings from 12-hour (AM/PM) format to 24-hour format.
        # Utilizes pandas' to_datetime for conversion and handles exceptions.
        try:
            return pd.to_datetime(time_str, format="%I:%M%p").strftime("%H:%M")
        except ValueError:
            # Handles cases where the time is already in 24-hour format.
            return pd.to_datetime(time_str, format="%H:%M").strftime("%H:%M")

    @staticmethod
    def create_time_slots(start, end):
        # Generates a list of time slots in 24-hour format, in 15-minute intervals.
        # Utilizes pandas' date_range for generating a range of datetime objects.
        start_dt = pd.to_datetime(start, format="%H:%M")
        end_dt = pd.to_datetime(end, format="%H:%M")
        slots = pd.date_range(start=start_dt, end=end_dt, freq="15T")
        # Formats each datetime object into a string.
        return [slot.strftime("%H:%M") for slot in slots]

    @staticmethod
    def parse_time_slot(time_description):
        # Parses a time slot description into a more structured format.
        # Splits the description into days and times, then processes each part.
        parts = time_description.split(" ")
        days = parts[0]  # Extracts the days part (e.g., 'MW').
        times = " ".join(parts[1:])  # Extracts the time part (e.g., '1 - 2:15').

        # Normalizes and splits the time range into start and end times.
        times = TimeSlotParser.normalize_time_str(times)
        start_time, end_time = [t.strip() for t in times.split("-")]

        # Converts times to 24-hour format and generates the time slots.
        start_time_24h = TimeSlotParser.convert_to_24h(start_time)
        end_time_24h = TimeSlotParser.convert_to_24h(end_time)
        time_slots = TimeSlotParser.create_time_slots(start_time_24h, end_time_24h)

        # Creates and returns identifiers for each time interval.
        return [days + slot.replace(":", "") for slot in time_slots]

import pandas as pd


class TimeSlotParser:
    @staticmethod
    def to_string(parsed_slots):
        # Creates a string representation of the parsed time slots
        return "\n".join(parsed_slots)

    @staticmethod
    def normalize_time_str(time_str):
        # Normalize time string to include minutes and AM/PM if necessary
        if "am" not in time_str and "pm" not in time_str:
            if "-" in time_str:  # if it's a range
                start, end = time_str.split("-")
                start = start.strip()
                end = end.strip()
                # Add ":00" if hour doesn't have minutes
                start += ":00" if ":" not in start else ""
                end += ":00" if ":" not in end else ""
                # Determine if start or end times are in the PM and if so, convert
                if int(start.split(":")[0]) < int(end.split(":")[0]):
                    end += "pm"
                return f"{start} - {end}"
            else:
                time_str += ":00"
        return time_str

    @staticmethod
    def convert_to_24h(time_str):
        # Convert AM/PM to 24-hour format
        try:
            return pd.to_datetime(time_str, format="%I:%M%p").strftime("%H:%M")
        except ValueError:
            # Already in 24-hour format
            return pd.to_datetime(time_str, format="%H:%M").strftime("%H:%M")

    @staticmethod
    def create_time_slots(start, end):
        # Generate a range of datetime objects every 15 minutes
        start_dt = pd.to_datetime(start, format="%H:%M")
        end_dt = pd.to_datetime(end, format="%H:%M")
        slots = pd.date_range(start=start_dt, end=end_dt, freq="15T")
        return [slot.strftime("%H:%M") for slot in slots]

    @staticmethod
    def parse_time_slot(time_description):
        # Split the days and times
        parts = time_description.split(" ")
        days = parts[0]  # The day part (e.g., 'MW')
        times = " ".join(parts[1:])  # The time part (e.g., '1 - 2:15')

        # Normalize time strings
        times = TimeSlotParser.normalize_time_str(times)

        # Split the normalized time range into start and end
        start_time, end_time = [t.strip() for t in times.split("-")]

        # Convert to 24-hour format
        start_time_24h = TimeSlotParser.convert_to_24h(start_time)
        end_time_24h = TimeSlotParser.convert_to_24h(end_time)

        # Create time slots
        time_slots = TimeSlotParser.create_time_slots(start_time_24h, end_time_24h)

        # Create identifiers for each interval
        return [days + slot.replace(":", "") for slot in time_slots]

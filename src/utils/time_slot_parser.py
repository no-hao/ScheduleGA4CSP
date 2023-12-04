import pandas as pd


class TimeSlotParser:
    @staticmethod
    def to_string(parsed_slots):
        return "\n".join(parsed_slots)

    @staticmethod
    def normalize_time_str(time_str):
        if "am" not in time_str and "pm" not in time_str:
            # If 'am' or 'pm' is missing, assume PM for times like "1:00 - 2:00"
            time_str += " pm"

        # Ensure minutes are present
        parts = time_str.split("-")
        parts = [part.strip() + (":00" if ":" not in part else "") for part in parts]
        return " - ".join(parts)

    @staticmethod
    def convert_to_24h(time_str):
        try:
            return pd.to_datetime(time_str).strftime("%H:%M")
        except ValueError:
            # If it fails, the time is likely already in 24-hour format
            return time_str

    @staticmethod
    def create_time_slots(start, end):
        start_dt = pd.to_datetime(start, format="%H:%M")
        end_dt = pd.to_datetime(end, format="%H:%M")
        slots = pd.date_range(start=start_dt, end=end_dt, freq="15T")
        return [slot.strftime("%H:%M") for slot in slots[:-1]]  # Exclude the end time

    @staticmethod
    def parse_time_slot(time_description):
        parts = time_description.split(" ")
        days = parts[0]
        times = " ".join(parts[1:])
        times = TimeSlotParser.normalize_time_str(times)
        start_time, end_time = [t.strip() for t in times.split("-")]
        start_time_24h = TimeSlotParser.convert_to_24h(start_time)
        end_time_24h = TimeSlotParser.convert_to_24h(end_time)
        time_slots = TimeSlotParser.create_time_slots(start_time_24h, end_time_24h)
        return [days + slot.replace(":", "") for slot in time_slots]

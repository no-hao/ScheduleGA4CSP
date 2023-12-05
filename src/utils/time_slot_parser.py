import pandas as pd


class TimeSlotParser:
    @staticmethod
    def to_string(parsed_slots):
        return "\n".join(parsed_slots)

    @staticmethod
    def create_time_slots(start, end, max_duration_hours=12):
        start_dt = pd.to_datetime(start, format="%H:%M")
        end_dt = pd.to_datetime(end, format="%H:%M")

        duration = (end_dt - start_dt).total_seconds() / 3600
        if start_dt >= end_dt or duration > max_duration_hours:
            raise ValueError(f"Invalid time slot duration: {start} - {end}")

        slots = pd.date_range(start=start_dt, end=end_dt, freq="5T")
        return [slot.strftime("%H:%M") for slot in slots[:-1]]

    @staticmethod
    def parse_time_slot(time_description):
        parts = time_description.split(" ")
        days = parts[0]
        times = " ".join(parts[1:])
        start_time, end_time = [t.strip() for t in times.split("-")]
        time_slots = TimeSlotParser.create_time_slots(start_time, end_time)
        return [days + slot.replace(":", "") for slot in time_slots]

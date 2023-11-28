from .time_slot_parser import TimeSlotParser
import pandas as pd
import os


class DataLoader:
    def __init__(self, file_name):
        # Navigate up two levels from the current file to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.file_path = os.path.join(project_root, "data", file_name)

    def load_sheet(self, sheet_name):
        return pd.read_excel(self.file_path, sheet_name=sheet_name)

    def preprocess_data(self, df, sheet_name):
        # Handling missing values
        df.fillna(method="ffill", inplace=True)  # Forward fill for missing values

        # Convert categorical data to numerical format (if needed)
        if sheet_name in ["Teacher Preference", "Teacher Satisfaction"]:
            df.replace(
                {
                    "Board Pref": {0: "None", 1: "Whiteboard", 2: "Chalkboard"},
                    "Time Pref": {
                        0: "None",
                        1: "Morning",
                        2: "Afternoon",
                        3: "Evening",
                    },
                    "Days Pref": {0: "No Pref", 1: "MWF", 2: "TR"},
                    "Type Pref": {0: "None", 1: "Pure", 2: "Applied"},
                },
                inplace=True,
            )

        # Process time slots sheet
        if sheet_name == "Time Slots":
            df["Time Slot Codes"] = df["Description"].apply(
                TimeSlotParser.parse_time_slot
            )

        return df

    def load_and_process_data(self):
        sheets = {
            "Simulated Course Sections": "Simulated Course Sections",
            "Classrooms": "Classrooms",
            "Time Slots": "Time Slots",
            "Teacher Preference": "Teacher Preference",
            "Teacher Satisfaction": "Teacher Satisfaction",
        }

        processed_data = {}
        for sheet_name, sheet_readable_name in sheets.items():
            df = self.load_sheet(sheet_name)
            processed_data[sheet_readable_name] = self.preprocess_data(df, sheet_name)
        return processed_data

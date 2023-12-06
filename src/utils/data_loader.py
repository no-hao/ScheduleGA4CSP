from .time_slot_parser import TimeSlotParser
import pandas as pd
import os


# Define a class DataLoader for handling data loading and preprocessing.
class DataLoader:
    # Constructor to initialize DataLoader with the filename of the dataset.
    def __init__(self, file_name):
        # Determine the project root directory by navigating up from the current file's directory.
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        # Construct the file path by joining the project root with the 'data' directory and the filename.
        self.file_path = os.path.join(project_root, "data", file_name)

    # Function to load a specific sheet from an Excel file.
    def load_sheet(self, sheet_name):
        # Use pandas to read a specific sheet from an Excel file.
        return pd.read_excel(self.file_path, sheet_name=sheet_name)

    # Function to preprocess data from a DataFrame.
    def preprocess_data(self, df, sheet_name):
        # Fill missing values in the DataFrame using forward fill method.
        df.fillna(method="ffill", inplace=True)

        # Conditional preprocessing based on the sheet name.
        # Convert categorical data to a more readable format.
        if sheet_name in ["Teacher Preference", "Teacher Satisfaction"]:
            df.replace(
                {
                    # Mapping numerical values to categorical labels for readability.
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

        # Process 'Time Slots' sheet differently.
        if sheet_name == "Time Slots":
            # Apply a custom parser to transform time slot descriptions.
            df["Time Slot Codes"] = df["Description"].apply(
                TimeSlotParser.parse_time_slots
            )

        return df

    # Function to load and process data from multiple sheets in an Excel file.
    def load_and_process_data(self):
        # Define a dictionary mapping sheet names to more readable names.
        sheets = {
            "Simulated Course Sections": "Simulated Course Sections",
            "Classrooms": "Classrooms",
            "Time Slots": "Time Slots",
            "Teacher Preference": "Teacher Preference",
            "Teacher Satisfaction": "Teacher Satisfaction",
        }

        # Dictionary to store processed data from each sheet.
        processed_data = {}
        for sheet_name, sheet_readable_name in sheets.items():
            # Load each sheet and apply preprocessing.
            df = self.load_sheet(sheet_name)
            processed_data[sheet_readable_name] = self.preprocess_data(df, sheet_name)
        # Return the dictionary containing processed data from all sheets.
        return processed_data

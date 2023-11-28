import unittest
import pandas as pd
from src.utils.data_loader import DataLoader


class TestDataLoader(unittest.TestCase):
    def setUp(self):
        # Setup a DataLoader instance with the actual Excel file
        self.loader = DataLoader("Simulated_Data.xlsx")

    def test_load_simulated_course_sections_sheet(self):
        # Test loading of simulated course sections sheet
        df = self.loader.load_sheet("(I) Simulated Course Sections")
        self.assertIsInstance(df, pd.DataFrame)
        # Additional assertions to check expected columns
        expected_columns = [
            "Course Section ID",
            "Course Number",
            "Section",
            "Units",
            "Course Type",
        ]

        # Print actual columns for debugging
        print("Actual columns in DataFrame:", df.columns.tolist())
        print("Expected columns:", expected_columns)

        self.assertTrue(all(column in df.columns for column in expected_columns))

    def test_load_classrooms_sheet(self):
        # Test loading of classrooms sheet
        df = self.loader.load_sheet("(J) Classrooms")
        self.assertIsInstance(df, pd.DataFrame)
        # Additional assertions to check expected columns
        expected_columns = ["Room Number", "Board Type"]
        self.assertTrue(all(column in df.columns for column in expected_columns))

    def test_load_time_slots_sheet(self):
        # Test loading of time slots sheet
        df = self.loader.load_sheet("(K) Time Slots")
        self.assertIsInstance(df, pd.DataFrame)
        # Additional assertions to check expected columns
        expected_columns = ["Time Slot ID", "Description"]
        self.assertTrue(all(column in df.columns for column in expected_columns))

    def test_load_teacher_preference_sheet(self):
        # Test loading of teacher preference sheet
        df = self.loader.load_sheet("Teacher Preference")
        self.assertIsInstance(df, pd.DataFrame)
        # Additional assertions to check expected columns
        expected_columns = [
            "Teacher ID",
            "Min Sections",
            "Max Sections",
            "Board Pref",
            "Time Pref",
            "Days Pref",
            "Type Pref",
        ]
        self.assertTrue(all(column in df.columns for column in expected_columns))

    def test_load_teacher_satisfaction_sheet(self):
        # Test loading of teacher satisfaction sheet
        df = self.loader.load_sheet("Teacher Satisfaction")
        self.assertIsInstance(df, pd.DataFrame)
        # Additional assertions to check expected columns
        expected_columns = [
            "Teacher ID",
            "Min Sections",
            "Max Sections",
            "Board Pref",
            "Time Pref",
            "Days Pref",
            # Assuming there are 29 'CS' columns, adjust the number as needed
        ] + [f"CS{i}" for i in range(1, 30)]

        # Print actual columns for debugging
        print("Actual columns in DataFrame:", df.columns.tolist())
        print("Expected columns:", expected_columns)

        self.assertTrue(all(column in df.columns for column in expected_columns))


if __name__ == "__main__":
    unittest.main()

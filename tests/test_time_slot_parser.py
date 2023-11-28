import unittest
from src.utils.time_slot_parser import TimeSlotParser


class TestTimeSlotParser(unittest.TestCase):
    def test_convert_to_24h(self):
        self.assertEqual(TimeSlotParser.convert_to_24h("11:30am"), "11:30")
        self.assertEqual(TimeSlotParser.convert_to_24h("12:45pm"), "12:45")

    def test_create_time_slots(self):
        expected_slots = ["11:30", "11:45", "12:00", "12:15", "12:30", "12:45"]
        self.assertEqual(
            TimeSlotParser.create_time_slots("11:30", "12:45"), expected_slots
        )

    def test_parse_time_slot(self):
        input_description = "MW 11:30 - 12:45pm"
        expected_identifiers = [
            "MW1130",
            "MW1145",
            "MW1200",
            "MW1215",
            "MW1230",
            "MW1245",
        ]
        self.assertEqual(
            TimeSlotParser.parse_time_slot(input_description), expected_identifiers
        )

    def test_to_string(self):
        input_description = "MW 11:30 - 12:45pm"
        parsed_slots = TimeSlotParser.parse_time_slot(input_description)
        string_representation = TimeSlotParser.to_string(parsed_slots)
        expected_string = "MW1130\nMW1145\nMW1200\nMW1215\nMW1230\nMW1245"
        self.assertEqual(string_representation, expected_string)


if __name__ == "__main__":
    unittest.main()

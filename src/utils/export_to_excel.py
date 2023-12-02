import pandas as pd


def export_to_excel(
    best_chromosome, time_slots_details, output_file_path="data/final_schedule.xlsx"
):
    """
    Exports the best chromosome (schedule) to an Excel file.

    :param best_chromosome: The best chromosome to be exported.
    :param time_slots_details: Dictionary or similar structure containing the details of the time slots.
    :param output_file_path: The path where the Excel file will be saved.
    """
    data = []
    for gene in best_chromosome.genes:
        teacher_id = gene[3]
        course_id = gene[0]["Course Section ID"]
        time_slot_id = gene[2]["Time Slot ID"]
        room = gene[1]["Room Number"]

        # Lookup the full details of the time slot
        time_slot_detail = time_slots_details.get(time_slot_id, "Unknown Time Slot")

        data.append([teacher_id, course_id, time_slot_detail, room])

    columns = ["Teacher ID", "Course ID", "Time Slot", "Room"]
    df = pd.DataFrame(data, columns=columns)

    df.to_excel(output_file_path, index=False)
    print(f"Schedule exported to {output_file_path}")

import pandas as pd


def export_to_excel(best_chromosome, output_file_path="data/final_schedule.xlsx"):
    """
    Exports the best chromosome (schedule) to an Excel file.

    :param best_chromosome: The best chromosome to be exported.
    :param output_file_path: The path where the Excel file will be saved.
    """
    data = []
    for gene in best_chromosome.genes:
        # Extract relevant information from each gene
        teacher_id = gene[3]
        course_id = gene[0]["Course Section ID"]
        time_slot = gene[2]["Time Slot ID"]
        room = gene[1]["Room Number"]
        data.append([teacher_id, course_id, time_slot, room])

    # Create a DataFrame with columns in the specified order
    columns = ["Teacher ID", "Course ID", "Time Slot", "Room"]
    df = pd.DataFrame(data, columns=columns)

    # Export to Excel
    df.to_excel(output_file_path, index=False)
    print(f"Schedule exported to {output_file_path}")

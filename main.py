import logging
from src.utils.data_loader import DataLoader
from src.utils.export_to_excel import export_to_excel
from src.algorithms.genetic_algorithm import GeneticAlgorithm


def setup_logging():
    logging.basicConfig(
        filename="genetic_algorithm.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def main():
    setup_logging()
    logging.info("Application Started")

    # Create an instance of DataLoader
    data_loader = DataLoader("Simulated_Data.xlsx")

    # Load and preprocess data using DataLoader methods
    course_sections_df = data_loader.load_sheet("(I) Simulated Course Sections")
    classrooms_df = data_loader.load_sheet("(J) Classrooms")
    time_slots_df = data_loader.load_sheet("(K) Time Slots")
    teacher_preferences_df = data_loader.load_sheet("Teacher Preference")
    teacher_satisfaction_df = data_loader.load_sheet("Teacher Satisfaction")

    # Convert DataFrames to the required format
    course_sections = course_sections_df.to_dict("records")
    classrooms = classrooms_df.to_dict("records")
    time_slots = time_slots_df.to_dict("records")
    teacher_preferences = teacher_preferences_df.set_index("Teacher ID").T.to_dict()
    teacher_satisfaction = teacher_satisfaction_df.set_index("Teacher ID").T.to_dict()

    # Create a dictionary for time slot details
    time_slot_details = {
        slot["Time Slot ID"]: slot["Description"] for slot in time_slots
    }

    # Initialize and run the genetic algorithm
    ga = GeneticAlgorithm(
        course_sections,
        classrooms,
        time_slots,
        teacher_preferences,
        teacher_satisfaction,
        population_size=10,
    )
    ga.run(generations=100)

    # Export the best chromosome to an Excel file
    best_chromosome = ga.population[0]  # Assuming this is your best chromosome
    export_to_excel(best_chromosome, time_slot_details, "data/final_schedule.xlsx")

    logging.info("Application Finished")


if __name__ == "__main__":
    main()

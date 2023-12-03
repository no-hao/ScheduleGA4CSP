import sys
import time
import logging
import threading
from src.utils.data_loader import DataLoader
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.utils.export_to_excel import export_to_excel, export_summary_statistics

# Global flag to control the animation thread
stop_animation = False


def setup_logging():
    logging.basicConfig(
        filename="genetic_algorithm.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def animated_loading():
    global stop_animation
    chars = "/—\\|"
    while not stop_animation:
        for char in chars:
            sys.stdout.write("\r" + "Processing data..." + char)
            time.sleep(0.1)
            sys.stdout.flush()


def clear_loading_line():
    sys.stdout.write("\r" + " " * 50 + "\r")  # Clear the line
    sys.stdout.flush()


def main():
    global stop_animation
    setup_logging()
    logging.info("Application Started")
    pop_size = int(input("Enter the population size: "))
    gen_size = int(input("Enter the generation size: "))

    # Start loading animation
    t = threading.Thread(target=animated_loading)
    t.start()

    # Data loading and processing
    data_loader = DataLoader("Simulated_Data.xlsx")
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

    # Initialize the genetic algorithm
    ga = GeneticAlgorithm(
        course_sections,
        classrooms,
        time_slots,
        teacher_preferences,
        teacher_satisfaction,
        population_size=pop_size,
    )

    # Running the genetic algorithm and getting statistics for each generation
    generation_statistics = ga.run(generations=gen_size)

    # Stop the animation
    stop_animation = True
    t.join()

    # Clear the loading line
    clear_loading_line()

    # Export the best chromosome to an Excel file
    best_chromosome = ga.population[0]  # Assuming this is your best chromosome
    export_to_excel(best_chromosome, time_slot_details, "data/final_schedule.xlsx")

    # Export summary statistics to an Excel file
    export_summary_statistics(generation_statistics, "data/summary_statistics.xlsx")
    logging.info("Summary statistics exported to data/summary_statistics.xlsx")

    logging.info("Application Finished")


if __name__ == "__main__":
    main()

import os
import sys
import time
import logging
import threading
from src.utils.visualizer import visualize_room_occupancy
from src.utils.data_loader import DataLoader
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.utils.export_to_excel import export_to_excel, export_summary_statistics

# Global flag to control the animation thread
stop_animation = False


def setup_logging():
    log_file_path = "genetic_algorithm.log"
    max_log_size = 5 * 1024 * 1024  # 5 MB, for example

    # Check if the log file exists and its size
    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > max_log_size:
        # Option 1: Delete the existing file
        os.remove(log_file_path)

        # Option 2: Rename/Archive the existing file
        # os.rename(log_file_path, log_file_path + ".old")

    # Set up logging as before
    logging.basicConfig(
        filename=log_file_path,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def animated_loading():
    global stop_animation
    animation_width = 28  # Width of the sliding bar animation
    animation_chars = [
        "■",
        "□",
        "▢",
        "▣",
        "▤",
        "▥",
        "▦",
        "▧",
        "▨",
        "▩",
        "▪",
        "▫",
    ]  # Unicode block characters
    while not stop_animation:
        for i in range(animation_width):
            bar = "".join(animation_chars[i % len(animation_chars)] * (i + 1))
            sys.stdout.write("\033[K\r" + f"[{bar}]")
            sys.stdout.flush()
            time.sleep(0.2)


def clear_loading_line():
    sys.stdout.write(
        "\r\033[K" + " " * 50 + "\r\033[K"
    )  # Clear the line and reset cursor position
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
    final_schedule_file = "data/final_schedule.xlsx"
    export_to_excel(best_chromosome, time_slot_details, final_schedule_file)

    # Export summary statistics to an Excel file
    export_summary_statistics(generation_statistics, "data/summary_statistics.xlsx")
    logging.info("Summary statistics exported to data/summary_statistics.xlsx")

    # Visualize the schedule
    visualize_room_occupancy("data/final_schedule.xlsx")
    logging.info("A visualized schedule was exported to docs/Room_Schedule.pdf")

    logging.info("Application Finished")


if __name__ == "__main__":
    main()

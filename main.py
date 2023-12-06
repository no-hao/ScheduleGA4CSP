import os
import sys
import time
import logging
import threading
from src.utils.data_loader import DataLoader
from src.utils.visualizer import visualize_room_occupancy
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.utils.export_to_excel import export_to_excel, export_summary_statistics

# Global flag to control the animation thread
stop_animation = False


def setup_logging():
    log_file_path = "genetic_algorithm.log"
    max_log_size = 5 * 1024 * 1024  # 5 MB

    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > max_log_size:
        os.remove(log_file_path)

    logging.basicConfig(
        filename=log_file_path,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def animated_loading():
    global stop_animation
    animation_width = 28
    animation_chars = ["■", "□", "▢", "▣", "▤", "▥", "▦", "▧", "▨", "▩", "▪", "▫"]
    while not stop_animation:
        for i in range(animation_width):
            bar = "".join(animation_chars[i % len(animation_chars)] * (i + 1))
            sys.stdout.write("\033[K\r" + f"[{bar}]")
            sys.stdout.flush()
            time.sleep(0.2)


def clear_loading_line():
    sys.stdout.write("\r\033[K" + " " * 50 + "\r\033[K")
    sys.stdout.flush()


def main():
    global stop_animation
    setup_logging()
    logging.info("Application Started")

    pop_size = int(input("Enter the population size: "))
    gen_size = int(input("Enter the generation size: "))

    # Static omega values for the Tricriteria model
    omega1 = 0.33  # Weight for day-of-week balance
    omega2 = 0.33  # Weight for teaching load balance
    omega3 = 0.34  # Weight for teacher satisfaction

    t = threading.Thread(target=animated_loading)
    t.start()

    data_loader = DataLoader("Simulated_Data.xlsx")
    course_sections_df = data_loader.load_sheet("(I) Simulated Course Sections")
    classrooms_df = data_loader.load_sheet("(J) Classrooms")
    time_slots_df = data_loader.load_sheet("(K) Time Slots")
    teacher_preferences_df = data_loader.load_sheet("Teacher Preference")
    teacher_satisfaction_df = data_loader.load_sheet("Teacher Satisfaction")

    course_sections = course_sections_df.to_dict("records")
    classrooms = classrooms_df.to_dict("records")
    time_slots = time_slots_df.to_dict("records")
    teacher_preferences = teacher_preferences_df.set_index("Teacher ID").T.to_dict()
    teacher_satisfaction = teacher_satisfaction_df.set_index("Teacher ID").T.to_dict()

    time_slot_details = {
        slot["Time Slot ID"]: slot["Description"] for slot in time_slots
    }

    ga = GeneticAlgorithm(
        course_sections,
        classrooms,
        time_slots,
        teacher_preferences,
        teacher_satisfaction,
        population_size=pop_size,
        omega1=omega1,
        omega2=omega2,
        omega3=omega3,
    )

    generation_statistics = ga.run(generations=gen_size)

    stop_animation = True
    t.join()
    clear_loading_line()

    best_chromosome = ga.population[0]
    final_schedule_file = "data/final_schedule.xlsx"
    export_to_excel(best_chromosome, time_slot_details, final_schedule_file)

    export_summary_statistics(generation_statistics, "data/summary_statistics.xlsx")
    logging.info("Summary statistics exported to data/summary_statistics.xlsx")

    visualize_room_occupancy("data/final_schedule.xlsx")
    logging.info("A visualized schedule was exported to docs/Room_Schedule.pdf")

    logging.info("Application Finished")


if __name__ == "__main__":
    main()

import random
import pandas as pd

# Load the Excel file
file_path = "data/Simulated_Data.xlsx"

# Reading each sheet into pandas DataFrames
course_sections_df = pd.read_excel(
    file_path, sheet_name="(I) Simulated Course Sections"
)
classrooms_df = pd.read_excel(file_path, sheet_name="(J) Classrooms")
time_slots_df = pd.read_excel(file_path, sheet_name="(K) Time Slots")
teacher_preferences_df = pd.read_excel(file_path, sheet_name="Teacher Preference")
teacher_satisfaction_df = pd.read_excel(file_path, sheet_name="Teacher Satisfaction")

# Converting DataFrames to lists/dictionaries for easier access in the genetic algorithm
course_sections = course_sections_df.to_dict("records")
classrooms = classrooms_df.to_dict("records")
time_slots = time_slots_df.to_dict("records")
teacher_preferences = teacher_preferences_df.set_index("Teacher ID").T.to_dict()
teacher_satisfaction = teacher_satisfaction_df.set_index("Teacher ID").T.to_dict()


class Chromosome:
    def __init__(self):
        self.genes = []  # Each gene is a tuple (CourseSection, Classroom, TimeSlot, Teacher)
        self.fitness = 0
        self.initialize_randomly()
        self.evaluate_fitness()

    def initialize_randomly(self):
        for section in course_sections:
            room = random.choice(classrooms)
            time_slot = random.choice(time_slots)
            teacher_id = random.choice(list(teacher_preferences.keys()))
            self.genes.append((section, room, time_slot, teacher_id))

    def __str__(self):
        gene_str = "\n".join(
            [
                f"Course: {gene[0]['Course Section ID']}, Room: {gene[1]['Room Number']}, "
                f"Time Slot: {gene[2]['Time Slot ID']}, Teacher: {gene[3]}"
                for gene in self.genes
            ]
        )
        return f"Chromosome (Fitness: {self.fitness}):\n{gene_str}"

    def evaluate_fitness(self):
        self.fitness = 100
        mw_count, tr_count = 0, 0
        course_assignments = set()

        for gene in self.genes:
            course, room, time_slot, teacher_id = gene

            # MWF vs. TTh balance
            if (
                "MW" in time_slot["Description"]
                or "WF" in time_slot["Description"]
                or "MF" in time_slot["Description"]
            ):
                mw_count += 1
            elif "TR" in time_slot["Description"]:
                tr_count += 1

            # Ensure each course is only assigned once
            course_id = course["Course Section ID"]
            if course_id in course_assignments:
                self.fitness -= 100  # High penalty for duplicate course assignment
            else:
                course_assignments.add(course_id)

            # Evaluate teacher preferences and satisfaction
            teacher_score = self.evaluate_teacher_preferences(
                teacher_id, course, room, time_slot
            )
            self.fitness -= (
                teacher_score
            )  # Lower score is better, so subtract from fitness

        # Balance between MWF and TTh courses
        balance_delta = abs(mw_count - tr_count)
        self.fitness -= balance_delta  # Penalty based on imbalance

    def evaluate_teacher_preferences(self, teacher_id, course, room, time_slot):
        preferences = teacher_preferences[teacher_id]
        satisfaction_scores = teacher_satisfaction[teacher_id]

        preference_score = 0

        # Check board preference
        if (
            preferences["Board Pref"] != 0
            and room["Board Type"] == preferences["Board Pref"]
        ):
            preference_score += 1

        # Check time preference
        if preferences["Time Pref"] != 0:
            if (
                preferences["Time Pref"] == 1
                and "am" in time_slot["Description"].lower()
            ):
                preference_score += 1
            elif preferences["Time Pref"] == 2 and (
                "pm" in time_slot["Description"].lower()
                and "11" not in time_slot["Description"]
            ):
                preference_score += 1
            elif (
                preferences["Time Pref"] == 3
                and "evening" in time_slot["Description"].lower()
            ):
                preference_score += 1

        # Check days preference
        if preferences["Days Pref"] != 0:
            if preferences["Days Pref"] == 1 and "MWF" in time_slot["Description"]:
                preference_score += 1
            elif preferences["Days Pref"] == 2 and "TR" in time_slot["Description"]:
                preference_score += 1

        # Check type preference
        if (
            preferences["Type Pref"] != 0
            and course["Course Type"] == preferences["Type Pref"]
        ):
            preference_score += 1

        # Calculate satisfaction score
        satisfaction_score = satisfaction_scores[f"CS{course['Course Section ID']}"]

        return preference_score + satisfaction_score

    def is_valid(self):
        return self.fitness >= 0


class GeneticAlgorithm:
    def __init__(self, population_size):
        self.population = [Chromosome() for _ in range(population_size)]

    def selection(self):
        return random.sample(self.population, 2)

    def crossover(self, parent1, parent2):
        child_genes = []
        for i in range(len(parent1.genes)):
            if random.random() < 0.5:
                child_genes.append(parent1.genes[i])
            else:
                child_genes.append(parent2.genes[i])
        child = Chromosome()
        child.genes = child_genes
        child.evaluate_fitness()
        return child

    def mutation(self, chromosome):
        idx1, idx2 = random.sample(range(len(chromosome.genes)), 2)
        chromosome.genes[idx1], chromosome.genes[idx2] = (
            chromosome.genes[idx2],
            chromosome.genes[idx1],
        )
        chromosome.evaluate_fitness()

    def run(self, generations):
        for generation in range(generations):
            print(f"Generation: {generation + 1}")
            new_population = []
            while len(new_population) < len(self.population):
                parents = self.selection()
                child = self.crossover(parents[0], parents[1])
                self.mutation(child)
                if child.is_valid():
                    new_population.append(child)
            self.population = new_population
            print(f"Completed Generation: {generation + 1}")


# Test run with reduced population size and generations
test_ga = GeneticAlgorithm(population_size=10)
test_ga.run(generations=10)

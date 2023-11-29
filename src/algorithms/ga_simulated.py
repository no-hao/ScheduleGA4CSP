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
        assigned_slots = set()
        teacher_assignments = {teacher_id: 0 for teacher_id in teacher_preferences}

        for section in course_sections:
            room = random.choice(classrooms)
            time_slot = random.choice(time_slots)

            # Avoid slot collisions
            while (room["Room Number"], time_slot["Time Slot ID"]) in assigned_slots:
                room = random.choice(classrooms)
                time_slot = random.choice(time_slots)

            # Select a teacher who hasn't exceeded their max sections
            eligible_teachers = [
                tid
                for tid, count in teacher_assignments.items()
                if count < teacher_preferences[tid]["Max Sections"]
            ]
            if not eligible_teachers:  # Fallback if all exceed max
                eligible_teachers = list(teacher_preferences.keys())

            teacher_id = random.choice(eligible_teachers)
            teacher_assignments[teacher_id] += 1

            assigned_slots.add((room["Room Number"], time_slot["Time Slot ID"]))
            self.genes.append((section, room, time_slot, teacher_id))

        print("Chromosome Initialized with fewer duplicates\n")

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
        print("Evaluating Fitness...")
        self.fitness = 0  # Start with a neutral fitness
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

            # Check for duplicate course assignment
            course_id = course["Course Section ID"]
            if course_id in course_assignments:
                self.fitness -= 5  # Reduced penalty for duplicate assignment
                print(f"Duplicate Assignment Detected for Course {course_id}")
            else:
                course_assignments.add(course_id)

            # Evaluate teacher preferences and satisfaction
            teacher_score = self.evaluate_teacher_preferences(
                teacher_id, course, room, time_slot
            )
            # Reward for matching preference (increased reward)
            self.fitness += (
                5 - teacher_score
            ) * 2  # Increase the reward for preference matching

        # Balance between MWF and TTh courses (less penalty)
        balance_delta = abs(mw_count - tr_count)
        self.fitness -= balance_delta  # Reduce the penalty for imbalance

        # Set a floor for fitness
        self.fitness = max(0, self.fitness)  # Ensure fitness is not negative
        print(f"Fitness Evaluated: {self.fitness}\n")

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

    # TODO: # Implement a more advanced selection strategy
    # Example: Rank-based selection or Roulette wheel selection
    def selection(self):
        # Implement a more sophisticated selection method
        # Example: Tournament selection
        tournament_size = 5
        tournament = random.sample(self.population, tournament_size)
        parent1 = max(tournament, key=lambda c: c.fitness)
        tournament.remove(parent1)
        parent2 = max(tournament, key=lambda c: c.fitness)
        print(f"Selected parents: {parent1.fitness}, {parent2.fitness}")
        return parent1, parent2

    # TODO: Modify the crossover and mutation methods to be more constraint-aware
    def crossover(self, parent1, parent2):
        child = Chromosome()
        child.genes = []
        assigned_slots = set()

        for i in range(len(parent1.genes)):
            # Choose a gene from one of the parents
            gene = parent1.genes[i] if random.random() < 0.5 else parent2.genes[i]

            # Check for duplicate assignments
            while (gene[1]["Room Number"], gene[2]["Time Slot ID"]) in assigned_slots:
                gene = (
                    gene[0],
                    random.choice(classrooms),
                    random.choice(time_slots),
                    gene[3],
                )

            assigned_slots.add((gene[1]["Room Number"], gene[2]["Time Slot ID"]))
            child.genes.append(gene)

        child.evaluate_fitness()
        print("Crossover result:", child)
        return child

    def mutation(self, chromosome):
        idx = random.randint(0, len(chromosome.genes) - 1)
        gene = chromosome.genes[idx]

        # Mutate either room or time slot
        if random.random() < 0.5:
            new_room = random.choice(classrooms)
            gene = (gene[0], new_room, gene[2], gene[3])
        else:
            new_time_slot = random.choice(time_slots)
            gene = (gene[0], gene[1], new_time_slot, gene[3])

        chromosome.genes[idx] = gene
        chromosome.evaluate_fitness()
        print("Mutation result:", chromosome)

    def run(self, generations):
        for generation in range(generations):
            print(f"Starting Generation: {generation + 1}")
            new_population = []

            # Keep some of the best chromosomes from the current generation
            best_chromosomes = sorted(
                self.population, key=lambda c: c.fitness, reverse=True
            )[:2]
            new_population.extend(best_chromosomes)

            while len(new_population) < len(self.population):
                parents = self.selection()
                child = self.crossover(parents[0], parents[1])
                self.mutation(child)

                # Instead of discarding, set minimum fitness to 0
                if child.fitness < 0:
                    child.fitness = 0

                new_population.append(child)

            self.population = sorted(
                new_population, key=lambda c: c.fitness, reverse=True
            )
            print(
                f"Best Chromosome Fitness in Generation {generation + 1}: {self.population[0].fitness}"
            )
            print(f"Completed Generation: {generation + 1}")
            # Optionally, you could add some logic to print the best chromosome of the generation


# TODO: Add detailed logging at various steps to analyze the behavior

# Test run with reduced population size and generations
print("Starting Genetic Algorithm Test Run")
test_ga = GeneticAlgorithm(population_size=10)
test_ga.run(generations=100)

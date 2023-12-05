import random
import logging


# class Chromosome:
# Description: This class represents a chromosome in the context of the genetic algorithm.
# It encapsulates all the properties and behaviors specific to a chromosome, such as
# initializing with given parameters, representing a solution, and calculating fitness.
class Chromosome:
    # def __init__(
    # Description: This method is responsible for initializing a new instance of the Chromosome class.
    # It takes course sections, classrooms, time slots, teacher preferences, and teacher satisfaction
    # as parameters to set up the chromosome.
    def __init__(
        self,
        course_sections,  # A list of course sections
        classrooms,  # A list of classrooms
        time_slots,  # A list of available time slots
        teacher_preferences,  # A dictionary of teacher preferences
        teacher_satisfaction,  # A dictionary of teacher satisfaction scores
    ):
        # Initialization of class attributes
        logging.debug("Initializing new Chromosome instance.")
        self.course_sections = course_sections
        self.classrooms = classrooms
        self.time_slots = time_slots
        self.teacher_preferences = teacher_preferences
        self.teacher_satisfaction = teacher_satisfaction
        self.genes = []  # List to store genes; each gene represents a course scheduling decision
        self.fitness = 0  # Fitness score of the chromosome

        # Initialize and evaluate the chromosome
        self.initialize_randomly()
        self.evaluate_fitness()
        logging.debug("Chromosome initialized with random genes.")

    # String representation of the Chromosome object
    def __str__(self):
        output = [f"Chromosome (Fitness: {self.fitness}):\n"]
        output.append("Course ID | Room | Time Slot | Teacher ID")
        output.append("----------|------|----------|-----------")
        for gene in self.genes:
            course_id = gene[0]["Course Section ID"]
            room = gene[1]["Room Number"]
            time_slot = gene[2]["Time Slot ID"]
            teacher_id = gene[3]
            output.append(f"{course_id:^10}|{room:^6}|{time_slot:^10}|{teacher_id:^11}")
        return "\n".join(output)

    # Method to check if the chromosome is valid
    def is_valid(self):
        logging.debug("Checking if chromosome is valid.")

        # Count the number of sections assigned to each teacher
        teacher_section_count = {
            teacher_id: 0 for teacher_id in self.teacher_preferences
        }
        for _, _, _, teacher_id in self.genes:
            teacher_section_count[teacher_id] += 1

        # Check if any teacher exceeds their max section limit
        is_valid_chromosome = all(
            teacher_section_count[teacher_id]
            <= self.teacher_preferences[teacher_id]["Max Sections"]
            for teacher_id in teacher_section_count
        )

        if not is_valid_chromosome:
            logging.warning(
                "Chromosome is invalid due to teacher section limit exceedance."
            )
        else:
            logging.debug("Chromosome is valid.")

        return is_valid_chromosome

    # Method to initialize the chromosome with random values
    def initialize_randomly(self):
        logging.info("Initializing Chromosome Randomly")

        # Reset genes and assigned slots
        self.genes = []
        assigned_slots = set()

        # Shuffle time slots and classrooms to create random combinations
        all_combinations = [
            (room, time_slot)
            for room in self.classrooms
            for time_slot in self.time_slots
        ]
        random.shuffle(all_combinations)

        # Initialize counters for teacher assignments
        teacher_assignments = {teacher_id: 0 for teacher_id in self.teacher_preferences}

        for section in self.course_sections:
            # Ensure unique assignment by popping a combination
            room, time_slot = all_combinations.pop()

            # Find eligible teachers who haven't exceeded their max section limit
            eligible_teachers = [
                tid
                for tid, count in teacher_assignments.items()
                if count < self.teacher_preferences[tid]["Max Sections"]
            ]
            if not eligible_teachers:
                eligible_teachers = list(self.teacher_preferences.keys())

            # Calculate weights based on teacher satisfaction
            teacher_satisfaction_weights = [
                1
                / (
                    1
                    + self.teacher_satisfaction[tid][
                        f"CS{section['Course Section ID']}"
                    ]
                )
                for tid in eligible_teachers
            ]

            # Select a teacher randomly based on weighted satisfaction
            teacher_id = random.choices(
                eligible_teachers, weights=teacher_satisfaction_weights, k=1
            )[0]
            teacher_assignments[teacher_id] += 1

            # Add the chosen combination to the chromosome
            self.genes.append((section, room, time_slot, teacher_id))
            assigned_slots.add((room["Room Number"], time_slot["Time Slot ID"]))

        logging.debug("Random initialization of chromosome completed.")

    # Method to check if a teacher's preferences are not met
    def not_meeting_preferences(self, teacher_id, course, room, time_slot):
        logging.debug(f"Checking if preferences are met for teacher {teacher_id}.")
        preferences = self.teacher_preferences[teacher_id]

        # Define preference checks as a series of conditions
        conditions = [
            preferences["Board Pref"] != 0
            and room["Board Type"] != preferences["Board Pref"],
            preferences["Time Pref"] == 1
            and "am" not in time_slot["Description"].lower(),
            preferences["Time Pref"] == 2
            and "pm" not in time_slot["Description"].lower()
            and "11" not in time_slot["Description"],
            preferences["Time Pref"] == 3
            and "evening" not in time_slot["Description"].lower(),
            preferences["Days Pref"] == 1 and "MWF" not in time_slot["Description"],
            preferences["Days Pref"] == 2 and "TR" not in time_slot["Description"],
            preferences["Type Pref"] != 0
            and course["Course Type"] != preferences["Type Pref"],
        ]

        # Check if any preference is violated
        preference_violated = any(conditions)

        if preference_violated:
            logging.debug(f"Preference violation found for teacher {teacher_id}.")
        else:
            logging.debug(f"No preference violation for teacher {teacher_id}.")

        return preference_violated

    # Method to evaluate a teacher's preference score
    def evaluate_teacher_preferences(self, teacher_id, course, room, time_slot):
        logging.debug(f"Evaluating preferences for teacher {teacher_id}.")
        preferences = self.teacher_preferences[teacher_id]

        # Initialize preference score
        preference_score = 0

        # Check and score each preference
        if (
            preferences["Board Pref"] != 0
            and room["Board Type"] == preferences["Board Pref"]
        ):
            preference_score += 1
        if preferences["Time Pref"] == 1 and "am" in time_slot["Description"].lower():
            preference_score += 1
        if (
            preferences["Time Pref"] == 2
            and "pm" in time_slot["Description"].lower()
            and "11" not in time_slot["Description"]
        ):
            preference_score += 1
        if (
            preferences["Time Pref"] == 3
            and "evening" in time_slot["Description"].lower()
        ):
            preference_score += 1
        if preferences["Days Pref"] == 1 and "MWF" in time_slot["Description"]:
            preference_score += 1
        if preferences["Days Pref"] == 2 and "TR" in time_slot["Description"]:
            preference_score += 1
        if (
            preferences["Type Pref"] != 0
            and course["Course Type"] == preferences["Type Pref"]
        ):
            preference_score += 1

        # Add satisfaction score to the preference score
        satisfaction_score = self.teacher_satisfaction[teacher_id][
            f"CS{course['Course Section ID']}"
        ]
        total_score = preference_score + satisfaction_score

        logging.debug(f"Total preference score for teacher {teacher_id}: {total_score}")
        return total_score

    # Method to evaluate the fitness of the chromosome
    def evaluate_fitness(self):
        logging.debug("Starting fitness evaluation.")
        self.fitness = 0
        mw_count, tr_count = 0, 0
        course_assignments = set()

        preference_weight = 5  # Adjusted weight for teacher preferences
        satisfaction_weight = 2  # Adjusted weight for teacher satisfaction
        deviation_penalty = 30  # Increased penalty for deviations from preferences
        balance_penalty_weight = 10  # Adjusted weight for imbalance penalty

        for gene in self.genes:
            course, room, time_slot, teacher_id = gene

            # Balance MWF and TR courses
            if any(day in time_slot["Description"] for day in ["M", "W", "F"]):
                mw_count += 1
            if any(day in time_slot["Description"] for day in ["T", "R"]):
                tr_count += 1
            logging.debug(
                f"Course {course['Course Section ID']} contributes to MW_count: {mw_count}, TR_count: {tr_count}"
            )

            # Check for duplicate course assignments
            course_id = course["Course Section ID"]
            if course_id in course_assignments:
                self.fitness -= 5  # Penalty for duplicate assignment
                logging.warning(
                    f"Duplicate Assignment Detected for Course {course_id}, applying penalty"
                )
            else:
                course_assignments.add(course_id)

            # Evaluate teacher preferences
            preference_score = self.evaluate_teacher_preferences(
                teacher_id, course, room, time_slot
            )
            logging.debug(
                f"Teacher preference score for course {course_id}: {preference_score}"
            )

            # Retrieve teacher satisfaction score
            satisfaction_score = self.teacher_satisfaction[teacher_id][
                f"CS{course['Course Section ID']}"
            ]
            logging.debug(
                f"Teacher satisfaction score for course {course_id}: {satisfaction_score}"
            )

            # Apply weighted scoring for preferences and satisfaction
            self.fitness += preference_score * preference_weight
            self.fitness += satisfaction_score * satisfaction_weight

            # Penalize deviations from preferences
            if self.not_meeting_preferences(teacher_id, course, room, time_slot):
                self.fitness -= deviation_penalty
                logging.debug(f"Deviation penalty applied for course {course_id}")

        # Calculate and apply the penalty for imbalance between MWF and TTh courses
        balance_delta = abs(mw_count - tr_count)
        self.fitness -= balance_delta * balance_penalty_weight
        logging.debug(
            f"Balance penalty applied: MW_count - {mw_count}, TR_count - {tr_count}, Delta - {balance_delta}"
        )

        logging.info("Fitness evaluation completed. Fitness: " + str(self.fitness))


# class GeneticAlgorithm:
# Description: This class represents the genetic algorithm itself. It includes methods for
# initializing the algorithm, performing selection, crossover, mutate, and running the
# algorithm to find an optimal or satisfactory solution.
class GeneticAlgorithm:
    # def __init__(
    # Description: This method is responsible for initializing a new instance of the GeneticAlgorithm class.
    # It sets up the algorithm with necessary parameters such as course sections, classrooms, and time slots.
    def __init__(
        self,
        course_sections,  # A list of course sections
        classrooms,  # A list of classrooms
        time_slots,  # A list of available time slots
        teacher_preferences,  # A dictionary of teacher preferences
        teacher_satisfaction,  # A dictionary of teacher satisfaction scores
        population_size,  # The size of the population for the genetic algorithm
    ):
        logging.info(
            "Initializing Genetic Algorithm with population size: "
            + str(population_size)
        )
        # Initialization of class attributes
        self.course_sections = course_sections
        self.classrooms = classrooms
        self.time_slots = time_slots
        self.teacher_preferences = teacher_preferences
        self.teacher_satisfaction = teacher_satisfaction

        # Creating an initial population of chromosomes
        self.population = [
            Chromosome(
                course_sections,
                classrooms,
                time_slots,
                teacher_preferences,
                teacher_satisfaction,
            )
            for _ in range(population_size)
        ]
        logging.debug("Genetic Algorithm initialized.")

    # Method for selecting parents from the population
    def selection(self):
        logging.debug("Selecting parents for crossover.")
        tournament = random.sample(self.population, 7)  # Tournament selection
        return sorted(tournament, key=lambda c: c.fitness, reverse=True)[
            :2
        ]  # Select top 2

    # Method for crossing over two parent chromosomes to create a child
    def crossover(self, parent1, parent2):
        logging.debug("Starting crossover for selected parents.")
        child = Chromosome(
            self.course_sections,
            self.classrooms,
            self.time_slots,
            self.teacher_preferences,
            self.teacher_satisfaction,
        )

        # Initialize child's genes and a set to track assigned slots
        child.genes = []
        assigned_slots = set()

        for gene1, gene2 in zip(parent1.genes, parent2.genes):
            # Choose a gene from either parent based on a random choice
            chosen_gene = gene1 if random.random() < 0.5 else gene2

            # Check for double-booking and select new room and time slot if necessary
            while (
                chosen_gene[1]["Room Number"],
                chosen_gene[2]["Time Slot ID"],
            ) in assigned_slots:
                chosen_gene = (
                    chosen_gene[0],
                    random.choice(self.classrooms),
                    random.choice(self.time_slots),
                    chosen_gene[3],
                )

            # Add the chosen gene to the child and update the assigned slots
            child.genes.append(chosen_gene)
            assigned_slots.add(
                (chosen_gene[1]["Room Number"], chosen_gene[2]["Time Slot ID"])
            )

        child.evaluate_fitness()
        logging.debug(f"Crossover result: Fitness - {child.fitness}")
        return child

    # Method for mutating a chromosome
    def mutate(self, chromosome):
        logging.info("Performing Mutation")
        idx = random.randint(0, len(chromosome.genes) - 1)
        gene = chromosome.genes[idx]

        # Randomly choose to change either the room or the time slot
        if random.random() < 0.5:
            new_room = random.choice(self.classrooms)
            gene = (gene[0], new_room, gene[2], gene[3])
        else:
            new_time_slot = random.choice(self.time_slots)
            gene = (gene[0], gene[1], new_time_slot, gene[3])

        chromosome.genes[idx] = gene
        chromosome.evaluate_fitness()
        logging.info("Mutation result: " + str(chromosome))

    def compute_summary_statistics(self):
        stats = {
            "total_courses": len(self.course_sections),
            "distribution": {"MWF": 0, "TR": 0},
            "teacher_preference_adherence": 0,
            "teacher_satisfaction": 0,
        }
        for chromosome in self.population:
            for gene in chromosome.genes:
                time_slot = gene[2]["Description"]
                teacher_id = gene[3]
                stats["distribution"][
                    "MWF" if any(d in time_slot for d in ["M", "W", "F"]) else "TR"
                ] += 1
                if not chromosome.not_meeting_preferences(teacher_id, *gene[:3]):
                    stats["teacher_preference_adherence"] += 1
                stats["teacher_satisfaction"] += self.teacher_satisfaction[teacher_id][
                    f"CS{gene[0]['Course Section ID']}"
                ]

        stats["teacher_preference_adherence"] /= len(self.population[0].genes)
        stats["teacher_satisfaction"] /= len(self.population[0].genes)
        return stats

    def run(self, generations):
        mutation_probability = 0.2  # Probability of mutation
        all_generation_statistics = []  # List to store statistics for each generation

        for generation in range(generations):
            logging.info(f"Starting Generation: {generation + 1}")
            new_population = []

            # Keeping the best chromosomes from the current population
            best_chromosomes = sorted(
                self.population, key=lambda c: c.fitness, reverse=True
            )[:2]
            new_population.extend(best_chromosomes)

            # Generate new chromosomes until the population is replenished
            while len(new_population) < len(self.population):
                parents = self.selection()
                child = self.crossover(parents[0], parents[1])
                if random.random() < mutation_probability:
                    self.mutate(child)
                new_population.append(child)

            # Replace the old population with the new one
            self.population = sorted(
                new_population, key=lambda c: c.fitness, reverse=True
            )

            # Compute and collect summary statistics for this generation
            summary_stats = self.compute_summary_statistics()
            summary_stats["generation"] = generation + 1  # Add generation number
            all_generation_statistics.append(summary_stats)

            logging.info(f"Completed Generation: {generation + 1}")

        return all_generation_statistics  # Return the statistics for all generations

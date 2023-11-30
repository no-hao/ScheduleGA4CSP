import random
import logging


class Chromosome:
    # Constructor for the Chromosome class
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
        # Formatting each gene in the chromosome for display
        gene_str = "\n".join(
            [
                f"Course: {gene[0]['Course Section ID']}, Room: {gene[1]['Room Number']}, "
                f"Time Slot: {gene[2]['Time Slot ID']}, Teacher: {gene[3]}"
                for gene in self.genes
            ]
        )
        return f"Chromosome (Fitness: {self.fitness}):\n{gene_str}"

    # Method to check if the chromosome is valid
    def is_valid(self):
        # Ensuring that no teacher is assigned more sections than allowed
        teacher_section_count = {
            teacher_id: 0 for teacher_id in self.teacher_preferences
        }
        for _, _, _, teacher_id in self.genes:
            teacher_section_count[teacher_id] += 1
            if (
                teacher_section_count[teacher_id]
                > self.teacher_preferences[teacher_id]["Max Sections"]
            ):
                logging.warning(
                    f"Chromosome is invalid due to teacher {teacher_id} exceeding max sections."
                )
                return False  # Invalid if a teacher exceeds their max section limit
        return True  # Valid if all teachers are within their section limits

    # Method to initialize the chromosome with random values
    def initialize_randomly(self):
        logging.info("Initializing Chromosome Randomly")
        assigned_slots = set()  # Tracks assigned room and time slot combinations
        teacher_assignments = {teacher_id: 0 for teacher_id in self.teacher_preferences}
        logging.info("Initializing Chromosome Randomly")

        for section in self.course_sections:
            # Randomly select a room and time slot, ensuring no double-booking
            room = random.choice(self.classrooms)
            time_slot = random.choice(self.time_slots)
            while (room["Room Number"], time_slot["Time Slot ID"]) in assigned_slots:
                room = random.choice(self.classrooms)
                time_slot = random.choice(self.time_slots)

            # Choosing an eligible teacher for the course section
            eligible_teachers = [
                tid
                for tid, count in teacher_assignments.items()
                if count < self.teacher_preferences[tid]["Max Sections"]
            ]
            if not eligible_teachers:
                eligible_teachers = list(self.teacher_preferences.keys())
            teacher_id = random.choice(eligible_teachers)
            teacher_assignments[teacher_id] += 1

            # Add the chosen combination to the chromosome
            assigned_slots.add((room["Room Number"], time_slot["Time Slot ID"]))
            self.genes.append((section, room, time_slot, teacher_id))
            logging.debug(
                f"Assigned course {section['Course Section ID']} to room {room['Room Number']}, time slot {time_slot['Time Slot ID']}, teacher {teacher_id}"
            )

        logging.debug("Random initialization of chromosome completed.")

    # Method to check if a teacher's preferences are not met
    def not_meeting_preferences(self, teacher_id, course, room, time_slot):
        preferences = self.teacher_preferences[teacher_id]
        # Checks if various preferences (board, time, days, type) are not met
        # Returns True if any preference is violated

        # Check board preference
        if (
            preferences["Board Pref"] != 0
            and room["Board Type"] != preferences["Board Pref"]
        ):
            return True

        # Check time preference
        if preferences["Time Pref"] != 0:
            if (
                preferences["Time Pref"] == 1
                and "am" not in time_slot["Description"].lower()
            ):
                return True
            elif preferences["Time Pref"] == 2 and (
                "pm" not in time_slot["Description"].lower()
                or "11" in time_slot["Description"]
            ):
                return True
            elif (
                preferences["Time Pref"] == 3
                and "evening" not in time_slot["Description"].lower()
            ):
                return True

        # Check days preference
        if preferences["Days Pref"] != 0:
            if preferences["Days Pref"] == 1 and "MWF" not in time_slot["Description"]:
                return True
            elif preferences["Days Pref"] == 2 and "TR" not in time_slot["Description"]:
                return True

        # Check type preference
        if (
            preferences["Type Pref"] != 0
            and course["Course Type"] != preferences["Type Pref"]
        ):
            return True

        # If none of the preferences are violated
        return False

    # Method to improve the schedule represented by the chromosome
    def improve_schedule(self):
        # Randomly mutates a gene to potentially improve the chromosome
        # Method for improving the current chromosome instance
        logging.debug("Improving chromosome with initial fitness: " + str(self.fitness))
        mutation_index = random.randint(0, len(self.genes) - 1)
        gene = self.genes[mutation_index]
        new_time_slot = random.choice(self.time_slots)
        self.genes[mutation_index] = (gene[0], gene[1], new_time_slot, gene[3])

        # Re-evaluate fitness after improvement
        self.evaluate_fitness()

        logging.debug("Post-improvement fitness: " + str(self.fitness))
        return self

    # Method to evaluate the fitness of the chromosome
    def evaluate_fitness(self):
        logging.debug("Starting fitness evaluation.")
        self.fitness = 0
        mw_count, tr_count = 0, 0
        course_assignments = set()

        preference_weight = 2  # Adjusted weight for teacher preferences
        satisfaction_weight = 2  # Adjusted weight for teacher satisfaction
        deviation_penalty = 10  # Increased penalty for deviations from preferences
        balance_penalty_weight = 5  # Adjusted weight for imbalance penalty

        for gene in self.genes:
            course, room, time_slot, teacher_id = gene

            # Balance MWF and TR courses
            if (
                "M" in time_slot["Description"]
                or "W" in time_slot["Description"]
                or "F" in time_slot["Description"]
            ):
                mw_count += 1
            if "T" in time_slot["Description"] or "R" in time_slot["Description"]:
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

    # Method to evaluate a teacher's preference score
    def evaluate_teacher_preferences(self, teacher_id, course, room, time_slot):
        preferences = self.teacher_preferences[teacher_id]
        satisfaction_scores = self.teacher_satisfaction[teacher_id]

        preference_score = 0
        # Calculate preference score based on various criteria (board, time, days, type)

        if (
            preferences["Board Pref"] != 0
            and room["Board Type"] == preferences["Board Pref"]
        ):
            preference_score += 1

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

        if preferences["Days Pref"] != 0:
            if preferences["Days Pref"] == 1 and "MWF" in time_slot["Description"]:
                preference_score += 1
            elif preferences["Days Pref"] == 2 and "TR" in time_slot["Description"]:
                preference_score += 1

        if (
            preferences["Type Pref"] != 0
            and course["Course Type"] == preferences["Type Pref"]
        ):
            preference_score += 1

        satisfaction_score = satisfaction_scores[f"CS{course['Course Section ID']}"]

        logging.debug(
            f"Calculated preference score for teacher {teacher_id}: {preference_score}"
        )
        return preference_score + satisfaction_score


class GeneticAlgorithm:
    # Constructor for the GeneticAlgorithm class
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
        tournament_size = 7  # Increased tournament size for more diversity
        tournament = random.sample(self.population, tournament_size)
        parent1 = max(tournament, key=lambda c: c.fitness)
        tournament.remove(parent1)
        parent2 = max(tournament, key=lambda c: c.fitness)
        logging.debug(
            f"Parents selected with fitness scores: {parent1.fitness}, {parent2.fitness}"
        )
        return parent1, parent2

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
        child.genes = []
        assigned_slots = set()

        for i in range(len(parent1.genes)):
            # Select a gene from one of the parents
            gene = parent1.genes[i] if random.random() < 0.5 else parent2.genes[i]
            # Ensure no double-booking in the child chromosome
            while (gene[1]["Room Number"], gene[2]["Time Slot ID"]) in assigned_slots:
                gene = (
                    gene[0],
                    random.choice(self.classrooms),
                    random.choice(self.time_slots),
                    gene[3],
                )

            assigned_slots.add((gene[1]["Room Number"], gene[2]["Time Slot ID"]))
            child.genes.append(gene)

        child.evaluate_fitness()
        logging.info("Crossover result: " + str(child))
        return child

    # Method for mutating a chromosome
    def mutation(self, chromosome):
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

    # Main method to run the genetic algorithm
    def run(self, generations):
        mutation_probability = 0.2  # Probability of mutation
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
                    self.mutation(child)
                new_population.append(child)

            # Replace the old population with the new one
            self.population = sorted(
                new_population, key=lambda c: c.fitness, reverse=True
            )
            logging.info(
                "New population established. Size: " + str(len(self.population))
            )
            logging.info(
                f"Best Chromosome Fitness in Generation {generation + 1}: {self.population[0].fitness}"
            )
            logging.info(f"Completed Generation: {generation + 1}")

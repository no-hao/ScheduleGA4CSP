import random
import logging


class Chromosome:
    def __init__(
        self,
        ga,  # GeneticAlgorithm instance
        course_sections,  # A list of course sections
        classrooms,  # A list of classrooms
        time_slots,  # A list of available time slots
        teacher_preferences,  # A dictionary of teacher preferences
        teacher_satisfaction,  # A dictionary of teacher satisfaction scores
    ):
        logging.debug("Initializing new Chromosome instance.")
        self.ga = ga
        self.course_sections = course_sections
        self.classrooms = classrooms
        self.time_slots = time_slots
        self.teacher_preferences = teacher_preferences
        self.teacher_satisfaction = teacher_satisfaction
        self.genes = []  # List to store genes; each gene represents a course scheduling decision
        self.fitness = 0  # Fitness score of the chromosome

        self.initialize_randomly()
        self.evaluate_fitness()
        logging.debug("Chromosome initialized with random genes.")

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

    def is_valid(self):
        logging.debug("Checking if chromosome is valid.")
        teacher_section_count = {
            teacher_id: 0 for teacher_id in self.teacher_preferences
        }
        for _, _, _, teacher_id in self.genes:
            teacher_section_count[teacher_id] += 1

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

    def initialize_randomly(self):
        logging.info("Initializing Chromosome Randomly")
        self.genes = []
        assigned_slots = set()

        all_combinations = [
            (room, time_slot)
            for room in self.classrooms
            for time_slot in self.time_slots
        ]
        random.shuffle(all_combinations)

        teacher_assignments = {teacher_id: 0 for teacher_id in self.teacher_preferences}

        for section in self.course_sections:
            room, time_slot = all_combinations.pop()

            eligible_teachers = [
                tid
                for tid, count in teacher_assignments.items()
                if count < self.teacher_preferences[tid]["Max Sections"]
            ]
            if not eligible_teachers:
                eligible_teachers = list(self.teacher_preferences.keys())

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

            teacher_id = random.choices(
                eligible_teachers, weights=teacher_satisfaction_weights, k=1
            )[0]
            teacher_assignments[teacher_id] += 1

            self.genes.append((section, room, time_slot, teacher_id))
            assigned_slots.add((room["Room Number"], time_slot["Time Slot ID"]))

        logging.debug("Random initialization of chromosome completed.")

    @staticmethod
    def calculate_load_balance(teachers_actual_load, teacher_preferences):
        total_deviation = 0
        for teacher_id, actual_load in teachers_actual_load.items():
            min_sections = teacher_preferences[teacher_id]["Min Sections"]
            max_sections = teacher_preferences[teacher_id]["Max Sections"]
            ideal_load = (min_sections + max_sections) / 2
            deviation = abs(actual_load - ideal_load)
            total_deviation += deviation
        return total_deviation

    def not_meeting_preferences(self, teacher_id, course, room, time_slot):
        logging.debug(f"Checking if preferences are met for teacher {teacher_id}.")
        preferences = self.teacher_preferences[teacher_id]

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

        preference_violated = any(conditions)

        if preference_violated:
            logging.debug(f"Preference violation found for teacher {teacher_id}.")
        else:
            logging.debug(f"No preference violation for teacher {teacher_id}.")

        return preference_violated

    def evaluate_teacher_preferences(self, teacher_id, course, room, time_slot):
        logging.debug(f"Evaluating preferences for teacher {teacher_id}.")
        preferences = self.teacher_preferences[teacher_id]

        preference_score = 0

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

        satisfaction_score = self.teacher_satisfaction[teacher_id][
            f"CS{course['Course Section ID']}"
        ]
        total_score = preference_score + satisfaction_score

        logging.debug(f"Total preference score for teacher {teacher_id}: {total_score}")
        return total_score

    def evaluate_fitness(self):
        logging.debug("Starting fitness evaluation.")
        self.fitness = 0
        mw_count, tr_count = 0, 0
        course_assignments = set()

        balance_score = 0  # Initialize balance score
        load_balance_score = 0
        satisfaction_score = 0

        for gene in self.genes:
            course, room, time_slot, teacher_id = gene

            if any(day in time_slot["Description"] for day in ["M", "W", "F"]):
                mw_count += 1
            if any(day in time_slot["Description"] for day in ["T", "R"]):
                tr_count += 1

            if course["Course Section ID"] in course_assignments:
                self.fitness -= 5
                logging.warning(
                    f"Duplicate Assignment Detected for Course {course['Course Section ID']}, applying penalty"
                )
            else:
                course_assignments.add(course["Course Section ID"])

            preference_score = self.evaluate_teacher_preferences(
                teacher_id, course, room, time_slot
            )
            satisfaction_score = self.teacher_satisfaction[teacher_id][
                f"CS{course['Course Section ID']}"
            ]

            self.fitness += preference_score * self.ga.preference_weight
            self.fitness += satisfaction_score * self.ga.satisfaction_weight

            if self.not_meeting_preferences(teacher_id, course, room, time_slot):
                self.fitness -= self.ga.deviation_penalty

        # Calculate the balance score based on the counts of MWF and TR courses
        balance_delta = abs(mw_count - tr_count)
        balance_score = 1 / (1 + balance_delta)  # Example scoring function

        # Apply the balance penalty weight
        self.fitness -= balance_delta * self.ga.balance_penalty_weight

        teachers_actual_load = {
            teacher_id: 0 for teacher_id in self.teacher_preferences
        }
        for _, _, _, teacher_id in self.genes:
            teachers_actual_load[teacher_id] += 1

        T = len(self.genes)  # Total number of teaching assignments
        load_balance_score = (
            Chromosome.calculate_load_balance(
                teachers_actual_load, self.teacher_preferences
            )
            / T
        )

        # Update the overall fitness score by incorporating the balance_score
        self.fitness = (
            self.ga.omega1 * balance_score
            + self.ga.omega2 * load_balance_score
            + self.ga.omega3 * satisfaction_score
        )

        logging.info("Fitness evaluation completed. Fitness: " + str(self.fitness))


class GeneticAlgorithm:
    def __init__(
        self,
        course_sections,  # A list of course sections
        classrooms,  # A list of classrooms
        time_slots,  # A list of available time slots
        teacher_preferences,  # A dictionary of teacher preferences
        teacher_satisfaction,  # A dictionary of teacher satisfaction scores
        population_size,  # The size of the population for the genetic algorithm
        omega1,  # Weight for day-of-week balance
        omega2,  # Weight for teaching load balance
        omega3,  # Weight for teacher satisfaction
    ):
        logging.info(
            "Initializing Genetic Algorithm with population size: "
            + str(population_size)
        )
        self.course_sections = course_sections
        self.classrooms = classrooms
        self.time_slots = time_slots
        self.teacher_preferences = teacher_preferences
        self.teacher_satisfaction = teacher_satisfaction
        self.population_size = population_size
        self.omega1 = omega1
        self.omega2 = omega2
        self.omega3 = omega3

        # Additional weights for the fitness function
        self.preference_weight = 5
        self.satisfaction_weight = 2
        self.deviation_penalty = 30
        self.balance_penalty_weight = 10

        self.population = [
            Chromosome(
                self,
                course_sections,
                classrooms,
                time_slots,
                teacher_preferences,
                teacher_satisfaction,
            )
            for _ in range(population_size)
        ]
        logging.debug("Genetic Algorithm initialized.")

    def selection(self):
        logging.debug("Selecting parents for crossover.")
        tournament = random.sample(self.population, 7)  # Tournament selection
        return sorted(tournament, key=lambda c: c.fitness, reverse=True)[:2]

    def crossover(self, parent1, parent2):
        logging.debug("Starting crossover for selected parents.")
        child = Chromosome(
            self,
            self.course_sections,
            self.classrooms,
            self.time_slots,
            self.teacher_preferences,
            self.teacher_satisfaction,
        )

        child.genes = []
        assigned_slots = set()

        for gene1, gene2 in zip(parent1.genes, parent2.genes):
            chosen_gene = gene1 if random.random() < 0.5 else gene2

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

            child.genes.append(chosen_gene)
            assigned_slots.add(
                (chosen_gene[1]["Room Number"], chosen_gene[2]["Time Slot ID"])
            )

        child.evaluate_fitness()
        logging.debug(f"Crossover result: Fitness - {child.fitness}")
        return child

    def mutate(self, chromosome):
        logging.info("Performing Mutation")
        gene_index = random.randint(0, len(chromosome.genes) - 1)
        mutated_gene = self._mutate_gene(chromosome.genes[gene_index])

        chromosome.genes[gene_index] = mutated_gene
        chromosome.evaluate_fitness()
        logging.info("Mutation result: " + str(chromosome))

    def _mutate_gene(self, gene):
        if random.random() < 0.5:
            new_room = random.choice(self.classrooms)
            return (gene[0], new_room, gene[2], gene[3])
        else:
            new_time_slot = random.choice(self.time_slots)
            return (gene[0], gene[1], new_time_slot, gene[3])

    def compute_statistics(self):
        logging.debug("Computing summary statistics for the population.")
        total_genes = len(self.course_sections) * len(self.population)
        stats = {
            "total_courses": len(self.course_sections),
            "distribution": {"MWF": 0, "TR": 0},
            "teacher_preference_adherence": 0,
            "teacher_satisfaction": 0,
            "average_fitness": 0,
            "max_fitness": 0,
            "preference_violations": 0,
            "course_assignment_duplicates": 0,
        }

        total_fitness = 0
        max_fitness = -float("inf")
        for chromosome in self.population:
            total_fitness += chromosome.fitness
            max_fitness = max(max_fitness, chromosome.fitness)

            duplicate_courses = set()
            for gene in chromosome.genes:
                time_slot = gene[2]["Description"]
                day_key = (
                    "MWF" if any(d in time_slot for d in ["M", "W", "F"]) else "TR"
                )
                stats["distribution"][day_key] += 1

                teacher_id = gene[3]
                preference_score = chromosome.evaluate_teacher_preferences(
                    teacher_id, *gene[:3]
                )
                stats["teacher_preference_adherence"] += preference_score
                stats["teacher_satisfaction"] += self.teacher_satisfaction[teacher_id][
                    f"CS{gene[0]['Course Section ID']}"
                ]

                course_id = gene[0]["Course Section ID"]
                if course_id in duplicate_courses:
                    stats["course_assignment_duplicates"] += 1
                else:
                    duplicate_courses.add(course_id)

                if chromosome.not_meeting_preferences(teacher_id, *gene[:3]):
                    stats["preference_violations"] += 1

        # Convert distribution to percentage
        total_courses = stats["distribution"]["MWF"] + stats["distribution"]["TR"]
        stats["distribution"]["MWF"] = (
            stats["distribution"]["MWF"] / total_courses
        ) * 100
        stats["distribution"]["TR"] = (
            stats["distribution"]["TR"] / total_courses
        ) * 100

        # Convert teacher satisfaction and preference adherence to an average percentage score
        stats["teacher_satisfaction"] = (
            stats["teacher_satisfaction"] / total_genes / 5
        ) * 100
        stats["teacher_preference_adherence"] = (
            stats["teacher_preference_adherence"] / total_genes / 5
        ) * 100

        # Convert preference violations to percentage
        stats["preference_violations"] = (
            stats["preference_violations"] / total_genes
        ) * 100

        # Average fitness and max fitness can be normalized if desired
        stats["average_fitness"] = total_fitness / len(self.population)
        stats["max_fitness"] = max_fitness

        logging.info("Summary statistics computed.")
        return stats

    def run(self, generations):
        logging.info(f"Running Genetic Algorithm for {generations} generations.")
        mutation_probability = 0.2
        all_generation_statistics = []

        for generation in range(generations):
            logging.info(f"Generation {generation + 1} started.")
            self._evolve_population(mutation_probability)
            summary_stats = self.compute_statistics()
            summary_stats["generation"] = generation + 1
            all_generation_statistics.append(summary_stats)
            logging.info(f"Generation {generation + 1} completed.")

        logging.info("Genetic Algorithm run completed.")
        return all_generation_statistics

    def _evolve_population(self, mutation_probability):
        new_population = self._select_and_breed_population()
        self._mutate_population(new_population, mutation_probability)
        self.population = sorted(new_population, key=lambda c: c.fitness, reverse=True)

    def _select_and_breed_population(self):
        new_population = []
        new_population.extend(
            sorted(self.population, key=lambda c: c.fitness, reverse=True)[:2]
        )

        while len(new_population) < len(self.population):
            parent1, parent2 = self.selection()
            child = self.crossover(parent1, parent2)
            new_population.append(child)

        return new_population

    def _mutate_population(self, population, mutation_probability):
        for chromosome in population:
            if random.random() < mutation_probability:
                self.mutate(chromosome)

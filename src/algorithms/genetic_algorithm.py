import random
import logging


class Chromosome:
    def __init__(
        self,
        course_sections,
        classrooms,
        time_slots,
        teacher_preferences,
        teacher_satisfaction,
    ):
        self.course_sections = course_sections
        self.classrooms = classrooms
        self.time_slots = time_slots
        self.teacher_preferences = teacher_preferences
        self.teacher_satisfaction = teacher_satisfaction
        self.genes = []  # Each gene is a tuple (CourseSection, Classroom, TimeSlot, Teacher)
        self.fitness = 0
        self.initialize_randomly()
        self.evaluate_fitness()

    def __str__(self):
        gene_str = "\n".join(
            [
                f"Course: {gene[0]['Course Section ID']}, Room: {gene[1]['Room Number']}, "
                f"Time Slot: {gene[2]['Time Slot ID']}, Teacher: {gene[3]}"
                for gene in self.genes
            ]
        )
        return f"Chromosome (Fitness: {self.fitness}):\n{gene_str}"

    def is_valid(self):
        return self.fitness >= 0

    def initialize_randomly(self):
        assigned_slots = set()
        teacher_assignments = {teacher_id: 0 for teacher_id in self.teacher_preferences}
        logging.info("Initializing Chromosome Randomly")

        for section in self.course_sections:
            room = random.choice(self.classrooms)
            time_slot = random.choice(self.time_slots)
            while (room["Room Number"], time_slot["Time Slot ID"]) in assigned_slots:
                room = random.choice(self.classrooms)
                time_slot = random.choice(self.time_slots)

            eligible_teachers = [
                tid
                for tid, count in teacher_assignments.items()
                if count < self.teacher_preferences[tid]["Max Sections"]
            ]
            if not eligible_teachers:
                eligible_teachers = list(self.teacher_preferences.keys())
            teacher_id = random.choice(eligible_teachers)
            teacher_assignments[teacher_id] += 1

            assigned_slots.add((room["Room Number"], time_slot["Time Slot ID"]))
            self.genes.append((section, room, time_slot, teacher_id))
            logging.debug(
                f"Assigned course {section['Course Section ID']} to room {room['Room Number']}, time slot {time_slot['Time Slot ID']}, teacher {teacher_id}"
            )

        logging.info("Chromosome Initialized")

    def evaluate_fitness(self):
        logging.info("Evaluating Fitness...")
        self.fitness = 0
        mw_count, tr_count = 0, 0
        course_assignments = set()

        for gene in self.genes:
            course, room, time_slot, teacher_id = gene
            if (
                "MW" in time_slot["Description"]
                or "WF" in time_slot["Description"]
                or "MF" in time_slot["Description"]
            ):
                mw_count += 1
            elif "TR" in time_slot["Description"]:
                tr_count += 1

            course_id = course["Course Section ID"]
            if course_id in course_assignments:
                self.fitness -= 5
                logging.warning(f"Duplicate Assignment Detected for Course {course_id}")
            else:
                course_assignments.add(course_id)

            teacher_score = self.evaluate_teacher_preferences(
                teacher_id, course, room, time_slot
            )
            self.fitness += (5 - teacher_score) * 2

        balance_delta = abs(mw_count - tr_count)
        self.fitness -= balance_delta

        self.fitness = max(0, self.fitness)
        logging.info(f"Fitness Evaluated: {self.fitness}")

    def evaluate_teacher_preferences(self, teacher_id, course, room, time_slot):
        preferences = self.teacher_preferences[teacher_id]
        satisfaction_scores = self.teacher_satisfaction[teacher_id]

        preference_score = 0

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

        return preference_score + satisfaction_score


class GeneticAlgorithm:
    def __init__(
        self,
        course_sections,
        classrooms,
        time_slots,
        teacher_preferences,
        teacher_satisfaction,
        population_size,
    ):
        self.course_sections = course_sections
        self.classrooms = classrooms
        self.time_slots = time_slots
        self.teacher_preferences = teacher_preferences
        self.teacher_satisfaction = teacher_satisfaction
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

    def selection(self):
        tournament_size = 5
        tournament = random.sample(self.population, tournament_size)
        parent1 = max(tournament, key=lambda c: c.fitness)
        tournament.remove(parent1)
        parent2 = max(tournament, key=lambda c: c.fitness)
        logging.info(f"Selected parents: {parent1.fitness}, {parent2.fitness}")
        return parent1, parent2

    def crossover(self, parent1, parent2):
        logging.info("Performing Crossover")
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
            gene = parent1.genes[i] if random.random() < 0.5 else parent2.genes[i]
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

    def mutation(self, chromosome):
        logging.info("Performing Mutation")
        idx = random.randint(0, len(chromosome.genes) - 1)
        gene = chromosome.genes[idx]

        if random.random() < 0.5:
            new_room = random.choice(self.classrooms)
            gene = (gene[0], new_room, gene[2], gene[3])
        else:
            new_time_slot = random.choice(self.time_slots)
            gene = (gene[0], gene[1], new_time_slot, gene[3])

        chromosome.genes[idx] = gene
        chromosome.evaluate_fitness()
        logging.info("Mutation result: " + str(chromosome))

    def run(self, generations):
        for generation in range(generations):
            logging.info(f"Starting Generation: {generation + 1}")
            new_population = []

            best_chromosomes = sorted(
                self.population, key=lambda c: c.fitness, reverse=True
            )[:2]
            new_population.extend(best_chromosomes)

            while len(new_population) < len(self.population):
                parents = self.selection()
                child = self.crossover(parents[0], parents[1])
                self.mutation(child)

                if child.fitness < 0:
                    child.fitness = 0

                new_population.append(child)

            self.population = sorted(
                new_population, key=lambda c: c.fitness, reverse=True
            )
            logging.info(
                f"Best Chromosome Fitness in Generation {generation + 1}: {self.population[0].fitness}"
            )
            logging.info(f"Completed Generation: {generation + 1}")

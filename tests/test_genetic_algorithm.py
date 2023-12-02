import unittest
from src.algorithms.genetic_algorithm import Chromosome, GeneticAlgorithm
from src.utils.data_loader import DataLoader

# Create an instance of DataLoader to load the actual data from Simulated_Data.xlsx
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

population_size = 10


class TestChromosome(unittest.TestCase):
    def setUp(self):
        self.chromosome = Chromosome(
            course_sections,
            classrooms,
            time_slots,
            teacher_preferences,
            teacher_satisfaction,
        )

    def test_initialization(self):
        self.assertIsNotNone(self.chromosome)
        self.assertEqual(len(self.chromosome.genes), len(course_sections))

    def test_fitness_evaluation(self):
        self.chromosome.evaluate_fitness()
        self.assertIsInstance(self.chromosome.fitness, (int, float))

    def test_preference_evaluation(self):
        # Ensure this test reflects your implementation for evaluating preferences
        pass

    def test_validity(self):
        self.assertTrue(self.chromosome.is_valid())


class TestGeneticAlgorithm(unittest.TestCase):
    def setUp(self):
        self.ga = GeneticAlgorithm(
            course_sections,
            classrooms,
            time_slots,
            teacher_preferences,
            teacher_satisfaction,
            population_size,
        )

    def test_crossover(self):
        parent1 = self.ga.population[0]
        parent2 = self.ga.population[1]
        child = self.ga.crossover(parent1, parent2)
        self.assertIsInstance(child, Chromosome)

    def test_mutation(self):
        chromosome = self.ga.population[0]
        original_genes = chromosome.genes.copy()
        self.ga.mutation(chromosome)
        self.assertNotEqual(original_genes, chromosome.genes)

    def test_selection(self):
        parent1, parent2 = self.ga.selection()
        self.assertIsInstance(parent1, Chromosome)
        self.assertIsInstance(parent2, Chromosome)

    def test_run_algorithm(self):
        self.ga.run(5)
        self.assertTrue(len(self.ga.population) == population_size)


if __name__ == "__main__":
    unittest.main()

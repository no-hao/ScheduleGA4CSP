import unittest
from src.algorithms.ga_simulated import GeneticAlgorithm, Chromosome


class TestGeneticAlgorithm(unittest.TestCase):
    def test_chromosome_initialization(self):
        chromosome = Chromosome()
        # Add assertions to test chromosome initialization
        # For example, check if all courses are assigned and there are no duplicates
        self.assertIsNotNone(chromosome.genes)  # Example assertion

    def test_fitness_function(self):
        chromosome = Chromosome()
        initial_fitness = chromosome.fitness
        chromosome.evaluate_fitness()
        # Add assertions to test fitness evaluation
        # For example, check if fitness is evaluated correctly
        self.assertNotEqual(initial_fitness, chromosome.fitness)  # Example assertion

    # Add more test methods as needed


if __name__ == "__main__":
    unittest.main()

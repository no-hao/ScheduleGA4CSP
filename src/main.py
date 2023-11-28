from algorithms.genetic_algorithm import GeneticAlgorithm
from utils.data_loader import DataLoader


def main():
    # Load and preprocess data
    data_loader = DataLoader()
    data = data_loader.load_data("path_to_data")

    # Initialize Genetic Algorithm
    ga = GeneticAlgorithm(data)

    # Run the GA to find the best schedule
    best_schedule = ga.run()

    # Output the best schedule
    print("Best Schedule:", best_schedule)


if __name__ == "__main__":
    main()

# Project Title: Genetic Algorithm for Course Scheduling

## Overview
This project implements a Genetic Algorithm (GA) based on specific models described in an attached academic thesis. The core objective is to automate the course scheduling process for educational institutions, utilizing both simulated and real-world data, particularly focusing on the Math & Stats department at Cal Poly Pomona. The project's highlight is the implementation of the Teacher Tricriteria Model from the thesis, which integrates three key objectives for optimized scheduling.

## Model Description
The Teacher Tricriteria Model combines three distinct objectives: balancing the assignment of different weekday course-sections, minimizing the difference between assigned and ideal teaching loads, and maximizing teacher satisfaction. This approach allows for a holistic consideration of various scheduling constraints and preferences.

## System Requirements
- Python 3.x
- Additional Python libraries as imported in the project files (e.g., pandas, matplotlib, openpyxl).

## Installation
1. Ensure Python 3.x is installed on your system.
2. Clone the repository to your local machine.
3. Install required Python libraries: pip install pandas matplotlib openpyxl.

## Usage
Run the main.py script from the command line:
```bash
python main.py
```
Follow the on-screen prompts to select the data set and configure the GA parameters.

## Data Handling
The project utilizes two data sets:
- Simulated Data: For testing and validating the GA models as described in the thesis.
- Real-World Data: Actual course scheduling data from Cal Poly Pomona's Math & Stats department.

## Visualization and Output
The script generates visualizations for room occupancy and GA metrics, aiding in the analysis of the scheduling algorithm's performance. Outputs are also saved in Excel format for further review and comparison.

## Algorithm Details
The GA implemented in this project involves:
- Hypothesis Representation: How each potential solution (schedule) is represented in the GA.
- Evaluation Function: The criteria used to evaluate the effectiveness of each hypothesis.
- Selection Mechanism: The process of selecting hypotheses for crossover and mutation.
- Population Size: How the size of the hypothesis pool is determined and managed.
- Operations: Details on crossover and mutation techniques used in the GA.

## Contribution
Contributions to this project are welcome. Please follow standard coding practices and ensure thorough testing of any new features or bug fixes.

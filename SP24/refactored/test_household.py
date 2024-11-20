import random
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import time

'''
The idea is to generate the number of people in each of the 4 large categories (male/female children/adults) first so that the total population would be close to the actual distribution.

Then generate each household in a specific order based on the composition of the household.

Children are unique in that they cannot be alone in a household and can help us determine the age of the parents in the household.

1. We start by generating family households with 1 or 2 adults with children, using data on the number of children in households.
   Each household should subtract 2 or 1 adult and subtract the number of children from the population.
   This step should use up all the children in the population.

2. Family households without children
   Subtract 2 adults from the population.

3. Next, we generate non-family households (living alone and not living alone).
   Each household should subtract 1+ adult from the population.

Now the rest of the population consists of grandparents living with child/grandchild, other relatives, and some special cases.

4. Assign grandparents and other relatives to the existing family households.
   Add almost all of the remaining adults to a small portion of the households.

5. The remaining households are special cases.

5. Iterate through the generated households and refine the age to match the distribution.

This approach should not include any optimization and should be fast in generating the households.

'''

# '''
# Census population data:
# '''
# #s0101
# population_distribution =  {
#     "male_child": 11.12,
#     "male_adult": 38.37,
#     "female_child": 10.58,
#     "female_adult": 39.94
# },
#
#
# '''
# Census household data:
# '''
# # DP02 + B11001
# household_type_distribution = {
#     "family_households": 65.4,
#     "nonfamily_households": 34.6,
#     "with_children": 28.8,
# }
#
# avg_household_size = 2.49
#
# # https://www2.census.gov/programs-surveys/demo/tables/families/2023/cps-2023/taba3.xls
# children_distribution = {
#     "single_mother_child_distribution": {
#         "1": 0.435,
#         "2": 0.363,
#         "3": 0.141,
#         "4+": 0.062
#     },
#     "single_father_child_distribution": {
#         "1": 0.423,
#         "2": 0.375,
#         "3": 0.141,
#         "4+": 0.060
#     },
#     "two_parent_child_distribution": {
#         "1": 0.429,
#         "2": 0.369,
#         "3": 0.141,
#         "4+": 0.061
#     }
# }
# household_w_children_distribution = {
#     "married_couple_with_children": 0.6068,
#     "single_mother_with_children": 0.3345,
#     "single_father_with_children": 0.0587
# }
# parent_age_distribution = {
#     "married_couple_with_children": {
#         "15-24": 0.02,
#         "25-34": 0.25,
#         "35-44": 0.40,
#         "45-54": 0.25,
#         "55-64": 0.07,
#         "65+": 0.01
#     },
#     "single_mother_with_children": {
#         "15-24": 0.08,
#         "25-34": 0.30,
#         "35-44": 0.35,
#         "45-54": 0.20,
#         "55-64": 0.06,
#         "65+": 0.01
#     },
#     "single_father_with_children": {
#         "15-24": 0.03,
#         "25-34": 0.22,
#         "35-44": 0.38,
#         "45-54": 0.28,
#         "55-64": 0.08,
#         "65+": 0.01
#     }
# }
#
# # Added data for households with children aged 18-25
# married_couples_percentages = {
#     "with_children_18_25": 13.51,
#     "with_children_under_18": 73.16,
#     "without_children": 26.84
# }
#
# # S11001
# nonfamily_percentages = {
#     "living_alone": 28.8,
#     "not_living_alone": 5.8,
# }
# dp02 and dp05
# total population over 65: 59307056
# total households with 1+ over 65: 42291037
# 59307056 - 42291037 = 17016019
# 42291037 / 59307056 = 0.713 * 100 = 71.3%
# 17016019 / 59307056 = 0.287 * 100 = 28.7%


# 7.2% of U.S. Family Households Were Multigenerational in 2020
# https://www.census.gov/library/stories/2023/06/several-generations-under-one-roof.html


'''
Data Hierarchy:
'''

input_data = {
    "total_households": 100000,
    "avg_household_size": 2.49,
    "avg_family_size": 3.09,
    "pop_info": {
        "population_distribution": {
            "male_child": 11.12,
            "male_adult": 38.37,
            "female_child": 10.58,
            "female_adult": 39.94
        },
        "parent_age_distribution": {
            "married_couple_with_children": {
                "15-24": 2,
                "25-34": 25,
                "35-44": 40,
                "45-54": 25,
                "55-64": 7,
                "65+": 1
            },
            "single_mother_with_children": {
                "15-24": 8,
                "25-34": 30,
                "35-44": 35,
                "45-54": 20,
                "55-64": 6,
                "65+": 1
            },
            "single_father_with_children": {
                "15-24": 3,
                "25-34": 22,
                "35-44": 38,
                "45-54": 28,
                "55-64": 8,
                "65+": 1
            }
        },
        "married_couple_without_children_age_distribution": {
            "15-24": 5,
            "25-34": 20,
            "35-44": 20,
            "45-54": 25,
            "55-64": 20,
            "65+": 10
        }
    },
    "household_info": {
        "family_households": {
            "total_percentage": 65.4,
            "with_children_under_18": {
                "total_percentage": 28.8,
                "distribution": {
                    "married_couple_with_children": {
                        "total_percentage": 60.68,
                        "number_of_children": {
                            "1": 42.9,
                            "2": 36.9,
                            "3": 14.1,
                            "4+": 6.1
                        }
                    },
                    "single_mother_with_children": {
                        "total_percentage": 33.45,
                        "number_of_children": {
                            "1": 43.5,
                            "2": 36.3,
                            "3": 14.1,
                            "4+": 6.2
                        }
                    },
                    "single_father_with_children": {
                        "total_percentage": 5.87,
                        "number_of_children": {
                            "1": 42.3,
                            "2": 37.5,
                            "3": 14.1,
                            "4+": 6
                        }
                    }
                }
            },
            "with_over_65": {
                "total_percentage": 20.6,
                "multi_generational": 7.2,
            },
            "size_distribution": {  # b11016
                '2': 44.17,
                '3': 22.54,
                '4': 18.69,
                '5': 8.82,
                '6': 3.48,
                '7+': 2.29
            }
        },
        "nonfamily_households": {
            "total_percentage": 34.6,
            "living_alone": {
                "total_percentage": 28.8,
                "male_over_65": 4.0,
                "female_over_65": 7.7,
            },
            "not_living_alone": 5.8,
            "size_distribution": {
                '1': 80.02,
                '2': 16.62,
                '3': 2.08,
                '4': 0.89,
                '5': 0.25,
                '6': 0.08,
                '7+': 0.06
            }
            # b09016

        },
        "married_couples_percentages": {
            "with_children_18_25": 13.51,
            "with_children_under_18": 73.16,
            "without_children": 26.84
        },
        "with_1+_over_65": {
            "total_percentage": 32.2,
            "living_alone": 11.6,
            "with_family": 20.6
        },
    }
}

generational_gap = 30
generational_gap_std = 7

# Person class definition
class Person:
    _last_id = 0

    def __init__(self, age: int, sex: int, hh_id: int = None, position_in_hh: str = None, tags: dict = None,
                 cbg: int = None):
        """
        Initializes the Person class
        """
        self.id = Person._last_id
        Person._last_id += 1
        self.age = age
        self.sex = sex
        self.hh_id = hh_id
        self.tags = tags
        self.cbg = cbg
        self.position_in_hh = position_in_hh  # Added attribute

    def to_dict(self):
        return {
            "id": self.id,
            "age": self.age,
            "sex": "m" if self.sex == 0 else "f",
            "hh_id": self.hh_id,
            "position_in_hh": self.position_in_hh,
            "tags": self.tags,
            "cbg": self.cbg
        }


# Household class definition
class Household:
    _last_id = 0

    def __init__(self, population: list = [], type=None, cbg: int = None):
        """
        Initializes the Household class
        """
        self.id = Household._last_id
        Household._last_id += 1
        self.population = population
        self.cbg = cbg
        self.type = type

        # Assign household id to each person in the household
        for person in self.population:
            person.hh_id = self.id

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "population": [person.to_dict() for person in self.population],
            "cbg": self.cbg
        }


# Helper functions

def generate_number_of_children_4plus():
    """
    Generates a number of children 4 or more, with probabilities decreasing as the number increases.
    """
    number_of_children_options = [4, 5, 6, 7, 8]
    probabilities = [0.5, 0.25, 0.15, 0.07, 0.03]  # Adjusted probabilities
    probabilities = np.array(probabilities)
    probabilities = probabilities / probabilities.sum()  # Normalize
    number_of_children = np.random.choice(number_of_children_options, p=probabilities)
    return number_of_children


def generate_children_ages(parent_age, number_of_children, max_child_age=17, twin_probability=0.05):
    """
    Generates a list of children's ages based on parent's age and number of children.
    Ensures age difference of at least one year unless they are twins.
    """
    min_parental_age_at_birth = 15
    max_parental_age_at_birth = 50

    max_oldest_child_age = min(parent_age - min_parental_age_at_birth, max_child_age)
    min_oldest_child_age = max(parent_age - max_parental_age_at_birth, 0)

    if max_oldest_child_age < min_oldest_child_age:
        # Parent is too young; assign child age 0
        oldest_child_age = 0
    else:
        oldest_child_age = np.random.randint(min_oldest_child_age, max_oldest_child_age + 1)

    children_ages = [oldest_child_age]

    while len(children_ages) < number_of_children:
        # Check if twins should be added
        if np.random.random() < twin_probability:
            children_ages.append(children_ages[-1])  # Add a twin
        else:
            # Ensure at least one year age gap
            new_age = children_ages[-1] - np.random.randint(1, 4)
            if new_age < 0:
                new_age = 0
            children_ages.append(new_age)

    # Ensure all ages are between 0 and max_child_age
    children_ages = [max(min(age, max_child_age), 0) for age in children_ages]

    # Shuffle the ages to avoid ordering from oldest to youngest
    np.random.shuffle(children_ages)

    return children_ages


def get_people_distribution(total_population):
    population_distribution = input_data["pop_info"]["population_distribution"]
    total_percentage = sum(population_distribution.values())

    return {
        "male_child": int(total_population * population_distribution["male_child"] / total_percentage),
        "male_adult": int(total_population * population_distribution["male_adult"] / total_percentage),
        "female_child": int(total_population * population_distribution["female_child"] / total_percentage),
        "female_adult": int(total_population * population_distribution["female_adult"] / total_percentage),
    }


def print_all_households(households):
    for household in households:
        print("Household ID:", household.id)
        for person in household.population:
            print(person.to_dict())
        print("**********************************************\n")


def print_all_people(people):
    for person in people:
        print(person.to_dict())
        print("**********************************************\n")


# Function to generate households with children under 18
def generate_households_with_children_under_18(number_of_households_with_children, distribution_with_children,
                                               parent_age_distribution, age_ranges, people_counts, households, people):
    # Generate married couple households with children under 18
    num_married_couple_with_children = int(
        number_of_households_with_children * (
                distribution_with_children["married_couple_with_children"]["total_percentage"] / 100)
    )

    num_single_mother_with_children = int(
        number_of_households_with_children * (
                distribution_with_children["single_mother_with_children"]["total_percentage"] / 100)
    )

    num_single_father_with_children = int(
        number_of_households_with_children * (
                distribution_with_children["single_father_with_children"]["total_percentage"] / 100)
    )

    # Generate married couple households with children under 18
    num_married_couple_generated = 0

    # Added progress bar here
    for _ in tqdm(range(num_married_couple_with_children), desc="Generating married couples with children"):
        # Determine number of children
        num_children_dist = distribution_with_children["married_couple_with_children"]["number_of_children"]
        prob = [
            num_children_dist["1"],
            num_children_dist["2"],
            num_children_dist["3"],
            num_children_dist["4+"]
        ]
        prob = np.array(prob)
        prob = prob / prob.sum()  # Normalize

        num_child = np.random.choice(
            ['1', '2', '3', '4+'],
            p=prob
        )

        if num_child == '4+':
            number_of_children = generate_number_of_children_4plus()
        else:
            number_of_children = int(num_child)

        # Assign age group to parents
        age_group_probabilities = np.array(list(parent_age_distribution["married_couple_with_children"].values()))
        age_group_probabilities = age_group_probabilities / age_group_probabilities.sum()  # Normalize

        age_group = np.random.choice(
            list(parent_age_distribution["married_couple_with_children"].keys()),
            p=age_group_probabilities
        )
        age_range = age_ranges[age_group]

        # Assign ages to parents
        parent1_age = np.random.randint(age_range[0], age_range[1] + 1)
        parent2_age = np.random.randint(age_range[0], age_range[1] + 1)

        # Create parent Person objects with position_in_hh
        parent1 = Person(age=parent1_age, sex=0, position_in_hh='parent')  # Male
        parent2 = Person(age=parent2_age, sex=1, position_in_hh='parent')  # Female

        # Decrement counts
        people_counts["male_adult"] -= 1
        people_counts["female_adult"] -= 1

        household_population = [parent1, parent2]

        # Generate children's ages (up to 17)
        children_ages = generate_children_ages(min(parent1_age, parent2_age), number_of_children, max_child_age=17)

        for child_age in children_ages:
            total_children_remaining = people_counts["male_child"] + people_counts["female_child"]

            male_child_prob = people_counts["male_child"] / total_children_remaining if total_children_remaining > 0 \
                else (0.5 * input_data["pop_info"]["population_distribution"]["male_child"]
                      / input_data["pop_info"]["population_distribution"]["female_child"])

            child_sex = np.random.choice([0, 1], p=[male_child_prob, 1 - male_child_prob])
            child = Person(age=child_age, sex=child_sex, position_in_hh='child')
            if child_sex == 0:
                people_counts["male_child"] -= 1
            else:
                people_counts["female_child"] -= 1
            household_population.append(child)

        # Create Household
        household = Household(population=household_population, type="family")
        households.append(household)
        people.extend(household_population)
        num_married_couple_generated += 1
    # Return the number of married couples generated
    return num_married_couple_generated, num_single_mother_with_children, num_single_father_with_children


# Function to generate single parent households with children under 18
def generate_single_parent_households_with_children(num_single_mother_with_children, num_single_father_with_children,
                                                    distribution_with_children, parent_age_distribution, age_ranges,
                                                    people_counts, households, people):
    # Generate single mother households with children under 18
    for _ in tqdm(range(num_single_mother_with_children), desc="Generating single mothers with children"):
        num_children_dist = distribution_with_children["single_mother_with_children"]["number_of_children"]
        prob = [
            num_children_dist["1"],
            num_children_dist["2"],
            num_children_dist["3"],
            num_children_dist["4+"]
        ]
        prob = np.array(prob)
        prob = prob / prob.sum()  # Normalize

        num_child = np.random.choice(
            ['1', '2', '3', '4+'],
            p=prob
        )

        if num_child == '4+':
            number_of_children = generate_number_of_children_4plus()
        else:
            number_of_children = int(num_child)

        age_group_probabilities = np.array(list(parent_age_distribution["single_mother_with_children"].values()))
        age_group_probabilities = age_group_probabilities / age_group_probabilities.sum()  # Normalize

        age_group = np.random.choice(
            list(parent_age_distribution["single_mother_with_children"].keys()),
            p=age_group_probabilities
        )
        age_range = age_ranges[age_group]
        mother_age = np.random.randint(age_range[0], age_range[1] + 1)

        mother = Person(age=mother_age, sex=1, position_in_hh='parent')  # Female
        people_counts["female_adult"] -= 1
        household_population = [mother]

        # Generate children's ages (up to 17)
        children_ages = generate_children_ages(mother_age, number_of_children, max_child_age=17)

        for child_age in children_ages:
            total_children_remaining = people_counts["male_child"] + people_counts["female_child"]
            male_child_prob = people_counts["male_child"] / total_children_remaining if total_children_remaining > 0 \
                else (0.5 * input_data["pop_info"]["population_distribution"]["male_child"]
                      / input_data["pop_info"]["population_distribution"]["female_child"])
            child_sex = np.random.choice([0, 1], p=[male_child_prob, 1 - male_child_prob])
            child = Person(age=child_age, sex=child_sex, position_in_hh='child')
            if child_sex == 0:
                people_counts["male_child"] -= 1
            else:
                people_counts["female_child"] -= 1
            household_population.append(child)

        household = Household(population=household_population, type="family")
        households.append(household)
        people.extend(household_population)

    # Generate single father households with children under 18
    for _ in tqdm(range(num_single_father_with_children), desc="Generating single fathers with children"):
        num_children_dist = distribution_with_children["single_father_with_children"]["number_of_children"]
        prob = [
            num_children_dist["1"],
            num_children_dist["2"],
            num_children_dist["3"],
            num_children_dist["4+"]
        ]
        prob = np.array(prob)
        prob = prob / prob.sum()  # Normalize

        num_child = np.random.choice(
            ['1', '2', '3', '4+'],
            p=prob
        )

        if num_child == '4+':
            number_of_children = generate_number_of_children_4plus()
        else:
            number_of_children = int(num_child)

        age_group_probabilities = np.array(list(parent_age_distribution["single_father_with_children"].values()))
        age_group_probabilities = age_group_probabilities / age_group_probabilities.sum()  # Normalize

        age_group = np.random.choice(
            list(parent_age_distribution["single_father_with_children"].keys()),
            p=age_group_probabilities
        )
        age_range = age_ranges[age_group]
        father_age = np.random.randint(age_range[0], age_range[1] + 1)

        father = Person(age=father_age, sex=0, position_in_hh='parent')  # Male
        people_counts["male_adult"] -= 1
        household_population = [father]

        # Generate children's ages (up to 17)
        children_ages = generate_children_ages(father_age, number_of_children, max_child_age=17)

        for child_age in children_ages:
            total_children_remaining = people_counts["male_child"] + people_counts["female_child"]
            male_child_prob = people_counts["male_child"] / total_children_remaining if total_children_remaining > 0 \
                else (0.5 * input_data["pop_info"]["population_distribution"]["male_child"]
                      / input_data["pop_info"]["population_distribution"]["female_child"])
            child_sex = np.random.choice([0, 1], p=[male_child_prob, 1 - male_child_prob])
            child = Person(age=child_age, sex=child_sex, position_in_hh='child')
            if child_sex == 0:
                people_counts["male_child"] -= 1
            else:
                people_counts["female_child"] -= 1
            household_population.append(child)

        household = Household(population=household_population, type="family")
        households.append(household)
        people.extend(household_population)


# Function to generate family households without children
def generate_family_households_without_children(num_married_couple_without_children,
                                                married_couple_without_children_age_distribution, age_ranges,
                                                people_counts, households, people):
    # Generate married couple households without children
    for _ in tqdm(range(num_married_couple_without_children), desc="Generating married couples without children"):
        # Assign age group to partners
        age_group_probabilities = np.array(list(married_couple_without_children_age_distribution.values()))
        age_group_probabilities = age_group_probabilities / age_group_probabilities.sum()  # Normalize

        age_group = np.random.choice(
            list(married_couple_without_children_age_distribution.keys()),
            p=age_group_probabilities
        )
        age_range = age_ranges[age_group]

        # Assign ages to partners
        partner1_age = np.random.randint(age_range[0], age_range[1] + 1)
        partner2_age = np.random.randint(age_range[0], age_range[1] + 1)

        # Create partner Person objects with position_in_hh
        partner1 = Person(age=partner1_age, sex=0, position_in_hh='partner')  # Male
        partner2 = Person(age=partner2_age, sex=1, position_in_hh='partner')  # Female

        # Decrement counts
        people_counts["male_adult"] -= 1
        people_counts["female_adult"] -= 1

        household_population = [partner1, partner2]

        # Create Household
        household = Household(population=household_population, type="family")
        households.append(household)
        people.extend(household_population)


# Function to add grandparents to households
def add_grandparents_to_households(num_multi_generational_households, households, people_counts, people):
    family_households_with_children = [
        hh for hh in households
        if any(person.position_in_hh == 'child' and person.age < 18 for person in hh.population)
    ]

    selected_households = random.sample(
        family_households_with_children,
        k=min(num_multi_generational_households, len(family_households_with_children))
    )

    # Added progress bar here
    for household in tqdm(selected_households, desc="Adding grandparents to households"):
        # Determine the number of grandparents (1 or 2)
        num_grandparents = np.random.randint(1, 3)

        parent_ages = [person.age for person in household.population if person.position_in_hh == 'parent']
        if not parent_ages:
            print("ERROR: No parents found in household")
            continue

        youngest_parent_age = min(parent_ages)

        for _ in range(num_grandparents):
            # Determine grandparent's sex based on population distribution
            male_grandparent_prob = people_counts["male_adult"] / (
                    people_counts["male_adult"] + people_counts["female_adult"]
            )
            grandparent_sex = np.random.choice([0, 1], p=[male_grandparent_prob, 1 - male_grandparent_prob])

            # Calculate grandparent's age (parent's age + generational gap)
            grandparent_generational_gap = np.random.normal(30, 7)
            grandparent_generational_gap = int(max(18, min(45, grandparent_generational_gap)))  # cap
            grandparent_age = youngest_parent_age + grandparent_generational_gap

            # Create the grandparent
            grandparent = Person(age=grandparent_age, sex=grandparent_sex, position_in_hh='grandparent')

            # Update the people counts
            if grandparent_sex == 0:
                people_counts["male_adult"] -= 1
            else:
                people_counts["female_adult"] -= 1

            # Add the grandparent to the household
            household.population.append(grandparent)

            # add the grandparent to the people list
            people.append(grandparent)


# Function to generate remaining family households
def generate_remaining_family_households(remaining_family_households, input_data, age_ranges, people_counts, households, people):
    def gen_placeholder_household(count, hh_size, households, people):
        if count <= 0:
            return
        for _ in tqdm(range(count), desc=f"Generating family households of size {hh_size}"):
            population = []
            for _ in range(hh_size):
                age = np.random.randint(18, 90)
                total_people_remaining = people_counts["male_adult"] + people_counts["female_adult"]
                male_prob = people_counts["male_adult"] / total_people_remaining if total_people_remaining > 0 else 0.5
                sex = np.random.choice([0, 1], p=[male_prob, 1 - male_prob])
                p = Person(age=age, sex=sex, position_in_hh="family_member")
                # Update people counts
                if sex == 0:
                    people_counts["male_adult"] -= 1
                else:
                    people_counts["female_adult"] -= 1
                population.append(p)
            h = Household(population=population, type="family")
            households.append(h)
            people.extend(population)

    def get_hh_size_count(total_family_households):
        size_distribution = input_data["household_info"]["family_households"]["size_distribution"]
        size_counts = {}
        for k, v in size_distribution.items():
            size_counts[k] = int(v * total_family_households / 100)
        return size_counts

    household_sizes = ["2", "3", "4", "5", "6", "7+"]

    # Get target counts for each household size
    total_family_households = int(input_data["total_households"] * (input_data["household_info"]["family_households"]["total_percentage"] / 100))
    target_household_size_counts = get_hh_size_count(total_family_households)

    # Initialize counts for generated family households
    generated_household_size_counts = {size: 0 for size in household_sizes}
    for household in households:
        if household.type == "family":
            size = len(household.population)
            if size >= 7:
                generated_household_size_counts["7+"] += 1
            else:
                generated_household_size_counts[str(size)] += 1

    # Calculate remaining households needed for each size
    remaining_household_size_counts = {k: target_household_size_counts[k] - generated_household_size_counts.get(k, 0)
                                       for k in household_sizes}

    # Handle negative counts by redistributing surplus
    total_surplus = sum(-v for v in remaining_household_size_counts.values() if v < 0)
    if total_surplus > 0:
        under_generated_sizes = [k for k, v in remaining_household_size_counts.items() if v > 0]
        total_under_generated = sum(remaining_household_size_counts[k] for k in under_generated_sizes)
        for k in under_generated_sizes:
            addition = int((remaining_household_size_counts[k] / total_under_generated) * total_surplus)
            remaining_household_size_counts[k] += addition

    # Generate households for each size
    for size, count in remaining_household_size_counts.items():
        hh_size = int(size) if size != "7+" else 7
        if count <= 0:
            continue
        gen_placeholder_household(count, hh_size, households, people)


# Function to generate non-family households
def generate_nonfamily_households(total_households, nonfamily_households, input_data, age_ranges, people_counts, households, people):
    living_alone = input_data["household_info"]["nonfamily_households"]["living_alone"]
    nonfamily_size_distribution = input_data["household_info"]["nonfamily_households"]["size_distribution"]
    hh_type = "nonfamily"

    # Correctly calculate the number of living alone households
    total_living_alone = int(nonfamily_households * (nonfamily_size_distribution['1'] / 100))
    male_over_65_living_alone = int(total_living_alone * (living_alone["male_over_65"] / living_alone["total_percentage"]))
    female_over_65_living_alone = int(total_living_alone * (living_alone["female_over_65"] / living_alone["total_percentage"]))
    other_living_alone = total_living_alone - male_over_65_living_alone - female_over_65_living_alone

    # Generate male single-person households over 65
    for _ in tqdm(range(male_over_65_living_alone), desc="Generating male 65+ living alone"):
        p = Person(age=np.random.randint(65, 90), sex=0, position_in_hh="alone")
        people.append(p)
        people_counts["male_adult"] -= 1
        h = Household(population=[p], type=hh_type)
        households.append(h)

    # Generate female single-person households over 65
    for _ in tqdm(range(female_over_65_living_alone), desc="Generating female 65+ living alone"):
        p = Person(age=np.random.randint(65, 90), sex=1, position_in_hh="alone")
        people.append(p)
        people_counts["female_adult"] -= 1
        h = Household(population=[p], type=hh_type)
        households.append(h)

    # Generate single-person households aged 18-64
    for _ in tqdm(range(other_living_alone), desc="Generating others living alone (18-64)"):
        age = np.random.randint(18, 65)
        total_people_remaining = people_counts["male_adult"] + people_counts["female_adult"]
        male_prob = people_counts["male_adult"] / total_people_remaining if total_people_remaining > 0 else 0.5
        sex = np.random.choice([0, 1], p=[male_prob, 1 - male_prob])
        p = Person(age=age, sex=sex, position_in_hh="alone")
        people.append(p)
        if p.sex == 0:
            people_counts["male_adult"] -= 1
        else:
            people_counts["female_adult"] -= 1
        h = Household(population=[p], type=hh_type)
        households.append(h)

    # Generate remaining nonfamily households (sizes >=2)
    total_non_living_alone_nonfamily_households = nonfamily_households - total_living_alone

    # Adjust size distribution excluding size '1'
    adjusted_size_distribution = {k: v for k, v in nonfamily_size_distribution.items() if k != '1'}
    total_percentage = sum(adjusted_size_distribution.values())
    adjusted_size_distribution = {k: (v / total_percentage) * 100 for k, v in adjusted_size_distribution.items()}

    # Calculate the number of households needed for each size
    nonfamily_households_needed_by_size = {
        k: int(total_non_living_alone_nonfamily_households * (v / 100))
        for k, v in adjusted_size_distribution.items()
    }

    # Handle negative counts by redistributing
    total_negative = sum(-v for v in nonfamily_households_needed_by_size.values() if v < 0)
    if total_negative > 0:
        positive_sizes = [k for k, v in nonfamily_households_needed_by_size.items() if v > 0]
        total_positive = sum(nonfamily_households_needed_by_size[k] for k in positive_sizes)
        for k in positive_sizes:
            reduction = int((nonfamily_households_needed_by_size[k] / total_positive) * total_negative)
            nonfamily_households_needed_by_size[k] -= reduction

    # Generate households for each size
    for size, count in nonfamily_households_needed_by_size.items():
        size_int = int(size) if size != "7+" else 7
        if count <= 0:
            continue
        for _ in tqdm(range(count), desc=f"Generating nonfamily households of size {size}"):
            population = []
            for _ in range(size_int):
                age = np.random.randint(18, 90)
                total_people_remaining = people_counts["male_adult"] + people_counts["female_adult"]
                male_prob = people_counts["male_adult"] / total_people_remaining if total_people_remaining > 0 else 0.5
                sex = np.random.choice([0, 1], p=[male_prob, 1 - male_prob])
                p = Person(age=age, sex=sex, position_in_hh="nonfamily_member")
                people.append(p)
                if p.sex == 0:
                    people_counts["male_adult"] -= 1
                else:
                    people_counts["female_adult"] -= 1
                population.append(p)
            h = Household(population=population, type="nonfamily")
            households.append(h)

    return households, people



# Main function to generate households
def gen_households(total_households, total_population):
    # Initialize people distribution
    people_counts = get_people_distribution(total_population)
    print("Initial People Counts:", people_counts)

    # Initialize lists to store people and households
    people = []
    households = []

    # Define age ranges
    age_ranges = {
        "15-24": (15, 24),
        "25-34": (25, 34),
        "35-44": (35, 44),
        "45-54": (45, 54),
        "55-64": (55, 64),
        "65+": (65, 90)
    }

    ######################################################################################################
    # Part 1: Generate households with children under 18
    ######################################################################################################
    household_info = input_data["household_info"]
    family_households_info = household_info["family_households"]
    with_children_under_18_info = family_households_info["with_children_under_18"]
    total_percentage_with_children_under_18 = with_children_under_18_info["total_percentage"] / 100

    number_of_households_with_children = int(total_households * total_percentage_with_children_under_18)

    distribution_with_children = with_children_under_18_info["distribution"]

    parent_age_distribution = input_data["pop_info"]["parent_age_distribution"]

    # Generate households with children under 18
    num_married_couple_generated, num_single_mother_with_children, num_single_father_with_children = generate_households_with_children_under_18(
        number_of_households_with_children,
        distribution_with_children,
        parent_age_distribution,
        age_ranges,
        people_counts,
        households,
        people
    )

    # Married couples percentages
    married_couples_percentages = household_info["married_couples_percentages"]

    # Update total number of married couples
    total_number_of_married_couples = int(
        num_married_couple_generated / (married_couples_percentages["with_children_under_18"] / 100))

    ######################################################################################################
    # Generating single parent households
    ######################################################################################################
    generate_single_parent_households_with_children(
        num_single_mother_with_children,
        num_single_father_with_children,
        distribution_with_children,
        parent_age_distribution,
        age_ranges,
        people_counts,
        households,
        people
    )

    ######################################################################################################
    # Part 2: Generate family households without children
    ######################################################################################################
    total_family_households = int(total_households * (family_households_info["total_percentage"] / 100))
    total_family_households_generated_with_children = (
            num_married_couple_generated +
            num_single_mother_with_children +
            num_single_father_with_children)
    number_of_family_households_without_children = total_family_households - total_family_households_generated_with_children

    # Number of married couples without children
    num_married_couple_without_children = int(
        total_number_of_married_couples * (married_couples_percentages["without_children"] / 100))
    num_married_couple_without_children = min(num_married_couple_without_children,
                                              number_of_family_households_without_children)

    married_couple_without_children_age_distribution = input_data["pop_info"][
        "married_couple_without_children_age_distribution"]

    # Generate married couple households without children
    generate_family_households_without_children(
        num_married_couple_without_children,
        married_couple_without_children_age_distribution,
        age_ranges,
        people_counts,
        households,
        people
    )

    # Update total family households generated
    total_family_households_generated = len([hh for hh in households if hh.type == "family"])
    remaining_family_households = total_family_households - total_family_households_generated

    ######################################################################################################
    # Add grandparents to family households with children to make them multi-generational
    ######################################################################################################
    num_multi_generational_households = int(
        total_family_households * (family_households_info["with_over_65"]["multi_generational"] / 100))

    add_grandparents_to_households(
        num_multi_generational_households,
        households,
        people_counts,
        people
    )

    ######################################################################################################
    # Generate remaining family households
    ######################################################################################################
    generate_remaining_family_households(
        remaining_family_households,
        input_data,
        age_ranges,
        people_counts,
        households,
        people
    )

    total_family_households_generated = len([hh for hh in households if hh.type == "family"])

    ######################################################################################################
    # Part 3: Generate non-family households
    ######################################################################################################
    nonfamily_households = total_households - total_family_households_generated
    households, people = generate_nonfamily_households(
        total_households,
        nonfamily_households,
        input_data,
        age_ranges,
        people_counts,
        households,
        people
    )

    print("Final People Counts:", people_counts)

    # Calculate people off by percentage
    people_off_by_percentage = {
        k: f"{round((v / total_population * 100), 2)}%"
        for k, v in people_counts.items()
    }
    print("People off by percentage:", people_off_by_percentage)

    return households, people


######################################################################################################
# Data validation
######################################################################################################

def plot_household_size_distribution(generated_data, reference_data, household_sizes, title):
    """
    Function to plot household size distribution.
    :param generated_data: Dictionary of generated household size percentages.
    :param reference_data: List of reference household size percentages.
    :param household_sizes: List of household size categories (e.g., ["1", "2", "3", ...]).
    :param title: Title for the plot.
    """
    plt.figure(figsize=(12, 7))
    bar_width = 0.35
    x_indices = range(len(household_sizes))

    # Plot reference data (left)
    plt.bar(x_indices,
            reference_data,
            width=bar_width, color='orange', label='Reference Data')

    # Plot generated data (right)
    plt.bar([x + bar_width for x in x_indices],
            [generated_data[size] for size in household_sizes],
            width=bar_width, color='lightblue', label='Generated Data')

    # Add titles and labels
    plt.title(f"Comparison of {title} Household Size Distribution", fontsize=16)
    plt.xlabel("Household Size", fontsize=14)
    plt.ylabel("Percentage of Total Households (%)", fontsize=14)
    plt.xticks([x + bar_width / 2 for x in x_indices], household_sizes, fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def visualize_hh_size(hh):
    # Plot family household size distribution
    family_household_size_distribution = input_data["household_info"]["family_households"]["size_distribution"]
    family_household_sizes = ["2", "3", "4", "5", "6", "7+"]
    family_household_size_counts = {size: 0 for size in family_household_sizes}
    for household in hh:
        if household.type == "family":
            size = len(household.population)
            if size >= 7:
                family_household_size_counts["7+"] += 1
            else:
                family_household_size_counts[str(size)] += 1
    total_family_households_generated = sum(family_household_size_counts.values())
    family_household_size_percentages = {
        size: (count / total_family_households_generated) * 100
        for size, count in family_household_size_counts.items()
    }
    plot_household_size_distribution(
        family_household_size_percentages,
        [family_household_size_distribution[size] for size in family_household_sizes],
        family_household_sizes,
        "Family"
    )

    # Plot non-family household size distribution
    nonfamily_household_size_distribution = input_data["household_info"]["nonfamily_households"]["size_distribution"]
    nonfamily_household_sizes = ["1", "2", "3", "4", "5", "6", "7+"]
    nonfamily_household_size_counts = {size: 0 for size in nonfamily_household_sizes}
    for household in hh:
        if household.type == "nonfamily":
            size = len(household.population)
            if size >= 7:
                nonfamily_household_size_counts["7+"] += 1
            else:
                nonfamily_household_size_counts[str(size)] += 1
    total_nonfamily_households_generated = sum(nonfamily_household_size_counts.values())
    nonfamily_household_size_percentages = {
        size: (count / total_nonfamily_households_generated) * 100
        for size, count in nonfamily_household_size_counts.items()
    }
    plot_household_size_distribution(
        nonfamily_household_size_percentages,
        [nonfamily_household_size_distribution[size] for size in nonfamily_household_sizes],
        nonfamily_household_sizes,
        "Non-Family"
    )


if __name__ == "__main__":
    start_time = time.time()
    total_households = input_data["total_households"]
    avg_household_size = input_data["avg_household_size"]
    total_population = int(total_households * avg_household_size)


    hh, people = gen_households(total_households, total_population)
    finalize_time = time.time()
    print("Time taken to generate all households:", round(finalize_time - start_time,2), "seconds")
    print("Total population generated:", len(people))
    visualize_hh_size(hh)

    print("family households:", len([household for household in hh if household.type == "family"]))
    print("nonfamily households:", len([household for household in hh if household.type == "nonfamily"]))
    print("Total households generated:", len(hh))

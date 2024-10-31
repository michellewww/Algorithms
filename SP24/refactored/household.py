import numpy as np
import pandas as pd
import random
import yaml
from enum import Enum

'''
    GLOBAL VARIABLES
'''

next_household_id = 0

poi_category = {
    '11': 'Agriculture, Forestry, Fishing and Hunting',
    '21': 'Mining, Quarrying, and Oil and Gas Extraction',
    '22': 'Utilities',
    '23': 'Construction',
    '31': 'Manufacturing',
    '32': 'Manufacturing',
    '33': 'Manufacturing',
    '42': 'Wholesale Trade',
    '44': 'Retail Trade',
    '45': 'Retail Trade',
    '48': 'Transportation and Warehousing',
    '49': 'Transportation and Warehousing',
    '51': 'Information',
    '52': 'Depository Credit Intermediation',
    '53': 'Real Estate and Rental and Leasing',
    '54': 'Professional, Scientific, and Technical Services',
    '55': 'Management of Companies and Enterprises',
    '56': 'Administrative and Support and Waste Management and Remediation Services',
    '61': 'Education',
    '62': 'Medical',
    '71': 'Arts, Entertainment, and Recreation',
    '72': 'Restaurants and Other Eating Places',
    '81': 'Others',
    '92': 'Public Administration' 
}

age_category = {
    "Preschool": (0, 4),
    "Adolescent": (5, 18),
    "Adult": (19, 64),
    "Retired": (65, 99)
}


'''
    Classe Definitions to use in pop_mov_sim
'''


class Person:
    '''
    Class for each individual
    '''

    def __init__(self, id, sex, age, cbg, household, hh_id):
        self.id = id
        self.sex = sex 
        self.age = age
        self.cbg = cbg
        self.household:Household = household
        self.hh_id = hh_id
        self.occupation = None
        self.occupation_id = 0
        self.work_time = (0, 0) #0 ~ 24
        self.availability = True
        self.left_from_work = False

        self.location:Household = household # where is the person now

    def set_occupation(self, occupation):
        self.occupation = occupation
        self.set_work_time()

    def set_work_time(self):
        if (self.occupation == poi_category['62'] or self.occupation == poi_category['72']) and random.random() <= 15 / 100: #if medical or food service && #15% night shift
            self.work_time = (17, 24) 
        elif self.occupation == poi_category['21']:  # if Mining, Quarrying, and Oil and Gas Extraction
            if random.random() <= 10 / 100:  # 10% night shift
                self.work_time = (18, 2)  # Night shift
            else:
                self.work_time = (6, 18)   # Day shift, longer 12 hour shift common
        elif self.occupation == poi_category['23']:  #if Construction
            start_time = random.randint(6, 8)  #tends to start earlier in the day
            end_time = random.randint(14, 18)
            self.work_time = (start_time, end_time)
        elif self.occupation != None: self.work_time = (9, 17)

    # assign the person to the designated household
    def assign_household(self, hh):
        if self.location.id != hh.id: # check if the person is already in designated household
            
            # remove the person from the current location
            try:
                self.location.population.remove(self)
            except ValueError as e:
                # print(f'key is not found when removing Person {self.id} from Household {self.location.id}')
                pass

            # add the person to the designated location
            if self not in hh.population:
                hh.population.append(self)
            
            self.location = hh
    
    def at_home(self) -> bool:
        return self.household.id == self.location.id

    def to_dict(self):
        return {
            'id':self.id,
            'cbg':self.cbg,
            'sex': self.sex,
            'age': self.age, # used by interhousehold movement
            'home': self.household.id, # used by interhousehold movement
            'availability':self.availability, # used by interhousehold movement
            'at_home':self.at_home(), # used by interhousehold movement
        }

    def __str__(self):
        return f"Person {self.id}"
    
    def __repr__(self):
        return self.__str__()
    
    #def write(self):
        #with open('people_occupation_worktime.txt', 'w') as of:
            #of.write(self)

class Population:

    '''
    Class for storing population
    '''

    def __init__(self):
        # total population
        self.total_count = 0
        # container for persons in the population
        self.population = []
    
    def populate_indiv(self, person):
        '''
        Populates the population with the person object
        @param person = Person class object to be added to population
        '''
        
        #adding population
        self.population = np.append(self.population, person)

class Household(Population):

    '''
    Household class, inheriting Population since its a small population
    '''
    
    global next_household_id

    def __init__(self, cbg, total_count=0, population=[]):
        global next_household_id
        super().__init__()
        self.total_count = total_count
        self.population:list[Person] = population
        self.cbg = cbg
        self.id = id  
        #print(f"Assigning Household ID: {self.id}")
        next_household_id += 1  
        self.social_days = 0 # 0 means no social event currently
        self.social_max_duration = 0


    def add_member(self, person):
        '''
        Adds member to the household, with sanity rules applied
        @param person = person to be added to household
        '''
        self.population.append(person)

    def start_social(self, duration:int):
        if (self.social_days != 0):
            raise ValueError("Alreay hosting social")
        elif (not self.population):
            raise ValueError("No population to host social")
        
        self.social_days = 1
        self.social_max_duration = duration
    
    def end_social(self):
        self.social_days = 0
        self.social_max_duration = 0
        
        for person in list(self.population):
            if person.household.id != self.id:
                person.assign_household(person.household)
    
    def is_social(self) -> bool:
        return self.social_days > 0

    def has_hosts(self) -> bool:
        for person in self.population:
            if person.household.id == self.id:
                return True
        return False


    def to_dict(self):
        return {
            'id':self.id,
            'cbg': self.cbg,
            'members': len(self.population)
        }

    def __str__(self):
        guests:list[Person] = []
        hosts:list[Person] = []

        for p in self.population:
            if p.hh_id == self.id:
                hosts.append(p)
            else:
                guests.append(p)

        return f"Household {self.id} with people {str(hosts)} and guests {str(guests)}"
    
    def __repr__(self):
        return self.__str__()
        

    #TODO: Add more functions for leaving/coming back, etc if needed
    #jiwoo: an idea would be to extend from the population info to create
    #more realistic dataset (combination) of population in a household
    
'''
    if ran(not imported), yields household assignment values
'''
if __name__=="__main__":

    #HELPER FUNCTIONS

    def create_households(pop_data, households, cbg):
        count = 1
        result = []
        '''
            FOR INFORMATION: family_percents = [married, opposite_sex, samesex, female_single, male_single, other]
        '''
        married, opposite_sex, samesex, female_single, male_single, other = 0, 1, 2, 3, 4, 5
        
        for i in range(int(households * pop_data["family_percents"][married] / 100)):
            result.append(create_married_hh(pop_data, cbg, count))
            count += 1

        for i in range(int(households * pop_data['family_percents'][samesex] / 100)):
            result.append(create_samesex_hh(pop_data, cbg, count))
            count += 1

        for i in range(int(households * pop_data['family_percents'][opposite_sex] / 100)):
            result.append(create_oppositesex_hh(pop_data, cbg, count))
            count += 1

        for i in range(int(households * pop_data['family_percents'][female_single] / 100)):
            result.append(create_femsingle_hh(pop_data, cbg, count))
            count += 1

        for i in range(int(households * pop_data['family_percents'][male_single] / 100)):
            result.append(create_malesingle_hh(pop_data, cbg, count))
            count += 1
        
        for i in range(int(households * pop_data['family_percents'][other] / 100)):
            result.append(create_other_hh(pop_data, cbg, count))
            count += 1

        return result     

    def create_married_hh(pop_data, cbg, count):

        household = Household(cbg)

    
        age_percent = pop_data['age_percent_married']
        age_group = random.choices(pop_data['age_groups_married'], age_percent)[0]
        
        husband_age = random.choice(range(age_group, age_group+10))
        household.add_member(Person(pop_data['count'], 0, husband_age, cbg, household, count))
        pop_data['count'] += 1
        wife_age = random.choice(range(age_group, age_group+10))
        household.add_member(Person(pop_data['count'], 1, wife_age, cbg, household, count))
        pop_data['count'] += 1

        # if there will be children. Old couples have less percent
        #jiwoo: are the numbers 0.1 and 0.05 statistically proven, or are these arbitrary numbers so far?
        children_percent = pop_data['children_true_percent']+0.1 if (age_group < 45 and age_group > 15) else 0.05

        child_bool = random.choices([True, False], [children_percent, 100-children_percent])[0]

        if child_bool:
            num_child = random.choices(pop_data['children_groups'], pop_data['children_percent'])[0]
            for i in range(num_child):
                household.add_member(Person(pop_data['count'], random.choices([0, 1], [pop_data['male_percent'], pop_data['female_percent']])[0], random.choice(range(1, 18)), cbg, household, count))
                pop_data['count'] += 1
        
        return household

    #jiwoo: for functions that create household with diff combinations of sex, consider
    #creating a separate helper function for the overlapping lines of code for increased efficiency
        
    def create_samesex_hh(pop_data, cbg, count):

        household = Household(cbg)

        age_percent = pop_data['age_percent']
        age_group = random.choices(pop_data['age_groups'], age_percent)[0] #i'm talking about these lines
        
        husband_age = random.choice(range(age_group, age_group+10))
        wife_age = random.choice(range(age_group, age_group+10))

        # gender == 0 means male, gender == 1 means female
        gender = random.choices([0, 1], [pop_data['male_percent'], pop_data['female_percent']])[0]
        household.add_member(Person(pop_data['count'], gender, husband_age, cbg, household, count))
        pop_data['count'] += 1
        household.add_member(Person(pop_data['count'], gender, wife_age, cbg, household, count))
        pop_data['count'] += 1

        # assign children based on sex
        children_percent = pop_data['same_sex_child_percent'][gender]
        child_bool = random.choices([True, False], [children_percent, 100 - children_percent])[0]
        if child_bool:
            household.add_member(Person(pop_data['count'],
                                        random.choices([0, 1], [pop_data['male_percent'], pop_data['female_percent']])[
                                            0], random.choice(range(1, 18)), cbg, household, count))
            pop_data['count'] += 1

        return household

    def create_oppositesex_hh(pop_data, cbg, count):

        household = Household(cbg)

        age_percent = pop_data['age_percent']
        age_group = random.choices(pop_data['age_groups'], age_percent)[0]
        
        husband_age = random.choice(range(age_group, age_group+10))
        wife_age = random.choice(range(age_group, age_group+10))

        household.add_member(Person(pop_data['count'], random.choices([0, 1], [pop_data['male_percent'], pop_data['female_percent']])[0], husband_age, cbg, household, count))
        pop_data['count'] += 1
        household.add_member(Person(pop_data['count'], random.choices([0, 1], [pop_data['male_percent'], pop_data['female_percent']])[0], wife_age, cbg, household, count))
        pop_data['count'] += 1

        # assign children
        children_percent = pop_data['opp_sex_child_percent']
        child_bool = random.choices([True, False], [children_percent, 100 - children_percent])[0]
        if child_bool:
            household.add_member(Person(pop_data['count'],
                                        random.choices([0, 1], [pop_data['male_percent'], pop_data['female_percent']])[
                                            0], random.choice(range(1, 18)), cbg, household, count))
            pop_data['count'] += 1

        return household

    def create_femsingle_hh(pop_data, cbg, count):
        household = Household(cbg)

        age_percent = pop_data['age_percent']
        age_group = random.choices(pop_data['age_groups'], age_percent)[0]
        
        age = random.choice(range(age_group, age_group+10))

        household.add_member(Person(pop_data['count'], 1, age, cbg, household, count))
        pop_data['count'] += 1

        # assign children
        children_percent = pop_data['femsingle_child_percent']
        child_bool = random.choices([True, False], [children_percent, 100 - children_percent])[0]
        if child_bool:
            household.add_member(Person(pop_data['count'],
                                        random.choices([0, 1], [pop_data['male_percent'], pop_data['female_percent']])[
                                            0], random.choice(range(1, 18)), cbg, household, count))
            pop_data['count'] += 1

        return household

    def create_malesingle_hh(pop_data, cbg, count):
        household = Household(cbg)

        age_percent = pop_data['age_percent']
        age_group = random.choices(pop_data['age_groups'], age_percent)[0]
        
        age = random.choice(range(age_group, age_group+10))

        household.add_member(Person(pop_data['count'], 0, age, cbg, household, count))
        pop_data['count'] += 1

        # assign children
        children_percent = pop_data['malesingle_child_percent']
        child_bool = random.choices([True, False], [children_percent, 100 - children_percent])[0]
        if child_bool:
            household.add_member(Person(pop_data['count'],
                                        random.choices([0, 1], [pop_data['male_percent'], pop_data['female_percent']])[
                                            0], random.choice(range(1, 18)), cbg, household, count))
            pop_data['count'] += 1

        return household

    def create_other_hh(pop_data, cbg, count):
        household = Household(cbg)

        age_percent = pop_data['age_percent']
        age_group = random.choices(pop_data['age_groups'], age_percent)[0]
        
        size_percent = pop_data['size_percent']
        size_group = random.choices(pop_data['size_groups'], size_percent)[0]
        
        for i in range(size_group):
            age = random.choice(range(age_group, age_group+10))
            household.add_member(Person(pop_data['count'], random.choices([0, 1], [pop_data['male_percent'], pop_data['female_percent']])[0], age, cbg, household, count))
            pop_data['count'] += 1
        
        return household

    def visualize_household(household):
        print("ANALYZING HOUSEHOLD " + str(household))
        print("The current household has "+ str(len(household.population)) + " members.")
        for i in range(len(household.population)):
            print("member " + str(i) + ": ")
            print("id: " + str(household.population[i].id))
            print("sex(0 is male): " + str(household.population[i].sex))
            print("age: " + str(household.population[i].age))

    def create_pop_from_cluster(cluster, census_df):
        populations = 0
        households = 0
        for i in cluster:
            i = int(i)
            populations += (int(census_df[census_df.census_block_group == i].values[0][1]))
            households += (int(census_df[census_df.census_block_group == i].values[0][3]))

        return populations, households

    # reading population information from yaml file
    pop_data = {}

    with open('input/population_info.yaml', mode="r", encoding="utf-8") as file:
        pop_data = yaml.full_load(file)

    print(pop_data) #TODO delete

    # Reading Census Information
    census_info = "input/safegraph_cbg_population_estimate.csv"
    census_df = pd.read_csv(census_info)

    # HELPER FUNCTIONS

    # read clusters into string array in order to easier census search
    cluster_df = pd.read_csv('input/clusters.csv')
    clusters = [str(i) for i in list(cluster_df['cbgs'])]

    household_list = []

    # get number of households
    for cbg in clusters:
        _, household = create_pop_from_cluster([cbg], census_df)
        household_list.append(create_households(pop_data, household, cbg))

    ##SHOULD NOT MODIFY INPUT FILES

    # Dump household list data into households.yaml file
    # with open('input/households.yaml', mode="wt", encoding="utf-8") as outstream:
    #     yaml.dump(household_list, outstream)

    print("Successfully Created Households")
    

def prepare_data_for_papdata(household_list):
    hh_info = {}
    for household in household_list:
        for home in household:  # Because create_households returns a list of Household instances
            hh_id = str(home.id)
            print(f"Preparing Household {hh_id} for Papdata")
            population = {}
            for person in home.population:
                population[str(person.id)] = {
                    "sex": person.sex,
                    "age": person.age,
                    "home": person.household.id,
                    "availability": person.availability,  # Note the typo correction here
                    # "work_naics": person.work_naics,
                    "work_time": person.work_time,
                }
            hh_info[hh_id] = {
                "cbg": home.cbg,
                "population": population
            }
    return hh_info

if __name__=="__main__":

    prepared_data = prepare_data_for_papdata(household_list)

    place_path = '../hagerstown.pois.csv'
    
    from papdata import Papdata
    papdata_processor = Papdata(prepared_data, place_path)
    papdata_processor.generate()

    print("Papdata JSON generation completed.")
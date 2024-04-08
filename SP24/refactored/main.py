import yaml
from household import Household, Person
from simulate import Simulate
from inter_hh import InterHousehold
import numpy as np

# Define a custom constructor for loading Person objects
def person_constructor(loader, node):
    fields = loader.construct_mapping(node)
    return Person(**fields)

# Define a custom constructor for loading Household objects
def household_constructor(loader, node):
    fields = loader.construct_mapping(node)
    return Household(**fields)

def load_household():
    with open('input/households.yaml', 'r', encoding='utf-8') as hhstream:
        hh_info_pre = yaml.load(hhstream, Loader=yaml.SafeLoader)
        # print(hh_info_pre)

    hh_info = []

    for list_hh in hh_info_pre:
        for hh in list_hh:
            hh_info.append(hh)
    return hh_info

def format_hh(hh_list:list[Household]):
    person_id_counter = 1
    for i in range(0, len(hh_list)):
        hh = hh_list[i]
        hh.total_count = len(hh.population)
        hh.id = i + 1
        for person in hh.population:
            person.hh_id = i + 1
            person.location = hh
            person.household = hh
            person.id = person_id_counter
            person_id_counter += 1
    return hh_list

if __name__ == "__main__":
    with open('input/simul_settings.yaml', mode="r", encoding='utf-8') as settingstream:
        settings = yaml.safe_load(settingstream)

    with open('input/barnsdall.yaml', mode="r", encoding='utf-8') as citystream:
        city_info = yaml.safe_load(citystream)

    category_info = 'input/barnsdall.pois.csv'

    yaml.SafeLoader.add_constructor('tag:yaml.org,2002:python/object:__main__.Person', person_constructor)
    yaml.SafeLoader.add_constructor('tag:yaml.org,2002:python/object:__main__.Household', household_constructor)
    
    hh_info = load_household()

    hh_info = format_hh(hh_info)
    
    simulate = Simulate(settings, city_info, hh_info, category_info)
    print("Starting simulation")
    simulate.start()
    print("Simulation has ended")
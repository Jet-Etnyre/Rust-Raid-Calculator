######################################
# Rust Raid Calculator
# - Jet Etnyre
# This script calculates the resources required to craft explosives
# and the damage they deal to various structures in Rust.
# Uses optmization techjiques to minimize sulfur usage.
######################################

import json

# Load the explosives data from a JSON file
# The JSON file should contain the explosive types, raw materials, and damage values.
try:
    with open('explosives.json', 'r') as file:
        explosives = json.load(file)
    file.close()
except FileNotFoundError:
    print("Error: 'explosives.json' file not found. Please ensure the file exists in the same directory as this script.")
    exit(1)

#Load the structure data from a JSON file
#The JSON file should contain the structure types and their hp values.
try:
    with open('structures.json', 'r') as file:
        structures = json.load(file)
    file.close()
except FileNotFoundError:
    print("Error: 'structures.json' file not found. Please ensure the file exists in the same directory as this script.")
    exit(1)

###########################
# Function to calculate resources required
# Inputs: explosive_type (str), quantity (int)
# Outputs: total_resources (dict)
###########################
def calculate_resources(explosive_type, quantity):
    if explosive_type not in explosives:
        raise ValueError(f"Explosive type '{explosive_type}' not found.")
    if quantity <= 0:
        raise ValueError("Quantity must be a positive integer.")
    if not isinstance(quantity, int):
        raise ValueError("Quantity must be an integer.")

    explosive = explosives[explosive_type]
    raw_materials = explosive['raw_materials']
    total_resources = {material: amount * quantity for material, amount in raw_materials.items()}
    return total_resources
############################
# Function to get specific damage values for a structure
# Inputs: explosive_list (list of str), structure (str)
# Outputs: damage_values (dict)
############################
def specific_damage_values(explosive_list, structure):
    if structure not in structures:
        raise ValueError(f"Structure '{structure}' not found.")
    
    damage_values = {}
    for explosive in explosive_list:
        if explosive not in explosives:
            raise ValueError(f"Explosive type '{explosive}' not found.")
        damage_values[explosive] = explosives[explosive]["damage_per_structure"][structure]
    return damage_values

print("Welcome to the Rust Raid Calculator!")
user_selection = input("Select an option:\n 1. Calculate resources for explosives\n 2. Provide Damage given a structure\n 0. Exit\n")
while user_selection != '0':
    
    #Resoource Calculation
    if user_selection == '1':
        try:
            resources = {}
            explosives_count = {}
            while True:
                # Prompt for explosive types and quantities
                print("Available explosives:")
                for explosive in explosives.keys():
                    print(f"- {explosive}")

                explosive_type = input("Enter the explosive type (or 'done' to finish): \n")
                if explosive_type.lower() == 'done':
                    break
                if explosive_type not in explosives:
                    print(f"Explosive type '{explosive_type}' not found. Please try again.")
                    continue

                # Prompt for quantity and validate input
                while True:
                    quantity_input = input(f"Enter the quantity of {explosive_type}: \n")
                    try:
                        quantity = int(quantity_input)
                        if quantity <= 0:
                            print("Quantity must be a positive integer. Please try again.")
                            continue
                        break
                    except ValueError:
                        print("Quantity must be an integer. Please try again.")
                        continue

                # Calculate resources and update counts
                if explosive_type in explosives_count:
                    explosives_count[explosive_type] += quantity
                else:
                    explosives_count[explosive_type] = quantity
                    
                resource = calculate_resources(explosive_type, quantity)
                for material, amount in resource.items():
                    if material in resources:
                        resources[material] += amount
                    else:
                        resources[material] = amount
                print("Current explosive count:")
                for exp, count in explosives_count.items():
                    print(f"{exp}: {count}")
            
            print("Total explosives crafted:")
            for exp, count in explosives_count.items():
                print(f"{exp}: {count}")
            print("Total resources required:")
            for material, amount in resources.items():
                print(f"{material}: {amount}")

        except ValueError as e:
            print(e)

    #Damage per structure display
    elif user_selection == '2':
        try:
            while True:
                # Prompt for structure type
                print("Available structures:")
                for structure in structures.keys():
                    print(f"- {structure}")

                structure = input("Enter the structure type (or type 'done' to exit): \n")
                if structure.lower() == 'done':
                    break
                if structure not in structures:
                    print(f"Structure '{structure}' not found. Please try again.")
                    continue

                #Prompt user for specific explosive types
                print("Available explosives:")
                for explosive in explosives.keys():
                    print(f"- {explosive}")
                explosive_set = set()
                while True:
                    # Display current selection and prompt for explosive input
                    print(f"Current selection: {', '.join(explosive_set) if explosive_set else '(none)'}")
                    explosive_input = input(
                        "Enter an explosive to add/remove "
                        "(or 'done' to finish, 'all' for all explosives, 'list' to show all explosives): \n"
                    ).strip().lower()
                    if explosive_input == 'done':
                        if not explosive_set:
                            print("You must select at least one explosive before continuing.")
                            continue
                        break
                    elif explosive_input == 'all':
                        explosive_set = set(explosives.keys())
                        print("All explosives added.")
                        continue
                    elif explosive_input == 'list':
                        print("Available explosives:")
                        for explosive in explosives.keys():
                            print(f"- {explosive}")
                        continue
                    elif explosive_input not in (exp.lower() for exp in explosives.keys()):
                        print(f"Explosive type '{explosive_input}' not found. Please try again.")
                        continue

                    # Find the actual case-sensitive explosive name
                    actual_exp = next(exp for exp in explosives.keys() if exp.lower() == explosive_input)
                    if actual_exp in explosive_set:
                        explosive_set.remove(actual_exp)
                        print(f"Removed '{actual_exp}' from selection.")
                    else:
                        explosive_set.add(actual_exp)
                        print(f"Added '{actual_exp}' to selection.")

                # Convert the set to a list for further processing
                explosive_list = list(explosive_set)
            
                # Calculate and display damage values
                damages = specific_damage_values(explosive_list, structure)
                print(f"Damage values for {structure} that has {structures[structure]} HP:")
                for explosive, damage in damages.items():
                    print(f"{explosive}: {damage} HP")
        except ValueError as e:
            print(e)

  
    else:
        print("Invalid selection. Please try again.")
    
    user_selection = input("Select an option:\n 1. Calculate resources for explosives\n 2. Provide Damage given a structure\n 0. Exit\n")



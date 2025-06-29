######################################
# Rust Raid Calculator
# - Jet Etnyre
# This script calculates the resources required to craft explosives
# and the damage they deal to various structures in Rust.
# Uses optmization techjiques to minimize sulfur usage.
######################################

import json
from pulp import *

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

print("Welcome to the Rust Raid Calculator!")
user_selection = input("Select an option:\n 1. Calculate resources for explosives\n 2. Provide Damage given a structure\n 3. Sulfur Optimizer\n 0. Exit\n")
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
            
             # Display totals for all explosives and resources
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

    elif user_selection == '3':
        try:
            # Prompt for structure types and quantities (user can select multiple)
            selected_structures = {}
            while True:
                print("Available structures:")
                for structure in structures.keys():
                    print(f"- {structure}")
                print(f"Current selection: {', '.join([f'{s} (x{q})' for s, q in selected_structures.items()]) if selected_structures else '(none)'}")
                structure_input = input("Enter a structure to add/remove (or 'done' to finish, 'list' to show all structures): \n").strip().lower()
                if structure_input == 'done':
                    if not selected_structures:
                        print("You must select at least one structure before continuing.")
                        continue
                    break
                elif structure_input == 'list':
                    print("Available structures:")
                    for structure in structures.keys():
                        print(f"- {structure}")
                    continue
                elif structure_input not in (s.lower() for s in structures.keys()):
                    print(f"Structure '{structure_input}' not found. Please try again.")
                    continue

                # Find the actual case-sensitive structure name
                actual_structure = next(s for s in structures.keys() if s.lower() == structure_input)
                if actual_structure in selected_structures:
                    del selected_structures[actual_structure]
                    print(f"Removed '{actual_structure}' from selection.")
                else:
                    while True:
                        qty_input = input(f"Enter the quantity for {actual_structure}: \n")
                        try:
                            qty = int(qty_input)
                            if qty <= 0:
                                print("Quantity must be a positive integer. Please try again.")
                                continue
                            selected_structures[actual_structure] = qty
                            print(f"Added '{actual_structure}' (x{qty}) to selection.")
                            break
                        except ValueError:
                            print("Quantity must be an integer. Please try again.")

            # selected_structures is now a dict: {structure_name: quantity, ...}
            print("Final structure selection:")
            for s, q in selected_structures.items():
                print(f"{s}: {q}")

            # Prompt user for specific explosive types to use in the optimizer
            print("Available explosives:")
            for explosive in explosives.keys():
                print(f"- {explosive}")
            explosive_dict = dict()
            while True:
                print(f"Current selection: {', '.join((f"{key}:{value}") for key, value in explosive_dict.items()) if explosive_dict else '(none)'}")
                explosive_input = input(
                    "Enter an explosive to add/remove "
                    "(or 'done' to finish, 'all' for all explosives, 'list' to show all explosives): \n"
                ).strip().lower()
                if explosive_input == 'done':
                    if not explosive_dict:
                        print("You must select at least one explosive before continuing.")
                        continue
                    break
                elif explosive_input == 'all':
                    for exp in explosives.keys():
                        if exp not in explosive_dict:
                            explosive_dict[exp] = 0
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
                if actual_exp in explosive_dict:
                    explosive_dict.pop(actual_exp)
                    print(f"Removed '{actual_exp}' from selection.")
                else:
                    while True:
                        qty_input = input(f"Enter the quantity for {actual_exp}: \n")
                        try:
                            qty = int(qty_input)
                            if qty < 0:
                                print("Quantity must 0 or greater. Please try again.")
                                continue
                            explosive_dict[actual_exp] = qty
                            print(f"Added '{actual_exp}' (x{qty}) to selection.")
                            break
                        except ValueError:
                            print("Quantity must be an integer. Please try again.")

            explosive_list = list(explosive_dict.keys())

            # --- Begin Linear Programming Model Setup ---
            prob = LpProblem("Rust_Raid_Optimizer", LpMinimize)

            # Create a decision variable for each (explosive, structure, instance) pair
            # This allows the optimizer to decide how many of each explosive to use on each structure instance
            explosive_vars = {}
            for struct, qty in selected_structures.items():
                for i in range(qty):
                    for exp in explosive_list:
                        explosive_vars[(exp, struct, i)] = LpVariable(f"{exp}_{struct}_{i+1}", explosive_dict[exp], cat='Integer')

            owned_vars = {}
            crafted_vars = {}

            for struct, qty in selected_structures.items():
                for i in range(qty):
                    for exp in explosive_list:
                        owned_vars[(exp, struct, i)] = LpVariable(f"owned_{exp}_{struct}_{i+1}", 0, cat='Integer')
                        crafted_vars[(exp, struct, i)] = LpVariable(f"crafted_{exp}_{struct}_{i+1}", 0, cat='Integer')

            # Constraint: total owned used ≤ owned amount
            for exp in explosive_list:
                prob += lpSum([owned_vars[(exp, struct, i)] for struct, qty in selected_structures.items() for i in range(qty)]) <= explosive_dict[exp]

            # Objective: minimize sulfur cost (only crafted explosives cost sulfur)
            prob += lpSum([
                crafted_vars[(exp, struct, i)] * explosives[exp]['raw_materials']['sulfur']
                for (exp, struct, i) in crafted_vars
            ]), "Total_Sulfur_Cost"

            # Calculate max single-hit damage for each structure
            max_damage = {struct: max(explosives[exp]['damage_per_structure'][struct] for exp in explosive_list) for struct in selected_structures}

            # Damage constraints: both owned and crafted count toward damage
            for struct, qty in selected_structures.items():
                for i in range(qty):
                    # Lower bound: must destroy the structure
                    prob += lpSum([
                        (owned_vars[(exp, struct, i)] + crafted_vars[(exp, struct, i)]) * explosives[exp]['damage_per_structure'][struct]
                        for exp in explosive_list
                    ]) >= structures[struct], f"{struct}_{i+1}_lower"
                    # Upper bound: don't use way more than needed
                    prob += lpSum([
                        (owned_vars[(exp, struct, i)] + crafted_vars[(exp, struct, i)]) * explosives[exp]['damage_per_structure'][struct]
                        for exp in explosive_list
                    ]) <= structures[struct] + max_damage[struct], f"{struct}_{i+1}_upper"
            
            # Solve the optimization problem using PuLP's default solver
            prob.solve()

            print("Optimization Results:")

            # Breakdown by structure: how much of each explosive is used on each structure, split by owned/crafted
            for struct, qty in selected_structures.items():
                print(f"\n{struct} (x{qty}):")
                for exp in explosive_list:
                    used_owned = sum(
                        int(owned_vars[(exp, struct, i)].varValue)
                        for i in range(qty)
                        if owned_vars[(exp, struct, i)].varValue and owned_vars[(exp, struct, i)].varValue > 0
                    )
                    used_crafted = sum(
                        int(crafted_vars[(exp, struct, i)].varValue)
                        for i in range(qty)
                        if crafted_vars[(exp, struct, i)].varValue and crafted_vars[(exp, struct, i)].varValue > 0
                    )
                    total_used = used_owned + used_crafted
                    if total_used > 0:
                        print(f"  {exp}: {total_used} (owned: {used_owned}, crafted: {used_crafted})")

            # Breakdown by structure instance: how much of each explosive is used on each individual structure, split by owned/crafted
            for struct, qty in selected_structures.items():
                for i in range(qty):
                    print(f"\n{struct} #{i+1}:")
                    for exp in explosive_list:
                        used_owned = int(owned_vars[(exp, struct, i)].varValue) if owned_vars[(exp, struct, i)].varValue else 0
                        used_crafted = int(crafted_vars[(exp, struct, i)].varValue) if crafted_vars[(exp, struct, i)].varValue else 0
                        total_used = used_owned + used_crafted
                        if total_used > 0:
                            print(f"  {exp}: {total_used} (owned: {used_owned}, crafted: {used_crafted})")

            # Totals for each explosive across all structures
            explosive_totals = {}
            explosive_owned_totals = {}
            explosive_crafted_totals = {}
            for (exp, struct, i) in explosive_vars:
                owned = int(owned_vars[(exp, struct, i)].varValue) if owned_vars[(exp, struct, i)].varValue else 0
                crafted = int(crafted_vars[(exp, struct, i)].varValue) if crafted_vars[(exp, struct, i)].varValue else 0
                explosive_totals[exp] = explosive_totals.get(exp, 0) + owned + crafted
                explosive_owned_totals[exp] = explosive_owned_totals.get(exp, 0) + owned
                explosive_crafted_totals[exp] = explosive_crafted_totals.get(exp, 0) + crafted

            print("\nTotal Explosives Used:")
            for exp in explosive_list:
                print(f"{exp}: {explosive_totals.get(exp,0)} (owned: {explosive_owned_totals.get(exp,0)}, crafted: {explosive_crafted_totals.get(exp,0)})")

            # Print total sulfur cost for the solution
            print(f"\nTotal Sulfur Cost (crafted only): {int(value(prob.objective))}")

            # Aggregate and display total resources required for the solution (owned + crafted)
            print("\nTotal Resources Required (owned + crafted):")
            total_resources = {}
            for (exp, struct, i) in explosive_vars:
                total = (int(owned_vars[(exp, struct, i)].varValue) if owned_vars[(exp, struct, i)].varValue else 0) + \
                        (int(crafted_vars[(exp, struct, i)].varValue) if crafted_vars[(exp, struct, i)].varValue else 0)
                if total > 0:
                    resource = calculate_resources(exp, total)
                    for material, amount in resource.items():
                        total_resources[material] = total_resources.get(material, 0) + amount
            for material, amount in total_resources.items():
                print(f"{material}: {amount}")

            # Aggregate and display total resources required for the crafted explosives only
            print("\nTotal Resources Required (crafted only):")
            crafted_resources = {}
            for (exp, struct, i) in crafted_vars:
                crafted = int(crafted_vars[(exp, struct, i)].varValue) if crafted_vars[(exp, struct, i)].varValue else 0
                if crafted > 0:
                    resource = calculate_resources(exp, crafted)
                    for material, amount in resource.items():
                        crafted_resources[material] = crafted_resources.get(material, 0) + amount

            if crafted_resources:
                for material, amount in crafted_resources.items():
                    print(f"{material}: {amount}")
            else:
                print("No crafted resources required. All explosives can be owned.")

          
        except ValueError as e:
            print(e)

    else:
        print("Invalid selection. Please try again.")
    
    # Prompt for next action at the end of each loop
    user_selection = input("Select an option:\n 1. Calculate resources for explosives\n 2. Provide Damage given a structure\n 3. Sulfur Optimizer\n 0. Exit\n")



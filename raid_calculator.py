######################################
# Rust Raid Calculator
# - Jet Etnyre
# This script calculates the resources required to craft explosives
# and the damage they deal to various structures in Rust.
# Uses optmization techjniques to minimize sulfur usage.
######################################

import json

# Load the explosives data from a JSON file
# The JSON file should contain the explosive types, raw materials, and damage values.
with open('explosives.json', 'r') as file:
    explosives = json.load(file)
file.close()

#Load the structure data from a JSON file
with open('structures.json', 'r') as file:
    structures = json.load(file)
file.close()

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
    return {
        'total_resources': total_resources
    }

def main():
    try:
        explosive_type = input("Enter explosive type (c4, rocket, high_velocity_rocket, explosive_ammo, f1_grenade, satchel_charge, beancan_grenade): ").strip().lower()
        quantity = int(input("Enter quantity: "))

        result = calculate_resources(explosive_type, quantity)
        print("Total resources required:")
        for material, amount in result['total_resources'].items():
            print(f"{material}: {amount}")

    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
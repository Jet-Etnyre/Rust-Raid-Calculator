from flask import Flask, render_template, request, redirect, url_for
import json
from pulp import *

# Load data
with open('explosives.json', 'r') as file:
    explosives = json.load(file)
with open('structures.json', 'r') as file:
    structures = json.load(file)

app = Flask(__name__)

def calculate_resources(explosive_type, quantity):
    explosive = explosives[explosive_type]
    raw_materials = explosive['raw_materials']
    total_resources = {material: amount * quantity for material, amount in raw_materials.items()}
    return total_resources

def specific_damage_values(explosive_list, structure):
    damage_values = {}
    for explosive in explosive_list:
        damage_values[explosive] = explosives[explosive]["damage_per_structure"][structure]
    return damage_values

def run_raid_optimizer(selected_structures, explosive_dict):
    """
    Runs the sulfur optimizer given selected structures and explosives (with owned amounts).
    Returns a dict with detailed breakdowns for display.
    """
    explosive_list = list(explosive_dict.keys())
    prob = LpProblem("Rust_Raid_Optimizer", LpMinimize)

    owned_vars = {}
    crafted_vars = {}

    # Create variables for each structure instance and explosive
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

    # Solve the optimization problem
    prob.solve()

    # Breakdown by structure instance
    structure_instance_usage = {}
    for struct, qty in selected_structures.items():
        structure_instance_usage[struct] = []
        for i in range(qty):
            instance_usage = {}
            for exp in explosive_list:
                used_owned = int(owned_vars[(exp, struct, i)].varValue) if owned_vars[(exp, struct, i)].varValue else 0
                used_crafted = int(crafted_vars[(exp, struct, i)].varValue) if crafted_vars[(exp, struct, i)].varValue else 0
                total_used = used_owned + used_crafted
                if total_used > 0:
                    instance_usage[exp] = {
                        "total": total_used,
                        "owned": used_owned,
                        "crafted": used_crafted
                    }
            structure_instance_usage[struct].append(instance_usage)


    # Per-structure summary (totals for each explosive per structure)
    structure_breakdown = {}
    structure_usage = {}
    for struct, instances in structure_instance_usage.items():
        structure_breakdown[struct] = len(instances)
        usage = {}
        for instance in instances:
            for exp, detail in instance.items():
                usage[exp] = usage.get(exp, 0) + detail["total"]
        structure_usage[struct] = usage

    # Totals for each explosive across all structures
    explosive_totals = {}
    explosive_owned_totals = {}
    explosive_crafted_totals = {}
    for (exp, struct, i) in owned_vars:
        owned = int(owned_vars[(exp, struct, i)].varValue) if owned_vars[(exp, struct, i)].varValue else 0
        crafted = int(crafted_vars[(exp, struct, i)].varValue) if crafted_vars[(exp, struct, i)].varValue else 0
        explosive_totals[exp] = explosive_totals.get(exp, 0) + owned + crafted
        explosive_owned_totals[exp] = explosive_owned_totals.get(exp, 0) + owned
        explosive_crafted_totals[exp] = explosive_crafted_totals.get(exp, 0) + crafted

    # Total resources (owned + crafted)
    total_resources = {}
    for (exp, struct, i) in owned_vars:
        total = (int(owned_vars[(exp, struct, i)].varValue) if owned_vars[(exp, struct, i)].varValue else 0) + \
                (int(crafted_vars[(exp, struct, i)].varValue) if crafted_vars[(exp, struct, i)].varValue else 0)
        if total > 0:
            resource = calculate_resources(exp, total)
            for material, amount in resource.items():
                total_resources[material] = total_resources.get(material, 0) + amount

    # Total resources (crafted only)
    crafted_resources = {}
    for (exp, struct, i) in crafted_vars:
        crafted = int(crafted_vars[(exp, struct, i)].varValue) if crafted_vars[(exp, struct, i)].varValue else 0
        if crafted > 0:
            resource = calculate_resources(exp, crafted)
            for material, amount in resource.items():
                crafted_resources[material] = crafted_resources.get(material, 0) + amount

    return {
        "structure_instance_usage": structure_instance_usage,
        "explosive_totals": explosive_totals,
        "explosive_owned_totals": explosive_owned_totals,
        "explosive_crafted_totals": explosive_crafted_totals,
        "sulfur_cost": int(value(prob.objective)),
        "total_resources": total_resources,
        "crafted_resources": crafted_resources,
        "structure_breakdown": structure_breakdown,
        "structure_usage": structure_usage,
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/resources", methods=["GET", "POST"])
def resources():
    result = None
    if request.method == "POST":
        explosive_type = request.form["explosive_type"]
        try:
            quantity = int(request.form["quantity"])
            if quantity <= 0:
                result = {"Error": "Quantity must be positive."}
            else:
                result = calculate_resources(explosive_type, quantity)
        except ValueError:
            result = {"Error": "Quantity must be an integer."}
    return render_template("resources.html", explosives=explosives, result=result)

@app.route("/damage", methods=["GET", "POST"])
def damage_per_structure():
    damages = None
    selected_structure = None
    selected_explosives = []
    if request.method == "POST":
        selected_structure = request.form.get("structure")
        selected_explosives = request.form.getlist("explosives")
        damages = specific_damage_values(selected_explosives, selected_structure)
    return render_template(
        "damage.html",
        structures=structures,
        explosives=explosives,
        damages=damages,
        selected_structure=selected_structure,
        selected_explosives=selected_explosives,
    )

@app.route("/optimizer", methods=["GET", "POST"])
def optimizer():
    results = None
    selected_structures = {}
    explosive_dict = {}
    if request.method == "POST":
        # Get selected structures and their quantities
        for struct in structures:
            qty = request.form.get(f"qty_{struct}")
            if qty and qty.isdigit() and int(qty) > 0:
                selected_structures[struct] = int(qty)
        # Get selected explosives and owned amounts
        for exp in explosives:
            # Only include explosives that are checked/selected
            if request.form.get(f"use_{exp}"):
                owned = request.form.get(f"owned_{exp}")
                try:
                    owned_amt = int(owned) if owned is not None and owned.strip() != "" else 0
                except ValueError:
                    owned_amt = 0
                explosive_dict[exp] = owned_amt
        # Only run if at least one structure and one explosive selected
        if selected_structures and explosive_dict:
            results = run_raid_optimizer(selected_structures, explosive_dict)
    return render_template(
        "optimizer.html",
        structures=structures,
        explosives=explosives,
        results=results,
        selected_structures=selected_structures,
        explosive_dict=explosive_dict,
    )

if __name__ == "__main__":
    app.run(debug=True)
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

def run_raid_optimizer(selected_structures, explosive_list):
    """
    Runs the sulfur optimizer given selected structures and explosives.
    Returns a dict with structure breakdown, explosive totals, sulfur cost, and total resources.
    """
    prob = LpProblem("Rust_Raid_Optimizer", LpMinimize)
    explosive_vars = {}
    for struct, qty in selected_structures.items():
        for i in range(qty):
            for exp in explosive_list:
                explosive_vars[(exp, struct, i)] = LpVariable(f"{exp}_{struct}_{i+1}", 0, cat='Integer')

    prob += lpSum([
        explosive_vars[(exp, struct, i)] * explosives[exp]['raw_materials']['sulfur']
        for (exp, struct, i) in explosive_vars
    ]), "Total_Sulfur_Cost"

    for (struct, qty) in selected_structures.items():
        for i in range(qty):
            prob += lpSum([
                explosive_vars[(exp, struct, i)] * explosives[exp]['damage_per_structure'][struct]
                for exp in explosive_list
            ]) >= structures[struct] + 1, f"{struct}_{i+1}"

    prob.solve()

    # Breakdown by structure
    structure_usage = {struct: {} for struct in selected_structures}
    for struct, qty in selected_structures.items():
        for exp in explosive_list:
            used = sum(
                int(explosive_vars[(exp, struct, i)].varValue)
                for i in range(qty)
                if explosive_vars[(exp, struct, i)].varValue and explosive_vars[(exp, struct, i)].varValue > 0
            )
            if used > 0:
                structure_usage[struct][exp] = used

    # Totals for each explosive
    explosive_totals = {}
    for (exp, struct, i), var in explosive_vars.items():
        if var.varValue and var.varValue > 0:
            explosive_totals[exp] = explosive_totals.get(exp, 0) + int(var.varValue)

    # Total resources
    total_resources = {}
    for (exp, struct, i), var in explosive_vars.items():
        if var.varValue and var.varValue > 0:
            resource = calculate_resources(exp, int(var.varValue))
            for material, amount in resource.items():
                total_resources[material] = total_resources.get(material, 0) + amount

    return {
        "structure_breakdown": selected_structures,
        "structure_usage": structure_usage,
        "explosive_totals": explosive_totals,
        "sulfur_cost": int(value(prob.objective)),
        "total_resources": total_resources,
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
    selected_explosives = []
    if request.method == "POST":
        # Get selected structures and their quantities
        for struct in structures:
            if request.form.get("structures") == struct or request.form.getlist("structures") and struct in request.form.getlist("structures"):
                qty = request.form.get(f"qty_{struct}")
                if qty and qty.isdigit() and int(qty) > 0:
                    selected_structures[struct] = int(qty)
        # Get selected explosives
        selected_explosives = request.form.getlist("explosives")
        if selected_structures and selected_explosives:
            results = run_raid_optimizer(selected_structures, selected_explosives)
    return render_template(
        "optimizer.html",
        structures=structures,
        explosives=explosives,
        results=results,
        selected_structures=selected_structures,
        selected_explosives=selected_explosives,
    )

if __name__ == "__main__":
    app.run(debug=True)
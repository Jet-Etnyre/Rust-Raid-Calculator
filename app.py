from flask import Flask, render_template_string, request
import json

# Load data as before
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
    if structure not in structures:
        raise ValueError(f"Structure '{structure}' not found.")
    damage_values = {}
    for explosive in explosive_list:
        if explosive not in explosives:
            raise ValueError(f"Explosive type '{explosive}' not found.")
        damage_values[explosive] = explosives[explosive]["damage_per_structure"][structure]
    return damage_values

HTML = """
<!doctype html>
<title>Rust Raid Calculator</title>
<h1>Rust Raid Calculator</h1>
<form method="post">
  <label for="explosive_type">Explosive type:</label>
  <select name="explosive_type">
    {% for exp in explosives %}
      <option value="{{exp}}">{{exp}}</option>
    {% endfor %}
  </select><br>
  <label for="quantity">Quantity:</label>
  <input name="quantity" type="number" min="1" required><br>
  <input type="submit" value="Calculate">
</form>
{% if result %}
  <h2>Resources Required:</h2>
  <ul>
    <h3>Total for {{request.form['explosive_type']}} ({{request.form['quantity']}}):</h3>
    {% for material, amount in result.items() %}
      <li>{{material}}: {{amount}}</li>
    {% endfor %}
  </ul>
{% endif %}
<a href="{{ url_for('damage_per_structure') }}">Damage Per Structure Calculator</a>
"""

DAMAGE_FORM = """
<!doctype html>
<title>Rust Raid Calculator - Damage Per Structure</title>
<h1>Damage Per Structure</h1>
<form method="post">
    <label for="structure">Select structure:</label>
    <select name="structure" required>
        {% for structure in structures %}
            <option value="{{structure}}" {% if structure == selected_structure %}selected{% endif %}>{{structure}}</option>
        {% endfor %}
    </select><br><br>
    <label>Select explosives (Ctrl+Click to select multiple):</label><br>
    <select name="explosives" multiple size="6" required>
        {% for explosive in explosives %}
            <option value="{{explosive}}" {% if explosive in selected_explosives %}selected{% endif %}>{{explosive}}</option>
        {% endfor %}
    </select><br><br>
    <input type="submit" value="Show Damage">
</form>
{% if damages %}
    <h2>Damage values for {{selected_structure}} ({{structures[selected_structure]}} HP):</h2>
    <ul>
    {% for explosive, damage in damages.items() %}
        <li>{{explosive}}: {{damage}} HP</li>
    {% endfor %}
    </ul>
{% endif %}
<a href="{{ url_for('index') }}">Back to Resource Calculator</a>
"""

@app.route("/", methods=["GET", "POST"])
def index():
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
    return render_template_string(HTML, explosives=explosives, result=result)

@app.route("/damage", methods=["GET", "POST"])
def damage_per_structure():
    damages = None
    selected_structure = None
    selected_explosives = []
    error = None
    if request.method == "POST":
        selected_structure = request.form.get("structure")
        selected_explosives = request.form.getlist("explosives")
        try:
            damages = specific_damage_values(selected_explosives, selected_structure)
        except Exception as e:
            error = str(e)
    return render_template_string(
        DAMAGE_FORM,
        structures=structures,
        explosives=explosives,
        damages=damages,
        selected_structure=selected_structure,
        selected_explosives=selected_explosives,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)
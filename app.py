from flask import Flask, render_template_string, request
import json

# Load data as before
with open('explosives.json', 'r') as file:
    explosives = json.load(file)

app = Flask(__name__)

def calculate_resources(explosive_type, quantity):
    explosive = explosives[explosive_type]
    raw_materials = explosive['raw_materials']
    total_resources = {material: amount * quantity for material, amount in raw_materials.items()}
    return total_resources

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

if __name__ == "__main__":
    app.run(debug=True)
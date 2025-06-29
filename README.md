# Rust Raid Calculator

A Python-based tool that helps players of **Rust** plan raids by minimizing sulfur cost and maximizing damage dealt to structures.

---

## Features
- Calculates total sulfur cost for chosen combinations of explosives
- Breaks down the resource cost (e.g., charcoal, low grade fuel, metal fragments)
- Supports a wide range of structures (e.g., metal walls, garage doors, turrets)
- Uses real in-game damage values for each explosive against different structures

---

## Optimization Engine

The tool  uses **PuLP**, a linear programming library, to automatically determine the most resource-efficient combination of explosives needed to destroy selected structures.

### How it Works
- The user selects the types and quantities of structures to raid alongside available explosives.
- For each structure instance, the program sets up a constraint to ensure the explosives deal at least the required damage (with a small buffer to prevent leftover health).
- The solver minimizes total sulfur usage while satisfying all damage constraints using integer counts of explosives.
- PuLP's built-in CBC (Coin-or Branch and Cut) solver is used to find the optimal combination.

---

## 📁 Project Contents
.
├── LICENSE                  # MIT license file
├── README.md                # Project overview and setup instructions
├── app.py                   # Flask web interface for raid input and optimization output
├── raid_calculator.py       # Core logic for sulfur cost minimization and damage modeling using PuLP
├── explosives.json          # Stores explosive damage values and material costs
├── structures.json          # Stores structure types and their corresponding HP values
├── static/
│   └── styles.css           # Styling for the web interface
├── templates/
│   └── [HTML files]         # HTML templates for Flask (e.g. index.html, results.html)

---

## 🚧 Status
This project is a work in progress. The optimization logic is complete, working on polishing a web app for ease of use

---

## Dependencies

- [PuLP](https://github.com/coin-or/pulp): Used for solving the optimization problem that determines the most sulfur-efficient explosive combination.

---

## 📜 License
This project is open-source and available under the **MIT License**.

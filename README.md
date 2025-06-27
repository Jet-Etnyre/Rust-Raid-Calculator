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
├─ app.py # Simple flask app
├─ raid_calculator.py # Core logic for computing sulfur-efficient raids
├─ explosives.json # JSON file with explosive stats and damage tables
├─ structures.json # JSON file with HP values for each structure
├─ README.md # Project overview and usage instructions
└─ LICENSE # MIT License terms

---

## 🚧 Status
This project is a work in progress. The optimization logic is complete, working on polishing a web app for ease of use

---

## Dependencies

- [PuLP](https://github.com/coin-or/pulp): Used for solving the optimization problem that determines the most sulfur-efficient explosive combination.

---

## 📜 License
This project is open-source and available under the **MIT License**.

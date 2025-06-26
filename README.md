# Rust Raid Calculator

A Python-based tool that helps players of **Rust** plan raids by minimizing sulfur cost and maximizing damage dealt to structures.

---

## 🔥 What It Does
- Calculates the most sulfur-efficient way to raid any structure in the game
- Uses real in-game values for structure HP and explosive damage
- Lets you specify which explosives are available to use
- Outputs a suggested combination of explosives to meet or exceed the target HP

---

## 🛠️ How to Use
This project is intended for personal or experimental use. Once a solver is added, you'll be able to input:
1. The structure you're targeting
2. Which explosives you currently have access to
3. The tool will return the cheapest sulfur path to destroy the target

--

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
This project is a work in progress. Solver logic will be added to automate the optimization process and handle edge cases like splash damage or soft-side raids.

---

## 📜 License
This project is open-source and available under the **MIT License**.

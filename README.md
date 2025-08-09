# Calculus Solver

A Python desktop application for solving calculus problems like integration, differentiation, and evaluation using natural language input. Built using Tkinter for the GUI and SymPy for symbolic computation.

---

## Features

- Solve indefinite and definite integrals
- Differentiate expressions
- Evaluate mathematical expressions
- Understands input in natural math language
- GUI includes:
  - Quick problem templates
  - Essential math symbol buttons
  - Scrollable output area
  - Clear and help functionality

---

## Requirements

- Python 3.x
- sympy
- tkinter (comes pre-installed with Python on most systems)

Install the required dependency using:

```bash
pip install sympy
How to Run
Save the script as calculus_solver.py and run it:

bash
Copy
Edit
python calculus_solver.py
Example Inputs
Integration
integrate x^2 dx

integrate sin(x) dx

integrate x^2 from 0 to 5

Differentiation
differentiate x^3 + 2*x

derive sin(x)*cos(x)

Evaluation
sin(pi/2)

cos(0)

sqrt(16)

2 + 3 * 4

Input Guidelines
Use * for multiplication: 2*x not 2x

Use ^ for exponents: x^2 not x2

Use sqrt(), log(), exp() for standard functions

Trigonometric functions are evaluated in radians

Use with respect to or dx, dy to specify variables

Use pi for π and E for Euler's constant

GUI Overview
Input box for typing calculus problems

Buttons for Solve and Clear

Quick Templates for common expressions

Symbol Buttons for easy expression building

Scrollable Output window

Help dialog explaining usage and syntax

Warning messages for common input mistakes

Limitations
Only supports single-variable expressions

No equation solving or multivariable calculus

Evaluation is numerical (floating point) where applicable
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import re

# Import SymPy more explicitly to ensure it's included in the executable
try:
    import sympy
    from sympy import sympify, integrate, diff, symbols, pi, E, exp, log, sin, cos, tan, sqrt, simplify
    from sympy.abc import x
    SYMPY_AVAILABLE = True
    print("SymPy imported successfully!")
except ImportError as e:
    SYMPY_AVAILABLE = False
    print(f"SymPy import failed: {e}")

def preprocess_expr(expr_str):
    if not expr_str:
        return expr_str
    
    # Handle common mathematical notation fixes
    expr_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr_str)  # 7x -> 7*x
    expr_str = re.sub(r'([a-zA-Z])(\d+)(?!\*)', r'\1^\2', expr_str)  # x2 -> x^2
    expr_str = re.sub(r'\bwrt\b', 'with respect to', expr_str, flags=re.IGNORECASE)
    
    # Handle dy/dx notation
    if 'dy' in expr_str.lower() and 'dx' in expr_str.lower():
        if 'find' in expr_str.lower() and '=' in expr_str:
            expr_str = re.sub(r'find\s+(\w+)\s+if\s+d\1\s*=\s*d(\w+)', r'differentiate \1 with respect to \2', expr_str, flags=re.IGNORECASE)
    
    # Fix common function notation
    functions = ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'sec', 'csc', 'cot', 'asin', 'acos', 'atan', 'ln']
    for func in functions:
        pattern = rf'\b{func}\s+(?!\()([a-zA-Z0-9_.^*/+\- ]+)'
        expr_str = re.sub(pattern, rf'{func}(\1)', expr_str)
    
    expr_str = re.sub(r'\bln\b', 'log', expr_str)  # ln -> log
    expr_str = re.sub(r'\be\^', 'exp', expr_str)   # e^x -> exp(x)
    
    return expr_str

def extract_expr_and_var(question):
    question = question.strip()

    # Find the operation
    op_match = re.search(r'\b(integrate|differentiate|derive|derivative|evaluate|calculate|solve)\b', question, re.IGNORECASE)
    op = op_match.group(1).lower() if op_match else None

    # If no explicit operation found, check if it looks like a simple evaluation
    if not op:
        # If the question contains mathematical expressions but no calculus keywords, assume evaluation
        if re.search(r'[+\-*/^()]|\b(sin|cos|tan|exp|log|sqrt)\b', question, re.IGNORECASE):
            op = 'evaluate'

    # Find "with respect to" variable
    wrt_match = re.search(r'with respect to\s+([a-zA-Z])', question, re.IGNORECASE)
    wrt = wrt_match.group(1) if wrt_match else None

    # Find bounds for definite integrals
    bounds_match = re.search(r'from\s+([-\w.]+)\s+to\s+([-\w.]+)', question, re.IGNORECASE)
    lower = upper = None
    if bounds_match:
        lower = bounds_match.group(1)
        upper = bounds_match.group(2)

    # Find dx, dy, etc.
    if not wrt:
        dx_match = re.search(r'd([a-zA-Z])\b', question)
        wrt = dx_match.group(1) if dx_match else None

    # Extract the expression
    expr_str = question
    expr_str = re.sub(r'\b(integrate|differentiate|derive|derivative|evaluate|calculate|solve)\b\s*', '', expr_str, flags=re.IGNORECASE)
    expr_str = re.sub(r'with respect to\s+[a-zA-Z]\w*', '', expr_str, flags=re.IGNORECASE)
    expr_str = re.sub(r'\s*d[a-zA-Z]\s*$', '', expr_str)
    expr_str = re.sub(r'from\s+[-\w.]+\s+to\s+[-\w.]+', '', expr_str, flags=re.IGNORECASE)
    expr_str = expr_str.strip()

    # If no variable found, default to 'x'
    if not wrt:
        wrt = 'x'

    return op, expr_str, wrt, lower, upper

def solve_calculus(question):
    if not SYMPY_AVAILABLE:
        return "Error: SymPy library not available. Please install SymPy to use this calculator."
    
    try:
        question = question.lower().strip()
        question = re.sub(r'[.?!]$', '', question)
        op, expr_str, wrt_str, lower, upper = extract_expr_and_var(question)

        expr_str = preprocess_expr(expr_str)
        wrt_str = preprocess_expr(wrt_str) if wrt_str else wrt_str

        if not expr_str or not op:
            return "Please enter a valid calculus expression, e.g. 'Integrate x^2 dx'."

        try:
            expr = sympify(expr_str)
        except Exception as e:
            return f"Could not parse the expression: '{expr_str}'. Error: {e}"

        # Handle the variable for differentiation/integration
        if wrt_str and len(wrt_str) == 1 and wrt_str.isalpha():
            wrt = sympify(wrt_str)
        else:
            free_vars = expr.free_symbols
            if free_vars:
                wrt = list(free_vars)[0]
            else:
                wrt = x

        if op == 'integrate':
            if lower and upper:
                try:
                    a = sympify(lower)
                    b = sympify(upper)
                    result = integrate(expr, (wrt, a, b))
                    result = simplify(result)
                    return f"Definite integral of {expr} from {a} to {b}:\n{result}"
                except Exception as e:
                    return f"Error during definite integration: {e}"
            else:
                result = integrate(expr, wrt)
                result = simplify(result)
                return f"Indefinite integral of {expr} w.r.t. {wrt}:\n{result} + C"

        elif op in ['differentiate', 'derive', 'derivative']:
            try:
                result = diff(expr, wrt)
                result = simplify(result)

                # Handle common simplifications
                result_str = str(result)
                result_str = result_str.replace('log(E)', '1')
                result_str = result_str.replace('log(exp(1))', '1')

                return f"Derivative of {expr} w.r.t. {wrt}:\n{result_str}"
            except Exception as e:
                return f"Error during differentiation: {e}"

        elif op in ['evaluate', 'calculate', 'solve']:
            try:
                # For evaluation, try to compute the numerical value
                result = expr.evalf()
                return f"Evaluation of {expr}:\n{result}"
            except Exception as e:
                return f"Error during evaluation: {e}"

        else:
            return "Supported operations: integrate, differentiate, evaluate"

    except Exception as e:
        return f"Error: {e}"

# GUI Functions
def clear_output():
    output.config(state=tk.NORMAL)
    output.delete(1.0, tk.END)
    output.config(state=tk.DISABLED)

def display_message(msg):
    output.config(state=tk.NORMAL)
    output.insert(tk.END, msg + "\n")
    output.config(state=tk.DISABLED)
    output.see(tk.END)

def solve_question():
    question = entry.get().strip()
    if not question:
        display_message("Please enter a question.")
        return
    
    clear_output()
    display_message("Solving: " + question + "\n")
    
    # Check for common notation issues
    warnings = []
    if re.search(r'\d[a-zA-Z]', question) and '*' not in question:
        warnings.append("⚠️ Did you mean to use * for multiplication? (e.g., 2*x instead of 2x)")
    
    if re.search(r'[a-zA-Z]\*\d+(?!\^)', question):
        warnings.append("⚠️ Did you mean exponentiation? Use ^ instead of * (e.g., x^2 instead of x*2)")
    
    if 'wrt' in question.lower():
        warnings.append("⚠️ Use 'with respect to' instead of 'wrt'")
    
    if warnings:
        for warning in warnings:
            display_message(warning)
        display_message("")
    
    ans = solve_calculus(question)
    display_message(ans)

def insert_text(text):
    entry.insert(tk.END, text)
    entry.focus()

def clear_input():
    entry.delete(0, tk.END)
    entry.focus()

def insert_template(template):
    clear_input()
    entry.insert(0, template)
    entry.focus()

def show_help():
    help_text = """CALCULUS SOLVER HELP

INTEGRATION:
• integrate x^2 dx
• integrate sin(x) dx
• integrate x^2 from 0 to 5

DIFFERENTIATION:
• differentiate x^3 + 2*x
• derive sin(x)*cos(x)

EVALUATION (NEW!):
• sin(5*18) → evaluates sin(90) in radians
• cos(pi/4) → evaluates cos(π/4)
• sqrt(16) → evaluates to 4
• 2+3*4 → evaluates to 14

IMPORTANT RULES:
⚠️ Write 7*x NOT 7x
⚠️ Write x^2 NOT x*2
⚠️ Trig functions use RADIANS not degrees
⚠️ For degrees: sin(30*pi/180) = sin(30°)

EXAMPLES:
✅ integrate 2*x^2 + 3*x dx
✅ differentiate sin(x^2)
✅ sin(pi/2) → gives 1
✅ cos(0) → gives 1"""
    messagebox.showinfo("Help", help_text)

def on_quit():
    if messagebox.askquestion("Exit", "Are you sure you want to exit?") == 'yes':
        root.destroy()

# GUI Setup
root = tk.Tk()
root.title("Calculus Solver")
root.geometry("1000x700")
root.configure(bg='#f0f0f0')

main_frame = tk.Frame(root, bg='#f0f0f0', padx=15, pady=15)
main_frame.pack(fill=tk.BOTH, expand=True)

title_label = tk.Label(main_frame, text="🧮 Calculus Solver", 
                      font=("Arial", 20, "bold"), bg='#f0f0f0', fg='#2c3e50')
title_label.pack(pady=(0, 20))

# Input section
input_frame = tk.Frame(main_frame, bg='#f0f0f0')
input_frame.pack(fill=tk.X, pady=(0, 15))

input_label = tk.Label(input_frame, text="Enter your calculus problem:", 
                      font=("Arial", 12, "bold"), bg='#f0f0f0')
input_label.pack(anchor=tk.W)

entry_frame = tk.Frame(input_frame, bg='#f0f0f0')
entry_frame.pack(fill=tk.X, pady=(5, 0))

entry = tk.Entry(entry_frame, font=("Arial", 14), relief=tk.RAISED, bd=2)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
entry.bind("<Return>", lambda e: solve_question())

solve_btn = tk.Button(entry_frame, text="🔍 Solve", font=("Arial", 12, "bold"), 
                     command=solve_question, bg='#3498db', fg='white', 
                     relief=tk.RAISED, bd=2, padx=20)
solve_btn.pack(side=tk.RIGHT, padx=(10, 0))

clear_btn = tk.Button(entry_frame, text="🗑️ Clear", font=("Arial", 12), 
                     command=clear_input, bg='#e74c3c', fg='white', 
                     relief=tk.RAISED, bd=2, padx=15)
clear_btn.pack(side=tk.RIGHT, padx=(5, 0))

# Quick templates
buttons_frame = tk.Frame(main_frame, bg='#f0f0f0')
buttons_frame.pack(fill=tk.X, pady=(0, 15))

templates_label = tk.Label(buttons_frame, text="🚀 Quick Templates:", 
                          font=("Arial", 14, "bold"), bg='#f0f0f0', fg='#2c3e50')
templates_label.pack(anchor=tk.W, pady=(0, 10))

template_frame = tk.Frame(buttons_frame, bg='#f0f0f0')
template_frame.pack(fill=tk.X, pady=(0, 15))

templates = [
    ("∫ x² dx", "integrate x^2 dx"),
    ("∫ sin(x) dx", "integrate sin(x) dx"),
    ("d/dx x³", "differentiate x^3"),
    ("∫₀¹ x² dx", "integrate x^2 from 0 to 1"),
]

for i, (display, template) in enumerate(templates):
    btn = tk.Button(template_frame, text=display, font=("Arial", 12, "bold"),
                   command=lambda t=template: insert_template(t),
                   bg='#9b59b6', fg='white', relief=tk.RAISED, bd=2, 
                   width=15, height=2)
    btn.pack(side=tk.LEFT, padx=5)

# Essential symbols
symbols_label = tk.Label(buttons_frame, text="🔢 Essential Symbols:", 
                        font=("Arial", 14, "bold"), bg='#f0f0f0', fg='#2c3e50')
symbols_label.pack(anchor=tk.W, pady=(10, 5))

symbol_frame = tk.Frame(buttons_frame, bg='#f0f0f0')
symbol_frame.pack(fill=tk.X)

symbols = [
    ("x", "x"), ("^", "^"), ("()", "()"), ("+", " + "), ("-", " - "), ("*", "*"),
    ("sin", "sin("), ("cos", "cos("), ("exp", "exp("), ("log", "log("), ("√", "sqrt("), ("π", "pi")
]

for i, (display, symbol) in enumerate(symbols):
    btn = tk.Button(symbol_frame, text=display, font=("Arial", 11, "bold"),
                   command=lambda s=symbol: insert_text(s),
                   bg='#27ae60', fg='white', relief=tk.RAISED, bd=2,
                   width=6, height=2)
    btn.pack(side=tk.LEFT, padx=2)

# Output section
output_label = tk.Label(main_frame, text="📋 Solution:", 
                       font=("Arial", 14, "bold"), bg='#f0f0f0', fg='#2c3e50')
output_label.pack(anchor=tk.W, pady=(15, 5))

output = ScrolledText(main_frame, font=("Consolas", 13), state=tk.DISABLED, 
                     wrap=tk.WORD, height=15, relief=tk.SUNKEN, bd=2,
                     bg='#ffffff', selectbackground='#3498db')
output.pack(fill=tk.BOTH, expand=True)

# Bottom buttons
bottom_frame = tk.Frame(main_frame, bg='#f0f0f0')
bottom_frame.pack(fill=tk.X, pady=(15, 0))

help_btn = tk.Button(bottom_frame, text="❓ Help", font=("Arial", 14, "bold"),
                    command=show_help, bg='#f39c12', fg='white',
                    relief=tk.RAISED, bd=3, padx=30, pady=10)
help_btn.pack(side=tk.LEFT)

quit_btn = tk.Button(bottom_frame, text="❌ Exit", font=("Arial", 14, "bold"),
                    command=on_quit, bg='#95a5a6', fg='white',
                    relief=tk.RAISED, bd=3, padx=30, pady=10)
quit_btn.pack(side=tk.RIGHT)

# Welcome message
welcome_msg = """🎓 Welcome to the Calculus Solver!

This tool helps you solve calculus problems and evaluate mathematical expressions.

🚀 HOW TO USE:
1. 📝 Type your problem or use Quick Templates
2. 🔘 Use symbol buttons for easy input
3. 🔍 Click Solve or press Enter

💡 EXAMPLES:
• integrate x^2 dx (calculus)
• differentiate sin(x) (calculus)
• sin(pi/2) (evaluation - gives 1)
• sqrt(16) (evaluation - gives 4)

📐 Note: Trig functions use radians!
Click '❓ Help' for more examples!
"""

display_message(welcome_msg)
entry.focus()

root.protocol("WM_DELETE_WINDOW", on_quit)
root.mainloop()
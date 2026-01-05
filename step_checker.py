from sympy import symbols, diff, simplify
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import sympy as sp
import streamlit as st
import re

x, y, t = symbols('x y t')
dy_dx = symbols('dy_dx')

# ----------------- UTILITY ----------------- #
def parse_expr_safe(expr):
    if isinstance(expr, str):

        # Allow equations: A = B → A - B
        if "=" in expr:
            lhs, rhs = expr.split("=", 1)
            expr = f"({lhs}) - ({rhs})"
        
        # Replace superscripts
        superscripts = {
            "⁰": "**0", "¹": "**1", "²": "**2", "³": "**3", "⁴": "**4",
            "⁵": "**5", "⁶": "**6", "⁷": "**7", "⁸": "**8", "⁹": "**9"
        }
        for sup, repl in superscripts.items():
            expr = expr.replace(sup, repl)

        # Replace math symbols
        expr = expr.replace("−","-").replace("×","*").replace("÷","/")

        # Fix caret and ln
        expr = expr.replace("^","**").replace("ln","log")

        # Auto-fix: y dy/dx  →  y*dy_dx
        expr = re.sub(r'([a-zA-Z])\s*dy/dx', r'\1*dy_dx', expr)

        # Map dy/dx to dy_dx
        expr = expr.replace("dy/dx", "dy_dx")

        transformations = (standard_transformations + (implicit_multiplication_application,))
        expr = parse_expr(expr, transformations=transformations,
                          local_dict={"x":x,"y":y,"t":t,"dy_dx":dy_dx})
    return expr

# ----------------- PARAMETRIC ----------------- #
def parametric_derivative_chain(x_t, y_t):
    dx_dt = diff(x_t, t)
    dy_dt = diff(y_t, t)
    if dx_dt == 0:
        raise ValueError("dx/dt is zero, derivative undefined.")
    return simplify(dy_dt / dx_dt)

# ----------------- IMPLICIT ----------------- #
def implicit_derivative(lhs, rhs=0):
    expr = lhs - rhs
    dx = diff(expr, x)
    dy = diff(expr, y)
    if dy == 0:
        raise ValueError("dy/dx undefined (division by zero).")
    return simplify(-dx / dy)

# ----------------- MAIN STEP CHECKER ----------------- #

def normalize_line(s: str) -> str:
    return s.strip().lower()

def analyze_steps(student_steps, expected_steps):
    """
    expected_steps: list of dicts like:
      {"label": "dx/dt", "expr": sympy_expr, "display": "\\frac{dx}{dt} = ..."}
    student_steps: list of raw strings
    """
    feedback = []

    student_norm = [normalize_line(s) for s in student_steps]
    expected_labels = [e["label"].lower() for e in expected_steps]

    # Detect missing by label presence
    missing = []
    for e in expected_steps:
        label = e["label"].lower()
        found = any(label in s for s in student_norm)
        if not found:
            # Use LaTeX for readable detail
            latex_expr = sp.latex(e["expr"])
            missing.append(f"{e['label']} = {latex_expr}")

    if missing:
        feedback.append("⚠️ Your steps are incomplete.")

    # Detect extras: student lines that don't reference any expected label
    extras = []
    for s in student_norm:
        if not any(lbl in s for lbl in expected_labels):
            extras.append(s)

    if extras:
        feedback.append("ℹ️ You provided more steps than needed, but they didn’t influence the final answer.")

    if not missing and not extras:
        feedback.append("✅ Steps match expected.")

    return feedback

def check_derivative_steps(student_steps, original_func=None, mode="Normal", parametric_inputs=None):
    feedback = []

    if mode == "Parametric":
        if not parametric_inputs or len(parametric_inputs) != 2:
            raise ValueError("Parametric mode requires x(t) and y(t).")
        x_expr, y_expr = parametric_inputs

        # Compute expected steps
        dx_dt = diff(x_expr, t)
        dy_dt = diff(y_expr, t)
        dy_dx_raw = dy_dt / dx_dt
        dy_dx_simplified = simplify(dy_dx_raw)

        expected_steps = [dx_dt, dy_dt, dy_dx_raw, dy_dx_simplified]

        for i, step in enumerate(student_steps):
            step_expr = parse_expr_safe(step)
            if i < len(expected_steps):
                expected = expected_steps[i]
            else:
                expected = dy_dx_simplified  # fallback to final answer

            if simplify(step_expr - expected) == 0:
                feedback.append(f"Step {i+1}: ✅ Correct")
            else:
                feedback.append(f"Step {i+1}: ❌ Incorrect. Correction: {expected}")
        return feedback


    if mode == "Implicit":
        if not isinstance(original_func, tuple) or len(original_func) != 2:
            raise ValueError("Implicit mode requires a tuple (lhs, rhs).")
        lhs, rhs = original_func
        correct_derivative = implicit_derivative(lhs, rhs)
        for i, step in enumerate(student_steps):
            step_expr = parse_expr_safe(step)
            if simplify(step_expr - correct_derivative) == 0:
                feedback.append(f"Step {i+1}: ✅ Correct")
            else:
                feedback.append(f"Step {i+1}: ❌ Incorrect. Correction: {correct_derivative}")
        return feedback

    #Normal mode
    elif mode == "Normal":
        correct_expr = parse_expr_safe(original_func)
    for i, step in enumerate(student_steps):
        step_expr = parse_expr_safe(step)
        expected = diff(correct_expr, x) if i == 0 else diff(parse_expr_safe(student_steps[i-1]), x)
        if simplify(step_expr - expected) == 0:
            feedback.append(f"Step {i+1}: ✅ Correct")
        else:
            feedback.append(f"Step {i+1}: ❌ Incorrect. Correction: {expected}")

    return feedback


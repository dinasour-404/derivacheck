from sympy import symbols, diff, simplify
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from step_explanations import STEP_EXPLANATIONS
import re
import sympy as sp
import streamlit as st

x, y, t = symbols('x y t')
dy_dx = symbols('dy_dx')

# ----------------- UTILITY ----------------- #
def parse_expr_safe(expr):
    if isinstance(expr, str):
        if "=" in expr:
            lhs, rhs = expr.split("=", 1)
            expr = f"({lhs}) - ({rhs})"

        superscripts = {"⁰":"**0","¹":"**1","²":"**2","³":"**3","⁴":"**4",
                        "⁵":"**5","⁶":"**6","⁷":"**7","⁸":"**8","⁹":"**9"}
        for sup, repl in superscripts.items():
            expr = expr.replace(sup, repl)

        expr = expr.replace("−","-").replace("×","*").replace("÷","/")
        expr = expr.replace("^","**").replace("ln","log")
        expr = re.sub(r'([a-zA-Z])\s*dy/dx', r'\1*dy_dx', expr)
        expr = expr.replace("dy/dx", "dy_dx")

        transformations = (standard_transformations + (implicit_multiplication_application,))
        expr = parse_expr(expr, transformations=transformations,
                          local_dict={"x":x,"y":y,"t":t,"dy_dx":dy_dx})
    return expr

# ----------------- DERIVATIVES ----------------- #
def parametric_derivative_chain(x_t, y_t):
    dx_dt = diff(x_t, t)
    dy_dt = diff(y_t, t)
    if dx_dt == 0:
        raise ValueError("dx/dt is zero, derivative undefined.")
    return simplify(dy_dt / dx_dt)

def implicit_derivative(lhs, rhs=0):
    expr = lhs - rhs
    dx = diff(expr, x)
    dy = diff(expr, y)
    if dy == 0:
        raise ValueError("dy/dx undefined (division by zero).")
    return simplify(-dx / dy)

# ----------------- FEEDBACK GENERATOR ----------------- #
def generate_missing_feedback(missing_steps):
    feedback = []
    for tag in missing_steps:
        explanation = STEP_EXPLANATIONS.get(tag)
        if explanation:
            feedback.append(
                f"📌 {explanation['title']}\nRequired step:\n{explanation['textbook']}"
            )
    return feedback

# ----------------- MAIN CHECKER ----------------- #
def check_derivative_steps(student_steps, original_func=None, mode="Normal", parametric_inputs=None):
    feedback = []
    missing_steps = []

    # ---------- PARAMETRIC ----------
    if mode == "Parametric":
        if not parametric_inputs or len(parametric_inputs) != 2:
            raise ValueError("Parametric mode requires x(t) and y(t).")
        x_expr, y_expr = parametric_inputs

        dx_dt = diff(x_expr, t)
        dy_dt = diff(y_expr, t)
        dy_dx_simplified = simplify(dy_dt / dx_dt)

        expected_steps = [dx_dt, dy_dt, dy_dx_simplified]

        for i, step in enumerate(student_steps):
            step_expr = parse_expr_safe(step)
            expected = expected_steps[i] if i < len(expected_steps) else dy_dx_simplified
            if simplify(step_expr - expected) == 0:
                feedback.append(f"Step {i+1}: ✅ Correct")
            else:
                feedback.append(f"Step {i+1}: ❌ Incorrect. Correction: {expected}")
                missing_steps.append("parametric_rule")

    # ---------- IMPLICIT ----------
    elif mode == "Implicit":
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
                # Detect missing dy/dx
                if "dy_dx" not in step:
                    missing_steps.append("implicit_dydx")

    # ---------- NORMAL ----------
    else:  # Normal mode
        correct_expr = parse_expr_safe(original_func)
        expected_derivative = diff(correct_expr, x)

        for i, step in enumerate(student_steps):
            step_expr = parse_expr_safe(step)
            if simplify(step_expr - expected_derivative) == 0:
                feedback.append(f"Step {i+1}: ✅ Correct")
            else:
                feedback.append(f"Step {i+1}: ❌ Incorrect. Correction: {expected_derivative}")
                # Detect missing rules
                s_str = str(step_expr)
                if "cos" in s_str and "-sin" not in s_str:
                    missing_steps.append("cos_rule")
                    missing_steps.append("missing_negative")
                if "**" in s_str and "*" not in s_str:
                    missing_steps.append("chain_rule")

    # ---------- GENERATE TEXTBOOK FEEDBACK ----------
    missing_feedback = generate_missing_feedback(missing_steps)

    return {
        "step_feedback": feedback,
        "missing_feedback": missing_feedback
    }

# ----------------- BACKEND HELPERS ----------------- #
def to_backend(expr: str) -> str:
    if not expr:
        return ""
    # Superscripts → Python power notation
    expr = expr.replace("⁰","**0").replace("¹","**1").replace("²","**2") \
               .replace("³","**3").replace("⁴","**4").replace("⁵","**5") \
               .replace("⁶","**6").replace("⁷","**7").replace("⁸","**8") \
               .replace("⁹","**9")
    # Replace math symbols
    expr = expr.replace("−","-").replace("×","*").replace("÷","/")
    return expr

def parse_expr_safe(expr: str):
    try:
        # Allow implicit multiplication (e.g., 4x → 4*x, 2(x+1) → 2*(x+1))
        transformations = (standard_transformations + (implicit_multiplication_application,))
        return parse_expr(expr, transformations=transformations)
    except Exception as e:
        raise e

def to_latex(expr: str) -> str:
    if not expr:
        return ""
    expr = expr.replace("**","^").replace("*","")
    expr = expr.replace("d/dx", r"\frac{d}{dx} ")
    expr = expr.replace("dy/dx", r"\frac{dy}{dx}")
    expr = re.sub(r"\b(sin|cos|tan|sec|csc|cot|ln|exp)\b", r"\\\1", expr)
    return expr

# ======================================================
# NEW STEP-BY-STEP CHECKER (ADDED, NOT REPLACING)
# ======================================================

def check_steps_against_expected(student_steps, expected_steps):
    feedback = []
    max_len = max(len(student_steps), len(expected_steps))

    for i in range(max_len):
        student = student_steps[i] if i < len(student_steps) else None
        expected = expected_steps[i]["expr"] if i < len(expected_steps) else None
        expected_display = expected_steps[i]["display"] if i < len(expected_steps) else None

        if student and expected:
            try:
                # Parse both into Sympy expressions for math equivalence
                student_expr = parse_expr_safe(to_backend(student))
                if sp.simplify(student_expr - expected) == 0:
                    feedback.append(f"✅ Step {i+1} correct: {student}")
                else:
                    feedback.append(f"\\text{{❌ Step {i+1} incorrect.}} \nCorrection: {expected_display}")
            except Exception:
                feedback.append(st.write(f"⚠️ Step {i+1} could not be parse \nYour Input: {student} Don't be such nonsense!`"))
        elif student and not expected:
            feedback.append(f"⚠️ Extra step {i+1}: {student}")
        elif expected and not student:
            feedback.append(st.write(f"❌ Missing step {i+1} \nCorrection: {expected_display}"))

<<<<<<< HEAD
    return feedback
=======
    return feedback
>>>>>>> e7d1cfb73026eb79f22c7334f5e52854f573ed0f

from sympy import simplify, symbols

# Optional: utility functions for normalization or comparison
def equivalent(expr1, expr2):
    """
    Check if two SymPy expressions are equivalent.
    """
    return simplify(expr1 - expr2) == 0

def normalize(expr):
    """
    Simplify and normalize an expression for comparison.
    """
    return simplify(expr)

# Main function your app calls
def check_derivative_steps(student_steps, original_func):
    """
    Check each step of a derivative against the correct derivative.

    Parameters:
    - student_steps: list of SymPy expressions (each step)
    - original_func: SymPy expression of the original function

    Returns:
    - List of feedback messages for each step
    """
    feedback = []
    x = symbols('x')
    correct = simplify(original_func)

    for i, step in enumerate(student_steps):
        # Compute expected derivative for this step
        expected = simplify(correct.diff(x) if i == 0 else student_steps[i-1].diff(x))
        if equivalent(step, expected):
            feedback.append(f"Step {i+1}: ✅ Correct")
        else:
            feedback.append(f"Step {i+1}: ❌ Incorrect. Correction: {expected}")
    return feedback

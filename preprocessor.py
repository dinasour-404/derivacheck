# preprocessor.py

from latex2sympy2 import latex2sympy
from sympy import simplify

def preprocess_input(input_text):
    """
    Convert user LaTeX input into a SymPy expression.
    Strips whitespace, parses LaTeX, and simplifies it.
    """
    input_text = input_text.strip()
    try:
        expr = latex2sympy(input_text)
        expr = simplify(expr)
        return expr
    except Exception as e:
        # Return error message instead of crashing
        return f"Error parsing input: {e}"

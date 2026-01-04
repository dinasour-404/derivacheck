from sympy import simplify, sympify

def replace_superscripts(expr_str):
    """Convert superscript characters to ** exponent format for sympy."""
    sup_map = {
        "⁰": "0", "¹": "1", "²": "2", "³": "3",
        "⁴": "4", "⁵": "5", "⁶": "6",
        "⁷": "7", "⁸": "8", "⁹": "9"
    }
    result = ""
    for c in expr_str:
        if c in sup_map:
            result += "**" + sup_map[c]
        else:
            result += c
    return result

def preprocess_input(input_text):
    """
    Convert user input into a SymPy expression.
    Handles superscripts and simplifies the result.
    """
    input_text = input_text.strip()
    try:
        input_text = replace_superscripts(input_text)
        expr = sympify(input_text)
        return simplify(expr)
    except Exception as e:
        return f"Error parsing input: {e}"

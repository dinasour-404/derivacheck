# ----------------- UTILITY ----------------- #
def parse_expr_safe(expr):
    if isinstance(expr, str):
        # Replace all superscript digits with Python power notation
        superscripts = {
            "⁰": "**0", "¹": "**1", "²": "**2", "³": "**3", "⁴": "**4",
            "⁵": "**5", "⁶": "**6", "⁷": "**7", "⁸": "**8", "⁹": "**9"
        }
        for sup, repl in superscripts.items():
            expr = expr.replace(sup, repl)

        # Replace math symbols
        expr = expr.replace("−", "-").replace("×", "*").replace("÷", "/")

        # Fix common mistakes
        expr = expr.replace("^", "**")  # caret to power
        expr = expr.replace("ln", "log")  # map ln to log

        # Use SymPy parser with implicit multiplication
        transformations = (standard_transformations + (implicit_multiplication_application,))
        try:
            print("Parsing:", expr)  # Debugging line
            expr = parse_expr(expr, transformations=transformations)
        except Exception as e:
            print("Failed to parse:", expr)
            raise
    return expr

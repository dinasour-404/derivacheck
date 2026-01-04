from sympy import simplify

# ---------------- UTILITY FUNCTIONS ---------------- #
def normalize(expr):
    """Simplify expression for consistent comparison."""
    return simplify(expr)

def equivalent(expr1, expr2):
    """Check if two expressions are mathematically equivalent."""
    return simplify(expr1 - expr2) == 0

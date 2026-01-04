from sympy import symbols, Pow, Mul

x = symbols('x')

def detect_rules(expr):
    """
    Detect which differentiation rules are involved in the expression.
    Returns: list of rules
    """
    rules = []

    # Power Rule
    if expr.has(Pow) or expr.is_polynomial(x):
        rules.append("Power Rule")

    # Product Rule
    if expr.is_Mul and any(term.has(x) for term in expr.args):
        rules.append("Product Rule")

    # Quotient Rule
    numerator, denominator = expr.as_numer_denom()
    if denominator.has(x):
        rules.append("Quotient Rule")

    # Chain Rule
    atoms = expr.atoms()
    if any(sub != x and sub.has(x) for sub in atoms):
        rules.append("Chain Rule")

    return list(set(rules))
from sympy import symbols, Pow, Mul

x = symbols('x')

def detect_rules(expr):
    """
    Detects which differentiation rules are involved in the expression.

    Parameters
    ----------
    expr : sympy expression
        The function to analyze

    Returns
    -------
    list of str
        Rules involved: 'Power Rule', 'Product Rule', 'Quotient Rule', 'Chain Rule'
    """
    rules = []

    # Power Rule: x**n or polynomials
    if expr.has(Pow) or expr.is_polynomial(x):
        rules.append("Power Rule")

    # Product Rule: multiplication of terms containing x
    if expr.is_Mul and any(term.has(x) for term in expr.args):
        rules.append("Product Rule")

    # Quotient Rule: division
    numerator, denominator = expr.as_numer_denom()
    if denominator.has(x):
        rules.append("Quotient Rule")

    # Chain Rule: any nested functions of x
    atoms = expr.atoms()
    if any(sub != x and sub.has(x) for sub in atoms):
        rules.append("Chain Rule")

    return list(set(rules))  # remove duplicates

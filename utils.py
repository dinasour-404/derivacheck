from sympy import simplify

def normalize(expr):
    """
    Simplifies the expression for consistent comparison.
    
    Parameters
    ----------
    expr : sympy expression
        The expression to simplify

    Returns
    -------
    sympy expression
        Simplified version
    """
    return simplify(expr)


def equivalent(expr1, expr2):
    """
    Checks if two SymPy expressions are mathematically equivalent.
    
    Parameters
    ----------
    expr1, expr2 : sympy expressions
        Expressions to compare

    Returns
    -------
    bool
        True if mathematically equivalent, False otherwise
    """
    return simplify(expr1 - expr2) == 0

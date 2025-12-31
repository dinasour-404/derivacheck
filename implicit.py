from sympy import diff, symbols, simplify

x, y = symbols('x y')

def implicit_derivative(lhs, rhs):
    """
    Computes dy/dx for an implicit equation lhs = rhs.

    Parameters
    ----------
    lhs : sympy expression
        Left-hand side of the equation
    rhs : sympy expression
        Right-hand side of the equation

    Returns
    -------
    sympy expression
        dy/dx
    """
    expr = lhs - rhs
    # Move all trhs

    # Compute derivative w.r.t x
    dx = diff(expr, x)
    dy = diff(expr, y)

    # Solve for dy/dx
    dydx = simplify(-dx / dy)
    return dydx

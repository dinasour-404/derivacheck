from sympy import symbols, diff, simplify, solve, latex

# Symbols
x, y, t = symbols('x y t')

# ---------------- PARAMETRIC ---------------- #
def parametric_derivative_chain(x_t, y_t):
    """
    Computes dy/dx for parametric equations using the chain rule.
    Returns (simplified expression, LaTeX string)
    """
    dx_dt = diff(x_t, t)
    dy_dt = diff(y_t, t)

    if dx_dt == 0:
        raise ValueError("dx/dt is zero, derivative undefined.")

    dydx = simplify(dy_dt / dx_dt)
    return dydx, latex(dydx)

# ---------------- IMPLICIT ---------------- #
def implicit_derivative(lhs, rhs=0):
    """
    Computes dy/dx for an implicit equation lhs = rhs.
    Returns (simplified expression, LaTeX string)
    """
    expr = lhs - rhs
    dydx_symbol = symbols('dy_dx')

    # Form equation: dx/dx + dy/dy * dy/dx = 0
    eq = diff(expr, x) + diff(expr, y) * dydx_symbol

    # Solve for dy/dx
    solutions = solve(eq, dydx_symbol)
    if not solutions:
        raise ValueError("Could not solve for dy/dx")

    dydx = simplify(solutions[0])
    return dydx, latex(dydx)
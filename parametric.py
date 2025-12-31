from sympy import diff, symbols, simplify

t = symbols('t')

def parametric_derivative_chain(x_t, y_t):
    """
    Computes dy/dx for parametric equations using the chain rule.

    Parameters
    ----------
    x_t : sympy expression
        x as a function of t
    y_t : sympy expression
        y as a function of t

    Returns
    -------
    sympy expression
        dy/dx
    """
    dx_dt = diff(x_t, t)
    dy_dt = diff(y_t, t)

    if dx_dt == 0:
        raise ValueError("dx/dt is zero, derivative undefined.")

    dydx = simplify(dy_dt / dx_dt)
    return dydx

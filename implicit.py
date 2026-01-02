from sympy import diff, symbols, simplify
# diff     : differentiation function
# symbols  : creates symbolic variables
# Function : creates symbolic functions (e.g. y(x))
# simplify : simplifies algebraic expressions

x = symbols('x')
# Independent variable

y = Function('y')(x)
# Declare y as a function of x (y = y(x))
# This is CRITICAL for implicit differentiation
# Now SymPy knows dy/dx ≠ 0 and applies the chain rule

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
    # Move everything to one side:
    # lhs = rhs  →  lhs - rhs = 0

    d_expr = diff(expr, x)
    # Differentiate the entire expression with respect to x
    # Because y = y(x), SymPy automatically applies:
    # d/dx(y) = dy/dx

    dydx = simplify(
        d_expr.solve(diff(y, x))[0]
    )
    # Solve the differentiated equation for dy/dx
    # diff(y, x) explicitly represents dy/dx
    # solve(...) returns a list → take the first solution
    # simplify the final expression for cleanliness

    return dydx
    # Return dy/dx as a symbolic expression

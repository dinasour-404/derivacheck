from sympy import diff, symbols
from .utils import normalize

x = symbols('x')

def true_derivative(expr):
    """
    Computes the derivative of a SymPy expression with respect to x.

    Parameters
    ----------
    expr : sympy expression
        The function to differentiate

    Returns
    -------
    sympy expression
        The derivative, simplified
    """
    derivative = diff(expr, x)
    return normalize(derivative)

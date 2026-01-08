# step_explanations.py

STEP_EXPLANATIONS = {

    # ---- Basic Trig Rules ----
    "cos_rule": {
        "title": "Derivative of cos(x)",
        "textbook": "d/dx [cos(x)] = −sin(x)"
    },

    "sin_rule": {
        "title": "Derivative of sin(x)",
        "textbook": "d/dx [sin(x)] = cos(x)"
    },

    "tan_rule": {
        "title": "Derivative of tan(x)",
        "textbook": "d/dx [tan(x)] = sec²(x)"
    },

    "sec_rule": {
        "title": "Derivative of sec(x)",
        "textbook": "d/dx [sec(x)] = sec(x)·tan(x)"
    },

    "csc_rule": {
        "title": "Derivative of csc(x)",
        "textbook": "d/dx [csc(x)] = −csc(x)·cot(x)"
    },

    "cot_rule": {
        "title": "Derivative of cot(x)",
        "textbook": "d/dx [cot(x)] = −csc²(x)"
    },

    # ---- Power / Polynomial Rules ----
    "power_rule": {
        "title": "Power Rule",
        "textbook": "d/dx [xⁿ] = n·xⁿ⁻¹"
    },

    "constant_rule": {
        "title": "Derivative of a Constant",
        "textbook": "d/dx [c] = 0"
    },

    # ---- Chain / Product / Quotient ----
    "chain_rule": {
        "title": "Chain Rule",
        "textbook": "If y = f(g(x)), then dy/dx = f′(g(x)) · g′(x)"
    },

    "product_rule": {
        "title": "Product Rule",
        "textbook": "d/dx [u·v] = u′·v + u·v′"
    },

    "quotient_rule": {
        "title": "Quotient Rule",
        "textbook": "d/dx [u/v] = (u′·v − u·v′)/v²"
    },

    # ---- Missing Negative Signs ----
    "missing_negative": {
        "title": "Missing Negative Sign",
        "textbook": "Check your derivative: d/dx [cos(x)] = −sin(x), d/dx [cot(x)] = −csc²(x)"
    },

    # ---- Implicit Differentiation ----
    "implicit_dydx": {
        "title": "Implicit Differentiation",
        "textbook": "When differentiating y with respect to x, include dy/dx: d/dx [yⁿ] = n·yⁿ⁻¹ · dy/dx"
    },

    "implicit_missing_chain": {
        "title": "Chain Rule in Implicit Differentiation",
        "textbook": "Remember: if y is a function of x, any term with y requires multiplying by dy/dx"
    },

    # ---- Parametric Differentiation ----
    "parametric_rule": {
        "title": "Parametric Differentiation",
        "textbook": "dy/dx = (dy/dt) / (dx/dt)"
    },

    "parametric_missing_chain": {
        "title": "Chain Rule in Parametric Differentiation",
        "textbook": "When differentiating y(t) or x(t), apply the chain rule: d/dt [y(t)] contributes to dy/dx"
    },

    # ---- Exponentials / Logarithms ----
    "exp_rule": {
        "title": "Derivative of Exponential",
        "textbook": "d/dx [e^x] = e^x"
    },

    "ln_rule": {
        "title": "Derivative of ln(x)",
        "textbook": "d/dx [ln(x)] = 1/x"
    },

    # ---- Common Mistakes ----
    "forgot_chain": {
        "title": "Forgot Chain Rule",
        "textbook": "Check if you missed multiplying by the derivative of the inner function"
    },

    "forgot_product": {
        "title": "Forgot Product Rule",
        "textbook": "Check if you differentiated each factor separately and added: (u·v)' = u'·v + u·v'"
    },

    "forgot_quotient": {
        "title": "Forgot Quotient Rule",
        "textbook": "Check: (u/v)' = (u'·v − u·v') / v²"
    },

}

import streamlit as st
import re
from step_checker import check_derivative_steps, parse_expr_safe

# ----------------- PAGE CONFIG ----------------- #
st.set_page_config(page_title="DerivaCheck", layout="centered")
st.title("🧮 DerivaCheck – Differentiation Step Checker")

# ----------------- SESSION STATE ----------------- #
defaults = {
    "mode": "Normal",
    "active_box": "Function",
    "func": "",
    "x_t": "",
    "y_t": "",
    "steps": "",
    "history": [],
    "waiting_power": False,
    "power_buffer": ""
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ----------------- MODE SELECTION ----------------- #
st.radio(
    "Differentiation Type:",
    ["Normal", "Implicit", "Parametric"],
    horizontal=True,
    key="mode"
)

# ----------------- ACTIVE BOX ----------------- #
boxes = ["Function", "Steps"] if st.session_state.mode != "Parametric" else ["x(t)", "y(t)", "Steps"]
if st.session_state.active_box not in boxes:
    st.session_state.active_box = boxes[0]

st.radio(
    "Math Keyboard Input Goes To:",
    boxes,
    horizontal=True,
    key="active_box"
)

# ----------------- INPUT BOXES ----------------- #
if st.session_state.mode in ["Normal", "Implicit"]:
    st.text_input("Enter Function / Equation:", key="func", placeholder="Example: 2x³ + 3x")
else:
    st.text_input("x(t) =", key="x_t", placeholder="Example: t²")
    st.text_input("y(t) =", key="y_t", placeholder="Example: t³")

st.text_area("Working steps (one per line):", key="steps", height=160)

# ----------------- KEYBOARD ----------------- #
st.markdown("### 🔢 Math Keyboard")

if st.session_state.mode == "Parametric":
    left_keys = [
        ["7","8","9","+","−"],
        ["4","5","6","×","÷"],
        ["1","2","3",".","π"],
        ["0","dx/dt","dy/dt","dy/dx","="],
        ["sqrt(","⌫","Clear"]
    ]
    right_keys = [
        ["a²","aᵇ","x","t",None],   # include t here
        ["("," )","y",None,None],
        ["sin(","cos(","tan(",None,None],
        ["sec(","ln(","exp(",None,None]
    ]
else:  # Normal or Implicit
    left_keys = [
        ["7","8","9","+","−"],
        ["4","5","6","×","÷"],
        ["1","2","3",".","π"],
        ["0","d/dx","dy/dx","sqrt(","="],
        ["⌫","Clear"]
    ]
    right_keys = [
        ["a²","aᵇ","x",None,None],  # no t here
        ["("," )","y",None,None],
        ["sin(","cos(","tan(",None,None],
        ["sec(","ln(","exp(",None,None]
    ]
    
# Superscript digit mapping
superscript_map = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"
}

def insert_key(key):
    if not key:
        return

    # Map active box names to session_state keys
    box_map = {
        "Function": "func",
        "x(t)": "x_t",
        "y(t)": "y_t",
        "Steps": "steps"
    }
    target = box_map[st.session_state.active_box]

    # Handle exponent start
    if key == "aᵇ":
        st.session_state.waiting_power = True
        st.session_state.power_buffer = ""
        return

    # If waiting for exponent digits
    if getattr(st.session_state, "waiting_power", False):
        if key.isdigit():
            # Add superscript digit visually
            st.session_state[target] += superscript_map[key]
            st.session_state.power_buffer += key
            return
        else:
            # End exponent mode if non-digit pressed
            st.session_state.waiting_power = False
            st.session_state.power_buffer = ""

    # Clear button
    if key == "Clear":
        st.session_state[target] = ""
        return

    # Backspace button
    if key == "⌫":
        st.session_state[target] = st.session_state[target][:-1]
        return

    # Default insertion
    st.session_state[target] += key

cols = st.columns([3,2])
for row in left_keys:
    row_cols = cols[0].columns(len(row))
    for i, key in enumerate(row):
        row_cols[i].button(key, on_click=insert_key, args=(key,), use_container_width=True)
for row in right_keys:
    row_cols = cols[1].columns(len(row))
    for i, key in enumerate(row):
        if key is not None:
            row_cols[i].button(key, on_click=insert_key, args=(key,), use_container_width=True)

import re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

# ----------------- BACKEND HELPERS ----------------- #
def to_backend(expr: str) -> str:
    if not expr:
        return ""
    # Superscripts → Python power notation
    expr = expr.replace("⁰","**0").replace("¹","**1").replace("²","**2") \
               .replace("³","**3").replace("⁴","**4").replace("⁵","**5") \
               .replace("⁶","**6").replace("⁷","**7").replace("⁸","**8") \
               .replace("⁹","**9")
    # Replace math symbols
    expr = expr.replace("−","-").replace("×","*").replace("÷","/")
    return expr

def parse_expr_safe(expr: str):
    try:
        # Allow implicit multiplication (e.g., 4x → 4*x, 2(x+1) → 2*(x+1))
        transformations = (standard_transformations + (implicit_multiplication_application,))
        return parse_expr(expr, transformations=transformations)
    except Exception as e:
        raise e

def to_latex(expr: str) -> str:
    if not expr:
        return ""
    expr = expr.replace("**","^").replace("*","")
    expr = expr.replace("d/dx", r"\frac{d}{dx} ")
    expr = expr.replace("dy/dx", r"\frac{dy}{dx}")
    expr = re.sub(r"\b(sin|cos|tan|sec|csc|cot|ln|exp)\b", r"\\\1", expr)
    return expr

# ----------------- CHECK BUTTON ----------------- #
st.divider()
if st.button("✅ Check Steps"):
    if st.session_state.mode in ["Normal","Implicit"] and not st.session_state.func.strip():
        st.error("Please enter a function/equation"); st.stop()
    if st.session_state.mode=="Parametric" and (not st.session_state.x_t.strip() or not st.session_state.y_t.strip()):
        st.error("Please enter both x(t) and y(t)"); st.stop()
    if not st.session_state.steps.strip():
        st.error("Please enter your steps"); st.stop()

    steps_lines = [l.strip() for l in st.session_state.steps.splitlines() if l.strip()]

    if st.session_state.mode=="Parametric":
        x_expr = parse_expr_safe(to_backend(st.session_state.x_t))
        y_expr = parse_expr_safe(to_backend(st.session_state.y_t))
        results = check_derivative_steps(
            student_steps=steps_lines,
            original_func=None,
            mode="Parametric",
            parametric_inputs=(x_expr, y_expr)
        )
    elif st.session_state.mode=="Implicit":
        func_str = st.session_state.func
        if "=" not in func_str:
            st.error("Implicit mode expects an equation like: x^2 + y^2 = 25"); st.stop()
        lhs_str, rhs_str = func_str.split("=", 1)
        lhs_expr = parse_expr_safe(to_backend(lhs_str.strip()))
        rhs_expr = parse_expr_safe(to_backend(rhs_str.strip()))
        results = check_derivative_steps(
            student_steps=steps_lines,
            original_func=(lhs_expr, rhs_expr),
            mode="Implicit"
        )
    else:
        # Normal mode
        func_expr = parse_expr_safe(to_backend(st.session_state.func))
        results = check_derivative_steps(
            student_steps=steps_lines,
            original_func=func_expr,
            mode="Normal"
        )

    # Preview
    st.markdown("### 👀 Preview")
    if st.session_state.mode=="Parametric":
        st.latex("x(t) = " + to_latex(st.session_state.x_t))
        st.latex("y(t) = " + to_latex(st.session_state.y_t))
    else:
        st.latex(to_latex(st.session_state.func))
    for line in st.session_state.steps.splitlines():
        st.latex(to_latex(line))

    # Feedback
    st.markdown("## 📋 Feedback")
    for msg in results:
        if "Correction:" in msg:
            user_input, correct = msg.split("Correction:",1)
            st.markdown("**Your Input:**"); st.latex(to_latex(user_input.strip()))
            st.markdown("**Correct Answer:**"); st.latex(to_latex(correct.strip()))
        else:
            st.write(msg)

    # Save history (unchanged)
    st.session_state.history.append({
        "mode": st.session_state.mode,
        "func": st.session_state.func,
        "x": st.session_state.x_t,
        "y": st.session_state.y_t,
        "steps": st.session_state.steps,
        "results": results
    })
    st.session_state.history = st.session_state.history[-10:]

# ----------------- HISTORY SIDEBAR ----------------- #
st.sidebar.markdown("### 🕘 History")
for h in reversed(st.session_state.history):
    st.sidebar.markdown(f"**Mode:** {h['mode']}")
    if h['mode']=="Parametric":
        st.sidebar.latex("x(t) = "+to_latex(h['x']))
        st.sidebar.latex("y(t) = "+to_latex(h['y']))
    else:
        st.sidebar.latex(to_latex(h['func']))
    st.sidebar.markdown("**Steps / Corrections:**")
    for msg in h['results']:
        if "Correction:" in msg:
            user_input, correct = msg.split("Correction:",1)
            st.sidebar.markdown("Your Input:"); st.sidebar.latex(to_latex(user_input.strip()))
            st.sidebar.markdown("Correct Answer:"); st.sidebar.latex(to_latex(correct.strip()))
        else:
            st.sidebar.write(msg)
    st.sidebar.divider()
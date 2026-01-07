import streamlit as st
import sympy as sp
import re
import sympy as sp
from sympy import simplify
from step_checker import check_derivative_steps, check_steps_against_expected, parse_expr_safe, analyze_steps
from user_interface import apply_neomath_theme, render_math_keyboard,set_background

# Apply theme at the start 
apply_neomath_theme()
set_background()

# ----------------- PAGE CONFIG ----------------- #
st.set_page_config(page_title="DerivaCheck", layout="wide")
st.markdown(
    '<div class="banner"><h1 class="banner-title">🧮 DerivaCheck – Differentiation Step Checker</h1></div>',
    unsafe_allow_html=True
)

# ----------------- TUTORIAL STATE ----------------- #
if "show_tutorial" not in st.session_state:
    st.session_state.show_tutorial = True  # show tutorial by default first time

# ----------------- TUTORIAL CONTENT ----------------- #
st.divider()
if st.session_state.show_tutorial:
    st.info("👋 Welcome to DerivaCheck! Let's walk through how to use it.")

    st.markdown("### Step 1: Choose Differentiation Type")
    st.markdown("Pick **Normal**, **Implicit**, or **Parametric** depending on your problem.")

    st.markdown("### Step 2: Enter Your Function or Equation")
    st.markdown("For example: `2x³ + 3x`")

    st.markdown("### Step 3: Add Your Working Steps")
    st.markdown("Write each of your working step on a new line.")

    st.markdown("### Step 4: Use the Math Keyboard")
    st.markdown("Tap buttons to insert symbols like `d/dx` or powers.")

    st.markdown("### Step 5: Press ✅ Check Steps")
    st.markdown("You'll see feedback comparing your steps to the correct solution.")

    # Hide tutorial button
    if st.button("Got it! Hide tutorial"):
        st.session_state.show_tutorial = False

# ----------------- SHOW BACK BUTTON ----------------- #
if not st.session_state.show_tutorial:
    if st.button("📖 Show Tutorial Again"):
        st.session_state.show_tutorial = True

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
        
if "cursor_pos" not in st.session_state:
    st.session_state.cursor_pos = 0


# ----------------- MODE SELECTION ----------------- #
st.divider()
st.markdown('<span class="section-label">Differentiation Type:</span>', unsafe_allow_html=True)
st.radio(
    label=" ",  # invisible label
    options=["Normal", "Implicit", "Parametric"],
    horizontal=True,
    key="mode",
    label_visibility="collapsed"  # hides default spacing
)


# ----------------- ACTIVE BOX ----------------- #
boxes = ["Function", "Steps"] if st.session_state.mode != "Parametric" else ["x(t)", "y(t)", "Steps"]
if st.session_state.active_box not in boxes:
    st.session_state.active_box = boxes[0]

st.markdown('<span class="section-label">Math Keyboard Input Goes To:</span>', unsafe_allow_html=True)
st.radio(
    label=" ",  # visually blank
    options=boxes,
    horizontal=True,
    key="active_box",
    label_visibility="collapsed"  # hides the default label spacing
)


# ----------------- INPUT BOXES ----------------- #
# Helper to provide placeholders based on mode
def get_placeholders():
    mode = st.session_state.mode

    if mode == "Normal":
        return {
            "func": "Example: 2x³ + 3x",
            "steps": "Example:\n1) d/dx (2x³ + 3x)\n2) 6x² + 3"
        }

    if mode == "Implicit":
        return {
            "func": "Example: x² + y² = 25",
            "steps": "Example:\n1) Differentiate both sides \n2) 2x + 2y dy/dx = 0"
        }

    # Parametric
    return {
        "x_t": "Example: t²",
        "y_t": "Example: t³",
        "steps": "Example:\n1) dx/dt = 2t\n2) dy/dt = 3t²\n3) dy/dx = (dy/dt)*(dt/dx)"
    }

# Get current placeholders
placeholders = get_placeholders()

if st.session_state.mode in ["Normal", "Implicit"]:
    st.text_input(
        "Enter Function / Equation:",
        key="func",
        placeholder=placeholders.get("func", "")
    )
else:
    st.info("💡 In parametric differentiation, you need both dx/dt and dy/dt. Enter them step by step!")
    st.text_input(
        "x(t) =",
        key="x_t",
        placeholder=placeholders.get("x_t", "")
    )
    st.text_input(
        "y(t) =",
        key="y_t",
        placeholder=placeholders.get("y_t", "")
    )

st.text_area(
    "Working steps (one per line):",
    key="steps",
    height=160,
    placeholder=placeholders.get("steps", "")
)

# ----------------- KEYBOARD ----------------- #
st.markdown("### 🔢 Math Keyboard")

cursor_pos = st.components.v1.html("""
<script>
const pos = window.streamlitCursorPos ?? 0;
window.parent.postMessage(
  { type: "streamlit:setCursor", value: pos },
  "*"
);
</script>
""", height=0)


if st.session_state.mode == "Parametric":
    left_keys = [
        ["1","2","3","+","−"],
        ["4","5","6","×","÷"],
        ["7","8","9",".","π"],
        ["0","dx/dt","dy/dt","dy/dx","="],
        ["sqrt(","⌫","Clear"]
    ]
    right_keys = [
        [None,"aᵇ","x","t",None,None],   # include t here
        [None,"("," )","y",None,None],
        [None,"sin(","cos(","tan(",None,None],
        [None,"sec(","ln(","exp(",None,None]
    ]
else:  # Normal or Implicit
    left_keys = [
        ["1","2","3","+","−"],
        ["4","5","6","×","÷"],
        ["7","8","9",".","π"],
        ["0","d/dx","dy/dx","sqrt(","="],
        ["⌫","Clear"]
    ]
    right_keys = [
        [None,"aᵇ","x",None,None,None],  # no t here
        [None,"("," )","y",None,None],
        [None,"sin(","cos(","tan(",None,None],
        [None,"sec(","ln(","exp(",None,None]
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

    # Default insertion at cursor
    pos = st.session_state.get("cursor_pos", len(st.session_state[target]))
    st.session_state[target] = st.session_state[target][:pos] + key + st.session_state[target][pos:]
    st.session_state["cursor_pos"] = pos + len(key)


cols = st.columns([3,2])
for row in left_keys:
    row_cols = cols[0].columns(len(row))
    for i, key in enumerate(row):
        display_key = "＋" if key == "+" else key  # fix plus sign
        row_cols[i].button(display_key, on_click=insert_key, args=(key,), use_container_width=True)
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

# ======================================================
# NEW STEP-BY-STEP CHECKER (ADDED, NOT REPLACING)
# ======================================================
def check_steps_against_expected(student_steps, expected_steps):
    feedback = []

    for i, step in enumerate(student_steps):
        try:
            step_expr = parse_expr_safe(step)
        except Exception:
            feedback.append(f"Step {i+1}: ❌ Invalid expression")
            continue

        if i >= len(expected_steps):
            feedback.append(f"Step {i+1}: ℹ️ Extra step (not required)")
            continue

        expected_expr = expected_steps[i]["expr"]

        if simplify(step_expr - expected_expr) == 0:
            feedback.append(f"Step {i+1}: ✅ Correct")
        else:
            feedback.append(
                f"Step {i+1}: ❌ Incorrect. Correction: {sp.latex(expected_expr)}"
            )

    if len(student_steps) < len(expected_steps):
        feedback.append("⚠️ Some expected steps are missing.")

    return feedback
# ----------------- CHECK BUTTON ----------------- #
st.divider()
if st.button("✅ Check Steps"):
    if st.session_state.mode in ["Normal","Implicit"] and not st.session_state.func.strip():
        st.error("Please enter a function/equation")
        st.stop()
    if st.session_state.mode=="Parametric" and (not st.session_state.x_t.strip() or not st.session_state.y_t.strip()):
        st.error("Please enter both x(t) and y(t)")
        st.stop()
    if not st.session_state.steps.strip():
        st.error("Please enter your steps")
        st.stop()

    steps_lines = [l.strip() for l in st.session_state.steps.splitlines() if l.strip()]

    # ---------------- PROCESS STEPS ---------------- #
    if st.session_state.mode=="Parametric":
        t = sp.symbols('t')
        x_expr = parse_expr_safe(to_backend(st.session_state.x_t))
        y_expr = parse_expr_safe(to_backend(st.session_state.y_t))

        dx_dt = sp.diff(x_expr, t)
        dy_dt = sp.diff(y_expr, t)
        dy_dx = sp.simplify(dy_dt / dx_dt)

        expected_steps = [
            {"label": "dx/dt", "expr": dx_dt, "display": r"\frac{dx}{dt} = " + sp.latex(dx_dt)},
            {"label": "dy/dt", "expr": dy_dt, "display": r"\frac{dy}{dt} = " + sp.latex(dy_dt)},
            {"label": "dy/dx", "expr": dy_dx, "display": r"\frac{dy}{dx} = " + sp.latex(dy_dx)},
        ]

        results = check_steps_against_expected(
           student_steps=steps_lines,
           expected_steps=expected_steps
        )


    elif st.session_state.mode=="Implicit":
        x, y = sp.symbols('x y')
        func_str = st.session_state.func
        lhs_str, rhs_str = func_str.split("=", 1)
        lhs_expr = parse_expr_safe(to_backend(lhs_str.strip()))
        rhs_expr = parse_expr_safe(to_backend(rhs_str.strip()))

        dy_dx_symbol = sp.Symbol('dy/dx')
        d_lhs = sp.diff(lhs_expr, x) + sp.diff(lhs_expr, y) * dy_dx_symbol
        d_rhs = sp.diff(rhs_expr, x) + sp.diff(rhs_expr, y) * dy_dx_symbol

        sol = sp.solve(sp.Eq(d_lhs, d_rhs), dy_dx_symbol)
        dy_dx = sp.simplify(sol[0]) if sol else None

        expected_steps = [
            {"label": "d/dx(lhs)", "expr": d_lhs, "display": r"\frac{d}{dx}(\text{LHS}) = " + sp.latex(d_lhs)},
            {"label": "d/dx(rhs)", "expr": d_rhs, "display": r"\frac{d}{dx}(\text{RHS}) = " + sp.latex(d_rhs)},
        ]
        if dy_dx is not None:
            expected_steps.append({"label": "dy/dx", "expr": dy_dx, "display": r"\frac{dy}{dx} = " + sp.latex(dy_dx)})

        results = check_steps_against_expected(
            student_steps=steps_lines,
            expected_steps=expected_steps
        )  

        

    else:  # Normal
        x = sp.symbols('x')
        func_expr = parse_expr_safe(to_backend(st.session_state.func))
        dfx = sp.simplify(sp.diff(func_expr, x))
        expected_steps = [
            {"label": "d/dx", "expr": dfx, "display": r"\frac{d}{dx} = " + sp.latex(dfx)},
        ]

        results = check_steps_against_expected(
           student_steps=steps_lines,
           expected_steps=expected_steps
        )


    # ---------------- PREVIEW ---------------- #
    st.markdown("### 👀 Preview")
    if st.session_state.mode=="Parametric":
        st.latex("x(t) = " + to_latex(st.session_state.x_t))
        st.latex("y(t) = " + to_latex(st.session_state.y_t))
    else:
        st.latex(to_latex(st.session_state.func))
    for line in st.session_state.steps.splitlines():
        st.latex(to_latex(line))

    # ---------------- FEEDBACK ---------------- #
    st.markdown("## 📋 Feedback")
    completeness_feedback = analyze_steps(steps_lines, expected_steps)
    results = completeness_feedback + results

    for msg in results:
        if "Correction:" in msg:
            user_input, correct = msg.split("Correction:",1)
            st.markdown("**Your Input:**")
            st.latex(to_latex(user_input.strip()))
            st.markdown("**Correct Answer:**")
            st.latex(to_latex(correct.strip()))
        else:
            st.write(msg)

    # ---------------- AUTO-COMPUTED REFERENCE ---------------- #
    st.markdown("### 🔮 Auto-computed reference")
    for e in expected_steps:
        st.latex(e["display"])

    # ---------------- SAVE HISTORY ---------------- #
    st.session_state.history.append({
        "mode": st.session_state.mode,
        "func": st.session_state.func,
        "x": st.session_state.x_t,
        "y": st.session_state.y_t,
        "steps": st.session_state.steps,
        "results": results
    })
    # Keep last 10 entries only
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
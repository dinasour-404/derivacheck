import streamlit as st
from step_checker import check_derivative_steps

# 2️⃣ Streamlit page config
st.set_page_config(page_title="DerivaCheck", layout="centered")

# ---------------- SESSION STATE ---------------- #
if "history" not in st.session_state:
    st.session_state.history = []  

if "original_function" not in st.session_state:
    st.session_state.original_function = ""

if "student_steps" not in st.session_state:
    st.session_state.student_steps = ""

if "active_box" not in st.session_state:
    st.session_state.active_box = "Function"

if "waiting_for_power" not in st.session_state:
    st.session_state.waiting_for_power = False

if "power_buffer" not in st.session_state:
    st.session_state.power_buffer = ""


#add function of switching between implicit and parametric

if "diff_mode" not in st.session_state:
    st.session_state.diff_mode = "Normal"

if "x_t" not in st.session_state:
    st.session_state.x_t = ""

if "y_t" not in st.session_state:
    st.session_state.y_t = ""


# ---------------- TITLE ---------------- #
st.title("🧮 DerivaCheck – Differentiation Step Checker")

# ✅ STEP 2: Mode selector goes here
st.markdown("### ⚙️ Differentiation Type")

st.session_state.diff_mode = st.radio(
    "Choose method:",
    ["Normal", "Implicit", "Parametric"],
    horizontal=True
)

st.divider()

## ---------------- ACTIVE INPUT SELECTOR ---------------- #

st.markdown("### ✏️ Select which box the math keyboard types into:")

if st.session_state.diff_mode == "Parametric":
    st.session_state.active_box = st.radio(
        "Send keyboard input to:",
        ["x(t)", "y(t)", "Steps"],
        horizontal=True
    )
else:
    st.session_state.active_box = st.radio(
        "Send keyboard input to:",
        ["Function", "Steps"],
        horizontal=True
    )

# ---------------- INPUT BOXES ---------------- #

if st.session_state.diff_mode == "Normal":
    st.session_state.original_function = st.text_input(
        "Enter y = f(x):",
        value=st.session_state.original_function,
        placeholder="Example: y = x³ + 4x"
    )

elif st.session_state.diff_mode == "Implicit":
    st.session_state.original_function = st.text_input(
        "Enter the equation:",
        value=st.session_state.original_function,
        placeholder="Example: x² + y² = 25"
    )

elif st.session_state.diff_mode == "Parametric":
    st.session_state.x_t = st.text_input(
        "x(t) =",
        value=st.session_state.x_t,
        placeholder="Example: t²"
    )
    st.session_state.y_t = st.text_input(
        "y(t) =",
        value=st.session_state.y_t,
        placeholder="Example: t³"
    )

st.session_state.student_steps = st.text_area(
    "Enter your working steps (one step per line):",
    value=st.session_state.student_steps,
    height=160
)

# ---------------- MATH KEYBOARD ---------------- #
st.markdown("### 🔢 Math Keyboard")

keyboard = [
    [None, None, None, None, None, None,None,"⌫","Clear",],
    # Numbers + add/subtract + powers
    ["7", "8", "9", "＋", "−", None, "a²", "aᵇ", "x","t"],

    # Numbers + multiply/divide + brackets + y
    ["4", "5", "6", "×", "÷", None, "(", ")", "y",],

    # Numbers + constants + trig
    ["1", "2", "3", ".", "π", None, "sin(", "cos(", "tan("],

    # Zero + calculus + actions
    ["0", "d/dx", "dy/dx","sqrt(", "=", None, "sec(", "ln(", "exp("]
]

    
# ---------------- Callback Functions ---------------- #

superscript_digits = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³",
    "4": "⁴", "5": "⁵", "6": "⁶",
    "7": "⁷", "8": "⁸", "9": "⁹"
}

def to_superscript(text):
    return "".join(superscript_digits.get(c, c) for c in text)


def add_key(key):
    symbol_map = {
        "＋": "+",
        "−": "-",
        "×": "*",
        "÷": "/",
        "a²": "²"
    }

    # ---------- Handle aᵇ ----------
    if key == "aᵇ":
        st.session_state.waiting_for_power = True
        st.session_state.power_buffer = ""
        return

    # ---------- Handle exponent input ----------
    if st.session_state.get("waiting_for_power", False):
        if key.isdigit():
            exponent = to_superscript(key)
            box = st.session_state.active_box

            if box == "Function":
                st.session_state.original_function += exponent
            elif box == "x(t)":
                st.session_state.x_t += exponent
            elif box == "y(t)":
                st.session_state.y_t += exponent
            else:  # Steps
                st.session_state.student_steps += exponent

            st.session_state.waiting_for_power = False
            st.session_state.power_buffer = ""
            return

    # ---------- Normal insertion ----------
    insert = symbol_map.get(key, key)
    box = st.session_state.active_box

    if box == "Function":
        st.session_state.original_function += insert
    elif box == "x(t)":
        st.session_state.x_t += insert
    elif box == "y(t)":
        st.session_state.y_t += insert
    else:  # Steps
        st.session_state.student_steps += insert


def delete_key():
    box = st.session_state.active_box

    if box == "Function":
        st.session_state.original_function = st.session_state.original_function[:-1]
    elif box == "x(t)":
        st.session_state.x_t = st.session_state.x_t[:-1]
    elif box == "y(t)":
        st.session_state.y_t = st.session_state.y_t[:-1]
    else:
        st.session_state.student_steps = st.session_state.student_steps[:-1]


def clear_box():
    box = st.session_state.active_box

    if box == "Function":
        st.session_state.original_function = ""
    elif box == "x(t)":
        st.session_state.x_t = ""
    elif box == "y(t)":
        st.session_state.y_t = ""
    else:
        st.session_state.student_steps = ""


# ---------------- Render Keyboard ----------------

# Mode-aware keyboard rules
mode = st.session_state.diff_mode

keyboard_rules = {
    "Normal": {"disable": [], "highlight": []},
    "Implicit": {"disable": [], "highlight": ["dy/dx"]},
    "Parametric": {"disable": [], "highlight": ["dy/dx"]}
}

rules = keyboard_rules.get(mode, {})
disable_keys = rules.get("disable", [])
highlight_keys = rules.get("highlight", [])

# ---------------- Render each row of the keyboard ----------------
for row_index, row in enumerate(keyboard):
    cols = st.columns(len(row))  # Create a column for each key in the row

    for col_index, key in enumerate(row):

        # ---------------- Handle gaps ----------------
        if key is None:
            cols[col_index].markdown("&nbsp;")  # invisible spacer
            continue

        # ---------------- Unique button key ----------------
        # Important for Streamlit to prevent fast-click / duplicate key issues
        button_key = f"{key}_{row_index}_{col_index}"

        is_disabled = key in disable_keys
        is_highlighted = key in highlight_keys

        # ---------------- CSS styling ----------------
        # Only row_index == 1 (second row) gets smaller buttons
        css_class = "small-row" if row_index == 1 else "math-btn"

        # ---------------- Render button ----------------
        with cols[col_index]:
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)

            if key == "⌫":
                st.button(
                    key,
                    key=button_key,
                    use_container_width=True,
                    on_click=delete_key
                )
            elif key == "Clear":
                st.button(
                    key,
                    key=button_key,
                    use_container_width=True,
                    on_click=clear_box
                )
            else:
                st.button(
                    key,
                    key=button_key,
                    use_container_width=True,
                    disabled=is_disabled,
                    help="Recommended for this method" if is_highlighted else None,
                    on_click=add_key,
                    args=(key,)
                )

            st.markdown("</div>", unsafe_allow_html=True)


# ---------- Frontend: Unicode superscript → LaTeX ----------

import re

def ui_to_latex(expr):
    # 1️⃣ Convert superscripts → LaTeX powers
    sup_map = {
        "⁰": "0", "¹": "1", "²": "2", "³": "3",
        "⁴": "4", "⁵": "5", "⁶": "6",
        "⁷": "7", "⁸": "8", "⁹": "9"
    }

    # Convert unicode superscripts to LaTeX
    result = ""
    i = 0
    while i < len(expr):
        c = expr[i]

        # Handle unicode superscripts
        if c in sup_map:
            power = ""
            while i < len(expr) and expr[i] in sup_map:
                power += sup_map[expr[i]]
                i += 1
            result += f"^{{{power}}}"

        # Handle manual ^ typing
        elif c == "^":
            i += 1
            power = ""
            while i < len(expr) and (expr[i].isdigit() or expr[i] in sup_map):
                power += sup_map.get(expr[i], expr[i])
                i += 1
            result += f"^{{{power}}}"

        else:
            result += c
            i += 1

    # 2️⃣ Insert explicit multiplication for SymPy
    result = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', result)
    result = re.sub(r'([a-zA-Z])(\d|\()', r'\1*\2', result)
    result = re.sub(r'(\})([a-zA-Z(])', r'\1*\2', result)

    return result



# ---------------- CHECK BUTTON ---------------- #
st.divider()

if st.button("✅ Check Steps"):

    mode = st.session_state.diff_mode

    # ---------- FRONTEND VALIDATION ----------
    if mode in ["Normal", "Implicit"]:
        if st.session_state.original_function.strip() == "":
            st.error("Please enter the function.")
            st.stop()

    elif mode == "Parametric":
        if st.session_state.x_t.strip() == "" or st.session_state.y_t.strip() == "":
            st.error("Please enter both x(t) and y(t).")
            st.stop()

    if st.session_state.student_steps.strip() == "":
        st.error("Please enter your working steps.")
        st.stop()

    # ---------- UI → LaTeX CONVERSION ----------
    latex_steps = ui_to_latex(st.session_state.student_steps.replace("",""))

    if mode in ["Normal", "Implicit"]:
        latex_function = ui_to_latex(
            st.session_state.original_function.replace(" ", "")
        )
    else:  # Parametric
        latex_function = {
            "x": ui_to_latex(st.session_state.x_t.replace(" ", "")),
            "y": ui_to_latex(st.session_state.y_t.replace(" ", ""))
        }

    # ---------- SAVE HISTORY (UI VERSION) ----------
    if mode in ["Normal", "Implicit"]:
        st.session_state.history.append({
            "mode": mode,
            "function": st.session_state.original_function,
            "steps": st.session_state.student_steps
        })
    else:  # Parametric
        st.session_state.history.append({
            "mode": mode,
            "x(t)": st.session_state.x_t,
            "y(t)": st.session_state.y_t,
            "steps": st.session_state.student_steps
        })

   # ---------- BACKEND CALL ----------
if mode == "Parametric":
    # Send x(t) and y(t) separately to backend
    x_expr = latex_function['x']
    y_expr = latex_function['y']

    results = check_derivative_steps(
        latex_steps,
        x_expr,
        y_expr,
        mode=mode
    )
else:
    # Normal or Implicit mode
    results = check_derivative_steps(
        latex_steps,
        latex_function,
        mode=mode
    )


    # ---------- PREVIEW ----------
    st.markdown("### 👀 Math Preview")

    if mode == "Parametric":
        st.latex("x(t) = " + latex_function["x"])
        st.latex("y(t) = " + latex_function["y"])

    st.latex(latex_steps)

    # ---------- FEEDBACK ----------
    st.markdown("## 📋 Feedback")
    for msg in results:
        if "Correction:" in msg:
            # Fix issue 5: only split once
            text, correction = msg.split("Correction:", 1)
            st.write(text.strip())
            st.latex(correction.strip())
        else:
            st.write(msg)

# ---------------- HISTORY SIDEBAR ----------------
st.sidebar.markdown("### 🕘 History")

if st.session_state.history:
    # show last 10 entries
    for i, item in enumerate(reversed(st.session_state.history[-10:]), 1):
        st.sidebar.markdown(f"**{i}. Mode:** {item['mode']}")

        if item["mode"] == "Parametric":
            st.sidebar.latex("x(t) = " + ui_to_latex(item["x(t)"]))
            st.sidebar.latex("y(t) = " + ui_to_latex(item["y(t)"]))
        else:
            st.sidebar.latex(ui_to_latex(item["function"]))

        st.sidebar.markdown("**Steps:**")
        st.sidebar.latex(ui_to_latex(item["steps"]))
        st.sidebar.divider()
else:
    st.sidebar.write("No history yet.")




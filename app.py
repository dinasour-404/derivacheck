import streamlit as st #streamlit was shortform to be used as st

#take other functions from other files
from preprocessor import preprocess_input 
from step_checker import check_derivative_steps
from sympy import latex, simplify

#set_page_config is the page name
st.set_page_config(page_title="DerivaCheck", page_icon = " ", layout="wide")


# ---------------- SESSION STATE ---------------- #
#st.session_state prevents the already written input from being erased when the coding need to rerun from the top
#referred to google docs for further explaination!
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


# ---------------- TITLE ---------------- #
st.title("MathGuard – Differentiation Step Checker")
st.write("Type your working steps. Use the math keyboard below for symbols.")
st.divider()


# ---------------- ACTIVE INPUT SELECTOR ---------------- #
st.markdown("### Select which box the math keyboard types into:")

# Radio button updates active_box, keep session state consistent
selected_box = st.radio(
    "Active input box:",
    ["Function", "Steps"],
    horizontal=True,
    index=0 if st.session_state.active_box == "Function" else 1
)


# Update session state only if selection changed
st.session_state.active_box = selected_box


# ---------------- INPUT BOXES ---------------- #
st.session_state.original_function = st.text_input(
    "Enter the original function f(x):",
    value=st.session_state.original_function,
    placeholder="Example: x^3+4*x+2 or x³+4x+2"
)


st.session_state.student_steps = st.text_area(
    "Enter your working steps (one step per line):",
    value=st.session_state.student_steps,
    height=160,
    placeholder="Example: 3*x^2 + 4"
)


# ---------------- MATH KEYBOARD ---------------- #
st.markdown("### Math Keyboard")
keys = [
    [None, None, None, None, None, None, None, "⌫", "Clear"],
    ["7", "8", "9", "＋", "−", None, "a²", "aᵇ", "x"],
    ["4", "5", "6", "×", "÷", None, "(", ")", "y"],
    ["1", "2", "3", ".", "π", None, "sin(", "cos(", "tan("],
    ["0", "d/dx", "dy/dx", "sqrt(", "=", None, "sec(", "ln(", "exp("]
]


# ---------------- Callback Functions ----------------

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


    # Handle aᵇ separately
    if key == "aᵇ":
        st.session_state.waiting_for_power = True
        st.session_state.power_buffer = ""  # store multiple digits
        return


    # If waiting for power (multi-digit)
    if st.session_state.get("waiting_for_power", False):
        if key.isdigit():
            st.session_state.power_buffer += key
            return  # do not insert yet
        else:
            # End of exponent, insert as superscript
            power = ''.join(c for c in st.session_state.power_buffer if c.isdigit())
            insert_sup = to_superscript(power)
            if st.session_state.active_box == "Function":
                st.session_state.original_function += insert_sup
            else:
                st.session_state.student_steps += insert_sup
            st.session_state.waiting_for_power = False
            st.session_state.power_buffer = ""


    # Normal insertion
    insert = symbol_map.get(key, key)
    if st.session_state.active_box == "Function":
        st.session_state.original_function += insert
    else:
        st.session_state.student_steps += insert


def delete_key():
    if st.session_state.active_box == "Function":
        st.session_state.original_function = st.session_state.original_function[:-1]
    else:
        st.session_state.student_steps = st.session_state.student_steps[:-1]


def clear_box():
    if st.session_state.active_box == "Function":
        st.session_state.original_function = ""
    else:
        st.session_state.student_steps = ""


# ---------------- Render Keyboard ----------------
for row_index, row in enumerate(keys):
    cols = st.columns(len(row))
    for col_index, key in enumerate(row):


        # Gap between groups
        if key is None:
            cols[col_index].markdown("&nbsp;")
            continue

        symbol_map_for_key = {
            "⌫": "back", 
            "Clear": "clear"
            }

        # Unique key for Streamlit button to prevent fast-click issues
        button_key = f"{st.session_state.active_box}_{symbol_map_for_key.get(key, key)}_{row_index}_{col_index}"


        # Attach appropriate callback
        if key == "⌫":
            cols[col_index].button(key, key=button_key, use_container_width=True, on_click=delete_key)
        elif key == "Clear":
            cols[col_index].button(key, key=button_key, use_container_width=True, on_click=clear_box)
        else:
            cols[col_index].button(key, key=button_key, use_container_width=True, on_click=add_key, args=(key,))

# ---------- Frontend: Unicode superscript → LaTeX ----------


import re

def ui_to_latex(expr):
    # ---------------- Superscript digits ----------------
    sup_map = {
        "⁰": "0", "¹": "1", "²": "2", "³": "3",
        "⁴": "4", "⁵": "5", "⁶": "6",
        "⁷": "7", "⁸": "8", "⁹": "9"
    }

    # Convert unicode superscripts to normal digits
    result = ""
    i = 0
    while i < len(expr):
        c = expr[i]
        if c in sup_map:
            power = ""
            while i < len(expr) and expr[i] in sup_map:
                power += sup_map[expr[i]]
                i += 1
            result += f"^{power}"
        else:
            result += c
            i += 1

    # ---------------- Safe exponent conversion ----------------
    # x^{ {2} } → x**(2)
    result = re.sub(r'\^\{\s*\{(\d+)\}\s*\}', r'**(\1)', result)
    # x^{2} → x**(2)
    result = re.sub(r'\^\{(\d+)\}', r'**(\1)', result)
    # x^2 → x**2
    result = re.sub(r'\^(\d+)', r'**\1', result)

    # ---------------- Explicit multiplication ----------------
    # number followed by letter or opening parenthesis → 8x → 8*x
    result = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', result)
    # letter followed by number or opening parenthesis → x2 → x*2
    result = re.sub(r'([a-zA-Z])(\d|\()', r'\1*\2', result)
    # closing brace followed by letter or opening parenthesis → }x → }*x
    result = re.sub(r'(\})([a-zA-Z(])', r'\1*\2', result)

    return result

from sympy import sympify, symbols

# ---------- NEW HELPER FUNCTION FOR HISTORY DISPLAY ----------
from sympy import sympify, latex, Symbol

def render_step_to_latex(step_str):
    """
    Convert a user-input step string to a valid LaTeX string for Streamlit.
    """
    x = Symbol('x')  # define symbols
    try:
        parsed = sympify(ui_to_latex(step_str.replace(" ", "")))
        return latex(parsed)
    except Exception as e:
        return f"\\text{{{step_str}}}"
    
# ---------------- CHECK BUTTON ----------------
st.divider()

if st.button("✅ Check Steps"):
    if st.session_state.original_function.strip() == "":
        st.error("Please enter the original function.")
    elif st.session_state.student_steps.strip() == "":
        st.error("Please enter your working steps.")
    else:
        # Convert UI input → safe SymPy string
        latex_function = ui_to_latex(st.session_state.original_function.replace(" ", ""))
        latex_steps = ui_to_latex(st.session_state.student_steps.replace(" ", ""))

        # Convert to SymPy expressions
        x = symbols('x')

        try:
            original_func_expr = sympify(latex_function)
        except Exception as e:
            st.error(f"Error parsing original function: {e}")
            original_func_expr = None

        student_steps_list = []
        for i, line in enumerate(latex_steps.splitlines()):
            line = line.strip()
            if line == "":
                continue
            try:
                student_steps_list.append(sympify(line))
            except Exception as e:
                st.error(f"Error parsing step {i+1}: '{line}': {e}")

        # Only check if parsing succeeded
        if original_func_expr is not None and student_steps_list:
            results = check_derivative_steps(student_steps_list, original_func_expr)

            # Preview (pretty math)
            st.markdown("### 👀 Math Preview")
            # Convert each line to SymPy and render
            for line in latex_steps.splitlines():
                if line.strip() == "":
                    continue
                try:
                    st.latex(latex(sympify(line.strip())))
                except:
                    st.write(line.strip())  # fallback if parsing fails

            # Feedback
            st.markdown("## 📋Feedback")
            for msg in results:
                if "Correction:" in msg:
                    text, correction = msg.split("Correction:")
                    st.write(text.strip())
                    st.latex(latex(sympify(correction.strip())))
                else:
                    st.write(msg)

            # Save to history
            st.session_state.history.append({
                "function": st.session_state.original_function,
                "steps": st.session_state.student_steps
            })

# ---------------- HISTORY SIDEBAR ----------------
st.sidebar.markdown("### 🕘 History")

if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[-10:]), 1):
        st.sidebar.markdown(f"**{i}. Function:**")
        st.sidebar.latex(render_step_to_latex(item["function"]))
        st.sidebar.markdown("**Steps:**")
        for line in item["steps"].splitlines():
            if line.strip():
                st.sidebar.latex(render_step_to_latex(line.strip()))
        st.sidebar.divider()
else:
    st.sidebar.write("No history yet.")
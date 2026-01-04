import streamlit as st
import base64

def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def apply_pink_theme():
    st.markdown("""
        <style>   
        /* Background */
        .main {
            background-color: #fff0f5; /* soft blush pink */
        }

        /* Titles */
        .title-box {
        background-color: #ffe4ec;
        border: 3px solid #c2185b;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        font-family: 'quicksand';
        font-size: 1.8rem;
        font-weight: bold;
        color: #c2185b;
        margin-bottom: 20px;
        box-shadow: 2px 2px 8px rgba(194, 24, 91, 0.2);
        }

        /* Sidebar */
        .css-1d391kg, .css-1lcbmhc {
            background-color: #ffe4ec !important;
            border-left: 4px solid #c2185b;
        }

        /* Buttons */
        .stButton button {
            background-color: #ffc1e3; /* soft pink */
            color: #4a004a;
            border: 2px solid #c2185b; /* darker pink border */
            border-radius: 10px;
            font-weight: bold;
            min-width: 40px;
            padding: 8px 16px;
            margin: 3px;
            transition: 0.3s;
        }
        .stButton button:hover {
            background-color: #77C0ff;
            transform: scale(1.05);
        }

        /* Input boxes */
        .stTextInput input, .stTextArea textarea {
            background-color: #fff5fa;
            border: 2px solid #c2185b;
            border-radius: 8px;
            color: #333;
        }

        /* Divider */
        hr {
            border: 1px solid #c2185b;
        }

        /* Keyboard buttons */
        .math-btn button {
            background-color: #ffd6eb;
            color: #4a004a;
            border: 2px solid #c2185b;
            border-radius: 6px;
            font-weight: 900px;
            margin: 2px;
        }
        .math-btn button:hover {
            background-color: #f8a8d6;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

def render_math_keyboard():
    keyboard = [
        ["7", "8", "9", "+", "−", "a²", "aᵇ", "x", "t"],
        ["4", "5", "6", "×", "÷", "(", ")", "y"],
        ["1", "2", "3", ".", "π", "sin(", "cos(", "tan("],
        ["0", "d/dx", "dy/dx", "sqrt(", "=", "sec(", "ln(", "exp("],
        ["⌫", "Clear"]
    ]

    for row in keyboard:
        cols = st.columns(len(row))
        for i, key in enumerate(row):
            if key:
                cols[i].button(key, key=f"{key}_{i}", use_container_width=True)

import streamlit as st
import base64
from streamlit_js_eval import streamlit_js_eval

# ---------- Background ----------
def set_background():
    theme = st.get_option("theme.base")  # returns "dark" or "light"
    image_file = "images/background1.jpg" if theme == "dark" else "images/background2.jpg"

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


# ---------- Theme ----------
def apply_neomath_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #0f0e1a;  /* deep indigo */
        }
                
        /* Title box */
        .title-box {
            background-color: #1e1b3a;
            border: 2px solid #00c8ff;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            font-family: 'Orbitron';
            font-size: 1.8rem;
            font-weight: bold;
            color: #ffffff;
            box-shadow: 0 0 12px rgba(0, 200, 255, 0.3);
            margin-bottom: 20px;
        }
        
        /* Banner styling */
        .banner {
            width: 100%;
            background: linear-gradient(90deg, #1e1b3a, #00c8ff);  /* glowing strip */
            padding: 20px;
            text-align: center;
            border-radius: 20px 20px 20px 20px;
            box-shadow: 0 4px 12px rgba(0, 200, 255, 0.3);
            position: relative;
            z-index: 1;
        }

        .banner-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.2rem;
            font-weight: bold;
            color: #ffffff;
            text-shadow: 0 0 8px rgba(0, 200, 255, 0.8);
            margin: 0;
        }

        /* Input boxes */
        .stTextInput input, .stTextArea textarea {
            background-color: #2a2540;
            border: 1px solid #00c8ff;
            border-radius: 8px;
            color: #ffffff;
            box-shadow: 0 0 6px rgba(0, 200, 255, 0.2);
        }

        /* Divider */
        hr {
            border: 1px solid #00c8ff;
        }
        
        /*Cursor colour */
            input:focus, textarea:focus {
            caret-color: #ff4da6;         /* cursor color */
            border-color: #ff4da6;
            box-shadow: 0 0 0 2px rgba(255, 77, 166, 0.3);
        }

        /* Wide grid */
        .keyboard-grid-wide {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
            gap: 10px;
            padding: 16px;
            background-color: #1e1b3a;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0, 200, 255, 0.1);
        }

        /* Compact grid */
        .keyboard-grid-compact {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));
            gap: 6px;
            padding: 12px;
            background-color: #1e1b3a;
            border-radius: 12px;
            box-shadow: 0 3px 8px rgba(0, 200, 255, 0.1);
        }

        /* Button styling */
        .math-btn button {
            background-color: #3f2b63;
            color: #ffffff;
            border: 2px solid #00c8ff;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1rem;
            padding: 10px;
            width: 100%;
            transition: all 0.2s ease-in-out;
        }
                
        /* Radio button container */
        .stRadio > div {
            background-color: transparent;
            color: #00c8ff;
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            font-size: 1rem;
            text-shadow: 0 0 4px rgba(0, 200, 255, 0.5);
        }

        /* Radio options */
        .stRadio div[role="radiogroup"] > label {
            background-color: #1e1b3a;
            border: 2px solid #00c8ff;
            border-radius: 8px;
            padding: 6px 12px;
            margin: 4px;
            color: #ffffff;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 0 6px rgba(0, 200, 255, 0.2);
        }   

        /* Hover effect */
            .stRadio div[role="radiogroup"] > label:hover {
            background-color: #00c8ff;
            color: #1e1b3a;
            transform: scale(1.03);
        }

        /* Selected option */
        .stRadio div[role="radiogroup"] > label[data-selected="true"] {
            background-color: #00c8ff;
            color: #1e1b3a;
            box-shadow: 0 0 10px rgba(0, 200, 255, 0.4);
        }

        .math-btn button:hover {
            background-color: #00c8ff;
            color: #1e1b3a;
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)

# ---------- Keyboard ----------
def render_math_keyboard():
    keyboard = [
        ["7", "8", "9", "+", "−", "aᵇ", "x", "t"],
        ["4", "5", "6", "×", "÷", "(", ")", "y"],
        ["1", "2", "3", ".", "π", "sin(", "cos(", "tan("],
        ["0", "d/dx", "dy/dx", "sqrt(", "=", "sec(", "ln(", "exp("],
        ["🔙", "🧹 Clear"]
    ]

    # Detect screen width
    width = streamlit_js_eval(js_expressions="screen.width", key="get_width")
    if width is None:
        width = 1200

    grid_class = "keyboard-grid-compact" if width < 800 else "keyboard-grid-wide"

    st.markdown(f'<div class="{grid_class}">', unsafe_allow_html=True)

    # Render each row of keys
    for row in keyboard:
        cols = st.columns(len(row))
        for i, key in enumerate(row):
            if cols[i].button(key, key=f"{key}_{i}"):
                st.session_state["last_key"] = key  # store pressed key

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- App ----------
def main():
    apply_neomath_theme()
    # Banner with title
    st.markdown(
        '<div class="banner"><h1 class="banner-title">DerivaCheck</h1></div>',
        unsafe_allow_html=True
    )
    
    render_math_keyboard()

if __name__ == "__main__":
    main()
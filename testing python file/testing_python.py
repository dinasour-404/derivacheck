import streamlit as st
import sympy as sp

x = sp.symbols('x')
f = x**2 + 3*x + 5

# Derivative
f_prime = sp.diff(f, x)

st.write("Plain output:", f_prime)       # x + 3 (just text)
st.latex(f_prime)    
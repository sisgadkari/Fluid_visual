import streamlit as st

st.set_page_config(page_title="Closed-tube Manometer Calculator", layout="wide")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>Closed-tube Differential Manometer</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='font-size:17px;'>
This tool calculates the pressure difference between two points in a system using a closed-tube manometer.
</div>
""", unsafe_allow_html=True)
st.markdown("""
---
**How to use:**  
- Enter the densities for manometer and system fluids.
- Use the sliders to set the heights of system and manometer fluids above the datum.
- The calculator shows the pressure difference between two points in the system.
---
""")

# --- First Row: Image | Formula | Inputs ---
img_col, form_col, input_col = st.columns([1, 1, 2])
with img_col:
    st.image("closedm.png", width=420, caption="Schematic of closed-tube manometer")
with form_col:
    st.markdown("""
    <br>
    <b>Formula:</b>
    <div style='font-size:22px; margin-top: 8px;'><b>
    P₁ + ρ<sub>o</sub>·g·a = P₂ + ρ<sub>o</sub>·g·(a − h) + ρ<sub>m</sub>·g·h
    </b></div>
    <br>
    <div style='font-size:16px;'>
    Rearranged for pressure difference:<br>
    <div style='font-size:20px;'><b>
    P₁ − P₂ = (ρ<sub>m</sub> − ρ<sub>o</sub>)·g·h
    </b></div>
    where:<br>
    &nbsp; ρ<sub>m</sub> = density of manometer fluid<br>
    &nbsp; ρ<sub>o</sub> = density of system fluid<br>
    &nbsp; h = height of manometer fluid above datum (right limb, m)<br>
    &nbsp; a = height of system fluid above datum (left limb, m)<br>
    &nbsp; g = gravity (default 9.81 m/s²)
    </div>
    """, unsafe_allow_html=True)
with input_col:
    st.header("Inputs")
    rho_m = st.number_input("Density of manometer fluid, ρₘ (kg/m³)", value=13600, step=100)
    rho_f = st.number_input("Density of system fluid, ρ_o (kg/m³)", value=1000, step=10)
    g = st.number_input("Gravity, g (m/s²)", value=9.81, format="%.2f")
    a = st.slider("Height of system fluid above datum, a (m)", min_value=0.00, max_value=0.30, value=0.10, step=0.01, format="%.2f")
    h = st.slider("Height of manometer fluid above datum, h (m)", min_value=0.00, max_value=0.20, value=0.08, step=0.01, format="%.2f")

st.markdown("---")

# --- Second Row: Result Display ---
st.header("Pressure Difference Result")
delta_P = (rho_m - rho_f) * g * h  # in Pascals
delta_P_kPa = delta_P / 1000

st.markdown(
    f"<div style='font-size:28px; font-weight:bold; color:#2e3b4e;'>"
    f"Pressure difference (P₁ - P₂):<br>{delta_P:,.1f} Pa &nbsp;({delta_P_kPa:,.3f} kPa)"
    f"</div>",
    unsafe_allow_html=True
)

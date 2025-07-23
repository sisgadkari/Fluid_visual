import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="U-tube Open Manometer Calculator", layout="wide")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>U-tube Open Manometer</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='font-size:17px;'>
This tool calculates the pressure difference between a point in a system (A) and atmospheric pressure using a U-tube open manometer.
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# --- First Row: Image | Formula | Inputs ---
img_col, form_col, input_col = st.columns([1, 1, 2])
with img_col:
    st.image("openm.png", width=420, caption="Schematic of U-tube open manometer")
with form_col:
    st.markdown("""
    <br>
    <b>Formula:</b>
    <div style='font-size:22px; margin-top: 8px;'><b>
    P<sub>1</sub> - P<sub>A</sub> = ρ<sub>m</sub>·g·h − ρ<sub>o</sub>·g·b
    </b></div>
    <br>
    <div style='font-size:16px;'>
    where:<br>
    &nbsp; ρ<sub>m</sub> = density of manometer fluid<br>
    &nbsp; h = height of manometer fluid above datum (m)<br>
    &nbsp; ρ<sub>o</sub> = density of fluid in system<br>
    &nbsp; b = height of system fluid above datum (m)<br>
    &nbsp; g = gravity (default 9.81 m/s²)
    </div>
    """, unsafe_allow_html=True)
with input_col:
    st.header("Inputs")
    preset = st.selectbox(
        "Choose a preset example (or Custom):",
        (
            "Mercury–Water (classic)",
            "Mercury–Air (gas pressure)",
            "Water–Air (sensitive)",
            "Oil–Water (lighter manometer)",
            "Water–Glycerin",
            "Custom"
        )
    )

    # Preset values
    if preset == "Mercury–Water (classic)":
        rho_m, rho_f = 13600, 1000
        st.info("Preset: Mercury (13,600 kg/m³) as manometer fluid, Water (1,000 kg/m³) as system fluid.")
    elif preset == "Mercury–Air (gas pressure)":
        rho_m, rho_f = 13600, 1.2
        st.info("Preset: Mercury (13,600 kg/m³) as manometer fluid, Air (1.2 kg/m³) as system fluid.")
    elif preset == "Water–Air (sensitive)":
        rho_m, rho_f = 1000, 1.2
        st.info("Preset: Water (1,000 kg/m³) as manometer fluid, Air (1.2 kg/m³) as system fluid.")
    elif preset == "Oil–Water (lighter manometer)":
        rho_m, rho_f = 850, 1000
        st.info("Preset: Oil (850 kg/m³) as manometer fluid, Water (1,000 kg/m³) as system fluid.")
    elif preset == "Water–Glycerin":
        rho_m, rho_f = 1260, 1000
        st.info("Preset: Glycerin (1,260 kg/m³) as manometer fluid, Water (1,000 kg/m³) as system fluid.")
    else:  # Custom
        rho_m = st.number_input("Density of manometer fluid, ρₘ (kg/m³)", value=13600, step=100)
        rho_f = st.number_input("Density of system fluid, ρ_o (kg/m³)", value=1000, step=10)

    h = st.slider("Height of manometer fluid above datum, h (m)", min_value=0.00, max_value=0.30, value=0.10, step=0.01, format="%.2f")
    b = st.slider("Height of system fluid above datum, b (m)", min_value=0.00, max_value=0.10, value=0.02, step=0.01, format="%.2f")
    g = st.number_input("Gravity, g (m/s²)", value=9.81, format="%.2f")

st.markdown("---")

# --- Second Row: Result Display ---
delta_P = rho_m * g * h - rho_f * g * b  # in Pascals (N/m²)
delta_P_kPa = delta_P / 1000  # in kPa

st.markdown(
    f"<div style='font-size:28px; font-weight:bold; color:#2e3b4e;'>"
    f"Pressure difference (P<sub>1</sub> - P<sub>A</sub>): {delta_P:,.1f} Pa &nbsp;({delta_P_kPa:,.3f} kPa)"
    f"</div>",
    unsafe_allow_html=True
)


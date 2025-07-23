import streamlit as st
import numpy as np

st.set_page_config(layout="wide")
st.markdown(
    "<h1 style='text-align: center;'>Surface Tension: Capillarity Effect</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h3 style='text-align: center; font-weight: normal;'>Capillarity effect refers to the rise or fall of a liquid in a small-diameter tube. It is caused by surface tension.</h3>",
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([2,3])

with col1:
    st.image("example11.png", width=500)
    st.image("example1.png", width=600)

with col2:
    st.title("Capillary Rise Calculator")

    # --- Preset Fluid Options ---
    fluid_choice = st.selectbox(
        "Choose a preset fluid:",
        (
            "Water (25°C)",
            "Mercury (25°C)",
            "Ethanol (25°C)",
            "Custom"
        )
    )

    # Preset values for [surface tension (N/m), density (kg/m³)]
    FLUIDS = {
        "Water (25°C)":    [0.0728, 997],
        "Mercury (25°C)":  [0.485, 13534],
        "Ethanol (25°C)":  [0.0223, 789],
    }

    if fluid_choice != "Custom":
        sigma, rho = FLUIDS[fluid_choice]
        st.markdown(
            f"<div style='font-size:18px;'>Surface tension (N/m): <b>{sigma}</b></div>", unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='font-size:18px;'>Liquid density (kg/m³): <b>{rho}</b></div>", unsafe_allow_html=True
        )
    else:
        st.markdown("<span style='font-size:20px;'>Surface tension (N/m)</span>", unsafe_allow_html=True)
        sigma = st.slider("", 0.01, 0.10, 0.0728)
        st.markdown("<span style='font-size:20px;'>Liquid density (kg/m³)</span>", unsafe_allow_html=True)
        rho = st.number_input("", value=1000)

    st.markdown("<span style='font-size:20px;'>Contact angle (degrees)</span>", unsafe_allow_html=True)
    theta_deg = st.slider("", 0, 180, 0)
    theta = np.deg2rad(theta_deg)

    st.markdown("<span style='font-size:20px;'>Capillary diameter (mm)</span>", unsafe_allow_html=True)
    d = st.slider("", 0.1, 5.0, 1.0) / 1000  # convert mm to m

    st.markdown("<span style='font-size:20px;'>Gravity (m/s²)</span>", unsafe_allow_html=True)
    g = st.number_input("", value=9.81)

    # Calculation
    if d > 0:
        h = (4 * sigma * np.cos(theta)) / (rho * g * d)
    else:
        h = 0

    st.title(f"Height of capillary rise (h): {h:.4f} m")

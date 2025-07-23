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
# Create two columns with equal width
col1, col2 = st.columns([2,3])

with col1:
    st.image("example11.png", width=500)
    st.image("example1.png", width=600)

with col2:
    st.title("Capillary Rise Calculator")

    # Sliders and inputs
    sigma = st.slider("Surface tension (N/m)", 0.01, 0.10, 0.0728)
    theta_deg = st.slider("Contact angle (degrees)", 0, 180, 0)
    theta = np.deg2rad(theta_deg)
    rho = st.number_input("Liquid density (kg/m³)", value=1000)
    d = st.slider("Capillary diameter (mm)", 0.1, 5.0, 1.0) / 1000  # convert mm to m
    g = st.number_input("Gravity (m/s²)", value=9.81)

    # Calculation
    if d > 0:
        h = (4 * sigma * np.cos(theta)) / (rho * g * d)
    else:
        h = 0

    st.title(f"Height of capillary rise (h): {h:.4f} m")

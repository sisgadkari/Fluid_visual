import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.markdown(
    "<h1 style='text-align: center;'>Hydrostatic Force on a Straight Side Wall</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<h4 style='text-align: center; font-weight: normal;'>Visualize the distribution of hydrostatic force along a vertical wall, and see the total force in kilonewtons (kN).</h4>",
    unsafe_allow_html=True
)

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

colA, colB, colC = st.columns([1, 2, 1])
with colB:
    st.image("example2.png",  width=800)


col1, col2 = st.columns([2, 3])

with col1:
    st.header("Input Parameters")
    D = st.slider("Depth of fluid (D) [m]", 0.1, 10.0, 2.0)
    w = st.slider("Width of wall (w) [m]", 0.1, 10.0, 3.0)
    rho = st.number_input("Fluid density (ρ) [kg/m³]", value=1000)
    g = st.number_input("Gravity (g) [m/s²]", value=9.81)

    F = 0.5 * rho * g * w * D**2  # in N
    F_kN = F / 1000  # Convert to kN

    st.markdown(
    f"<div style='font-size:32px; font-weight:bold; color:black; text-align:center;'>Total Hydrostatic Force (F): {F_kN:,.2f} kN</div>",
    unsafe_allow_html=True
)
    st.caption("F = 0.5 × ρ × g × w × D² (in kN)")

with col2:
    st.header("Force Distribution Along Wall")
    depths = np.linspace(0, D, 100)
    force_per_depth = (rho * g * depths * w) / 1000  # in kN per meter

    fig_force = go.Figure()
    fig_force.add_trace(go.Scatter(
        x=force_per_depth,
        y=depths,
        mode='lines',
        line=dict(color='firebrick', width=3),
        name='Force per depth (kN/m)'
    ))

    fig_force.update_yaxes(autorange="reversed")
    fig_force.update_layout(
        title="Force per Meter of Wall vs. Depth",
        xaxis_title="Force per meter (kN/m)",
        yaxis_title="Depth (m)",
        plot_bgcolor='white',
        hovermode="y"
    )

    st.plotly_chart(fig_force, use_container_width=True)

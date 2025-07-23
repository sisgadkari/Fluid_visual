import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.markdown(
    "<h1 style='text-align: center;'>Hydrostatic Force on an Inclined Wall</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<h4 style='text-align: center; font-weight: normal;'>Calculate total hydrostatic force and see an interactive diagram of the wall and water.</h4>",
    unsafe_allow_html=True
)

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 3])

with col1:
    st.header("Input Parameters")

    # Wall length
    L_slider, L_input = st.columns([2, 1])
    with L_slider:
        L = st.slider("Wall length (L) [m]", 0.1, 10.0, 3.0, step=0.01)
    with L_input:
        L = st.number_input(" ", min_value=0.1, max_value=10.0, value=L, step=0.01, key="L_input")

    # Wall width
    w_slider, w_input = st.columns([2, 1])
    with w_slider:
        w = st.slider("Wall width (w) [m]", 0.1, 10.0, 2.0, step=0.01)
    with w_input:
        w = st.number_input("  ", min_value=0.1, max_value=10.0, value=w, step=0.01, key="w_input")

    # Inclination angle
    th_slider, th_input = st.columns([2, 1])
    with th_slider:
        theta_deg = st.slider("Inclination angle θ (degrees, from horizontal)", 0, 90, 30)
    with th_input:
        theta_deg = st.number_input("   ", min_value=0, max_value=90, value=theta_deg, step=1, key="th_input")
    theta_rad = np.deg2rad(theta_deg)
    rho = st.number_input("Fluid density (ρ) [kg/m³]", value=1000)
    g = st.number_input("Gravity (g) [m/s²]", value=9.81)

    # Total hydrostatic force calculation
    FN = 0.5 * rho * g * w * L**2 * np.sin(theta_rad)  # in N
    FN_kN = FN / 1000  # in kN

    st.markdown(
        f"<div style='font-size:32px; font-weight:bold; color:black; text-align:center;'>Total Hydrostatic Force (F<sub>N</sub>): {FN_kN:,.2f} kN</div>",
        unsafe_allow_html=True
    )
    st.caption("F<sub>N</sub> = 0.5 × ρ × g × w × L² × sin(θ)", unsafe_allow_html=True)

with col2:
    st.header("Inclined Wall Geometry Visualization")

    # Geometry: bottom left at (0, 0)
    x0, y0 = 0, 0
    x1, y1 = L * np.cos(theta_rad), L * np.sin(theta_rad)

    fig = go.Figure()

    # Draw wall
    fig.add_trace(go.Scatter(
        x=[x0, x1], y=[y0, y1],
        mode='lines',
        line=dict(color="blue", width=8),
        name='Inclined Wall'
    ))

    # Draw rectangle for water above the wall
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=x1,
        y1=max(1.2*y1, 1.2*L),  # Make sure the rectangle covers above the wall
        line=dict(color="lightblue", width=0),
        fillcolor="lightblue",
        opacity=0.6,
        layer="below"
    )

    # Calculate midpoint of the wall
    mid_x = (x0 + x1) / 2
    mid_y = (y0 + y1) / 2

    # Offset perpendicular to wall for theta annotation
    dx = x1 - x0
    dy = y1 - y0
    length = np.sqrt(dx**2 + dy**2)
    offset = 0.15 * L

    perp_x = -dy / length
    perp_y = dx / length

    label_x = mid_x + offset * perp_x
    label_y = mid_y + offset * perp_y

    fig.add_annotation(
        x=label_x,
        y=label_y,
        text=f"θ = {theta_deg}°",
        showarrow=False,
        font=dict(size=16, color="black")
    )

    fig.update_xaxes(range=[-0.1*L, 1.3*L], title="x (m)", scaleanchor="y", scaleratio=1, visible=False)
    fig.update_yaxes(range=[-0.1*L, max(1.3*y1, 1.3*L)], title="y (m)", visible=False)

    fig.update_layout(
        width=350,
        height=350,
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False,
        title=""
    )

    # Show plot and image side by side inside this column using nested columns
    plot_col, img_col = st.columns([3, 2])
    with plot_col:
        st.plotly_chart(fig, use_container_width=True)
    with img_col:
        st.image("example3.png", width=280, caption="Reference: Inclined wall setup")

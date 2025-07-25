import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# --- Page Configuration ---
st.set_page_config(layout="wide")

# --- App Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>💧 Interactive Capillary Rise Simulator</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>Explore how surface tension causes liquids to rise or fall in small tubes. Adjust the parameters on the left and watch the liquid level animate to its new height.</p>",
    unsafe_allow_html=True
)
st.markdown("---")

# --- Initialize Session State ---
# This will hold the height from the previous run to enable animation.
if 'previous_h' not in st.session_state:
    st.session_state.previous_h = None


# --- Layout ---
col1, col2 = st.columns([1, 1])

# --- Column 1: Input Controls ---
with col1:
    st.header("🔬 Parameters")

    # --- Preset Fluid Options ---
    fluid_choice = st.selectbox(
        "Choose a preset fluid:",
        ("Water (20°C)", "Mercury (20°C)", "Ethanol (20°C)", "Custom"),
        key="fluid_selector"
    )

    # Preset values for [surface tension (N/m), density (kg/m³), color]
    FLUID_PROPERTIES = {
        "Water (20°C)":   {'sigma': 0.0728, 'rho': 998, 'color': 'rgba(100, 170, 255, 0.7)'},
        "Mercury (20°C)": {'sigma': 0.485, 'rho': 13534, 'color': 'rgba(180, 180, 180, 0.7)'},
        "Ethanol (20°C)": {'sigma': 0.0223, 'rho': 789, 'color': 'rgba(200, 150, 255, 0.7)'},
    }
    
    if fluid_choice == "Custom":
        st.subheader("Custom Fluid Properties")
        sigma = st.slider("Surface Tension (σ) [N/m]", 0.01, 0.5, 0.0728, 0.001, format="%.4f")
        rho = st.number_input("Liquid Density (ρ) [kg/m³]", value=998)
        liquid_color = 'rgba(100, 170, 255, 0.7)'
    else:
        properties = FLUID_PROPERTIES[fluid_choice]
        sigma = properties['sigma']
        rho = properties['rho']
        liquid_color = properties['color']
        st.info(f"Loaded properties for **{fluid_choice}**.")
        st.markdown(f"**Surface Tension (σ):** `{sigma}` N/m")
        st.markdown(f"**Liquid Density (ρ):** `{rho}` kg/m³")

    st.subheader("Tube and Angle Properties")
    # Sliders now start at a neutral state (h=0) and are always enabled.
    theta_deg = st.slider("Contact Angle (θ) [degrees]", 0, 180, 90)
    d_mm = st.slider("Capillary Diameter (d) [mm]", 0.1, 10.0, 1.0, 0.1)
    
    d_m = d_mm / 1000
    g = 9.81
    theta_rad = np.deg2rad(theta_deg)

    # --- Calculation ---
    if d_m > 0 and rho > 0:
        h = (4 * sigma * np.cos(theta_rad)) / (rho * g * d_m)
    else:
        h = 0
    
    st.markdown("---")
    st.header("📈 Results")
    st.metric(label="Calculated Capillary Rise (h)", value=f"{h * 1000:.2f} mm")
    st.latex(r'''\Large h = \frac{4 \sigma \cos(\theta)}{\rho g d}''')


# --- Column 2: Visualization ---
with col2:
    st.header("🖼️ Visualization")
    plot_placeholder = st.empty()

    # This function creates the plot for a given instantaneous height
    def generate_plot(instant_h=0):
        tube_radius_vis = d_mm / 2
        h_vis_target = h * 1000
        max_y_val = max(abs(h_vis_target), 5)
        plot_y_range = [-max_y_val * 0.5, max_y_val * 1.5]
        plot_height = plot_y_range[1]
        beaker_radius = 15
        beaker_bottom = min(-5, h_vis_target - 2)

        fig = go.Figure()
        line_color = liquid_color.replace('0.7', '1')

        # 1. Draw beaker and liquid
        fig.add_shape(type="line", x0=-beaker_radius, y0=beaker_bottom, x1=-beaker_radius, y1=0, line=dict(color="grey", width=2))
        fig.add_shape(type="line", x0=beaker_radius, y0=beaker_bottom, x1=beaker_radius, y1=0, line=dict(color="grey", width=2))
        fig.add_shape(type="line", x0=-beaker_radius, y0=beaker_bottom, x1=beaker_radius, y1=beaker_bottom, line=dict(color="grey", width=2))
        
        # Liquid around the tube
        fig.add_trace(go.Scatter(x=[-beaker_radius, -tube_radius_vis, -tube_radius_vis, -beaker_radius], y=[beaker_bottom, beaker_bottom, 0, 0], fill='toself', fillcolor=liquid_color, mode='none'))
        fig.add_trace(go.Scatter(x=[tube_radius_vis, beaker_radius, beaker_radius, tube_radius_vis], y=[beaker_bottom, beaker_bottom, 0, 0], fill='toself', fillcolor=liquid_color, mode='none'))

        # 2. Draw tube and meniscus
        fig.add_shape(type="line", x0=-tube_radius_vis, y0=beaker_bottom, x1=-tube_radius_vis, y1=plot_height, line=dict(color="darkgrey", width=3))
        fig.add_shape(type="line", x0=tube_radius_vis, y0=beaker_bottom, x1=tube_radius_vis, y1=plot_height, line=dict(color="darkgrey", width=3))

        meniscus_x = np.linspace(-tube_radius_vis, tube_radius_vis, 100)
        curvature_direction = -1 if theta_deg < 90 else 1
        meniscus_y = instant_h - curvature_direction * (meniscus_x**2 / (tube_radius_vis * 2)) * np.tan(np.deg2rad(90 - theta_deg if theta_deg < 90 else theta_deg - 90)) if tube_radius_vis > 0 else instant_h
        if tube_radius_vis > 0:
            meniscus_y -= (meniscus_y[-1] - instant_h)
        
        x_fill = np.concatenate([meniscus_x, [tube_radius_vis, -tube_radius_vis]])
        y_fill = np.concatenate([meniscus_y, [beaker_bottom, beaker_bottom]])
        fig.add_trace(go.Scatter(x=x_fill, y=y_fill, fill='toself', fillcolor=liquid_color, mode='none', hoverinfo='none'))
        fig.add_trace(go.Scatter(x=meniscus_x, y=meniscus_y, mode='lines', line=dict(color=line_color), hoverinfo='none'))

        # Position the annotation dynamically based on the tube radius
        annotation_base_x = tube_radius_vis + 1.5
        fig.add_annotation(x=annotation_base_x, y=instant_h / 2, ax=annotation_base_x, ay=0, text="", showarrow=True, arrowhead=3, arrowwidth=2, arrowcolor="black")
        fig.add_annotation(x=annotation_base_x + 0.5, y=instant_h / 2, text=f"h = {instant_h:.2f} mm", showarrow=False, font=dict(size=28), xanchor='left')

        fig.update_layout(
            xaxis=dict(range=[-25, 25], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[beaker_bottom - 1, plot_y_range[1]], zeroline=False, title_text="Height (mm)"),
            showlegend=False, height=600, plot_bgcolor='white'
        )
        return fig

    # --- Main Visualization and Animation Logic ---
    h_vis_target = h * 1000
    start_h = st.session_state.previous_h
    end_h = h_vis_target
    
    # On the very first run, start_h is None. Set it to the target to prevent animation.
    if start_h is None:
        start_h = end_h

    # Animate if the height has changed.
    if not np.isclose(start_h, end_h):
        animation_steps = 15
        for i in range(animation_steps + 1):
            intermediate_h = start_h + (end_h - start_h) * (i / animation_steps)
            fig = generate_plot(intermediate_h)
            plot_placeholder.plotly_chart(fig, use_container_width=True)
            time.sleep(0.03)
    # If height hasn't changed, just draw the static plot.
    else:
        fig = generate_plot(end_h)
        plot_placeholder.plotly_chart(fig, use_container_width=True)
    
    # Always update the previous height for the next run
    st.session_state.previous_h = end_h

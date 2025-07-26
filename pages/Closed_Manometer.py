import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# --- Page Configuration ---
st.set_page_config(page_title="U-Tube Manometer", layout="wide")

# --- Initialize Session State for Animation ---
if 'previous_h_mano' not in st.session_state:
    st.session_state.previous_h_mano = None

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>Interactive U-Tube Manometer</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
This tool demonstrates how a U-tube manometer measures the pressure difference in a pipe.
Select a real-world scenario or adjust the parameters manually to see how the manometer fluid levels respond.
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# --- Layout ---
col1, col2 = st.columns([2, 3])

# --- Column 1: Inputs and Results ---
with col1:
    st.header("🔬 Parameters")

    # --- Interactive Scenarios ---
    SCENARIOS = {
        "Custom...": {
            "rho_f": 1.2, "rho_m": 13600.0, 
            "desc": "Manually enter all values below."
        },
        "Air Duct vs. Water Manometer": {
            "rho_f": 1.2, "rho_m": 1000.0,
            "desc": "A common setup for measuring small pressure changes in ventilation systems."
        },
        "Water Pipe vs. Mercury Manometer": {
            "rho_f": 1000.0, "rho_m": 13600.0,
            "desc": "Used for measuring larger pressure differences in water pipes, like across a pump or filter."
        },
        "Natural Gas vs. Oil Manometer": {
            "rho_f": 0.8, "rho_m": 820.0,
            "desc": "A sensitive setup for measuring low-pressure natural gas systems."
        }
    }

    scenario_choice = st.selectbox(
        "Interactive 'What-If' Scenarios",
        options=list(SCENARIOS.keys())
    )
    
    selected_scenario = SCENARIOS[scenario_choice]
    st.info(selected_scenario["desc"])
    
    st.subheader("Fluid Properties")
    rho_f = st.number_input("Density of System Fluid (ρ_system) [kg/m³]", value=selected_scenario["rho_f"], step=0.1, help="Typically a gas like air (~1.2 kg/m³)")
    rho_m = st.number_input("Density of Manometer Fluid (ρ_mano) [kg/m³]", value=selected_scenario["rho_m"], step=100.0, help="Typically mercury (13600 kg/m³)")
    g = st.number_input("Gravity (g) [m/s²]", value=9.81, format="%.2f")

    st.subheader("Manometer Height Control")
    h_cm = st.slider("Height Difference (h) [cm]", min_value=-20.0, max_value=20.0, value=10.0, step=0.5, format="%.1f cm")
    h = h_cm / 100 # Convert cm to meters for calculation
    
    # Add flow visualization option
    show_flow = st.checkbox("Show Flow Direction", value=True)

    # --- Calculation ---
    delta_P = (rho_m - rho_f) * g * h
    delta_P_kPa = delta_P / 1000

    st.markdown("---")
    st.header("📈 Results")
    
    # Color-coded pressure indicator
    if delta_P_kPa > 0:
        delta_color = "normal"
        interpretation = "P₁ > P₂ (Higher pressure at left)"
    elif delta_P_kPa < 0:
        delta_color = "inverse" 
        interpretation = "P₁ < P₂ (Higher pressure at right)"
    else:
        delta_color = "off"
        interpretation = "P₁ = P₂ (Equal pressures)"
    
    st.metric(label="Pressure Difference (P₁ - P₂)", value=f"{delta_P_kPa:,.3f} kPa", delta=interpretation, delta_color=delta_color)
    
    st.markdown("<b>Full Formula (Pressure balance at lower interface):</b>", unsafe_allow_html=True)
    st.latex(r'''P_1 + \rho_{sys} g a = P_2 + \rho_{sys} g (a-h) + \rho_{mano} g h''')
    st.markdown("<b>Rearranged for Pressure Difference:</b>", unsafe_allow_html=True)
    st.latex(r'''P_1 - P_2 = ( \rho_{mano} - \rho_{sys} ) g h''')

# --- Column 2: Visualization ---
with col2:
    st.header("🖼️ Visualization")
    plot_placeholder = st.empty()

    # --- Pre-calculate static geometry for the plot ---
    pipe_y = 0.5
    pipe_radius = 0.05
    tube_inner_radius = 0.045
    tube_outer_radius = 0.055
    # Make U-tube connect directly to pipe bottom
    tube_top_y = pipe_y - pipe_radius  # U-tube top connects to pipe bottom
    bend_y_center = 0.1
    tube_bottom = bend_y_center - tube_outer_radius
    
    # Connecting tubes dimensions
    conn_tube_inner_radius = 0.015
    conn_tube_outer_radius = 0.020
    conn_left_x = -0.25
    conn_right_x = 0.25
    
    fixed_yaxis_range = [tube_bottom - 0.1, pipe_y + pipe_radius + 0.15]
    fixed_xaxis_range = [-0.5, 0.5]

    # Enhanced color scheme
    system_fluid_color = 'rgba(135, 206, 250, 0.7)'  # Light blue for gas/air
    manometer_fluid_color = 'rgba(255, 69, 0, 0.8)'  # Red-orange for manometer fluid
    glass_color = 'rgba(211, 211, 211, 0.4)'
    pipe_color = 'rgba(169, 169, 169, 0.8)'

    def get_bend_points(radius, y_center):
        theta = np.linspace(np.pi, 2 * np.pi, 50)
        return radius * np.cos(theta), radius * np.sin(theta) + y_center

    x_outer_bend, y_outer_bend = get_bend_points(tube_outer_radius, bend_y_center)
    x_inner_bend, y_inner_bend = get_bend_points(tube_inner_radius, bend_y_center)

    # --- Function to generate the plot for a specific height ---
    def generate_manometer_plot(h_inst, show_flow_arrows):
        level_center = bend_y_center + 0.1
        level_left = level_center - h_inst / 2
        level_right = level_center + h_inst / 2
        
        fig = go.Figure()

        # 1. Draw Pipe with better styling
        # Pipe body
        fig.add_shape(type="rect", 
                     x0=-0.5, y0=pipe_y-pipe_radius, 
                     x1=0.5, y1=pipe_y+pipe_radius, 
                     fillcolor=pipe_color, line_width=0)
        # Pipe walls (3D effect)
        fig.add_shape(type="line", 
                     x0=-0.5, y0=pipe_y+pipe_radius, 
                     x1=0.5, y1=pipe_y+pipe_radius, 
                     line=dict(color='black', width=2))
        fig.add_shape(type="line", 
                     x0=-0.5, y0=pipe_y-pipe_radius, 
                     x1=0.5, y1=pipe_y-pipe_radius, 
                     line=dict(color='black', width=2))
        
        # System fluid in pipe
        fig.add_shape(type="rect", 
                     x0=-0.5, y0=pipe_y-pipe_radius+0.005, 
                     x1=0.5, y1=pipe_y+pipe_radius-0.005, 
                     fillcolor=system_fluid_color, line_width=0)
        
        # 2. Draw Connecting Tubes (pressure taps) - Starting from inside the pipe
        # Left connecting tube
        conn_left_points_x = [
            conn_left_x - conn_tube_outer_radius, conn_left_x - conn_tube_outer_radius,
            -tube_outer_radius, -tube_outer_radius,
            -tube_inner_radius, -tube_inner_radius,
            conn_left_x - conn_tube_inner_radius, conn_left_x - conn_tube_inner_radius,
            conn_left_x + conn_tube_inner_radius, conn_left_x + conn_tube_inner_radius,
            conn_left_x + conn_tube_outer_radius, conn_left_x + conn_tube_outer_radius
        ]
        conn_left_points_y = [
            pipe_y - pipe_radius + 0.01, bend_y_center + tube_outer_radius,
            bend_y_center + tube_outer_radius, tube_top_y,
            tube_top_y, bend_y_center + tube_outer_radius,
            bend_y_center + tube_outer_radius, pipe_y - pipe_radius + 0.01,
            pipe_y - pipe_radius + 0.01, bend_y_center + tube_outer_radius + 0.01,
            bend_y_center + tube_outer_radius + 0.01, pipe_y - pipe_radius + 0.01
        ]
        fig.add_trace(go.Scatter(x=conn_left_points_x, y=conn_left_points_y, 
                                fill="toself", fillcolor=glass_color, 
                                mode='none', hoverinfo='none'))
        
        # Right connecting tube  
        conn_right_points_x = [
            conn_right_x - conn_tube_outer_radius, conn_right_x - conn_tube_outer_radius,
            conn_right_x - conn_tube_inner_radius, conn_right_x - conn_tube_inner_radius,
            tube_inner_radius, tube_inner_radius,
            tube_outer_radius, tube_outer_radius,
            conn_right_x + conn_tube_outer_radius, conn_right_x + conn_tube_outer_radius,
            conn_right_x + conn_tube_inner_radius, conn_right_x + conn_tube_inner_radius
        ]
        conn_right_points_y = [
            pipe_y - pipe_radius + 0.01, bend_y_center + tube_outer_radius + 0.01,
            bend_y_center + tube_outer_radius + 0.01, pipe_y - pipe_radius + 0.01,
            tube_top_y, bend_y_center + tube_outer_radius,
            bend_y_center + tube_outer_radius, tube_top_y,
            pipe_y - pipe_radius + 0.01, bend_y_center + tube_outer_radius,
            bend_y_center + tube_outer_radius, pipe_y - pipe_radius + 0.01
        ]
        fig.add_trace(go.Scatter(x=conn_right_points_x, y=conn_right_points_y, 
                                fill="toself", fillcolor=glass_color, 
                                mode='none', hoverinfo='none'))
        
        # 3. Draw U-tube glass - Now connected directly to pipe
        x_glass = np.concatenate([
            [-tube_outer_radius, -tube_outer_radius], x_outer_bend, [tube_outer_radius, tube_outer_radius],
            [tube_inner_radius, tube_inner_radius], x_inner_bend[::-1], [-tube_inner_radius, -tube_inner_radius]
        ])
        y_glass = np.concatenate([
            [tube_top_y, bend_y_center], y_outer_bend, [bend_y_center, tube_top_y],
            [tube_top_y, bend_y_center], y_inner_bend[::-1], [bend_y_center, tube_top_y]
        ])
        fig.add_trace(go.Scatter(x=x_glass, y=y_glass, fill="toself", 
                                fillcolor=glass_color, mode='none', hoverinfo='none'))

        # 4. Draw Fluids
        # Manometer fluid
        fig.add_shape(type="rect", 
                     x0=-tube_outer_radius, y0=bend_y_center, 
                     x1=-tube_inner_radius, y1=level_left, 
                     fillcolor=manometer_fluid_color, line_width=0)
        fig.add_shape(type="rect", 
                     x0=tube_inner_radius, y0=bend_y_center, 
                     x1=tube_outer_radius, y1=level_right, 
                     fillcolor=manometer_fluid_color, line_width=0)
        x_mano_bend = np.concatenate([x_outer_bend, x_inner_bend[::-1]])
        y_mano_bend = np.concatenate([y_outer_bend, y_inner_bend[::-1]])
        fig.add_trace(go.Scatter(x=x_mano_bend, y=y_mano_bend, fill="toself", 
                                fillcolor=manometer_fluid_color, mode='none', hoverinfo='none'))
        
        # System fluid in U-tube and connecting tubes
        # Left side
        fig.add_shape(type="rect", 
                     x0=-tube_outer_radius, y0=level_left, 
                     x1=-tube_inner_radius, y1=tube_top_y, 
                     fillcolor=system_fluid_color, line_width=0)
        fig.add_shape(type="rect", 
                     x0=conn_left_x-conn_tube_inner_radius, y0=pipe_y-pipe_radius, 
                     x1=conn_left_x+conn_tube_inner_radius, y1=bend_y_center+tube_outer_radius, 
                     fillcolor=system_fluid_color, line_width=0)
        # Right side
        fig.add_shape(type="rect", 
                     x0=tube_inner_radius, y0=level_right, 
                     x1=tube_outer_radius, y1=tube_top_y, 
                     fillcolor=system_fluid_color, line_width=0)
        fig.add_shape(type="rect", 
                     x0=conn_right_x-conn_tube_inner_radius, y0=pipe_y-pipe_radius, 
                     x1=conn_right_x+conn_tube_inner_radius, y1=bend_y_center+tube_outer_radius, 
                     fillcolor=system_fluid_color, line_width=0)

        # 5. Flow arrows (if enabled)
        if show_flow_arrows:
            # Main flow arrow
            fig.add_annotation(
                x=-0.3, y=pipe_y, ax=-0.1, ay=pipe_y,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=2,
                arrowwidth=2, arrowcolor="darkblue"
            )
            fig.add_annotation(
                x=-0.1, y=pipe_y, ax=0.1, ay=pipe_y,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=2,
                arrowwidth=2, arrowcolor="darkblue"
            )
            fig.add_annotation(
                x=0.1, y=pipe_y, ax=0.3, ay=pipe_y,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=2,
                arrowwidth=2, arrowcolor="darkblue"
            )
            fig.add_annotation(x=0, y=pipe_y+pipe_radius+0.05, text="Flow →", 
                             showarrow=False, font=dict(size=12, color="darkblue"))

        # 6. Annotations
        # Pressure labels with colored backgrounds
        fig.add_shape(type="rect", 
                     x0=conn_left_x-0.05, y0=pipe_y-0.03, 
                     x1=conn_left_x+0.05, y1=pipe_y+0.03, 
                     fillcolor="white", line=dict(color="black", width=1))
        fig.add_annotation(x=conn_left_x, y=pipe_y, text="<b>P₁</b>", 
                          showarrow=False, font=dict(size=18, color="red" if h_inst > 0 else "blue"))
        
        fig.add_shape(type="rect", 
                     x0=conn_right_x-0.05, y0=pipe_y-0.03, 
                     x1=conn_right_x+0.05, y1=pipe_y+0.03, 
                     fillcolor="white", line=dict(color="black", width=1))
        fig.add_annotation(x=conn_right_x, y=pipe_y, text="<b>P₂</b>", 
                          showarrow=False, font=dict(size=18, color="blue" if h_inst > 0 else "red"))
        
        # Height dimension
        if abs(h_inst) > 0.01:  # Only show if there's a significant difference
            fig.add_shape(type="line", 
                         x0=tube_outer_radius + 0.05, y0=level_left, 
                         x1=tube_outer_radius + 0.05, y1=level_right, 
                         line=dict(color="black", width=1))
            # Add arrows at ends
            fig.add_shape(type="line", 
                         x0=tube_outer_radius + 0.04, y0=level_left, 
                         x1=tube_outer_radius + 0.06, y1=level_left, 
                         line=dict(color="black", width=1))
            fig.add_shape(type="line", 
                         x0=tube_outer_radius + 0.04, y0=level_right, 
                         x1=tube_outer_radius + 0.06, y1=level_right, 
                         line=dict(color="black", width=1))
            fig.add_annotation(x=tube_outer_radius + 0.06, y=level_center, 
                             text=f"h = {h_inst*100:.1f} cm", 
                             showarrow=False, xanchor="left", font=dict(size=14))
        
        # Fluid labels
        fig.add_annotation(x=0, y=bend_y_center - 0.02, 
                          text=f"Manometer Fluid<br>(ρ = {rho_m:.0f} kg/m³)", 
                          showarrow=False, yanchor="top", font=dict(size=10))
        fig.add_annotation(x=0, y=pipe_y + pipe_radius + 0.08, 
                          text=f"System Fluid<br>(ρ = {rho_f:.1f} kg/m³)", 
                          showarrow=False, yanchor="bottom", font=dict(size=10))
        
        # Interface markers
        fig.add_shape(type="line", 
                     x0=-tube_inner_radius-0.01, y0=level_left, 
                     x1=-tube_inner_radius+0.01, y1=level_left, 
                     line=dict(color="black", width=2))
        fig.add_shape(type="line", 
                     x0=tube_inner_radius-0.01, y0=level_right, 
                     x1=tube_inner_radius+0.01, y1=level_right, 
                     line=dict(color="black", width=2))

        fig.update_layout(
            xaxis=dict(range=fixed_xaxis_range, visible=False),
            yaxis=dict(range=fixed_yaxis_range, visible=False),
            showlegend=False,
            height=600,
            plot_bgcolor='white',
            margin=dict(t=0, b=0, l=0, r=0)
        )
        return fig

    # --- Animation Logic ---
    start_h = st.session_state.previous_h_mano
    end_h = h

    if start_h is None:
        start_h = end_h

    if not np.isclose(start_h, end_h):
        animation_steps = 20
        for i in range(animation_steps + 1):
            intermediate_h = start_h + (end_h - start_h) * (i / animation_steps)
            fig = generate_manometer_plot(intermediate_h, show_flow)
            plot_placeholder.plotly_chart(fig, use_container_width=True)
            time.sleep(0.02)
    else:
        fig = generate_manometer_plot(end_h, show_flow)
        plot_placeholder.plotly_chart(fig, use_container_width=True)
    
    st.session_state.previous_h_mano = end_h
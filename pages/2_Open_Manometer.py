import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# --- Page Configuration ---
st.set_page_config(page_title="Open-Tube Manometer", layout="wide")

# --- Initialize Session State for Animation ---
if 'previous_heights_open' not in st.session_state:
    st.session_state.previous_heights_open = None

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>Interactive Open-Tube Manometer</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
This tool calculates the pressure at a point in a system (P₁) relative to atmospheric pressure using an open U-tube manometer.
Select a scenario or adjust the parameters manually to see how the fluid levels change.
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
            "rho_m": 13600.0, "rho_f": 1000.0,
            "desc": "Manually enter all values below."
        },
        "Mercury–Water (classic)": {
            "rho_m": 13600.0, "rho_f": 1000.0,
            "desc": "Measures water pressure with a mercury manometer."
        },
        "Mercury–Air (gas pressure)": {
            "rho_m": 13600.0, "rho_f": 1.2,
            "desc": "Measures gas pressure. Note the system fluid's effect is minimal."
        },
        "Water–Air (sensitive)": {
            "rho_m": 1000.0, "rho_f": 1.2,
            "desc": "A sensitive setup for measuring small gas pressure differences."
        }
    }
    
    scenario_choice = st.selectbox("Interactive 'What-If' Scenarios", options=list(SCENARIOS.keys()))
    selected_scenario = SCENARIOS[scenario_choice]
    st.info(selected_scenario["desc"])

    st.subheader("Fluid Properties")
    rho_m = st.number_input("Density of Manometer Fluid (ρₘ) [kg/m³]", value=selected_scenario["rho_m"], step=100.0)
    rho_f = st.number_input("Density of System Fluid (ρₒ) [kg/m³]", value=selected_scenario["rho_f"], step=10.0)
    g = st.number_input("Gravity (g) [m/s²]", value=9.81, format="%.2f")

    st.subheader("Manometer Heights")
    h = st.slider("Height 'h' (m)", min_value=0.00, max_value=0.50, value=0.25, step=0.01, format="%.2f", help="Height of manometer fluid above the datum.")
    b = st.slider("Height 'b' (m)", min_value=0.00, max_value=0.50, value=0.10, step=0.01, format="%.2f", help="Height of system fluid above the datum.")

    # --- Calculation ---
    delta_P = rho_m * g * h - rho_f * g * b
    delta_P_kPa = delta_P / 1000

    st.markdown("---")
    st.header("📈 Theory")
    st.latex(r'''P_1 - P_{atm} = \rho_m g h - \rho_o g b''')

# --- Column 2: Visualization ---
with col2:
    st.header("🖼️ Visualization")

    # Move the result metric here, just below the Visualization header
    st.metric(label="Gauge Pressure at P₁ (P₁ - Pₐₜₘ)", value=f"{delta_P_kPa:,.3f} kPa")

    plot_placeholder = st.empty()

    # --- Pre-calculate static geometry ---
    vessel_right_edge = -0.25
    vessel_width = 0.2
    vessel_height = 0.2
    
    # Define different radii for connecting tube and U-tube
    conn_tube_inner_radius = 0.0130  # Thin connecting tube
    conn_tube_outer_radius = 0.0135  # Maintain reasonable wall thickness
    u_tube_inner_radius = 0.05
    u_tube_outer_radius = 0.06
    
    bend_y_center = 0
    
    fixed_yaxis_range = [-0.2, 0.8]
    fixed_xaxis_range = [-0.5, 0.5]

    system_fluid_color = 'rgba(240, 240, 210, 0.7)'
    manometer_fluid_color = 'rgba(0, 100, 255, 0.8)'
    glass_color = 'rgba(211, 211, 211, 0.4)'

    def get_bend_points(radius, y_center, start_angle=np.pi, end_angle=2*np.pi):
        theta = np.linspace(start_angle, end_angle, 50)
        return radius * np.cos(theta), radius * np.sin(theta) + y_center

    x_outer_bend, y_outer_bend = get_bend_points(u_tube_outer_radius, bend_y_center)
    x_inner_bend, y_inner_bend = get_bend_points(u_tube_inner_radius, bend_y_center)

    # --- Function to generate plot ---
    def generate_plot(h_inst, b_inst):
        datum_y = 0.2
        pipe_center_y = datum_y + b_inst
        level_left_mano = datum_y
        level_right_mano = datum_y + h_inst
        
        fig = go.Figure()

        # 1. Draw Glassware
        vessel_left_edge = vessel_right_edge - vessel_width
        vessel_bottom = pipe_center_y - vessel_height/2
        vessel_top = pipe_center_y + vessel_height/2
        
        # Vessel walls (as filled rectangles)
        # Left wall
        fig.add_shape(type="rect", 
                     x0=vessel_left_edge - 0.01, y0=vessel_bottom, 
                     x1=vessel_left_edge, y1=vessel_top, 
                     fillcolor=glass_color, line_width=0)
        # Right wall
        fig.add_shape(type="rect", 
                     x0=vessel_right_edge, y0=vessel_bottom, 
                     x1=vessel_right_edge + 0.01, y1=vessel_top, 
                     fillcolor=glass_color, line_width=0)
        # Bottom wall
        fig.add_shape(type="rect", 
                     x0=vessel_left_edge - 0.01, y0=vessel_bottom - 0.01, 
                     x1=vessel_right_edge + 0.01, y1=vessel_bottom, 
                     fillcolor=glass_color, line_width=0)
        # Top wall
        fig.add_shape(type="rect", 
                     x0=vessel_left_edge - 0.01, y0=vessel_top, 
                     x1=vessel_right_edge + 0.01, y1=vessel_top + 0.01, 
                     fillcolor=glass_color, line_width=0)
        
        # Horizontal Connecting Tube (filled hollow tube)
        transition_x = -u_tube_outer_radius
        
        conn_tube_x = [
            vessel_right_edge, vessel_right_edge,
            transition_x, transition_x,
            transition_x, transition_x,
            vessel_right_edge, vessel_right_edge
        ]
        conn_tube_y = [
            pipe_center_y - conn_tube_outer_radius, pipe_center_y + conn_tube_outer_radius,
            pipe_center_y + conn_tube_outer_radius, pipe_center_y + conn_tube_inner_radius,
            pipe_center_y - conn_tube_inner_radius, pipe_center_y - conn_tube_outer_radius,
            pipe_center_y - conn_tube_outer_radius, pipe_center_y - conn_tube_outer_radius
        ]
        fig.add_trace(go.Scatter(x=conn_tube_x, y=conn_tube_y, 
                                fill="toself", fillcolor=glass_color, 
                                mode='none', hoverinfo='none'))
        
        # Transition piece (from thin tube to thick U-tube)
        trans_x = [
            transition_x, transition_x,
            transition_x - 0.02, transition_x - 0.02,
            transition_x - 0.02, transition_x - 0.02,
            transition_x, transition_x
        ]
        trans_y = [
            pipe_center_y - conn_tube_outer_radius, pipe_center_y + conn_tube_outer_radius,
            pipe_center_y + u_tube_outer_radius, pipe_center_y + u_tube_inner_radius,
            pipe_center_y - u_tube_inner_radius, pipe_center_y - u_tube_outer_radius,
            pipe_center_y - conn_tube_outer_radius, pipe_center_y - conn_tube_outer_radius
        ]
        fig.add_trace(go.Scatter(x=trans_x, y=trans_y, 
                                fill="toself", fillcolor=glass_color, 
                                mode='none', hoverinfo='none'))
        
        # U-Tube Glass
        x_glass = np.concatenate([[-u_tube_outer_radius, -u_tube_outer_radius], x_outer_bend, 
                                 [u_tube_outer_radius, u_tube_outer_radius, u_tube_inner_radius, u_tube_inner_radius], 
                                 x_inner_bend[::-1], [-u_tube_inner_radius, -u_tube_inner_radius, -u_tube_outer_radius]])
        y_glass = np.concatenate([[pipe_center_y, bend_y_center], y_outer_bend, 
                                 [bend_y_center, 0.7, 0.7, bend_y_center], 
                                 y_inner_bend[::-1], [bend_y_center, pipe_center_y, pipe_center_y]])
        fig.add_trace(go.Scatter(x=x_glass, y=y_glass, fill="toself", fillcolor=glass_color, 
                                mode='none', hoverinfo='none'))

        # 2. Draw Manometer Fluid
        fig.add_shape(type="rect", x0=-u_tube_outer_radius, y0=bend_y_center, 
                     x1=-u_tube_inner_radius, y1=level_left_mano, 
                     fillcolor=manometer_fluid_color, line_width=0)
        fig.add_shape(type="rect", x0=u_tube_inner_radius, y0=bend_y_center, 
                     x1=u_tube_outer_radius, y1=level_right_mano, 
                     fillcolor=manometer_fluid_color, line_width=0)
        x_mano_bend = np.concatenate([x_outer_bend, x_inner_bend[::-1]])
        y_mano_bend = np.concatenate([y_outer_bend, y_inner_bend[::-1]])
        fig.add_trace(go.Scatter(x=x_mano_bend, y=y_mano_bend, fill="toself", 
                                fillcolor=manometer_fluid_color, mode='none', hoverinfo='none'))

        # 3. Draw System Fluid
        fig.add_shape(type="rect", 
                     x0=vessel_left_edge, y0=vessel_bottom, 
                     x1=vessel_right_edge, y1=vessel_top, 
                     fillcolor=system_fluid_color, line_width=0)
        fig.add_shape(type="rect", 
                     x0=vessel_right_edge, y0=pipe_center_y - conn_tube_inner_radius, 
                     x1=transition_x - 0.02, y1=pipe_center_y + conn_tube_inner_radius, 
                     fillcolor=system_fluid_color, line_width=0)
        fig.add_shape(type="rect", 
                     x0=-u_tube_outer_radius, y0=level_left_mano, 
                     x1=-u_tube_inner_radius, y1=pipe_center_y, 
                     fillcolor=system_fluid_color, line_width=0)

        # 4. Annotations
        fig.add_annotation(x=vessel_right_edge - vessel_width/2, y=pipe_center_y, 
                          text="<b>P₁</b>", showarrow=False, font=dict(size=18))
        fig.add_annotation(x=u_tube_outer_radius, y=0.72, text="<b>Pₐₜₘ</b>", 
                          showarrow=True, arrowhead=2, ax=0, ay=20)
        
        # Datum Line
        fig.add_shape(type="line", x0=-0.3, y0=datum_y, x1=0.3, y1=datum_y, 
                     line=dict(color="black", width=1, dash="dash"))
        fig.add_annotation(x=-0.31, y=datum_y, text="Datum", showarrow=False, xanchor="right")
        
        tick_len = 0.015
        # Dimension line for 'b'
        b_line_x = -u_tube_outer_radius - 0.05
        fig.add_shape(type="line", x0=b_line_x, y0=datum_y, x1=b_line_x, y1=pipe_center_y, 
                     line=dict(color="black", width=1))
        fig.add_shape(type="line", x0=b_line_x - tick_len, y0=datum_y, 
                     x1=b_line_x + tick_len, y1=datum_y, line=dict(color="black", width=1))
        fig.add_shape(type="line", x0=b_line_x - tick_len, y0=pipe_center_y, 
                     x1=b_line_x + tick_len, y1=pipe_center_y, line=dict(color="black", width=1))
        fig.add_annotation(x=b_line_x - tick_len, y=(datum_y+pipe_center_y)/2, 
                          text=f"b={b_inst:.2f}m", showarrow=False, xanchor="right")
        
        # Dimension line for 'h'
        h_line_x = u_tube_outer_radius + 0.05
        fig.add_shape(type="line", x0=h_line_x, y0=datum_y, x1=h_line_x, y1=level_right_mano, 
                     line=dict(color="black", width=1))
        fig.add_shape(type="line", x0=h_line_x - tick_len, y0=datum_y, 
                     x1=h_line_x + tick_len, y1=datum_y, line=dict(color="black", width=1))
        fig.add_shape(type="line", x0=h_line_x - tick_len, y0=level_right_mano, 
                     x1=h_line_x + tick_len, y1=level_right_mano, line=dict(color="black", width=1))
        fig.add_annotation(x=h_line_x + tick_len, y=(datum_y+level_right_mano)/2, 
                          text=f"h={h_inst:.2f}m", showarrow=False, xanchor="left")

        fig.update_layout(
            xaxis=dict(range=fixed_xaxis_range, visible=False),
            yaxis=dict(range=fixed_yaxis_range, visible=False),
            showlegend=False, height=600, plot_bgcolor='white', margin=dict(t=0, b=0, l=0, r=0)
        )
        return fig

    # --- Animation Logic ---
    start_heights = st.session_state.previous_heights_open
    end_heights = {'h': h, 'b': b}

    if start_heights is None:
        start_heights = end_heights

    if not (np.isclose(start_heights['h'], end_heights['h']) and np.isclose(start_heights['b'], end_heights['b'])):
        animation_steps = 20
        for i in range(animation_steps + 1):
            inter_h = start_heights['h'] + (end_heights['h'] - start_heights['h']) * (i / animation_steps)
            inter_b = start_heights['b'] + (end_heights['b'] - start_heights['b']) * (i / animation_steps)
            fig = generate_plot(inter_h, inter_b)
            plot_placeholder.plotly_chart(fig, use_container_width=True)
            time.sleep(0.02)
    else:
        fig = generate_plot(end_heights['h'], end_heights['b'])
        plot_placeholder.plotly_chart(fig, use_container_width=True)
    
    st.session_state.previous_heights_open = end_heights

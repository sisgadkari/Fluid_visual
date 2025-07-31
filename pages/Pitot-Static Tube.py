import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(page_title="Interactive Pitot-Static Tube", layout="wide")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>Interactive Pitot-Static Tube Velocity Measurement</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
Explore how a Pitot-static tube measures flow velocity by comparing stagnation and static pressures.
Adjust the manometer height to see how it relates to flow velocity through Bernoulli's equation.
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# --- Main Layout ---
col1, col2 = st.columns([2, 3])

# --- Column 1: Inputs and Results ---
with col1:
    st.header("🔬 Parameters")

    # --- Interactive Scenarios ---
    SCENARIOS = {
        "Custom...": {
            "rho_f": 1.225, "rho_m": 1000.0, "altitude": 0,
            "desc": "Manually adjust all parameters below."
        },
        "Aircraft at Sea Level": {
            "rho_f": 1.225, "rho_m": 1000.0, "altitude": 0,
            "desc": "Standard conditions for aircraft speed measurement at sea level."
        },
        "Aircraft at 10,000 ft": {
            "rho_f": 0.905, "rho_m": 1000.0, "altitude": 3048,
            "desc": "Typical cruising altitude for small aircraft (ρ decreases with altitude)."
        },
        "Wind Tunnel Testing": {
            "rho_f": 1.2, "rho_m": 850.0, "altitude": 0,
            "desc": "Low-speed wind tunnel with oil manometer for precise measurements."
        },
        "Water Flow Measurement": {
            "rho_f": 1000.0, "rho_m": 13600.0, "altitude": 0,
            "desc": "Measuring water velocity in pipes using mercury manometer."
        },
        "HVAC Duct Airflow": {
            "rho_f": 1.18, "rho_m": 1000.0, "altitude": 0,
            "desc": "Measuring air velocity in ventilation ducts."
        }
    }
    
    scenario = st.selectbox("Select Application Scenario", list(SCENARIOS.keys()))
    selected = SCENARIOS[scenario]
    st.info(selected["desc"])
    
    st.subheader("Fluid Properties")
    col_1, col_2 = st.columns(2)
    with col_1:
        rho_f = st.number_input("Flow Fluid Density ρ_f (kg/m³)", 
                               value=selected["rho_f"], min_value=0.1, step=0.1, format="%.3f")
    with col_2:
        rho_m = st.number_input("Manometer Fluid ρ_m (kg/m³)", 
                               value=selected["rho_m"], min_value=100.0, step=10.0, format="%.1f")
    
    g = 9.81
    altitude = selected.get("altitude", 0)
    
    # Temperature effects on air density
    if scenario != "Custom...":
        temp_c = st.slider("Temperature (°C)", -40, 50, 15, 
                          help="Temperature affects air density")
        # Adjust air density for temperature (if flow fluid is air-like)
        if rho_f < 10:  # Likely a gas
            T_kelvin = temp_c + 273.15
            rho_f = rho_f * (288.15 / T_kelvin)  # Ideal gas law adjustment
            st.caption(f"Adjusted air density: {rho_f:.3f} kg/m³")
    
    st.subheader("Manometer Reading")
    
    # Set appropriate range based on application
    if "Aircraft" in scenario:
        h_max = 100.0
        h_default = 20.0
    elif "Water" in scenario:
        h_max = 30.0
        h_default = 5.0
    else:
        h_max = 50.0
        h_default = 10.0
    
    h_cm = st.slider("Manometer Height h (cm)", 0.0, h_max, h_default, step=0.5,
                     help="Height difference in the U-tube manometer")
    h_mano = h_cm / 100
    
    # Calculate velocity from manometer height
    delta_P = rho_m * g * h_mano
    U = np.sqrt(2 * delta_P / rho_f) if rho_f > 0 else 0
    
    # Convert to other units
    U_kmh = U * 3.6
    U_mph = U * 2.237
    U_knots = U * 1.944
    
    # Additional parameters
    show_calibration = st.checkbox("Show Calibration Factor", value=False)
    if show_calibration:
        C_pitot = st.slider("Pitot Tube Coefficient C", 0.90, 1.10, 1.00, step=0.01,
                           help="Accounts for viscous effects and probe geometry")
        U_corrected = U * C_pitot
    else:
        C_pitot = 1.0
        U_corrected = U
    
    st.markdown("---")
    st.header("📈 Results")
    
    # Display results in metric format
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.metric("Flow Velocity", f"{U:.2f} m/s")
        st.metric("Pressure Difference", f"{delta_P/1000:.3f} kPa")
        st.metric("Dynamic Pressure q", f"{0.5*rho_f*U**2/1000:.3f} kPa")
    
    with col_r2:
        if "Aircraft" in scenario:
            st.metric("Airspeed", f"{U_knots:.1f} knots")
        else:
            st.metric("Velocity", f"{U_kmh:.1f} km/h")
        st.metric("Mach Number", f"{U/340:.3f}" if rho_f < 10 else "N/A")
        Re = rho_f * U * 0.01 / 1.8e-5  # Approximate Reynolds number
        st.metric("Reynolds Number", f"{Re:.0e}")
    
    # Show equations
    with st.expander("📐 Governing Equations"):
        st.latex(r"\text{Bernoulli's Equation: } P_{\text{static}} + \frac{1}{2}\rho U^2 = P_{\text{stagnation}}")
        st.latex(r"\Delta P = P_{\text{stag}} - P_{\text{static}} = \frac{1}{2}\rho U^2")
        st.latex(r"\text{Manometer: } \Delta P = \rho_m g h")
        st.latex(r"\text{Therefore: } U = \sqrt{\frac{2 \rho_m g h}{\rho_f}}")
        if show_calibration:
            st.latex(r"U_{\text{actual}} = C \cdot U_{\text{theoretical}}")

# --- Column 2: Visualization ---
with col2:
    st.header("🖼️ Visualization")
    
    # Visualization options
    vis_col1, vis_col2, vis_col3 = st.columns(3)
    with vis_col1:
        show_streamlines = st.checkbox("Show Streamlines", value=True)
    with vis_col2:
        show_pressure = st.checkbox("Show Pressure Field", value=False)
    with vis_col3:
        show_details = st.checkbox("Show Probe Details", value=True)
    
    plot_placeholder = st.empty()
    
    # Enhanced color scheme
    fluid_color = 'rgba(224, 242, 254, 0.8)'
    probe_color = 'rgba(107, 114, 128, 1)'
    stagnation_color = 'rgba(239, 68, 68, 0.7)'  # Red
    static_color = 'rgba(59, 130, 246, 0.7)'     # Blue
    manometer_fluid_color = 'rgba(16, 185, 129, 0.8)'  # Green
    glass_color = 'rgba(209, 213, 219, 0.4)'
    
    def generate_pitot_plot(h_inst, velocity):
        fig = go.Figure()
        
        # Flow field dimensions
        field_width = 10
        field_height = 4
        
        # Probe geometry
        probe_length = 7.0
        probe_outer_r = 0.24
        probe_inner_r = 0.14
        static_port_x = 3.6
        
        # 1. Draw flow field with gradient
        if show_pressure and velocity > 0:
            # Create pressure field gradient
            x_grid = np.linspace(-2, field_width, 50)
            y_grid = np.linspace(-field_height/2, field_height/2, 30)
            
            for i in range(len(x_grid)-1):
                for j in range(len(y_grid)-1):
                    x_pos = (x_grid[i] + x_grid[i+1]) / 2
                    y_pos = (y_grid[j] + y_grid[j+1]) / 2
                    
                    # Calculate local pressure (simplified)
                    if x_pos < 0 and abs(y_pos) < probe_outer_r * 1.5:
                        # Stagnation region
                        pressure_factor = 1.0
                    else:
                        # Normal flow
                        pressure_factor = 0.5
                    
                    color_intensity = int(255 * (1 - pressure_factor))
                    fig.add_shape(type="rect",
                                 x0=x_grid[i], y0=y_grid[j],
                                 x1=x_grid[i+1], y1=y_grid[j+1],
                                 fillcolor=f'rgba({color_intensity}, {color_intensity}, 255, 0.3)',
                                 line_width=0)
        else:
            # Simple flow field background
            fig.add_shape(type="rect", x0=-2, y0=-field_height/2, 
                         x1=field_width, y1=field_height/2,
                         fillcolor=fluid_color, line_width=0)
        
        # Add boundary walls
        fig.add_shape(type="line", x0=-2, y0=field_height/2, 
                     x1=field_width, y1=field_height/2,
                     line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=-2, y0=-field_height/2,
                     x1=field_width, y1=-field_height/2,
                     line=dict(color="black", width=2))
        
        # 2. Draw streamlines with realistic flow behavior
        if show_streamlines and velocity > 0:
            n_streamlines = 12
            y_starts = np.linspace(-field_height/2 * 0.9, field_height/2 * 0.9, n_streamlines)
            
            for y_start in y_starts:
                if abs(y_start) < probe_outer_r:
                    # Streamlines that hit the probe
                    # Stagnation streamline
                    x_stream = np.linspace(-2, -0.1, 50)
                    y_stream = y_start * (1 - x_stream / -2) ** 2
                else:
                    # Streamlines that go around
                    x_points = np.linspace(-2, field_width, 100)
                    y_deflection = np.zeros_like(x_points)
                    
                    for i, x in enumerate(x_points):
                        if -0.5 < x < probe_length:
                            # Deflection around probe
                            deflection_strength = np.exp(-(x - probe_length/2)**2 / 2)
                            min_distance = probe_outer_r * 1.3
                            if abs(y_start) < min_distance * 2:
                                y_deflection[i] = np.sign(y_start) * deflection_strength * \
                                                 (min_distance - abs(y_start)) * 0.5
                    
                    y_stream = y_start + y_deflection
                    x_stream = x_points
                
                fig.add_trace(go.Scatter(x=x_stream, y=y_stream, mode='lines',
                                       line=dict(color='rgba(0, 0, 0, 0.3)', width=1),
                                       hoverinfo='none', showlegend=False))
                
                # Add flow arrows
                if y_start % (field_height/6) < field_height/12:
                    arrow_x = -1.5
                    fig.add_annotation(x=arrow_x, y=y_start,
                                     ax=arrow_x + 0.3, ay=y_start,
                                     showarrow=True, arrowhead=2, arrowsize=1.5,
                                     arrowwidth=2, arrowcolor="darkblue")
        
        # 3. Draw Pitot-static tube with details
        # Probe body
        fig.add_shape(type="rect", x0=0, y0=-probe_outer_r,
                     x1=probe_length, y1=probe_outer_r,
                     fillcolor=probe_color, line_width=0)
        
        # Hemispherical nose
        theta = np.linspace(-np.pi/2, np.pi/2, 50)
        x_nose = probe_outer_r * np.cos(theta)
        y_nose = probe_outer_r * np.sin(theta)
        fig.add_trace(go.Scatter(x=x_nose, y=y_nose, fill="toself",
                               fillcolor=probe_color, mode='none',
                               hoverinfo='none', showlegend=False))
        
        if show_details:
            # Inner tube (stagnation pressure)
            fig.add_shape(type="rect", x0=0, y0=-probe_inner_r,
                         x1=probe_length, y1=probe_inner_r,
                         fillcolor="lightgrey", line_width=0)
            
            # Stagnation pressure port
            fig.add_shape(type="circle", x0=-0.04, y0=-probe_inner_r/2,
                         x1=0.04, y1=probe_inner_r/2,
                         fillcolor=stagnation_color, line_width=0)
            
            # Enhanced static pressure ports - showing circumferential distribution
            n_static_ports = 8  # Total ports around circumference
            port_radius = 0.03  # Port hole radius
            
            for i in range(n_static_ports):
                angle = i * 2 * np.pi / n_static_ports
                port_y = probe_outer_r * 0.85 * np.sin(angle)
                port_z = probe_outer_r * 0.85 * np.cos(angle)  # For 3D effect
                
                # Determine visibility and appearance based on angle
                if abs(angle - np.pi/2) < np.pi/4 or abs(angle - 3*np.pi/2) < np.pi/4:
                    # Top and bottom ports (fully visible)
                    port_color = static_color
                    port_size = port_radius
                    port_opacity = 1.0
                elif abs(angle) < np.pi/4 or abs(angle - np.pi) < np.pi/4:
                    # Front and back ports (partially visible)
                    port_color = static_color
                    port_size = port_radius * 0.7
                    port_opacity = 0.6
                else:
                    # Side ports (visible as ellipses to show perspective)
                    port_color = static_color
                    port_size = port_radius * 0.5
                    port_opacity = 0.8
                
                # Only draw ports that would be visible from this 2D side view
                if abs(port_y) > probe_inner_r * 1.1:  # Avoid overlap with inner tube
                    fig.add_shape(type="circle",
                                 x0=static_port_x - port_size,
                                 y0=port_y - port_size,
                                 x1=static_port_x + port_size,
                                 y1=port_y + port_size,
                                 fillcolor=port_color,
                                 line=dict(color="darkblue", width=1),
                                 opacity=port_opacity)
            
            # Add indication of circumferential distribution with dashed circles
            # Top circumferential indication
            circle_theta = np.linspace(0, 2*np.pi, 100)
            circle_x = static_port_x + probe_outer_r * 0.85 * 0.3 * np.cos(circle_theta)
            circle_y = probe_outer_r * 0.85 * np.sin(circle_theta)
            fig.add_trace(go.Scatter(x=circle_x, y=circle_y, mode='lines',
                                   line=dict(color='rgba(59, 130, 246, 0.4)', width=1, dash='dot'),
                                   hoverinfo='none', showlegend=False))
            

            
            # Pressure pathways
            fig.add_shape(type="rect", x0=0, y0=-probe_inner_r/3,
                         x1=probe_length, y1=probe_inner_r/3,
                         fillcolor=stagnation_color, line_width=0, opacity=0.5)
            fig.add_shape(type="rect", x0=static_port_x, y0=probe_inner_r,
                         x1=probe_length, y1=probe_outer_r*0.8,
                         fillcolor=static_color, line_width=0, opacity=0.5)
        
        # 4. Enhanced U-tube manometer (following the original manometer design)
        mano_x = probe_length + 1.5
        mano_bend_y_center = -3.0
        tube_inner_radius = 0.08
        tube_outer_radius = 0.10
        
        # Left and right tube x positions
        tube_spacing = 0.2  # Half distance between tube centers
        left_tube_x = mano_x - tube_spacing
        right_tube_x = mano_x + tube_spacing
        
        # Manometer top position
        mano_top_y = -0.5
        
        # Calculate fluid levels
        level_center = mano_bend_y_center + 0.3
        level_left = level_center + h_inst
        level_right = level_center - h_inst
        
        # Function to generate bend points (from original manometer)
        def get_bend_points(radius, y_center):
            theta = np.linspace(np.pi, 2 * np.pi, 50)
            return radius * np.cos(theta), radius * np.sin(theta) + y_center
        
        # Get bend points for outer and inner curves
        # Outer bend connects the outer edges of the tubes
        outer_bend_radius = tube_spacing + tube_outer_radius
        x_outer_bend, y_outer_bend = get_bend_points(outer_bend_radius, mano_bend_y_center)
        
        # Inner bend connects the inner edges of the tubes  
        inner_bend_radius = tube_spacing - tube_outer_radius + tube_inner_radius
        x_inner_bend, y_inner_bend = get_bend_points(inner_bend_radius, mano_bend_y_center)
        
        # Shift bends to center position
        x_outer_bend = x_outer_bend + mano_x
        x_inner_bend = x_inner_bend + mano_x
        
        # Draw U-tube glass
        x_glass = np.concatenate([
            [left_tube_x - tube_outer_radius, left_tube_x - tube_outer_radius], 
            x_outer_bend, 
            [right_tube_x + tube_outer_radius, right_tube_x + tube_outer_radius],
            [right_tube_x + tube_inner_radius, right_tube_x + tube_inner_radius], 
            x_inner_bend[::-1], 
            [left_tube_x - tube_inner_radius, left_tube_x - tube_inner_radius]
        ])
        y_glass = np.concatenate([
            [mano_top_y, mano_bend_y_center], 
            y_outer_bend, 
            [mano_bend_y_center, mano_top_y],
            [mano_top_y, mano_bend_y_center], 
            y_inner_bend[::-1], 
            [mano_bend_y_center, mano_top_y]
        ])
        fig.add_trace(go.Scatter(x=x_glass, y=y_glass, fill="toself", 
                                fillcolor=glass_color, mode='none', 
                                hoverinfo='none', showlegend=False))
        
        # Connecting lines from probe to manometer
        # Stagnation connection (red) to left tube
        fig.add_trace(go.Scatter(x=[probe_length, probe_length + 0.5, left_tube_x],
                               y=[0, -0.2, -0.2],
                               mode='lines', line=dict(color=stagnation_color, width=3),
                               hoverinfo='none', showlegend=False))
        
        # Static connection (blue) to right tube
        fig.add_trace(go.Scatter(x=[probe_length, probe_length + 0.5, right_tube_x],
                               y=[probe_outer_r*0.9, -0.1, -0.1],
                               mode='lines', line=dict(color=static_color, width=3),
                               hoverinfo='none', showlegend=False))
        
        # Add connecting tube glass structures
        conn_tube_inner_radius = 0.03
        conn_tube_outer_radius = 0.04
        
        # Left connecting tube glass
        fig.add_shape(type="rect", 
                     x0=left_tube_x - conn_tube_outer_radius, y0=-0.2,
                     x1=left_tube_x - conn_tube_inner_radius, y1=mano_top_y,
                     fillcolor=glass_color, line_width=0)
        fig.add_shape(type="rect", 
                     x0=left_tube_x + conn_tube_inner_radius, y0=-0.2,
                     x1=left_tube_x + conn_tube_outer_radius, y1=mano_top_y,
                     fillcolor=glass_color, line_width=0)
        
        # Right connecting tube glass
        fig.add_shape(type="rect", 
                     x0=right_tube_x - conn_tube_outer_radius, y0=-0.1,
                     x1=right_tube_x - conn_tube_inner_radius, y1=mano_top_y,
                     fillcolor=glass_color, line_width=0)
        fig.add_shape(type="rect", 
                     x0=right_tube_x + conn_tube_inner_radius, y0=-0.1,
                     x1=right_tube_x + conn_tube_outer_radius, y1=mano_top_y,
                     fillcolor=glass_color, line_width=0)
        
        # System fluid in connecting tubes
        # Left connecting tube
        fig.add_shape(type="rect", 
                     x0=left_tube_x - conn_tube_inner_radius, y0=-0.2,
                     x1=left_tube_x + conn_tube_inner_radius, y1=mano_top_y,
                     fillcolor=stagnation_color, line_width=0, opacity=0.5)
        
        # Right connecting tube
        fig.add_shape(type="rect", 
                     x0=right_tube_x - conn_tube_inner_radius, y0=-0.1,
                     x1=right_tube_x + conn_tube_inner_radius, y1=mano_top_y,
                     fillcolor=static_color, line_width=0, opacity=0.5)
        
        # Draw Manometer Fluids (exactly like original)
        # Manometer fluid in left column
        fig.add_shape(type="rect", 
                     x0=left_tube_x, y0=mano_bend_y_center, 
                     x1=left_tube_x + (tube_outer_radius - tube_inner_radius), y1=level_left, 
                     fillcolor=manometer_fluid_color, line_width=0)
        # Manometer fluid in right column
        fig.add_shape(type="rect", 
                     x0=right_tube_x - (tube_outer_radius - tube_inner_radius), y0=mano_bend_y_center, 
                     x1=right_tube_x, y1=level_right, 
                     fillcolor=manometer_fluid_color, line_width=0)
        
        # Bottom bend manometer fluid
        x_mano_bend = np.concatenate([x_outer_bend, x_inner_bend[::-1]])
        y_mano_bend = np.concatenate([y_outer_bend, y_inner_bend[::-1]])
        fig.add_trace(go.Scatter(x=x_mano_bend, y=y_mano_bend, fill="toself", 
                                fillcolor=manometer_fluid_color, mode='none', hoverinfo='none', showlegend=False))
        
        # System fluid on top of manometer fluid
        # Left side
        fig.add_shape(type="rect", 
                     x0=left_tube_x, y0=level_left, 
                     x1=left_tube_x + (tube_outer_radius - tube_inner_radius), y1=mano_top_y, 
                     fillcolor=stagnation_color, line_width=0, opacity=0.5)
        # Right side
        fig.add_shape(type="rect", 
                     x0=right_tube_x - (tube_outer_radius - tube_inner_radius), y0=level_right, 
                     x1=right_tube_x, y1=mano_top_y, 
                     fillcolor=static_color, line_width=0, opacity=0.5)
        
        # Interface markers
        fig.add_shape(type="line", 
                     x0=left_tube_x + (tube_outer_radius - tube_inner_radius) - 0.02, 
                     y0=level_left, 
                     x1=left_tube_x + (tube_outer_radius - tube_inner_radius) + 0.02, 
                     y1=level_left, 
                     line=dict(color="black", width=2))
        fig.add_shape(type="line", 
                     x0=right_tube_x - (tube_outer_radius - tube_inner_radius) - 0.02, 
                     y0=level_right, 
                     x1=right_tube_x - (tube_outer_radius - tube_inner_radius) + 0.02, 
                     y1=level_right, 
                     line=dict(color="black", width=2))
        
        # Height dimension
        if abs(h_inst) > 0.01:
            dim_x = right_tube_x + 0.05
            fig.add_shape(type="line",
                         x0=dim_x, y0=level_left,
                         x1=dim_x, y1=level_right,
                         line=dict(color="black", width=1))
            # Add arrows at ends
            fig.add_shape(type="line", 
                         x0=dim_x - 0.01, y0=level_left, 
                         x1=dim_x + 0.01, y1=level_left, 
                         line=dict(color="black", width=1))
            fig.add_shape(type="line", 
                         x0=dim_x - 0.01, y0=level_right, 
                         x1=dim_x + 0.01, y1=level_right, 
                         line=dict(color="black", width=1))
            fig.add_annotation(x=dim_x + 0.02, y=level_center,
                             text=f"h = {h_inst*100:.1f} cm",
                             showarrow=False, xanchor="left", font=dict(size=14))
        
        # 5. Annotations and labels
        # Velocity annotation with arrow
        if velocity > 0:
            fig.add_annotation(x=-1, y=field_height/2+0.3,
                             text=f"U = {velocity:.1f} m/s",
                             showarrow=False, font=dict(size=16, color="darkblue"))
            
            # Dynamic pressure annotation
            fig.add_annotation(x=probe_length/2, y=-probe_outer_r-0.7,
                             text=f"q = ½ρU² = {0.5*rho_f*velocity**2/1000:.2f} kPa",
                             showarrow=False, font=dict(size=10))
        
        # Pressure labels
        fig.add_annotation(x=-0.2, y=0.3, text="P₀<br>(Stagnation)",
                          showarrow=False, font=dict(size=12, color="darkred"),
                          bgcolor="white", bordercolor="darkred", borderwidth=1)
        fig.add_annotation(x=static_port_x, y=probe_outer_r+0.3, text="P<br>(Static)",
                          showarrow=False, font=dict(size=12, color="darkblue"),
                          bgcolor="white", bordercolor="darkblue", borderwidth=1)
        
        # Manometer labels
        fig.add_annotation(x=left_tube_x, y=mano_top_y + 0.1, text="P₀",
                          showarrow=False, font=dict(size=14, color="darkred"))
        fig.add_annotation(x=right_tube_x, y=mano_top_y + 0.1, text="P",
                          showarrow=False, font=dict(size=14, color="darkblue"))
        
        # Title
        fig.add_annotation(x=probe_length/2, y=probe_outer_r+0.8,
                          text="Pitot-Static Tube",
                          showarrow=False, font=dict(size=16, color="black", family="Arial Black"))
        
        # Manometer fluid label
        fig.add_annotation(x=(left_tube_x + right_tube_x) / 2, y=mano_bend_y_center - 0.05,
                          text=f"Manometer Fluid<br>(ρ = {rho_m:.0f} kg/m³)",
                          showarrow=False, font=dict(size=10), yanchor="top")
        
        # Layout
        fig.update_layout(
            xaxis=dict(range=[-2, field_width], visible=False),
            yaxis=dict(range=[-4.5, 3], scaleanchor="x", scaleratio=1, visible=False),
            plot_bgcolor="white",
            margin=dict(l=0, r=0, t=0, b=0),
            height=600,
            showlegend=False
        )
        
        return fig
    
    # Display the plot without animation
    fig = generate_pitot_plot(h_mano, U)
    plot_placeholder.plotly_chart(fig, use_container_width=True)

# Educational content
with st.expander("📚 Understanding Pitot-Static Tubes"):
    st.markdown("""
    ### How Pitot-Static Tubes Work
    
    A Pitot-static tube measures fluid velocity by comparing two pressures:
    
    1. **Stagnation Pressure (P₀)**: Total pressure when flow is brought to rest
    2. **Static Pressure (P)**: Pressure of the moving fluid
    
    The difference between these pressures is the **dynamic pressure**, which is directly related to velocity.
    
    ### Key Design Features
    
    - **Stagnation Port**: Forward-facing opening captures total pressure
    - **Static Ports**: Side holes measure static pressure (usually 4-8 ports)
    - **Port Location**: Static ports placed where flow is undisturbed (5-10 diameters from nose)
    - **Alignment**: Must be aligned with flow direction (±15° typically acceptable)
    
    ### Common Applications
    
    - **Aviation**: Airspeed measurement (all aircraft)
    - **Wind Tunnels**: Velocity surveys and calibration
    - **HVAC**: Duct flow measurement
    - **Industrial**: Stack gas velocity, water flow
    - **Marine**: Ship speed through water
    
    ### Advantages & Limitations
    
    **Advantages:**
    - Simple, no moving parts
    - Direct velocity measurement
    - Wide velocity range
    - Proven reliability
    
    **Limitations:**
    - Requires alignment with flow
    - Can be affected by turbulence
    - Needs density correction for gases
    - Can clog in dirty fluids
    """)

# Advanced calculations section
with st.expander("🔧 Advanced Calculations & Error Analysis"):
    st.markdown("### Compressibility Effects")
    if U > 100:  # High speed
        st.warning("At high speeds, compressibility effects become important!")
        M = U / 340  # Approximate Mach number
        st.latex(r"\text{For } M > 0.3: \quad \frac{P_0 - P}{q} = 1 + \frac{M^2}{4} + \frac{M^4}{40} + ...")
    
    st.markdown("### Error Analysis")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        alignment_error = st.slider("Alignment Error (°)", 0, 30, 5)
        error_factor = np.cos(np.radians(alignment_error))
        velocity_error = (1-error_factor)*100
        st.write(f"Velocity Error: {velocity_error:.1f}%")
        st.caption("Misalignment reduces measured stagnation pressure")
    
    with col_e2:
        density_uncertainty = st.slider("Density Uncertainty (%)", 0, 10, 2)
        velocity_uncertainty = density_uncertainty / 2
        st.write(f"Velocity Uncertainty: ±{velocity_uncertainty:.1f}%")
        st.caption("Velocity uncertainty is half of density uncertainty")
    
    st.markdown("### Practical Measurement Tips")
    st.info("""
    - **Temperature Correction**: Essential for gas measurements
    - **Multiple Readings**: Average several measurements for accuracy
    - **Probe Size**: Should be < 1/20 of duct diameter to minimize blockage
    - **Turbulence**: Wait for steady reading in turbulent flow
    """)
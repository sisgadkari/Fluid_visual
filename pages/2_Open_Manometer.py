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

# Create tabs for different aspects
tab1, tab2, tab3 = st.tabs(["🎯 Interactive Simulation", "📚 Understanding Manometers", "📋 Application Examples"])

with tab1:
    # --- Main Layout ---
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
                "desc": "Measures water pressure with a mercury manometer. Mercury's high density allows for compact designs."
            },
            "Mercury–Air (gas pressure)": {
                "rho_m": 13600.0, "rho_f": 1.2,
                "desc": "Measures gas pressure. The system fluid's effect is minimal due to low gas density."
            },
            "Water–Air (sensitive)": {
                "rho_m": 1000.0, "rho_f": 1.2,
                "desc": "A sensitive setup for measuring small gas pressure differences. Larger height changes for same pressure."
            },
            "Oil–Water (industrial)": {
                "rho_m": 850.0, "rho_f": 1000.0,
                "desc": "Industrial application using oil as manometer fluid for water systems."
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
        
        # Calculate individual components
        pressure_from_h = rho_m * g * h
        pressure_from_b = rho_f * g * b
        
        # Calculate pressure in atmospheres and psi for reference
        delta_P_atm = delta_P / 101325
        delta_P_psi = delta_P / 6894.76

        st.markdown("---")
        st.header("📊 Results Summary")
        
        # Main result in a prominent box
        st.metric(label="Gauge Pressure at P₁ (P₁ - Pₐₜₘ)", value=f"{delta_P_kPa:,.3f} kPa", 
                 delta=f"{delta_P_atm:.4f} atm" if abs(delta_P_atm) > 0.001 else None)
        
        # Additional unit conversions
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("In Pascals", f"{delta_P:,.1f} Pa")
        with col_r2:
            st.metric("In psi", f"{delta_P_psi:.3f} psi")
        
        st.markdown("---")
        st.header("🧮 Step-by-Step Calculation")
        
        with st.expander("📖 See Detailed Breakdown", expanded=False):
            st.markdown("### Pressure Balance Equation")
            st.latex(r'P_1 - P_{atm} = \rho_m g h - \rho_o g b')
            
            st.markdown("### Step 1: Calculate Pressure from Manometer Fluid Column")
            st.latex(r'P_{manometer} = \rho_m \times g \times h')
            st.write(f"P_manometer = {rho_m} × {g} × {h}")
            st.write(f"P_manometer = **{pressure_from_h:,.2f} Pa** = **{pressure_from_h/1000:.3f} kPa**")
            
            st.markdown("### Step 2: Calculate Pressure from System Fluid Column")
            st.latex(r'P_{system} = \rho_o \times g \times b')
            st.write(f"P_system = {rho_f} × {g} × {b}")
            st.write(f"P_system = **{pressure_from_b:,.2f} Pa** = **{pressure_from_b/1000:.3f} kPa**")
            
            st.markdown("### Step 3: Calculate Net Gauge Pressure")
            st.latex(r'P_1 - P_{atm} = P_{manometer} - P_{system}')
            st.write(f"ΔP = {pressure_from_h:,.2f} - {pressure_from_b:,.2f}")
            st.write(f"ΔP = **{delta_P:,.2f} Pa** = **{delta_P_kPa:.3f} kPa**")
            
            # Physical interpretation
            st.markdown("### Physical Interpretation")
            if delta_P > 0:
                st.success(f"✅ P₁ is **{delta_P_kPa:.3f} kPa above** atmospheric pressure (positive gauge pressure)")
            elif delta_P < 0:
                st.warning(f"⚠️ P₁ is **{abs(delta_P_kPa):.3f} kPa below** atmospheric pressure (vacuum)")
            else:
                st.info("ℹ️ P₁ equals atmospheric pressure (zero gauge pressure)")
        
        st.markdown("---")
        st.header("🔍 Analysis Insights")
        
        with st.expander("💡 Pressure Contributions", expanded=False):
            # Create a simple breakdown
            st.markdown("**Pressure Component Breakdown:**")
            
            total_magnitude = abs(pressure_from_h) + abs(pressure_from_b)
            h_percentage = (abs(pressure_from_h) / total_magnitude * 100) if total_magnitude > 0 else 0
            b_percentage = (abs(pressure_from_b) / total_magnitude * 100) if total_magnitude > 0 else 0
            
            st.write(f"• Manometer fluid column (h): {pressure_from_h/1000:.3f} kPa ({h_percentage:.1f}% contribution)")
            st.write(f"• System fluid column (b): -{pressure_from_b/1000:.3f} kPa ({b_percentage:.1f}% contribution)")
            st.write(f"• **Net result**: {delta_P_kPa:.3f} kPa")
            
            # Density ratio analysis
            density_ratio = rho_m / rho_f if rho_f > 0 else float('inf')
            st.markdown(f"**Density Ratio (ρₘ/ρₒ):** {density_ratio:.2f}")
            
            if density_ratio > 10:
                st.info("💡 High density ratio: Manometer fluid dominates the pressure reading. Small changes in 'h' cause large pressure changes.")
            elif density_ratio < 2:
                st.info("💡 Low density ratio: Both columns contribute significantly. System is more sensitive but requires careful reading.")

        with st.expander("🎯 Design Considerations", expanded=False):
            st.markdown("**Manometer Selection Criteria:**")
            
            # Sensitivity analysis
            sensitivity = 1 / (rho_m * g) if rho_m > 0 else 0
            st.write(f"• **Sensitivity**: {sensitivity*1000:.4f} m/kPa")
            st.write("  (How much the manometer reading changes per unit pressure)")
            
            # Range analysis
            max_pressure_readable = rho_m * g * 0.5 / 1000  # Assuming 0.5m is practical max
            st.write(f"• **Practical measuring range**: 0 to ~{max_pressure_readable:.1f} kPa")
            st.write("  (Based on maximum readable height of 0.5 m)")
            
            st.markdown("**Application Suitability:**")
            if scenario_choice == "Mercury–Water (classic)":
                st.success("✅ Excellent for measuring moderate to high water pressures. Compact design due to mercury's high density.")
            elif scenario_choice == "Mercury–Air (gas pressure)":
                st.success("✅ Ideal for gas pressure measurements. System fluid effect negligible.")
            elif scenario_choice == "Water–Air (sensitive)":
                st.success("✅ Best for low-pressure gas measurements. High sensitivity but requires more space.")
            elif scenario_choice == "Oil–Water (industrial)":
                st.warning("⚠️ Moderate sensitivity. Suitable when mercury is undesirable for safety reasons.")

    # --- Column 2: Visualization ---
    with col2:
        st.header("🖼️ Visualization")

        # Visualization controls
        vis_col1, vis_col2 = st.columns(2)
        with vis_col1:
            show_pressure_labels = st.checkbox("Show Pressure Values", value=True)
        with vis_col2:
            show_datum_details = st.checkbox("Show Datum Reference", value=True)

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
            if show_datum_details:
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
            
            # Add pressure values if enabled
            if show_pressure_labels:
                # Calculate pressures at key points
                P1_abs = 101.325 + delta_P_kPa  # Approximate absolute pressure
                fig.add_annotation(x=vessel_right_edge - vessel_width/2, y=vessel_top + 0.05,
                                  text=f"P₁ = {P1_abs:.2f} kPa (abs)<br>{delta_P_kPa:.3f} kPa (gauge)",
                                  showarrow=False, font=dict(size=10), 
                                  bgcolor="rgba(255,255,255,0.8)", bordercolor="blue", borderwidth=1)

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

with tab2:
    st.header("📚 Understanding Open-Tube Manometers")
    
    col_edu1, col_edu2 = st.columns([1, 1])
    
    with col_edu1:
        st.markdown("""
        ### What is an Open-Tube Manometer?
        
        An open-tube manometer is a U-shaped tube containing a fluid (manometer fluid) used to measure 
        the **gauge pressure** of a system relative to atmospheric pressure.
        
        ### How It Works
        
        1. **One end** connects to the system whose pressure (P₁) you want to measure
        2. **Other end** is open to atmosphere (Pₐₜₘ)
        3. **Pressure difference** causes the manometer fluid to rise/fall
        4. **Height difference** indicates the gauge pressure
        
        ### Key Principle: Pressure Balance
        
        At any horizontal level in a static fluid, the pressure must be the same. By applying this 
        principle at the datum level (bottom of U-tube), we get:
        """)
        
        st.latex(r'P_1 + \rho_o g b = P_{atm} + \rho_m g h')
        
        st.markdown("""
        Rearranging gives us the **gauge pressure equation**:
        """)
        
        st.latex(r'P_1 - P_{atm} = \rho_m g h - \rho_o g b')
    
    with col_edu2:
        st.markdown("""
        ### Critical Design Parameters
        
        **1. Manometer Fluid Selection**
        - **Mercury (ρ = 13,600 kg/m³)**: 
          - ✅ Compact design, high density
          - ⚠️ Toxic, requires careful handling
          - Best for: Moderate to high pressures
        
        - **Water (ρ = 1,000 kg/m³)**:
          - ✅ Safe, cheap, readily available
          - ❌ Requires more height for same pressure
          - Best for: Low pressure gas measurements
        
        - **Oil (ρ = 850 kg/m³)**:
          - ✅ Safer than mercury, moderate sensitivity
          - ⚠️ May evaporate or degrade over time
          - Best for: Industrial applications avoiding mercury
        
        **2. Sensitivity vs. Range Trade-off**
        - Lower density fluids → More sensitive (larger h for same ΔP)
        - Higher density fluids → Wider range (measure higher pressures)
        
        **3. Reading Accuracy**
        - Meniscus reading: ±0.5 mm typical
        - Temperature effects on fluid density
        - Parallax errors in visual reading
        """)
    
    st.markdown("---")
    
    st.markdown("### Common Measurement Scenarios")
    
    scenario_col1, scenario_col2 = st.columns(2)
    
    with scenario_col1:
        st.markdown("""
        #### Positive Gauge Pressure (h > b·ρₒ/ρₘ)
        
        - System pressure **above** atmospheric
        - Manometer fluid pushed **down** on system side
        - Manometer fluid rises **up** on atmospheric side
        - Common in: Pressurized tanks, pumps, compressors
        
        **Visual indicator**: Right column higher than left
        """)
    
    with scenario_col2:
        st.markdown("""
        #### Negative Gauge Pressure (h < b·ρₒ/ρₘ)
        
        - System pressure **below** atmospheric (vacuum)
        - Manometer fluid pulled **up** on system side
        - Manometer fluid falls **down** on atmospheric side
        - Common in: Suction lines, vacuum systems, condensers
        
        **Visual indicator**: Right column lower than left
        """)
    
    st.markdown("---")
    
    st.markdown("### Advantages & Limitations")
    
    adv_col1, adv_col2 = st.columns(2)
    
    with adv_col1:
        st.success("""
        **Advantages:**
        - ✅ Simple construction, no calibration needed
        - ✅ Visual indication of pressure
        - ✅ No power supply required
        - ✅ Direct reading (based on fundamental principles)
        - ✅ Highly reliable, few failure modes
        - ✅ Inexpensive compared to electronic sensors
        """)
    
    with adv_col2:
        st.warning("""
        **Limitations:**
        - ⚠️ Requires visual access for reading
        - ⚠️ Not suitable for rapidly fluctuating pressures
        - ⚠️ Can be bulky for high-pressure applications
        - ⚠️ Mercury manometers have safety concerns
        - ⚠️ Temperature affects fluid density (needs correction)
        - ⚠️ Cannot measure very low pressure differences accurately
        """)

with tab3:
    st.header("📋 Real-World Applications")
    
    st.markdown("""
    Open-tube manometers are used across many industries despite the availability of modern electronic 
    pressure sensors. Their simplicity and reliability make them valuable for specific applications.
    """)
    
    app_col1, app_col2 = st.columns(2)
    
    with app_col1:
        st.markdown("""
        ### Industrial Applications
        
        **1. HVAC Systems**
        - Measuring duct pressure in ventilation systems
        - Checking filter pressure drop
        - Balancing air flow in buildings
        - *Typical fluid: Water or colored water*
        
        **2. Gas Distribution**
        - Natural gas pipeline pressure monitoring
        - Low-pressure gas regulator testing
        - Fuel gas pressure verification
        - *Typical fluid: Water or light oil*
        
        **3. Laboratory Use**
        - Calibrating pressure sensors
        - Teaching fluid mechanics principles
        - Verifying equipment performance
        - *Typical fluid: Mercury or water*
        
        **4. Water Treatment**
        - Filter backwash pressure monitoring
        - Pump suction line checks
        - Tank level indication
        - *Typical fluid: Mercury*
        """)
    
    with app_col2:
        st.markdown("""
        ### Process Industries
        
        **5. Chemical Plants**
        - Reactor vessel pressure monitoring
        - Distillation column differential pressure
        - Heat exchanger pressure drop
        - *Typical fluid: Mercury or specialized fluids*
        
        **6. Petroleum Refining**
        - Crude oil tank vapor space pressure
        - Fractionating column pressure
        - Pipeline pressure monitoring
        - *Typical fluid: Mercury*
        
        **7. Power Generation**
        - Boiler draft measurement
        - Condenser vacuum monitoring
        - Air flow measurement in ducts
        - *Typical fluid: Water*
        
        **8. Medical Applications**
        - Blood pressure measurement (sphygmomanometer)
        - Respiratory equipment calibration
        - Anesthesia machine pressure checks
        - *Typical fluid: Mercury (traditional)*
        """)
    
    st.markdown("---")
    
    st.markdown("### Safety Considerations")
    
    safety_col1, safety_col2, safety_col3 = st.columns(3)
    
    with safety_col1:
        st.markdown("""
        #### Mercury Manometers
        
        **Hazards:**
        - Toxic vapor inhalation
        - Skin contact absorption
        - Environmental contamination
        
        **Precautions:**
        - Use in well-ventilated areas
        - Spill containment trays
        - Personal protective equipment
        - Proper disposal procedures
        - Consider alternatives when possible
        """)
    
    with safety_col2:
        st.markdown("""
        #### Overpressure Protection
        
        **Risks:**
        - Manometer fluid blown out
        - Glass tube breakage
        - Fluid contamination
        
        **Protection Methods:**
        - Pressure relief valves
        - Overflow reservoirs
        - Reinforced tubing
        - Pressure limiters
        - Regular inspection
        """)
    
    with safety_col3:
        st.markdown("""
        #### General Safety
        
        **Best Practices:**
        - Clear labeling of fluid type
        - Secure mounting
        - Protection from impact
        - Regular maintenance
        - Operator training
        - Emergency procedures
        - Documentation
        """)
    
    st.markdown("---")
    
    st.markdown("### Practical Measurement Tips")
    
    st.info("""
    **For Accurate Readings:**
    
    1. **Eliminate Air Bubbles**: Ensure no air is trapped in the connecting tubes or U-tube
    2. **Allow Time to Stabilize**: Wait for fluid levels to stop moving before reading
    3. **Read at Eye Level**: Avoid parallax errors by positioning eye level with meniscus
    4. **Account for Meniscus**: Read from the bottom of the meniscus for mercury, top for water
    5. **Temperature Correction**: Apply density corrections if temperature varies significantly
    6. **Check for Leaks**: Verify all connections are tight and no fluid is leaking
    7. **Vertical Alignment**: Ensure the manometer is mounted truly vertical
    8. **Zero Reference**: Verify the datum reference point is correct
    """)
    
    st.markdown("### Modern Alternatives")
    
    st.markdown("""
    While open-tube manometers remain useful, modern alternatives include:
    
    | Technology | Advantages | When to Use |
    |-----------|-----------|-------------|
    | **Digital Manometers** | Electronic display, data logging, no toxic fluids | When automation or digital recording needed |
    | **Pressure Transducers** | Fast response, remote monitoring, compact | When space limited or rapid response needed |
    | **Magnehelic Gauges** | Direct reading, no liquid, low cost | When measuring small pressure differences |
    | **Smart Pressure Sensors** | Wireless communication, self-calibrating | When IoT integration desired |
    
    However, **open-tube manometers are still preferred** for:
    - Calibration standards (no drift)
    - Teaching and demonstrations (visual understanding)
    - Simple installations (no power required)
    - Backup/verification (independent of electronics)
    """)

# Add a comparison tool at the bottom
st.markdown("---")
st.header("🔧 Quick Comparison Tool")

comp_col1, comp_col2, comp_col3 = st.columns(3)

with comp_col1:
    pressure_to_measure = st.number_input("Pressure to Measure (kPa)", value=10.0, step=1.0)

with comp_col2:
    st.markdown("### Required Heights")
    
    # Calculate for different fluids
    pressure_pa = pressure_to_measure * 1000
    
    h_mercury = pressure_pa / (13600 * 9.81)
    h_water = pressure_pa / (1000 * 9.81)
    h_oil = pressure_pa / (850 * 9.81)
    
    st.write(f"**Mercury**: {h_mercury*100:.1f} cm ({h_mercury:.3f} m)")
    st.write(f"**Water**: {h_water*100:.1f} cm ({h_water:.3f} m)")
    st.write(f"**Oil**: {h_oil*100:.1f} cm ({h_oil:.3f} m)")

with comp_col3:
    st.markdown("### Recommendations")
    
    if pressure_to_measure < 5:
        st.success("✅ Water manometer suitable (< 50 cm height)")
    elif pressure_to_measure < 20:
        st.info("💡 Mercury preferred for compact design")
    else:
        st.warning("⚠️ Consider electronic sensor or high-range manometer")
    
    if h_water > 2.0:
        st.error("❌ Water manometer impractical (> 2 m height)")

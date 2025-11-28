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
st.markdown("<h1 style='text-align: center;'>Interactive U-Tube Manometer (Differential Pressure)</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
This tool demonstrates how a U-tube manometer measures the pressure difference between two points in a pipe or system.
Select a real-world scenario or adjust the parameters manually to see how the manometer fluid levels respond.
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# Create tabs for different aspects
tab1, tab2, tab3 = st.tabs(["🎯 Interactive Simulation", "📚 Understanding Differential Manometers", "📋 Application Examples"])

with tab1:
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
            "Air Duct with Water Manometer": {
                "rho_f": 1.2, "rho_m": 1000.0,
                "desc": "Common setup for measuring small pressure changes in HVAC ventilation systems. High sensitivity due to low fluid density."
            },
            "Water Pipe with Mercury Manometer": {
                "rho_f": 1000.0, "rho_m": 13600.0,
                "desc": "Used for measuring larger pressure differences in water pipes, such as across pumps, filters, or flow restrictions."
            },
            "Natural Gas with Oil Manometer": {
                "rho_f": 0.8, "rho_m": 820.0,
                "desc": "Sensitive setup for measuring low-pressure differences in natural gas distribution systems."
            },
            "Steam Line with Mercury Manometer": {
                "rho_f": 0.6, "rho_m": 13600.0,
                "desc": "High-temperature application measuring pressure drop across steam system components."
            }
        }

        scenario_choice = st.selectbox(
            "Interactive 'What-If' Scenarios",
            options=list(SCENARIOS.keys())
        )
        
        selected_scenario = SCENARIOS[scenario_choice]
        st.info(selected_scenario["desc"])
        
        st.subheader("Fluid Properties")
        rho_f = st.number_input("Density of System Fluid (ρ_system) [kg/m³]", value=selected_scenario["rho_f"], step=0.1, help="The fluid flowing in the pipe (e.g., air, water, gas)")
        rho_m = st.number_input("Density of Manometer Fluid (ρ_mano) [kg/m³]", value=selected_scenario["rho_m"], step=100.0, help="The fluid in the U-tube (e.g., mercury, water, oil)")
        g = st.number_input("Gravity (g) [m/s²]", value=9.81, format="%.2f")

        st.subheader("Manometer Height Control")
        h_cm = st.slider("Height Difference (h) [cm]", min_value=-20.0, max_value=20.0, value=10.0, step=0.5, format="%.1f cm", 
                        help="Positive: P₁ > P₂ (left side higher pressure), Negative: P₁ < P₂ (right side higher pressure)")
        h = h_cm / 100 # Convert cm to meters for calculation
        
        # Add visualization controls
        col_vis1, col_vis2 = st.columns(2)
        with col_vis1:
            show_flow = st.checkbox("Show Flow Direction", value=True)
        with col_vis2:
            show_pressure_values = st.checkbox("Show Pressure Values", value=False)

        # --- Calculation ---
        delta_P = (rho_m - rho_f) * g * h
        delta_P_kPa = delta_P / 1000
        
        # Calculate individual components
        manometer_contribution = rho_m * g * h
        system_contribution = rho_f * g * h
        
        # Additional unit conversions
        delta_P_Pa = delta_P
        delta_P_mbar = delta_P / 100
        delta_P_psi = delta_P / 6894.76

        st.markdown("---")
        st.header("📊 Results Summary")
        
        # Color-coded pressure indicator
        if delta_P_kPa > 0:
            delta_color = "normal"
            interpretation = "P₁ > P₂ (Higher pressure at left)"
            pressure_direction = "→"
        elif delta_P_kPa < 0:
            delta_color = "inverse" 
            interpretation = "P₁ < P₂ (Higher pressure at right)"
            pressure_direction = "←"
        else:
            delta_color = "off"
            interpretation = "P₁ = P₂ (Equal pressures)"
            pressure_direction = "="
        
        st.metric(label="Pressure Difference (P₁ - P₂)", value=f"{delta_P_kPa:,.3f} kPa", 
                 delta=interpretation, delta_color=delta_color)
        
        # Additional units in columns
        col_unit1, col_unit2, col_unit3 = st.columns(3)
        with col_unit1:
            st.metric("In Pascals", f"{delta_P_Pa:,.1f} Pa")
        with col_unit2:
            st.metric("In mbar", f"{delta_P_mbar:.2f} mbar")
        with col_unit3:
            st.metric("In psi", f"{delta_P_psi:.3f} psi")
        
        st.markdown("---")
        st.header("🧮 Step-by-Step Calculation")
        
        with st.expander("📖 See Detailed Breakdown", expanded=False):
            st.markdown("### Pressure Balance Equation")
            st.markdown("At the datum level (lower interface in both limbs), pressures must be equal:")
            st.latex(r'P_1 + \rho_{sys} g a = P_2 + \rho_{sys} g (a-h) + \rho_{mano} g h')
            
            st.markdown("where 'a' is the height of system fluid column above datum on the left side.")
            
            st.markdown("### Step 1: Expand and Simplify")
            st.latex(r'P_1 + \rho_{sys} g a = P_2 + \rho_{sys} g a - \rho_{sys} g h + \rho_{mano} g h')
            
            st.markdown("The ρ_sys·g·a terms cancel out:")
            st.latex(r'P_1 = P_2 - \rho_{sys} g h + \rho_{mano} g h')
            
            st.markdown("### Step 2: Rearrange for Pressure Difference")
            st.latex(r'P_1 - P_2 = (\rho_{mano} - \rho_{sys}) g h')
            
            st.markdown("### Step 3: Calculate Manometer Fluid Contribution")
            st.write(f"**Manometer fluid pressure:** ρ_mano × g × h")
            st.write(f"= {rho_m} × {g} × {h}")
            st.write(f"= **{manometer_contribution:,.2f} Pa** = **{manometer_contribution/1000:.3f} kPa**")
            
            st.markdown("### Step 4: Calculate System Fluid Contribution")
            st.write(f"**System fluid pressure:** ρ_sys × g × h")
            st.write(f"= {rho_f} × {g} × {h}")
            st.write(f"= **{system_contribution:,.2f} Pa** = **{system_contribution/1000:.3f} kPa**")
            
            st.markdown("### Step 5: Calculate Net Pressure Difference")
            st.write(f"**ΔP = (ρ_mano - ρ_sys) × g × h**")
            st.write(f"ΔP = ({rho_m} - {rho_f}) × {g} × {h}")
            st.write(f"ΔP = **{delta_P:,.2f} Pa** = **{delta_P_kPa:.3f} kPa**")
            
            # Physical interpretation
            st.markdown("### Physical Interpretation")
            if delta_P > 0:
                st.success(f"✅ Point P₁ is at **{delta_P_kPa:.3f} kPa higher** pressure than P₂")
                st.info("The fluid in the left limb is pushed down by the higher pressure, raising the right limb.")
            elif delta_P < 0:
                st.success(f"✅ Point P₂ is at **{abs(delta_P_kPa):.3f} kPa higher** pressure than P₁")
                st.info("The fluid in the right limb is pushed down by the higher pressure, raising the left limb.")
            else:
                st.info("ℹ️ Points P₁ and P₂ are at equal pressure (no pressure difference)")
        
        st.markdown("---")
        st.header("🔍 Analysis Insights")
        
        with st.expander("💡 Pressure Components Analysis", expanded=False):
            st.markdown("**Understanding the (ρ_mano - ρ_sys) Factor:**")
            
            density_difference = rho_m - rho_f
            st.write(f"• Density difference: {density_difference:.1f} kg/m³")
            st.write(f"• Manometer fluid contribution: +{manometer_contribution/1000:.3f} kPa")
            st.write(f"• System fluid counteraction: -{system_contribution/1000:.3f} kPa")
            st.write(f"• **Net pressure difference**: {delta_P_kPa:.3f} kPa")
            
            # Analyze the significance of system fluid
            if rho_f < rho_m * 0.01:  # System fluid < 1% of manometer fluid
                st.info("💡 **System fluid effect negligible**: The low density of system fluid (gas) means it barely affects the reading. The manometer acts almost as if there's a vacuum above the manometer fluid.")
            elif rho_f > rho_m * 0.5:  # System fluid > 50% of manometer fluid
                st.warning("⚠️ **System fluid effect significant**: The system fluid density is substantial compared to the manometer fluid. This reduces sensitivity but makes the measurement more stable.")
            else:
                st.info("💡 **Moderate system fluid effect**: The system fluid provides some counterbalance, reducing the net reading compared to what the manometer fluid height alone would indicate.")
            
            # Sensitivity analysis
            sensitivity = 1 / ((rho_m - rho_f) * g) if (rho_m - rho_f) > 0 else 0
            st.markdown(f"**Sensitivity:** {sensitivity*1000:.4f} m/kPa")
            st.caption("How much the manometer reading changes per unit pressure difference")

        with st.expander("🎯 Measurement Characteristics", expanded=False):
            st.markdown("**Key Performance Indicators:**")
            
            # Range calculation
            max_readable_h = 0.5  # meters, practical limit
            max_pressure = (rho_m - rho_f) * g * max_readable_h / 1000
            st.write(f"• **Practical measuring range**: 0 to ±{max_pressure:.1f} kPa")
            st.write(f"  (Based on maximum readable height of ±{max_readable_h*100} cm)")
            
            # Resolution
            reading_resolution = 0.001  # 1 mm = 0.001 m
            pressure_resolution = (rho_m - rho_f) * g * reading_resolution
            st.write(f"• **Pressure resolution**: {pressure_resolution:.2f} Pa")
            st.write(f"  (Assuming minimum readable height of 1 mm)")
            
            # Response time estimate
            if rho_f < 10:  # Gas
                response_category = "Fast (~1-3 seconds)"
                response_note = "Gas systems equilibrate quickly"
            else:  # Liquid
                response_category = "Moderate (~5-15 seconds)"
                response_note = "Liquid inertia slows response"
            st.write(f"• **Estimated response time**: {response_category}")
            st.caption(response_note)
            
            st.markdown("**Application Suitability:**")
            if scenario_choice == "Air Duct with Water Manometer":
                st.success("✅ Excellent for HVAC applications. High sensitivity for low-pressure measurements. Safe, non-toxic fluid.")
            elif scenario_choice == "Water Pipe with Mercury Manometer":
                st.success("✅ Ideal for water systems with moderate to high pressure drops. Compact due to mercury's high density.")
                st.warning("⚠️ Requires careful handling due to mercury toxicity.")
            elif scenario_choice == "Natural Gas with Oil Manometer":
                st.success("✅ Good for low-pressure gas systems. Safer than mercury with reasonable sensitivity.")
            elif scenario_choice == "Steam Line with Mercury Manometer":
                st.warning("⚠️ High-temperature application requires special materials and careful installation.")

        with st.expander("⚖️ Comparison with Open Manometer", expanded=False):
            st.markdown("**Key Differences:**")
            
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                st.markdown("**Differential (U-Tube) Manometer:**")
                st.write("✅ Measures pressure *difference* (P₁ - P₂)")
                st.write("✅ Both ends connected to system")
                st.write("✅ Independent of atmospheric pressure")
                st.write("✅ Ideal for measuring pressure drops")
                st.write("✅ Used across: pumps, filters, flow meters")
                st.latex(r'\Delta P = (\rho_m - \rho_f) g h')
            
            with col_comp2:
                st.markdown("**Open Manometer:**")
                st.write("✅ Measures *gauge* pressure (P - P_atm)")
                st.write("✅ One end open to atmosphere")
                st.write("✅ Reference is atmospheric pressure")
                st.write("✅ Ideal for measuring absolute system pressure")
                st.write("✅ Used for: tank pressure, vessel pressure")
                st.latex(r'P_{gauge} = \rho_m g h - \rho_f g b')
            
            st.info("💡 **When to use differential manometer**: When you need to measure pressure *change* across a component (pump, valve, orifice, filter). When to use open manometer: When you need to know the *absolute* pressure in a vessel or tank.")

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
        def generate_manometer_plot(h_inst, show_flow_arrows, show_p_values):
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
                pipe_y - pipe_radius + 0.01, bend_y_center + tube_outer_radius + 0.01,
                bend_y_center + tube_outer_radius + 0.01, tube_top_y,
                tube_top_y, bend_y_center + tube_outer_radius,
                bend_y_center + tube_outer_radius, tube_top_y,
                pipe_y - pipe_radius + 0.01, bend_y_center + tube_outer_radius,
                bend_y_center + tube_outer_radius, pipe_y - pipe_radius + 0.01
            ]
            fig.add_trace(go.Scatter(x=conn_left_points_x, y=conn_left_points_y, 
                                    fill="toself", fillcolor=glass_color, 
                                    mode='none', hoverinfo='none'))
            
            # Right connecting tube
            conn_right_points_x = [
                conn_right_x - conn_tube_outer_radius, conn_right_x - conn_tube_outer_radius,
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
            
            # Show pressure values if enabled (main result display matching Capillary Rise style)
            if show_p_values:
                # Calculate instantaneous pressure difference
                delta_P_inst = (rho_m - rho_f) * g * h_inst
                delta_P_kPa_inst = delta_P_inst / 1000
                
                # Result label at top of visualization
                if delta_P_kPa_inst > 0:
                    result_text = f"<b>ΔP (P₁ - P₂): {delta_P_kPa_inst:.3f} kPa</b>"
                    bg_color = "rgba(0, 100, 200, 0.9)"
                    border_color = "darkblue"
                elif delta_P_kPa_inst < 0:
                    result_text = f"<b>ΔP (P₁ - P₂): {delta_P_kPa_inst:.3f} kPa</b>"
                    bg_color = "rgba(200, 100, 0, 0.9)"
                    border_color = "darkorange"
                else:
                    result_text = f"<b>ΔP (P₁ - P₂): 0.000 kPa</b>"
                    bg_color = "rgba(100, 100, 100, 0.9)"
                    border_color = "gray"
                
                fig.add_annotation(
                    x=0,
                    y=fixed_yaxis_range[1] - 0.02,
                    text=result_text,
                    showarrow=False,
                    font=dict(size=20, color="white"),
                    bgcolor=bg_color,
                    bordercolor=border_color,
                    borderwidth=2,
                    borderpad=8
                )
            
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
                fig = generate_manometer_plot(intermediate_h, show_flow, show_pressure_values)
                plot_placeholder.plotly_chart(fig, use_container_width=True)
                time.sleep(0.02)
        else:
            fig = generate_manometer_plot(end_h, show_flow, show_pressure_values)
            plot_placeholder.plotly_chart(fig, use_container_width=True)
        
        st.session_state.previous_h_mano = end_h

with tab2:
    st.header("📚 Understanding Differential Manometers")
    
    col_edu1, col_edu2 = st.columns([1, 1])
    
    with col_edu1:
        st.markdown("""
        ### What is a Differential Manometer?
        
        A differential manometer (U-tube type) measures the **pressure difference** between two points 
        in a flowing system. Unlike an open manometer (which measures gauge pressure), both ends are 
        connected to the system.
        
        ### How It Works
        
        1. **Two pressure taps** connect to points P₁ and P₂ in the system
        2. **U-tube contains** a manometer fluid (usually denser than system fluid)
        3. **Pressure difference** causes the manometer fluid to rise on one side
        4. **Height difference (h)** indicates the pressure difference
        
        ### Key Principle: Pressure Balance
        
        At the datum level (lower interface in both limbs), pressures must be equal:
        """)
        
        st.latex(r'P_1 + \rho_{sys} g a = P_2 + \rho_{sys} g (a-h) + \rho_{mano} g h')
        
        st.markdown("""
        After simplification, this gives us:
        """)
        
        st.latex(r'P_1 - P_2 = (\rho_{mano} - \rho_{sys}) g h')
        
        st.markdown("""
        This is the **fundamental equation** for differential manometers.
        """)
    
    with col_edu2:
        st.markdown("""
        ### Why (ρ_mano - ρ_sys)?
        
        The key insight is that **both fluids contribute** to the pressure balance:
        
        - **Manometer fluid** (heavier): Creates pressure proportional to ρ_mano·g·h
        - **System fluid** (lighter): Counteracts with pressure ρ_sys·g·h
        - **Net effect**: Only the density *difference* matters
        
        ### Special Cases
        
        **When system fluid is a gas (ρ_sys ≈ 0):**
        - ρ_mano - ρ_sys ≈ ρ_mano
        - Formula simplifies to: ΔP ≈ ρ_mano·g·h
        - System fluid has negligible effect
        
        **When densities are similar:**
        - Small density difference → High sensitivity
        - Large height change for small ΔP
        - Good for low-pressure measurements
        
        **When ρ_mano >> ρ_sys:**
        - Large density difference → Low sensitivity  
        - Compact design, wider range
        - Good for high-pressure measurements
        """)
    
    st.markdown("---")
    
    st.markdown("### Reading the Manometer")
    
    reading_col1, reading_col2, reading_col3 = st.columns(3)
    
    with reading_col1:
        st.markdown("""
        #### Positive Reading (h > 0)
        
        - **Left limb lower** than right
        - P₁ **greater than** P₂
        - Pressure **decreases** left to right
        - Common: downstream of restrictions
        
        **Examples:**
        - After a pump (pressure boost)
        - Entering a restriction (orifice)
        - Higher elevation upstream
        """)
    
    with reading_col2:
        st.markdown("""
        #### Negative Reading (h < 0)
        
        - **Right limb lower** than left
        - P₂ **greater than** P₁
        - Pressure **increases** left to right
        - Unusual but possible
        
        **Examples:**
        - Reverse flow conditions
        - Downstream of a pump
        - Lower elevation upstream
        """)
    
    with reading_col3:
        st.markdown("""
        #### Zero Reading (h = 0)
        
        - **Both limbs equal** height
        - P₁ **equals** P₂
        - No pressure difference
        - System balanced
        
        **Indicates:**
        - No flow (static condition)
        - Perfectly balanced system
        - Zero pressure drop
        """)
    
    st.markdown("---")
    
    st.markdown("### Manometer Fluid Selection")
    
    st.markdown("""
    The choice of manometer fluid is critical for accurate measurements:
    """)
    
    fluid_col1, fluid_col2 = st.columns(2)
    
    with fluid_col1:
        st.markdown("""
        #### For Gas/Air Systems (ρ_sys ≈ 1-2 kg/m³):
        
        | Fluid | Density | Best For |
        |-------|---------|----------|
        | **Water** | 1000 kg/m³ | Low pressures, high sensitivity, HVAC |
        | **Light Oil** | 800-900 kg/m³ | Slightly lower sensitivity, cleaner than water |
        | **Mercury** | 13,600 kg/m³ | High pressures, compact design, lab use |
        
        **Recommendation**: Water for HVAC and low-pressure work; mercury only when space is limited.
        """)
    
    with fluid_col2:
        st.markdown("""
        #### For Liquid Systems (ρ_sys ≈ 800-1000 kg/m³):
        
        | Fluid | Density | Best For |
        |-------|---------|----------|
        | **Mercury** | 13,600 kg/m³ | Water/oil systems, industrial standard |
        | **Tetrabromoethane** | 2950 kg/m³ | Medium range, less toxic than mercury |
        | **Carbon Tetrachloride** | 1590 kg/m³ | Low density difference, high sensitivity |
        
        **Recommendation**: Mercury is standard for water systems despite toxicity concerns; alternatives exist for safety-critical applications.
        """)
    
    st.markdown("---")
    
    st.markdown("### Advantages & Limitations")
    
    adv_col1, adv_col2 = st.columns(2)
    
    with adv_col1:
        st.success("""
        **Advantages:**
        - ✅ **Direct measurement** - no calibration needed
        - ✅ **Visual indication** - immediate reading
        - ✅ **No power required** - purely mechanical
        - ✅ **Highly reliable** - few failure modes
        - ✅ **Accurate** - based on fundamental principles
        - ✅ **Wide pressure range** - selectable by fluid choice
        - ✅ **Low cost** - simple construction
        - ✅ **Independent** - not affected by electrical noise
        """)
    
    with adv_col2:
        st.warning("""
        **Limitations:**
        - ⚠️ **Slow response** - takes time to stabilize
        - ⚠️ **Not for fluctuating** pressures - averages over time
        - ⚠️ **Bulky** - requires vertical space
        - ⚠️ **Mercury hazard** - toxicity and disposal concerns
        - ⚠️ **Temperature sensitive** - density changes with temperature
        - ⚠️ **Fragile** - glass tubes can break
        - ⚠️ **Installation critical** - must be truly vertical
        - ⚠️ **Limited range** - constrained by tube length
        """)

with tab3:
    st.header("📋 Real-World Applications")
    
    st.markdown("""
    Differential manometers are essential instruments across many industries for measuring pressure 
    drops, which indicate flow rates, filter conditions, and equipment performance.
    """)
    
    app_col1, app_col2 = st.columns(2)
    
    with app_col1:
        st.markdown("""
        ### Primary Applications
        
        **1. Orifice Plate Flow Measurement**
        - Most common application
        - Measures pressure drop across orifice
        - Flow rate calculated from ΔP
        - Standard in process industries
        - *Typical fluids: Water manometer for gas, mercury for liquids*
        
        **2. Venturi Meter**
        - More accurate than orifice plate
        - Lower permanent pressure loss
        - Measures throat pressure vs. inlet
        - Used for custody transfer
        - *Typical fluids: Mercury or water depending on system*
        
        **3. Filter Pressure Drop**
        - Indicates filter loading/clogging
        - Triggers maintenance when ΔP exceeds limit
        - Critical for air handling systems
        - Common in clean rooms
        - *Typical fluids: Water for air systems*
        
        **4. Pump Performance Testing**
        - Measures pressure rise across pump
        - Verifies pump curve
        - Detects pump degradation
        - Essential for maintenance
        - *Typical fluids: Mercury for water pumps*
        """)
    
    with app_col2:
        st.markdown("""
        ### Industrial Examples
        
        **5. Heat Exchanger Monitoring**
        - Shell-side or tube-side pressure drop
        - Indicates fouling or blockage
        - Maintenance planning tool
        - Performance verification
        - *Typical fluids: Mercury*
        
        **6. Duct Systems (HVAC)**
        - Static pressure measurements
        - Damper balancing
        - Fan performance verification
        - Air handler testing
        - *Typical fluids: Water or colored alcohol*
        
        **7. Packed Bed/Catalyst Reactors**
        - Measures bed pressure drop
        - Indicates catalyst deterioration
        - Detects channeling
        - Operating limit monitoring
        - *Typical fluids: Mercury*
        
        **8. Pitot-Static Tube**
        - Velocity measurement in pipes/ducts
        - Combination with differential manometer
        - Flow profiling
        - Stack velocity testing
        - *Typical fluids: Water or mercury*
        """)
    
    st.markdown("---")
    
    st.markdown("### Case Study: Orifice Plate Flow Meter")
    
    case_col1, case_col2, case_col3 = st.columns(3)
    
    with case_col1:
        st.markdown("""
        #### Setup
        - **System**: Natural gas pipeline
        - **Pipe diameter**: 100 mm
        - **Orifice diameter**: 50 mm (β = 0.5)
        - **Manometer fluid**: Water
        - **Gas density**: 0.8 kg/m³
        """)
    
    with case_col2:
        st.markdown("""
        #### Reading
        - **Observed h**: 25 cm
        - **ΔP calculated**: 2.44 kPa
        - **Flow coefficient**: 0.61
        - **Pipe area**: 0.00785 m²
        """)
    
    with case_col3:
        st.markdown("""
        #### Result
        - **Flow rate**: ~125 m³/h
        - **Velocity**: ~4.4 m/s
        - **Reynolds number**: ~55,000
        - **Regime**: Turbulent ✓
        """)
    
    st.info("💡 **Key insight**: Water manometer provides excellent sensitivity for gas flow measurement. The 25 cm reading is easily readable and corresponds to a reasonable flow velocity.")
    
    st.markdown("---")
    
    st.markdown("### Safety & Best Practices")
    
    safety_col1, safety_col2, safety_col3 = st.columns(3)
    
    with safety_col1:
        st.markdown("""
        #### Installation
        
        **Critical Points:**
        - Mount truly vertical (check with level)
        - Secure firmly to prevent vibration
        - Protect from temperature extremes
        - Provide adequate lighting for reading
        - Install shut-off valves for isolation
        - Include drain/fill ports
        
        **Common Mistakes:**
        - ❌ Tilted installation
        - ❌ Exposed to direct sunlight
        - ❌ Vibration from nearby equipment
        - ❌ Inaccessible location
        """)
    
    with safety_col2:
        st.markdown("""
        #### Operation
        
        **Best Practices:**
        - Fill slowly to avoid air bubbles
        - Bleed air from high points
        - Allow time to stabilize before reading
        - Read at eye level (avoid parallax)
        - Read from meniscus bottom (mercury)
        - Read from meniscus top (water)
        - Record temperature for corrections
        
        **Maintenance:**
        - Check fluid level monthly
        - Clean glass tubes regularly
        - Verify zero reading periodically
        - Inspect for leaks
        """)
    
    with safety_col3:
        st.markdown("""
        #### Mercury Safety
        
        **If Using Mercury:**
        - ⚠️ Use in ventilated area
        - ⚠️ Spill containment trays required
        - ⚠️ PPE: gloves, safety glasses
        - ⚠️ Mercury vapor monitor nearby
        - ⚠️ Emergency spill kit available
        - ⚠️ Proper disposal procedures
        - ⚠️ Training required for operators
        
        **Alternatives:**
        - Consider digital manometers
        - Use water where feasible
        - Evaluate non-toxic fluids
        - Pressure transducers for permanent installations
        """)
    
    st.markdown("---")
    
    st.markdown("### Troubleshooting Common Issues")
    
    ts_col1, ts_col2 = st.columns(2)
    
    with ts_col1:
        st.markdown("""
        | Problem | Cause | Solution |
        |---------|-------|----------|
        | **Erratic readings** | Air bubbles in fluid | Bleed air from system |
        | **Reading drifts** | Temperature change | Allow thermal equilibration |
        | **No reading** | Taps plugged | Clean pressure taps |
        | **Reading too high** | System fluid in manometer | Drain and refill correctly |
        | **Slow response** | Restriction in connecting tubes | Check for blockages |
        """)
    
    with ts_col2:
        st.markdown("""
        | Problem | Cause | Solution |
        |---------|-------|----------|
        | **Oscillating levels** | Flow pulsations | Add dampening reservoir |
        | **Asymmetric levels** | Tube not vertical | Re-level installation |
        | **Fluid contaminated** | System leakage | Replace manometer fluid |
        | **Reading reversed** | Connections swapped | Verify tap locations |
        | **Meniscus unclear** | Dirty glass | Clean with appropriate solvent |
        """)
    
    st.markdown("---")
    
    st.markdown("### Modern Alternatives & When to Use Them")
    
    st.markdown("""
    While U-tube manometers remain valuable, consider these alternatives:
    """)
    
    alt_col1, alt_col2 = st.columns(2)
    
    with alt_col1:
        st.markdown("""
        **When to Keep Using U-Tube Manometers:**
        - ✅ Calibration/verification of other instruments
        - ✅ Teaching and demonstrations
        - ✅ Low-budget installations
        - ✅ No power available
        - ✅ Harsh electrical environments
        - ✅ Need for visual confirmation
        - ✅ Permanent low-pressure installations
        """)
    
    with alt_col2:
        st.markdown("""
        **When to Switch to Alternatives:**
        - Digital differential pressure gauges: fast response needed
        - Pressure transducers: remote monitoring required
        - Differential pressure transmitters: automation/control
        - Smart sensors: data logging and analysis
        - Magnehelic gauges: portable field use
        - Micromanometers: very low pressures (<1 Pa)
        """)

# Add a practical calculator at the bottom
st.markdown("---")
st.header("🧮 Quick Differential Pressure Calculator")

calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)

with calc_col1:
    calc_h = st.number_input("Height Reading h (cm)", value=15.0, step=1.0)
    calc_rho_m = st.number_input("ρ_manometer (kg/m³)", value=13600.0, step=100.0)

with calc_col2:
    calc_rho_f = st.number_input("ρ_system (kg/m³)", value=1000.0, step=10.0)
    calc_g = st.number_input("g (m/s²)", value=9.81, format="%.2f")

with calc_col3:
    calc_dp = (calc_rho_m - calc_rho_f) * calc_g * (calc_h/100)
    st.metric("ΔP (kPa)", f"{calc_dp/1000:.3f}")
    st.metric("ΔP (psi)", f"{calc_dp/6894.76:.3f}")

with calc_col4:
    st.metric("ΔP (Pa)", f"{calc_dp:.1f}")
    st.metric("ΔP (mbar)", f"{calc_dp/100:.2f}")

st.caption("💡 **Tip**: Use this calculator to quickly check pressure differences for different manometer configurations before installation.")

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(page_title="Interactive Pitot-Static Tube", layout="wide")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>✈️ Interactive Pitot-Static Tube Velocity Measurement</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
Explore how a Pitot-static tube measures flow velocity by comparing stagnation and static pressures.
Adjust the manometer height to see how it relates to flow velocity through Bernoulli's equation.
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# Create tabs for different aspects
tab1, tab2, tab3 = st.tabs(["🎯 Interactive Simulation", "📚 Understanding Pitot-Static Tubes", "📋 Real-World Applications"])

with tab1:
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
                "desc": "Standard conditions for aircraft speed measurement at sea level. Air density: 1.225 kg/m³"
            },
            "Aircraft at 10,000 ft": {
                "rho_f": 0.905, "rho_m": 1000.0, "altitude": 3048,
                "desc": "Typical cruising altitude for small aircraft. Reduced air density requires correction."
            },
            "Aircraft at 30,000 ft": {
                "rho_f": 0.458, "rho_m": 1000.0, "altitude": 9144,
                "desc": "Commercial jet cruising altitude. Very low air density, significant compressibility effects."
            },
            "Wind Tunnel Testing": {
                "rho_f": 1.2, "rho_m": 850.0, "altitude": 0,
                "desc": "Low-speed wind tunnel with oil manometer for precise, sensitive measurements."
            },
            "Water Flow Measurement": {
                "rho_f": 1000.0, "rho_m": 13600.0, "altitude": 0,
                "desc": "Measuring water velocity in pipes using mercury manometer. Common in hydraulics labs."
            },
            "HVAC Duct Airflow": {
                "rho_f": 1.18, "rho_m": 1000.0, "altitude": 0,
                "desc": "Measuring air velocity in ventilation ducts for HVAC system balancing."
            },
            "Supersonic Wind Tunnel": {
                "rho_f": 1.225, "rho_m": 1000.0, "altitude": 0,
                "desc": "High-speed testing. Compressibility effects are critical (Mach > 0.3)."
            }
        }
        
        scenario = st.selectbox("Select Application Scenario", list(SCENARIOS.keys()))
        selected = SCENARIOS[scenario]
        st.info(selected["desc"])
        
        st.subheader("Fluid Properties")
        col_1, col_2 = st.columns(2)
        with col_1:
            rho_f = st.number_input("Flow Fluid Density ρ_f (kg/m³)", 
                                   value=selected["rho_f"], min_value=0.1, step=0.1, format="%.3f",
                                   help="Density of the fluid being measured (air, water, etc.)")
        with col_2:
            rho_m = st.number_input("Manometer Fluid ρ_m (kg/m³)", 
                                   value=selected["rho_m"], min_value=100.0, step=10.0, format="%.1f",
                                   help="Density of fluid in the U-tube manometer")
        
        g = 9.81
        altitude = selected.get("altitude", 0)
        
        # Temperature effects on air density
        if scenario != "Custom...":
            temp_c = st.slider("Temperature (°C)", -40, 50, 15, 
                              help="Temperature affects air density via ideal gas law")
            # Adjust air density for temperature (if flow fluid is air-like)
            if rho_f < 10:  # Likely a gas
                T_kelvin = temp_c + 273.15
                rho_f_adjusted = rho_f * (288.15 / T_kelvin)  # Ideal gas law adjustment
                if abs(rho_f_adjusted - rho_f) > 0.001:
                    st.caption(f"Temperature-adjusted density: {rho_f_adjusted:.3f} kg/m³")
                    rho_f = rho_f_adjusted
        
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
        U_fps = U * 3.281
        
        # Dynamic pressure
        q = 0.5 * rho_f * U**2
        
        # Additional parameters
        show_calibration = st.checkbox("Show Calibration Factor", value=False,
                                       help="Real Pitot tubes have a calibration coefficient")
        if show_calibration:
            C_pitot = st.slider("Pitot Tube Coefficient C", 0.90, 1.10, 1.00, step=0.01,
                               help="Accounts for viscous effects and probe geometry")
            U_corrected = U * C_pitot
        else:
            C_pitot = 1.0
            U_corrected = U
        
        # Visualization options
        col_vis1, col_vis2, col_vis3 = st.columns(3)
        with col_vis1:
            show_streamlines = st.checkbox("Show Streamlines", value=True)
        with col_vis2:
            show_pressure = st.checkbox("Show Pressure Field", value=False)
        with col_vis3:
            show_details = st.checkbox("Show Probe Details", value=True)
        
        st.markdown("---")
        st.header("📊 Results Summary")
        
        # Display results in metric format
        st.metric("Flow Velocity (U)", f"{U:.2f} m/s", 
                 delta=f"{U_kmh:.1f} km/h" if rho_f < 10 else f"{U_fps:.2f} ft/s")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("Pressure Difference", f"{delta_P/1000:.3f} kPa")
        with col_r2:
            st.metric("Dynamic Pressure q", f"{q/1000:.3f} kPa")
        with col_r3:
            if "Aircraft" in scenario:
                st.metric("Airspeed", f"{U_knots:.1f} knots")
            else:
                st.metric("Velocity", f"{U_kmh:.1f} km/h")
        
        # Additional useful metrics
        col_r4, col_r5, col_r6 = st.columns(3)
        with col_r4:
            if rho_f < 10:  # Gas flow
                Mach = U / 340.29  # Speed of sound at 15°C
                st.metric("Mach Number", f"{Mach:.3f}")
            else:
                st.metric("In ft/s", f"{U_fps:.2f}")
        with col_r5:
            # Approximate Reynolds number (assuming 10 mm probe diameter)
            D_probe = 0.01  # m
            if rho_f < 10:
                mu = 1.8e-5  # Pa·s for air
            else:
                mu = 1.0e-3  # Pa·s for water
            Re = rho_f * U * D_probe / mu if mu > 0 else 0
            st.metric("Reynolds Number", f"{Re:.0e}")
        with col_r6:
            if rho_f < 10:
                st.metric("In mph", f"{U_mph:.1f}")
            else:
                st.metric("In m/s", f"{U:.2f}")
        
        st.markdown("---")
        st.header("🧮 Step-by-Step Calculation")
        
        with st.expander("📖 See Detailed Breakdown", expanded=False):
            st.markdown("### Bernoulli's Equation Applied")
            st.markdown("The Pitot-static tube measures velocity by comparing stagnation and static pressures:")
            st.latex(r'P_{static} + \frac{1}{2}\rho U^2 = P_{stagnation}')
            
            st.markdown("### Step 1: Define Pressure Difference")
            st.markdown("The difference between stagnation and static pressure:")
            st.latex(r'\Delta P = P_{stag} - P_{static} = \frac{1}{2}\rho U^2')
            st.write("This pressure difference is the **dynamic pressure (q)**")
            
            st.markdown("### Step 2: Measure with Manometer")
            st.markdown("The U-tube manometer converts pressure difference to height:")
            st.latex(r'\Delta P = \rho_m g h')
            st.write(f"ΔP = {rho_m} kg/m³ × {g} m/s² × {h_mano} m")
            st.write(f"ΔP = **{delta_P:.2f} Pa** = **{delta_P/1000:.3f} kPa**")
            
            st.markdown("### Step 3: Equate Pressure Relations")
            st.markdown("Set the two expressions for ΔP equal:")
            st.latex(r'\rho_m g h = \frac{1}{2}\rho_f U^2')
            
            st.markdown("### Step 4: Solve for Velocity")
            st.markdown("Rearrange to solve for flow velocity U:")
            st.latex(r'U = \sqrt{\frac{2 \rho_m g h}{\rho_f}}')
            st.write(f"U = √[(2 × {rho_m} × {g} × {h_mano}) / {rho_f}]")
            st.write(f"U = √[{2 * rho_m * g * h_mano:.2f} / {rho_f}]")
            st.write(f"U = √{2 * rho_m * g * h_mano / rho_f:.2f}")
            st.write(f"U = **{U:.2f} m/s**")
            
            st.markdown("### Step 5: Apply Calibration (if needed)")
            if show_calibration:
                st.latex(r'U_{actual} = C \times U_{theoretical}')
                st.write(f"U_actual = {C_pitot} × {U:.2f}")
                st.write(f"U_actual = **{U_corrected:.2f} m/s**")
            
            st.markdown("### Step 6: Calculate Dynamic Pressure")
            st.markdown("Dynamic pressure represents the kinetic energy per unit volume:")
            st.latex(r'q = \frac{1}{2}\rho U^2')
            st.write(f"q = 0.5 × {rho_f} × {U:.2f}²")
            st.write(f"q = **{q:.2f} Pa** = **{q/1000:.3f} kPa**")
            
            # Physical interpretation
            st.markdown("### Physical Interpretation")
            if U > 0:
                if rho_f < 10:  # Gas
                    Mach = U / 340.29
                    if Mach < 0.3:
                        st.success(f"✅ **Subsonic incompressible flow**: Velocity = {U:.2f} m/s ({U_knots:.1f} knots). Bernoulli equation is accurate.")
                    elif Mach < 0.8:
                        st.warning(f"⚠️ **Subsonic compressible flow**: Mach = {Mach:.2f}. Compressibility corrections needed for high accuracy.")
                    elif Mach < 1.2:
                        st.error(f"❌ **Transonic flow**: Mach = {Mach:.2f}. Standard Pitot-static tube readings unreliable. Use supersonic probe.")
                    else:
                        st.error(f"❌ **Supersonic flow**: Mach = {Mach:.2f}. Shock waves present. Requires supersonic Pitot probe and isentropic relations.")
                else:  # Liquid
                    st.success(f"✅ **Liquid flow**: Velocity = {U:.2f} m/s. Incompressible flow, Bernoulli equation is accurate.")
                
                # Reynolds number interpretation
                if Re < 1000:
                    st.info("💡 Low Reynolds number: Laminar flow, viscous effects significant")
                elif Re < 10000:
                    st.info("💡 Moderate Reynolds number: Transitional flow regime")
                else:
                    st.info("💡 High Reynolds number: Turbulent flow, inertial forces dominate")
        
        st.markdown("---")
        st.header("🔍 Analysis Insights")
        
        with st.expander("💡 Sensitivity Analysis", expanded=False):
            st.markdown("**How parameters affect the measurement:**")
            
            # Manometer fluid effect
            st.markdown("#### 1. Manometer Fluid Density (ρ_m)")
            st.write(f"• Current value: {rho_m} kg/m³")
            
            # Calculate for different manometer fluids
            h_needed_water = (0.5 * rho_f * U**2) / (1000 * g) * 100 if U > 0 else 0  # cm
            h_needed_mercury = (0.5 * rho_f * U**2) / (13600 * g) * 100 if U > 0 else 0  # cm
            h_needed_oil = (0.5 * rho_f * U**2) / (850 * g) * 100 if U > 0 else 0  # cm
            
            st.write(f"**For current velocity ({U:.2f} m/s):**")
            st.write(f"• Water manometer: {h_needed_water:.2f} cm")
            st.write(f"• Oil manometer: {h_needed_oil:.2f} cm")
            st.write(f"• Mercury manometer: {h_needed_mercury:.2f} cm")
            
            if rho_f < 10:  # Gas flow
                st.info("💡 For gas flow, water manometers provide good sensitivity. Mercury gives more compact readings but less sensitivity.")
            else:
                st.info("💡 For liquid flow, mercury is standard to avoid very large manometer heights.")
            
            # Flow density effect
            st.markdown("#### 2. Flow Fluid Density (ρ_f)")
            st.write(f"• Current value: {rho_f:.3f} kg/m³")
            st.write(f"• Effect: U ∝ 1/√ρ_f")
            
            if rho_f < 1:
                st.warning("⚠️ Very low density (high altitude or hot gas): Velocity is high for given ΔP. Ensure probe can handle high speeds.")
            elif rho_f < 10:
                st.success("✅ Gas flow: Standard Pitot-static tube works well for subsonic speeds.")
            else:
                st.info("💡 Liquid flow: Lower velocities for same ΔP. More robust measurement.")
            
            # Temperature effect (for gases)
            if rho_f < 10:
                st.markdown("#### 3. Temperature Effect on Air Density")
                if 'temp_c' in locals():
                    st.write(f"• Current temperature: {temp_c}°C")
                
                    # Show density at different temperatures
                    temps = [-20, 0, 20, 40]
                    st.write("**Air density at different temperatures:**")
                    for T in temps:
                        T_K = T + 273.15
                        rho_at_T = 1.225 * (288.15 / T_K)
                        st.write(f"• {T}°C: ρ = {rho_at_T:.3f} kg/m³")
                    
                    st.info("💡 For accurate measurements, always correct for actual temperature or use temperature-compensated instruments.")
            
            # Manometer height sensitivity
            st.markdown("#### 4. Measurement Resolution")
            
            # Minimum readable height
            h_min = 0.001  # 1 mm
            delta_P_min = rho_m * g * h_min
            U_min = np.sqrt(2 * delta_P_min / rho_f) if rho_f > 0 else 0
            
            st.write(f"• Minimum readable manometer height: 1 mm")
            st.write(f"• Corresponding velocity resolution: {U_min:.3f} m/s")
            
            if U_min > 0.5:
                st.warning("⚠️ Low resolution for low velocities. Consider more sensitive manometer or transducer.")
            else:
                st.success("✅ Good resolution for measuring range.")

        with st.expander("⚖️ Accuracy & Error Sources", expanded=False):
            st.markdown("**Factors affecting measurement accuracy:**")
            
            col_err1, col_err2 = st.columns(2)
            
            with col_err1:
                st.markdown("#### Systematic Errors")
                
                st.write("**1. Probe Alignment**")
                alignment_error = st.slider("Misalignment Angle (°)", 0, 30, 5, key="align_err")
                error_factor = np.cos(np.radians(alignment_error))
                velocity_error = (1 - error_factor) * 100
                st.write(f"• Velocity error: -{velocity_error:.1f}%")
                st.caption("Misalignment reduces measured stagnation pressure")
                
                st.write("**2. Calibration Coefficient**")
                st.write(f"• Typical range: 0.98 - 1.01")
                st.write(f"• Current C: {C_pitot}")
                if C_pitot != 1.0:
                    st.write(f"• Corrected velocity: {U_corrected:.2f} m/s")
                
                st.write("**3. Compressibility Effects**")
                if rho_f < 10:
                    Mach = U / 340.29
                    if Mach > 0.3:
                        compressibility_error = (Mach**2 / 4) * 100
                        st.write(f"• Mach number: {Mach:.2f}")
                        st.write(f"• Compressibility error: ~{compressibility_error:.1f}%")
                        st.warning("⚠️ Apply compressibility correction for M > 0.3")
            
            with col_err2:
                st.markdown("#### Random Errors")
                
                st.write("**1. Density Uncertainty**")
                density_uncertainty = st.slider("Density Uncertainty (%)", 0, 10, 2, key="dens_uncert")
                velocity_uncertainty = density_uncertainty / 2
                st.write(f"• Velocity uncertainty: ±{velocity_uncertainty:.1f}%")
                st.caption("Velocity uncertainty is half of density uncertainty")
                
                st.write("**2. Manometer Reading**")
                h_uncertainty = 0.5  # mm
                relative_h_uncertainty = (h_uncertainty / (h_cm * 10)) * 100
                st.write(f"• Height reading: ±{h_uncertainty} mm")
                st.write(f"• Relative uncertainty: ±{relative_h_uncertainty:.1f}%")
                
                st.write("**3. Flow Turbulence**")
                st.write("• Fluctuating velocity causes reading variations")
                st.write("• Average multiple readings for best accuracy")
                st.write("• Use damping in manometer if needed")
            
            st.markdown("---")
            st.markdown("#### Total Measurement Uncertainty")
            
            # Combine errors (RSS method)
            total_uncertainty = np.sqrt(velocity_error**2 + velocity_uncertainty**2 + relative_h_uncertainty**2)
            st.write(f"**Combined uncertainty (RSS): ±{total_uncertainty:.1f}%**")
            st.write(f"**Velocity range: {U*(1-total_uncertainty/100):.2f} - {U*(1+total_uncertainty/100):.2f} m/s**")

        with st.expander("🎯 Practical Measurement Tips", expanded=False):
            st.markdown("**Best Practices for Accurate Measurements:**")
            
            tip_col1, tip_col2 = st.columns(2)
            
            with tip_col1:
                st.markdown("""
                #### Installation Guidelines
                
                **Probe Positioning:**
                - ✅ Align parallel to flow (within ±5°)
                - ✅ Place in uniform flow region
                - ✅ Avoid wall boundary layers (>0.5D from walls)
                - ✅ Keep away from upstream disturbances (>10D)
                - ✅ Ensure static ports face perpendicular to flow
                
                **Manometer Setup:**
                - ✅ Mount vertically using spirit level
                - ✅ Eliminate air bubbles in connecting tubes
                - ✅ Use appropriate manometer fluid
                - ✅ Protect from temperature fluctuations
                - ✅ Provide damping for fluctuating flows
                """)
            
            with tip_col2:
                st.markdown("""
                #### Measurement Procedure
                
                **Before Measuring:**
                - ✅ Record ambient temperature and pressure
                - ✅ Check for blockages in probe holes
                - ✅ Verify zero reading with no flow
                - ✅ Ensure manometer fluid is clean
                
                **During Measurement:**
                - ✅ Wait for reading to stabilize (10-30 sec)
                - ✅ Take multiple readings and average
                - ✅ Note any flow fluctuations
                - ✅ Read manometer at eye level (avoid parallax)
                
                **After Measuring:**
                - ✅ Apply temperature correction to density
                - ✅ Apply calibration coefficient if known
                - ✅ Check compressibility if M > 0.3
                - ✅ Calculate and report uncertainty
                """)

    # --- Column 2: Visualization ---
    with col2:
        st.header("🖼️ Visualization")
        
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
                theta_angle = np.linspace(np.pi, 2 * np.pi, 50)
                return radius * np.cos(theta_angle), radius * np.sin(theta_angle) + y_center
            
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
        
        # Display the plot
        fig = generate_pitot_plot(h_mano, U)
        plot_placeholder.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("📚 Understanding Pitot-Static Tubes")
    
    col_edu1, col_edu2 = st.columns([1, 1])
    
    with col_edu1:
        st.markdown("""
        ### What is a Pitot-Static Tube?
        
        A Pitot-static tube (also called a Prandtl tube) is a device that measures fluid velocity by 
        comparing two pressures:
        
        1. **Stagnation Pressure (P₀)**: The total pressure when the fluid is brought to rest at the nose
        2. **Static Pressure (P)**: The pressure of the moving fluid measured by side ports
        
        The difference between these is the **dynamic pressure (q)**, which directly relates to velocity.
        
        ### The Physics: Bernoulli's Equation
        
        For incompressible flow along a streamline:
        """)
        
        st.latex(r'P + \frac{1}{2}\rho U^2 + \rho g h = \text{constant}')
        
        st.markdown("""
        For horizontal flow (neglecting elevation changes):
        """)
        
        st.latex(r'P + \frac{1}{2}\rho U^2 = P_0')
        
        st.markdown("""
        Where:
        - **P** = static pressure (Pa)
        - **ρ** = fluid density (kg/m³)
        - **U** = flow velocity (m/s)
        - **P₀** = stagnation pressure (Pa)
        
        ### The Velocity Equation
        
        Rearranging Bernoulli's equation and measuring ΔP with a manometer:
        """)
        
        st.latex(r'U = \sqrt{\frac{2(P_0 - P)}{\rho}} = \sqrt{\frac{2\rho_m g h}{\rho_f}}')
    
    with col_edu2:
        st.markdown("""
        ### Key Design Features
        
        **1. Stagnation Port (Nose)**
        - Forward-facing opening at tip
        - Fluid brought completely to rest (U = 0)
        - Measures total pressure P₀ = P + ½ρU²
        - Hemispherical or conical nose shape
        
        **2. Static Ports (Side Holes)**
        - 4-8 radial holes around circumference
        - Located 5-10 diameters downstream of nose
        - Measure static pressure P of moving fluid
        - Must be perpendicular to flow direction
        - Averaged to eliminate flow asymmetry
        
        **3. Probe Body**
        - Streamlined to minimize disturbance
        - Length/diameter ratio typically 10:1
        - Two concentric tubes (stagnation inner, static outer)
        - Made of stainless steel or brass
        
        ### Why Static Ports Must Be Downstream
        
        Near the nose, pressure is affected by the stagnation point. Static ports must be in a region where:
        - Flow has reattached to the probe
        - Pressure equals free-stream static pressure
        - Flow disturbance is minimal
        
        This typically occurs 5-10 diameters downstream.
        """)
    
    st.markdown("---")
    
    st.markdown("### Types of Pitot Tubes")
    
    type_col1, type_col2, type_col3 = st.columns(3)
    
    with type_col1:
        st.markdown("""
        #### Standard Pitot-Static Tube
        
        - **Single probe** with both ports
        - **Compact** design
        - **Most common** type
        - **Applications**: Aircraft, wind tunnels
        
        **Advantages:**
        - Simple installation
        - Direct ΔP measurement
        - Self-contained
        
        **Limitations:**
        - Alignment critical
        - Static ports must be clean
        - Not for dirty fluids
        """)
    
    with type_col2:
        st.markdown("""
        #### Separate Pitot & Static Probes
        
        - **Two probes** used independently
        - Static probe on **wall** or separate location
        - **More accurate** for research
        - **Applications**: Precision measurements
        
        **Advantages:**
        - Optimal positioning for each
        - Less alignment sensitivity
        - Can use static ring
        
        **Limitations:**
        - More complex setup
        - Two measurement points
        - Higher cost
        """)
    
    with type_col3:
        st.markdown("""
        #### S-Type (Reverse) Pitot
        
        - **Two forward-facing ports** at different angles
        - Measures **velocity direction** too
        - **Robust** for dirty flows
        - **Applications**: Stack testing, flue gas
        
        **Advantages:**
        - Works in dusty conditions
        - Self-cleaning design
        - Measures flow angle
        
        **Limitations:**
        - Needs calibration
        - Less accurate than standard
        - Larger size
        """)
    
    st.markdown("---")
    
    st.markdown("### Compressibility Effects")
    
    compress_col1, compress_col2 = st.columns(2)
    
    with compress_col1:
        st.markdown("""
        #### When Compressibility Matters
        
        For **gas flows**, density changes with pressure and velocity. The incompressible Bernoulli 
        equation becomes inaccurate when:
        
        - **Mach number M > 0.3**
        - Velocity > ~100 m/s for air at sea level
        - Pressure changes > ~5% of absolute pressure
        
        #### Compressibility Correction
        
        For subsonic compressible flow (0.3 < M < 0.8):
        """)
        
        st.latex(r'\frac{P_0 - P}{q} = 1 + \frac{M^2}{4} + \frac{M^4}{40} + ...')
        
        st.markdown("""
        Where:
        - M = U/a (Mach number)
        - a = speed of sound ≈ 340 m/s for air at 15°C
        """)
    
    with compress_col2:
        st.markdown("""
        #### Supersonic Flow (M > 1)
        
        Standard Pitot-static tubes **cannot be used** in supersonic flow because:
        
        1. **Shock waves** form ahead of the probe
        2. Pressure jump across shock is **not** predicted by Bernoulli
        3. Need **supersonic Pitot probe** with special nose
        
        **Supersonic Pitot Equation:**
        """)
        
        st.latex(r'\frac{P_0}{P} = \left[\frac{(\gamma+1)M^2}{2}\right]^{\frac{\gamma}{\gamma-1}} \left[\frac{1-\gamma+2\gamma M^2}{\gamma+1}\right]^{\frac{1}{\gamma-1}}')
        
        st.markdown("""
        Where γ = 1.4 for air
        
        **Note:** This is the Rayleigh Pitot formula combining normal shock relations 
        with isentropic flow.
        """)
    
    st.markdown("---")
    
    st.markdown("### Advantages & Limitations")
    
    adv_col1, adv_col2 = st.columns(2)
    
    with adv_col1:
        st.success("""
        **Advantages:**
        - ✅ **Direct measurement** - velocity from first principles
        - ✅ **No calibration needed** (if aligned)
        - ✅ **No moving parts** - highly reliable
        - ✅ **Wide velocity range** - 1-300+ m/s
        - ✅ **Simple principle** - easy to understand
        - ✅ **Proven technology** - used since 1730s
        - ✅ **Inexpensive** - low cost construction
        - ✅ **Real-time reading** - instant response
        - ✅ **Pressure-based** - not affected by EMI
        """)
    
    with adv_col2:
        st.warning("""
        **Limitations:**
        - ⚠️ **Alignment critical** - must face flow (±5-10°)
        - ⚠️ **Point measurement** - only at probe location
        - ⚠️ **Flow disturbance** - probe blocks flow
        - ⚠️ **Density needed** - requires temperature measurement
        - ⚠️ **Not for pulsating flow** - measures time-averaged
        - ⚠️ **Can clog** - not suitable for dirty fluids
        - ⚠️ **Low velocity limit** - resolution limited by ΔP sensor
        - ⚠️ **Compressibility** - correction needed for M > 0.3
        - ⚠️ **Turbulence sensitivity** - fluctuations cause errors
        """)

with tab3:
    st.header("📋 Real-World Applications")
    
    st.markdown("""
    Pitot-static tubes are one of the most widely used velocity measurement devices, essential in 
    aviation, HVAC, and industrial applications. Their simplicity and reliability make them irreplaceable 
    despite modern electronic alternatives.
    """)
    
    app_col1, app_col2 = st.columns(2)
    
    with app_col1:
        st.markdown("""
        ### Aviation Applications
        
        **1. Aircraft Airspeed Measurement**
        - **Every aircraft** has at least one Pitot-static system
        - **Primary flight instrument** - essential for safety
        - **Types**: 
          - Pitot-static tube for indicated airspeed
          - Total air temperature probe for true airspeed
        - **Location**: Nose, wing, or fuselage
        - **Critical**: Blockage can cause crashes
        - **Heating**: Electric heat prevents ice formation
        - **Redundancy**: Commercial aircraft have 2-3 systems
        
        *Example: Boeing 737 has 2 Pitot tubes and 4 static ports*
        
        **2. Wind Tunnel Testing**
        - **Velocity surveys**: Map flow field
        - **Model testing**: Measure local velocities
        - **Calibration standard**: Reference measurement
        - **Types**: 
          - Standard Pitot-static for subsonic
          - Supersonic cone probes for M > 1
        - **Precision**: Research-grade accuracy (±0.2%)
        
        **3. Helicopter Airspeed**
        - **Hover performance**: Very low velocities
        - **Rotor downwash**: Complex flow field
        - **Multiple probes**: Determine flight state
        - **Challenge**: Rotorcraft turbulence
        
        **4. Glider/Sailplane**
        - **Optimized for low speed**: Sensitive instruments
        - **Total energy compensation**: Accounts for altitude changes
        - **MacCready speed**: Optimal cruise calculation
        """)
    
    with app_col2:
        st.markdown("""
        ### HVAC & Building Systems
        
        **5. Duct Velocity Measurement**
        - **Balancing air systems**: Ensure proper flow distribution
        - **Commissioning**: Verify design performance
        - **Troubleshooting**: Identify blockages
        - **Standard practice**: ASHRAE guidelines
        - **Portable instruments**: Hand-held Pitot + micromanometer
        
        **6. Fume Hood Face Velocity**
        - **Safety critical**: Protect laboratory workers
        - **Regulation**: OSHA requires 80-120 ft/min
        - **Testing**: Annual certification required
        - **Low velocities**: Special low-range probes
        
        **7. Clean Room Monitoring**
        - **Laminar flow verification**: Ensure unidirectional flow
        - **Filter integrity**: Check for leaks
        - **Typical velocity**: 0.3-0.5 m/s (60-100 ft/min)
        - **Standard**: ISO 14644
        
        **8. Building Pressurization**
        - **Smoke control**: Maintain pressure differentials
        - **Stairwell pressure**: Keep fire stairs positive
        - **Operating room pressure**: Positive for sterile zones
        """)
    
    st.markdown("---")
    
    st.markdown("### Industrial & Process Applications")
    
    industrial_col1, industrial_col2 = st.columns(2)
    
    with industrial_col1:
        st.markdown("""
        **9. Stack/Chimney Velocity**
        - **EPA Method 2**: Regulatory requirement
        - **Emissions calculation**: Volumetric flow rate
        - **High temperature**: Special materials (Inconel)
        - **Typical range**: 5-25 m/s
        - **Traverse**: Multi-point measurement required
        
        **10. Spray Booth Airflow**
        - **Paint booth certification**: Safety requirement
        - **Capture velocity**: Ensure containment
        - **Face velocity**: 0.4-0.6 m/s typical
        - **Testing frequency**: Quarterly or semi-annually
        
        **11. Baghouse/Filter Velocity**
        - **Filter face velocity**: Optimize performance
        - **Bag inspection**: Find damaged bags
        - **Typical**: 1.5-3 m/min (0.025-0.05 m/s)
        - **Prevents**: Cake formation issues
        
        **12. Forced Draft Fan**
        - **Performance testing**: Verify flow rate
        - **Efficiency**: Optimize operation
        - **Fan curve**: Develop characteristic curve
        - **Maintenance**: Detect degradation
        """)
    
    with industrial_col2:
        st.markdown("""
        **13. Cooling Tower Velocity**
        - **Fan performance**: Air flow measurement
        - **Approach temperature**: Correlate with velocity
        - **Fill inspection**: Check for blockage
        - **Drift eliminator**: Verify effectiveness
        
        **14. Dryer/Oven Velocity**
        - **Product quality**: Ensure uniform drying
        - **Energy efficiency**: Optimize air flow
        - **Temperature uniformity**: Correlate with velocity
        - **Conveyor belt dryers**: Critical parameter
        
        **15. Pneumatic Conveying**
        - **Saltation velocity**: Prevent settling
        - **Erosion monitoring**: Detect excessive velocity
        - **System design**: Verify calculated velocities
        - **Typical range**: 15-30 m/s for dilute phase
        
        **16. Flare Stack Velocity**
        - **Combustion efficiency**: Proper mixing
        - **Smokeless operation**: Velocity control
        - **Regulatory**: EPA requirements
        - **Exit velocity**: 6-120 m/s typical
        """)
    
    st.markdown("---")
    
    st.markdown("### Marine & Underwater")
    
    marine_col1, marine_col2 = st.columns(2)
    
    with marine_col1:
        st.markdown("""
        **17. Ship Speed Log**
        - **Underwater Pitot tube**: Measures speed through water
        - **Types**: 
          - Rodmeter: Mechanical speedometer
          - Electronic log: Pressure transducer
        - **Accuracy**: ±2-3% typical
        - **Alternative to**: GPS (gives speed over water)
        
        **18. Submarine Velocity**
        - **Silent operation**: No moving parts
        - **Depth compensation**: Pressure correction
        - **Redundant systems**: Safety critical
        - **Tactical**: Covert operations
        """)
    
    with marine_col2:
        st.markdown("""
        **19. Remotely Operated Vehicle (ROV)**
        - **Current measurement**: Underwater currents
        - **Thruster control**: Maintain position
        - **Pipeline inspection**: Flow verification
        - **Oceanography**: Current profiling
        
        **20. Wave Basin Testing**
        - **Model testing**: Ship and offshore platform
        - **Current generation**: Verify test conditions
        - **Calibration**: Flow field mapping
        - **Research**: Hydrodynamics studies
        """)
    
    st.markdown("---")
    
    st.markdown("### Sports & Recreation")
    
    st.markdown("""
    **21. Skydiving**
    - **Audible altimeter**: Velocity-based warning
    - **Automatic activation device (AAD)**: Deploys reserve parachute
    - **Velocity measurement**: Free fall speed
    
    **22. Sailboat Racing**
    - **Tactical instrument**: Wind speed and direction
    - **Performance optimization**: Sail trim
    - **Mast-head unit**: True wind measurement
    
    **23. Automotive Testing**
    - **Wind tunnel testing**: Aerodynamic development
    - **Coast-down testing**: Drag verification
    - **Cooling system**: Radiator air flow
    """)
    
    st.markdown("---")
    
    st.markdown("### Research & Development")
    
    research_col1, research_col2 = st.columns(2)
    
    with research_col1:
        st.markdown("""
        **24. Combustion Research**
        - **Flame velocity**: Propagation studies
        - **Burner development**: Flow characterization
        - **Stability analysis**: Velocity fluctuations
        
        **25. Heat Transfer Studies**
        - **Forced convection**: Local velocity measurement
        - **Flow visualization**: Velocity field mapping
        - **Boundary layer**: Velocity profiles
        """)
    
    with research_col2:
        st.markdown("""
        **26. Environmental Monitoring**
        - **Stack emissions**: Regulatory compliance
        - **Ambient air**: Dispersion studies
        - **Indoor air quality**: Ventilation rates
        
        **27. Sports Aerodynamics**
        - **Cycling**: Time trial position optimization
        - **Ski jumping**: Wind tunnel testing
        - **Motorsports**: Wind tunnel development
        """)
    
    st.markdown("---")
    
    st.markdown("### Installation Best Practices")
    
    install_col1, install_col2, install_col3 = st.columns(3)
    
    with install_col1:
        st.markdown("""
        #### Location Selection
        
        **Choose locations where:**
        - Flow is fully developed
        - Velocity profile is uniform
        - Turbulence is minimal
        - Flow is parallel to duct/pipe
        
        **Avoid:**
        - Near bends (< 10D downstream)
        - Near dampers/valves
        - Near obstructions
        - Wall boundary layers
        - Junctions/tees
        - Expansions/contractions
        """)
    
    with install_col2:
        st.markdown("""
        #### Probe Installation
        
        **Alignment:**
        - Parallel to flow (within ±5°)
        - Perpendicular to walls
        - Centered in duct (for uniform flow)
        
        **Mounting:**
        - Rigid support
        - Vibration isolation
        - Removable for cleaning
        - Pressure-tight seal
        
        **Protection:**
        - Guard against impact
        - Heating if needed (ice prevention)
        - Drain holes for moisture
        """)
    
    with install_col3:
        st.markdown("""
        #### Manometer/Transducer
        
        **Connection:**
        - Short, rigid tubing
        - No leaks
        - Proper slope (drain condensate)
        - Separate routing (no interference)
        
        **Instrumentation:**
        - Vertical mounting
        - Temperature compensation
        - Damping if needed
        - Regular calibration
        
        **Maintenance:**
        - Check for blockages
        - Clean static ports
        - Verify zero reading
        - Inspect for damage
        """)
    
    st.markdown("---")
    
    st.markdown("### Troubleshooting Guide")
    
    trouble_col1, trouble_col2 = st.columns(2)
    
    with trouble_col1:
        st.markdown("""
        | Problem | Possible Cause | Solution |
        |---------|---------------|----------|
        | **No reading** | Blocked ports | Clean with fine wire, compressed air |
        | | Disconnected tubing | Check connections, repair leaks |
        | | Probe facing wrong way | Verify flow direction, realign |
        | **Erratic reading** | Turbulent flow | Move probe, add damping |
        | | Air bubbles in lines | Purge system, check for leaks |
        | | Vibration | Isolate probe, secure mounting |
        | **Reading too low** | Misalignment | Align within ±5° of flow |
        | | Damaged probe | Inspect, replace if deformed |
        | | Incorrect density | Verify temperature, update ρ |
        """)
    
    with trouble_col2:
        st.markdown("""
        | Problem | Possible Cause | Solution |
        |---------|---------------|----------|
        | **Reading too high** | Static ports blocked | Clean ports, verify 4-8 open |
        | | Probe in accelerating flow | Move to uniform section |
        | | Temperature error | Correct for actual temperature |
        | **Slow response** | Long connecting lines | Shorten tubing, increase diameter |
        | | Restricted lines | Check for kinks, blockages |
        | | Heavy damping | Reduce damping time constant |
        | **Reading drifts** | Temperature change | Allow thermal equilibration |
        | | Manometer fluid evaporation | Refill, use non-volatile fluid |
        | | Density change | Update calibration |
        """)
    
    st.markdown("---")
    
    st.markdown("### Modern Alternatives")
    
    st.markdown("""
    While Pitot-static tubes remain essential, consider these alternatives:
    """)
    
    alt_col1, alt_col2 = st.columns(2)
    
    with alt_col1:
        st.markdown("""
        **When to Use Pitot-Static Tubes:**
        - ✅ Standard velocity measurement
        - ✅ Calibration/verification of other instruments
        - ✅ Simple installations
        - ✅ High reliability needed
        - ✅ Wide velocity range
        - ✅ Hostile environments (EMI, radiation)
        - ✅ Low cost requirement
        - ✅ Aviation (mandatory)
        """)
    
    with alt_col2:
        st.markdown("""
        **When to Consider Alternatives:**
        - Thermal anemometer: Very low velocities (< 0.5 m/s)
        - Hot-wire anemometer: Turbulence measurements, fast response
        - Vortex shedding: Permanent installation, digital output
        - Ultrasonic: Dirty fluids, no moving parts
        - Laser Doppler velocimetry: Non-intrusive, 3D velocity
        - Particle image velocimetry: Whole-field measurement
        - Pressure transducer Pitot: Data logging, remote reading
        """)

# Add velocity calculator
st.markdown("---")
st.header("🧮 Quick Velocity Calculator")

calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)

with calc_col1:
    calc_h = st.number_input("Height h (cm)", value=15.0, step=1.0, key="calc_h")
    calc_rho_m = st.number_input("ρ_manometer (kg/m³)", value=1000.0, step=100.0, key="calc_rho_m")

with calc_col2:
    calc_rho_f = st.number_input("ρ_fluid (kg/m³)", value=1.225, step=0.1, format="%.3f", key="calc_rho_f")
    calc_g = st.number_input("g (m/s²)", value=9.81, format="%.2f", key="calc_g")

with calc_col3:
    calc_delta_P = calc_rho_m * calc_g * (calc_h/100)
    calc_U = np.sqrt(2 * calc_delta_P / calc_rho_f) if calc_rho_f > 0 else 0
    st.metric("Velocity (m/s)", f"{calc_U:.2f}")
    st.metric("Velocity (km/h)", f"{calc_U*3.6:.1f}")

with calc_col4:
    st.metric("Velocity (knots)", f"{calc_U*1.944:.1f}")
    st.metric("ΔP (kPa)", f"{calc_delta_P/1000:.3f}")

st.caption("💡 **Tip**: Use this calculator to quickly check velocities for different manometer readings and fluid densities.")

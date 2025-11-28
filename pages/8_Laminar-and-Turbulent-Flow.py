import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Laminar and Turbulent Flow", layout="wide")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>🌊 Laminar and Turbulent Flow in Pipes</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
Explore the fundamental difference between smooth laminar flow and chaotic turbulent flow.
Visualize velocity profiles, particle paths, and understand the critical Reynolds number.
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# Create tabs for different aspects
tab1, tab2, tab3 = st.tabs(["🎯 Interactive Simulation", "📚 Understanding Flow Regimes", "📋 Real-World Applications"])

with tab1:
    # --- Main Layout ---
    col1, col2 = st.columns([2, 3])

    # --- Column 1: Inputs and Results ---
    with col1:
        st.header("🔬 Parameters")
        
        # --- Interactive Scenarios ---
        SCENARIOS = {
            "Custom...": {
                "fluid": "Water", "D": 0.1, "V": 0.5,
                "desc": "Manually adjust all parameters below."
            },
            "Water in Garden Hose": {
                "fluid": "Water", "D": 0.016, "V": 2.0,
                "desc": "Garden hose: 16mm diameter, 2 m/s velocity. Re ≈ 32,000 (turbulent)."
            },
            "Oil in Pipeline": {
                "fluid": "Oil", "D": 0.5, "V": 1.5,
                "desc": "Oil pipeline: 50cm diameter, 1.5 m/s. High viscosity → lower Re ≈ 85,000."
            },
            "Slow Water Flow": {
                "fluid": "Water", "D": 0.01, "V": 0.15,
                "desc": "Small tube, slow flow: 1cm diameter, 0.15 m/s. Re ≈ 1,500 (laminar)."
            },
            "Blood in Artery": {
                "fluid": "Blood", "D": 0.004, "V": 0.3,
                "desc": "Human artery: 4mm diameter, 0.3 m/s. Re ≈ 400 (laminar)."
            },
            "Air in Duct": {
                "fluid": "Air", "D": 0.3, "V": 5.0,
                "desc": "HVAC duct: 30cm diameter, 5 m/s. Low density but Re ≈ 100,000 (turbulent)."
            },
            "Honey Dripping": {
                "fluid": "Honey", "D": 0.005, "V": 0.05,
                "desc": "Very viscous: 5mm tube, 0.05 m/s. Extremely low Re ≈ 0.3 (highly laminar)."
            }
        }
        
        scenario = st.selectbox("Select Flow Scenario", list(SCENARIOS.keys()))
        selected = SCENARIOS[scenario]
        st.info(selected["desc"])
        
        st.subheader("Fluid Properties")
        fluid_type = st.selectbox("Select Fluid", ["Water", "Oil", "Blood", "Air", "Honey", "Custom"],
                                  index=["Water", "Oil", "Blood", "Air", "Honey", "Custom"].index(selected["fluid"]) if selected["fluid"] in ["Water", "Oil", "Blood", "Air", "Honey"] else 0)
        
        # Fluid property presets
        if fluid_type == "Water":
            rho_default = 1000.0
            mu_default = 0.001
        elif fluid_type == "Oil":
            rho_default = 900.0
            mu_default = 0.05
        elif fluid_type == "Blood":
            rho_default = 1060.0
            mu_default = 0.003
        elif fluid_type == "Air":
            rho_default = 1.2
            mu_default = 1.8e-5
        elif fluid_type == "Honey":
            rho_default = 1400.0
            mu_default = 10.0
        else:
            rho_default = 1000.0
            mu_default = 0.001
        
        c1, c2 = st.columns(2)
        with c1:
            if fluid_type == "Custom":
                rho = st.number_input("Density ρ (kg/m³)", value=1000.0, min_value=0.1, step=10.0, format="%.1f")
            else:
                rho = rho_default
                st.metric("Density ρ", f"{rho:.1f} kg/m³")
        
        with c2:
            if fluid_type == "Custom":
                mu = st.number_input("Viscosity μ (Pa·s)", value=0.001, min_value=0.00001, step=0.0001, format="%.5f")
            else:
                mu = mu_default
                st.metric("Viscosity μ", f"{mu:.5f} Pa·s" if mu >= 0.001 else f"{mu:.2e} Pa·s")
        
        nu = mu / rho if rho > 0 else 0  # Kinematic viscosity
        
        st.subheader("Pipe and Flow Conditions")
        c1, c2 = st.columns(2)
        with c1:
            D = st.slider("Pipe Diameter D (cm)", 0.1, 100.0, selected["D"]*100, step=0.1,
                         help="Internal diameter of pipe") / 100  # Convert to meters
        with c2:
            V = st.slider("Average Velocity V (m/s)", 0.01, 10.0, selected["V"], step=0.01,
                         help="Mean velocity of flow")
        
        st.subheader("Visualization Options")
        
        show_velocity_profile = st.checkbox("Show velocity profile", value=True)
        show_particle_paths = st.checkbox("Show particle streamlines", value=True)
        
        if show_particle_paths:
            n_particles = st.slider("Number of streamlines", 5, 31, 15, step=2,
                                   help="Number of particle paths to display (odd number for center)")
            
            col_anim1, col_anim2 = st.columns(2)
            with col_anim1:
                use_static_view = st.radio("Display mode", 
                                          ["Static (full path)", "Animated (developing)"],
                                          help="Static shows complete paths, Animated shows flow development")
            with col_anim2:
                if use_static_view == "Static (full path)":
                    highlight_center = st.checkbox("Highlight center streamline", value=False,
                                                   help="Emphasize the centerline particle path")

        # --- Calculations ---
        # Reynolds number
        Re = (rho * V * D) / mu if mu > 0 else 0
        
        # Flow regime determination
        if Re < 2300:
            flow_regime = "Laminar"
            regime_color = "🟢"
        elif Re <= 4000:
            flow_regime = "Transitional"
            regime_color = "🟡"
        else:
            flow_regime = "Turbulent"
            regime_color = "🔴"
        
        # Volumetric flow rate
        Q = (np.pi * D**2 / 4) * V
        Q_L_s = Q * 1000  # Convert to L/s
        
        # Friction factor (Moody diagram approximations)
        if Re < 2300:  # Laminar
            f = 64 / Re if Re > 0 else 0
        else:  # Turbulent (smooth pipe, Colebrook-White approximation)
            f = 0.316 / (Re**0.25) if Re > 0 else 0
        
        # Pressure drop per meter (Darcy-Weisbach)
        if D > 0 and V > 0:
            pressure_drop = f * (rho * V**2) / (2 * D)  # Pa/m
        else:
            pressure_drop = 0
        
        # Entry length (distance to fully developed flow)
        if Re < 2300:  # Laminar
            L_e = 0.05 * Re * D
        else:  # Turbulent
            L_e = 4.4 * (Re**(1/6)) * D
        
        # Maximum velocity
        if Re < 2300:  # Laminar (parabolic)
            V_max = 2 * V
        else:  # Turbulent (power law, n=7)
            n = 7
            V_max = V * (n + 1) * (2*n + 1) / (2 * n**2)

        st.markdown("---")
        st.header("📈 Results Summary")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric(label="Reynolds Number (Re)", value=f"{Re:,.0f}",
                      help="Dimensionless number indicating flow regime")
            st.metric(label=f"Flow Regime {regime_color}", value=flow_regime,
                      help="Laminar: Re<2300, Transitional: 2300<Re<4000, Turbulent: Re>4000")
        with col_r2:
            st.metric(label="Flow Rate (Q)", value=f"{Q_L_s:.2f} L/s",
                      help="Volumetric flow rate")
            st.metric(label="Friction Factor (f)", value=f"{f:.5f}",
                      help="Darcy friction factor for pressure drop calculation")
        
        col_r3, col_r4 = st.columns(2)
        with col_r3:
            st.metric(label="Pressure Drop", value=f"{pressure_drop/1000:.2f} kPa/m",
                      help="Pressure loss per meter of pipe length")
            st.metric(label="Max Velocity", value=f"{V_max:.2f} m/s",
                      help="Maximum velocity at pipe centerline")
        with col_r4:
            st.metric(label="Entry Length", value=f"{L_e:.2f} m",
                      help="Distance for flow to become fully developed")
            st.metric(label="Kinematic Viscosity", value=f"{nu:.2e} m²/s",
                      help="ν = μ/ρ")
        
        st.markdown("---")
        st.header("🧮 Step-by-Step Calculation")
        
        with st.expander("📖 See Detailed Breakdown", expanded=False):
            st.markdown("### Reynolds Number Calculation")
            
            st.markdown("#### Step 1: Understand Reynolds Number")
            st.write("The Reynolds number is a dimensionless parameter that predicts flow regime:")
            st.latex(r'Re = \frac{\rho V D}{\mu} = \frac{V D}{\nu}')
            st.write("Where:")
            st.write("• **ρ** = fluid density (kg/m³)")
            st.write("• **V** = average velocity (m/s)")
            st.write("• **D** = pipe diameter (m)")
            st.write("• **μ** = dynamic viscosity (Pa·s)")
            st.write("• **ν** = kinematic viscosity (m²/s)")
            
            st.write("\n**Physical meaning:**")
            st.latex(r'Re = \frac{\text{Inertial Forces}}{\text{Viscous Forces}}')
            st.write("• High Re → Inertia dominates → Turbulent flow")
            st.write("• Low Re → Viscosity dominates → Laminar flow")
            
            st.markdown("#### Step 2: Calculate Reynolds Number")
            st.write(f"**Given data:**")
            st.write(f"• ρ = {rho:.2f} kg/m³")
            st.write(f"• V = {V:.3f} m/s")
            st.write(f"• D = {D:.4f} m = {D*100:.2f} cm")
            st.write(f"• μ = {mu:.5f} Pa·s" if mu >= 0.001 else f"• μ = {mu:.2e} Pa·s")
            
            st.write(f"\n**Calculation:**")
            st.write(f"Re = ({rho:.2f} × {V:.3f} × {D:.4f}) / {mu:.5f}" if mu >= 0.001 else f"Re = ({rho:.2f} × {V:.3f} × {D:.4f}) / {mu:.2e}")
            st.write(f"Re = {rho * V * D:.4f} / {mu:.5f}" if mu >= 0.001 else f"Re = {rho * V * D:.4f} / {mu:.2e}")
            st.write(f"Re = **{Re:,.0f}**")
            
            st.markdown("#### Step 3: Determine Flow Regime")
            st.write("**Critical Reynolds numbers:**")
            st.write("• Re < 2,300: **Laminar flow** 🟢")
            st.write("  - Smooth, parallel layers")
            st.write("  - Parabolic velocity profile")
            st.write("  - Predictable and stable")
            st.write("\n• 2,300 < Re < 4,000: **Transitional flow** 🟡")
            st.write("  - Unstable, fluctuating")
            st.write("  - Switches between laminar and turbulent")
            st.write("  - Difficult to predict")
            st.write("\n• Re > 4,000: **Turbulent flow** 🔴")
            st.write("  - Chaotic, mixing motion")
            st.write("  - Flatter velocity profile")
            st.write("  - Random fluctuations")
            
            st.write(f"\n**Your flow:** Re = {Re:,.0f} → **{flow_regime}** {regime_color}")
            
            st.markdown("#### Step 4: Calculate Associated Parameters")
            
            st.write("**A. Flow Rate**")
            st.latex(r'Q = A \times V = \frac{\pi D^2}{4} \times V')
            st.write(f"Q = π × ({D:.4f})² / 4 × {V:.3f}")
            st.write(f"Q = {Q:.6f} m³/s = **{Q_L_s:.2f} L/s**")
            
            st.write("\n**B. Friction Factor**")
            if Re < 2300:
                st.write("For laminar flow:")
                st.latex(r'f = \frac{64}{Re}')
                st.write(f"f = 64 / {Re:,.0f} = **{f:.6f}**")
            else:
                st.write("For turbulent flow (smooth pipe, Blasius equation):")
                st.latex(r'f = \frac{0.316}{Re^{0.25}}')
                st.write(f"f = 0.316 / ({Re:,.0f})^0.25 = **{f:.6f}**")
            
            st.write("\n**C. Pressure Drop (Darcy-Weisbach equation)**")
            st.latex(r'\frac{dP}{dL} = f \times \frac{\rho V^2}{2D}')
            st.write(f"dP/dL = {f:.6f} × ({rho:.2f} × {V:.3f}²) / (2 × {D:.4f})")
            st.write(f"dP/dL = {pressure_drop:.2f} Pa/m = **{pressure_drop/1000:.3f} kPa/m**")
            
            st.write("\n**D. Entry Length**")
            if Re < 2300:
                st.write("For laminar flow:")
                st.latex(r'L_e = 0.05 \times Re \times D')
                st.write(f"L_e = 0.05 × {Re:,.0f} × {D:.4f} = **{L_e:.3f} m**")
            else:
                st.write("For turbulent flow:")
                st.latex(r'L_e = 4.4 \times Re^{1/6} \times D')
                st.write(f"L_e = 4.4 × ({Re:,.0f})^(1/6) × {D:.4f} = **{L_e:.3f} m**")
            
            st.markdown("### Physical Interpretation")
            
            if Re < 2300:
                st.success(f"🟢 **Laminar Flow** (Re = {Re:,.0f})")
                st.write("**Characteristics:**")
                st.write(f"• Smooth, orderly flow with parallel layers")
                st.write(f"• No mixing between layers")
                st.write(f"• Parabolic velocity profile (V_max = {V_max:.2f} m/s = 2×V_avg)")
                st.write(f"• Low pressure drop ({pressure_drop/1000:.3f} kPa/m)")
                st.write(f"• Entry length: {L_e:.2f}m (relatively long for laminar)")
                st.write(f"\n**Applications:** Lubrication, microfluidics, blood flow, viscous fluids")
            elif Re <= 4000:
                st.warning(f"🟡 **Transitional Flow** (Re = {Re:,.0f})")
                st.write("**Characteristics:**")
                st.write(f"• Unstable flow, fluctuates between laminar and turbulent")
                st.write(f"• Unpredictable behavior")
                st.write(f"• Velocity profile varies with time")
                st.write(f"• Entry length: {L_e:.2f}m")
                st.write(f"\n**Design approach:** Usually avoided in practice. Design for either laminar or turbulent.")
            else:
                st.error(f"🔴 **Turbulent Flow** (Re = {Re:,.0f})")
                st.write("**Characteristics:**")
                st.write(f"• Chaotic, mixing flow with eddies")
                st.write(f"• Random velocity fluctuations")
                st.write(f"• Flatter velocity profile (V_max = {V_max:.2f} m/s ≈ 1.2×V_avg)")
                st.write(f"• Higher pressure drop ({pressure_drop/1000:.3f} kPa/m)")
                st.write(f"• Entry length: {L_e:.2f}m (shorter for turbulent)")
                st.write(f"\n**Applications:** Most industrial piping, water distribution, HVAC")
        
        st.markdown("---")
        st.header("🔍 Analysis Insights")
        
        with st.expander("💡 Parameter Effects on Flow Regime", expanded=False):
            st.markdown("**How each parameter affects Reynolds number and flow regime:**")
            
            st.markdown("#### 1. Effect of Velocity (V)")
            st.write(f"• Current velocity: **V = {V:.3f} m/s**")
            st.write(f"• **Relationship**: Re ∝ V (linear)")
            
            velocities = [V*0.25, V*0.5, V*0.75, V, V*1.5, V*2]
            velocity_data = []
            for v_temp in velocities:
                re_temp = (rho * v_temp * D) / mu
                regime = "Laminar" if re_temp < 2300 else ("Transitional" if re_temp <= 4000 else "Turbulent")
                velocity_data.append({
                    "Velocity (m/s)": f"{v_temp:.3f}",
                    "Re": f"{re_temp:,.0f}",
                    "Regime": regime,
                    "Ratio": f"×{v_temp/V:.2f}"
                })
            st.table(pd.DataFrame(velocity_data))
            
            st.success("✅ Increasing velocity increases Re linearly. Can transition from laminar to turbulent!")
            
            st.markdown("#### 2. Effect of Diameter (D)")
            st.write(f"• Current diameter: **D = {D*100:.2f} cm**")
            st.write(f"• **Relationship**: Re ∝ D (linear)")
            
            diameters = [D*0.5, D*0.75, D, D*1.5, D*2]
            diameter_data = []
            for d_temp in diameters:
                re_temp = (rho * V * d_temp) / mu
                regime = "Laminar" if re_temp < 2300 else ("Transitional" if re_temp <= 4000 else "Turbulent")
                diameter_data.append({
                    "Diameter (cm)": f"{d_temp*100:.2f}",
                    "Re": f"{re_temp:,.0f}",
                    "Regime": regime,
                    "Ratio": f"×{d_temp/D:.2f}"
                })
            st.table(pd.DataFrame(diameter_data))
            
            st.info("💡 Larger pipes have higher Re at same velocity. Easier to achieve turbulent flow.")
            
            st.markdown("#### 3. Effect of Viscosity (μ)")
            st.write(f"• Current viscosity: **μ = {mu:.5f} Pa·s**" if mu >= 0.001 else f"• Current viscosity: **μ = {mu:.2e} Pa·s**")
            st.write(f"• **Relationship**: Re ∝ 1/μ (inverse)")
            
            st.write("\n**Comparison of different fluids:**")
            fluid_comparison = [
                {"Fluid": "Water (20°C)", "μ (Pa·s)": 0.001, "ρ (kg/m³)": 1000},
                {"Fluid": "Air (20°C)", "μ (Pa·s)": 1.8e-5, "ρ (kg/m³)": 1.2},
                {"Fluid": "Blood", "μ (Pa·s)": 0.003, "ρ (kg/m³)": 1060},
                {"Fluid": "Olive Oil", "μ (Pa·s)": 0.08, "ρ (kg/m³)": 910},
                {"Fluid": "Honey", "μ (Pa·s)": 10.0, "ρ (kg/m³)": 1400},
                {"Fluid": "Glycerol", "μ (Pa·s)": 1.5, "ρ (kg/m³)": 1260}
            ]
            
            fluid_re_data = []
            for fluid_info in fluid_comparison:
                re_f = (fluid_info["ρ (kg/m³)"] * V * D) / fluid_info["μ (Pa·s)"]
                regime = "Laminar" if re_f < 2300 else ("Transitional" if re_f <= 4000 else "Turbulent")
                fluid_re_data.append({
                    "Fluid": fluid_info["Fluid"],
                    "Viscosity": f"{fluid_info['μ (Pa·s)']:.2e}",
                    "Re": f"{re_f:,.0f}",
                    "Regime": regime
                })
            st.table(pd.DataFrame(fluid_re_data))
            
            st.warning("⚠️ High viscosity fluids (honey, glycerol) remain laminar even at high velocities!")
            
            st.markdown("#### 4. Effect of Temperature")
            st.write("Temperature affects viscosity significantly:")
            st.write("\n**For liquids:**")
            st.write("• Higher temperature → Lower viscosity → Higher Re")
            st.write("• Example: Water at 0°C (μ=0.0018 Pa·s) vs 100°C (μ=0.0003 Pa·s)")
            st.write("• Re increases by factor of 6 with temperature!")
            
            st.write("\n**For gases:**")
            st.write("• Higher temperature → Higher viscosity → Lower Re")
            st.write("• But density also decreases, complex interaction")

        with st.expander("⚙️ Practical Design Considerations", expanded=False):
            st.markdown("**Engineering considerations for pipe flow design:**")
            
            st.markdown("#### 1. When to Design for Laminar vs Turbulent")
            
            st.write("**Prefer Laminar Flow when:**")
            st.write("• Minimizing pressure drop is critical")
            st.write("• Preventing mixing (maintaining stratification)")
            st.write("• Working with high-viscosity fluids")
            st.write("• Precise flow control needed (microfluidics)")
            st.write("• Examples: Blood in small vessels, oil lubrication, honey processing")
            
            st.write("\n**Prefer Turbulent Flow when:**")
            st.write("• Heat transfer enhancement needed (mixing improves heat transfer)")
            st.write("• Preventing settling of particles")
            st.write("• Uniform concentration desired (reactors)")
            st.write("• Most industrial applications (water, gas distribution)")
            st.write("• Examples: Water pipes, HVAC, chemical reactors")
            
            st.markdown("#### 2. Pressure Drop Implications")
            
            st.write(f"**Your system:**")
            st.write(f"• Pressure drop: {pressure_drop/1000:.3f} kPa/m")
            st.write(f"• For 100m pipe: ΔP = {pressure_drop*100/1000:.2f} kPa")
            
            if Re < 2300:
                st.write(f"\n**Laminar regime:** Pressure drop is relatively low")
                st.write(f"• Doubling velocity → doubles pressure drop (linear)")
                st.write(f"• Friction factor f = 64/Re")
            else:
                st.write(f"\n**Turbulent regime:** Higher pressure drop")
                st.write(f"• Doubling velocity → ~4× pressure drop (quadratic)")
                st.write(f"• Friction factor f ≈ 0.316/Re^0.25")
            
            st.markdown("#### 3. Entry Length Considerations")
            
            st.write(f"**Your entry length: L_e = {L_e:.2f} m**")
            st.write("\nEntry length is the distance required for:")
            st.write("• Velocity profile to fully develop")
            st.write("• Boundary layer to reach pipe center")
            st.write("• Pressure drop correlations to become accurate")
            
            if L_e > 10:
                st.warning(f"⚠️ Long entry length ({L_e:.1f}m). Consider:")
                st.write("• Measuring pressure drop well downstream")
                st.write("• Using developing flow corrections")
            else:
                st.success(f"✅ Short entry length ({L_e:.1f}m). Fully developed flow achieved quickly.")

    # --- Column 2: Visualization ---
    with col2:
        st.header("🖼️ Visualization")
        
        # Create subplot figure with two visualizations
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.45, 0.55],
            subplot_titles=("Velocity Profile Across Pipe", 
                          "Particle Streamlines" if show_particle_paths else ""),
            vertical_spacing=0.15
        )
        
        # --- 1. VELOCITY PROFILE ---
        if show_velocity_profile:
            # Generate velocity profile based on flow regime
            r_points = np.linspace(-1, 1, 200)  # Normalized radial position (-1 to 1)
            
            if Re < 2300:  # Laminar - parabolic (Hagen-Poiseuille)
                v_profile_norm = 2 * (1 - r_points**2)  # Normalized to average velocity
                profile_color = 'green'
                profile_name = 'Laminar (Parabolic)'
            elif Re <= 4000:  # Transitional - blend between laminar and turbulent
                trans_factor = (Re - 2300) / (4000 - 2300)
                
                # Laminar profile
                v_laminar = 2 * (1 - r_points**2)
                
                # Turbulent profile (1/7 power law)
                # For turbulent: v/v_max = (1 - r)^(1/n) where n=7
                r_abs = np.abs(r_points)
                v_turbulent = (1 - r_abs)**(1/7)
                # Normalize so average = 1
                # For power law: v_avg/v_max = (n+1)(2n+1)/(2n^2) = 8*15/(2*49) = 0.816
                v_turbulent = v_turbulent / 0.816
                
                # Blend between laminar and turbulent
                v_profile_norm = v_laminar * (1 - trans_factor) + v_turbulent * trans_factor
                profile_color = 'orange'
                profile_name = 'Transitional'
            else:  # Turbulent - 1/7 power law
                # Turbulent profile is MUCH flatter in the core
                # v/v_max = (1 - r)^(1/7) where r is distance from wall
                r_abs = np.abs(r_points)
                v_profile_norm = (1 - r_abs)**(1/7)
                # Normalize so average = 1
                # For 1/7 power law: v_avg/v_max = 0.816, so v_max/v_avg = 1.225
                v_profile_norm = v_profile_norm / 0.816
                profile_color = 'red'
                profile_name = 'Turbulent (1/7 Power Law)'
            
            v_profile = v_profile_norm * V  # Scale to actual velocity
            
            # Add velocity profile
            fig.add_trace(
                go.Scatter(
                    x=v_profile,
                    y=r_points,
                    mode='lines',
                    fill='tozerox',
                    fillcolor=f'rgba({"0,255,0" if profile_color=="green" else ("255,165,0" if profile_color=="orange" else "255,0,0")}, 0.3)',
                    line=dict(color=profile_color, width=3),
                    name=profile_name,
                    hovertemplate='Velocity: %{x:.3f} m/s<br>Radial position: %{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Add centerline and average velocity markers
            fig.add_vline(x=V, line_dash="dash", line_color="gray", row=1, col=1,
                         annotation_text=f"Avg V={V:.2f}m/s", annotation_position="top")
            fig.add_vline(x=V_max, line_dash="dot", line_color="darkred", row=1, col=1,
                         annotation_text=f"Max V={V_max:.2f}m/s", annotation_position="bottom right")
            
            # Add annotations explaining the profile
            if Re < 2300:
                fig.add_annotation(
                    x=V*0.5, y=0,
                    text="Parabolic profile<br>V_max = 2×V_avg",
                    showarrow=False,
                    font=dict(size=10, color="green"),
                    bgcolor="rgba(255,255,255,0.8)",
                    row=1, col=1
                )
            elif Re > 4000:
                fig.add_annotation(
                    x=V*0.7, y=0,
                    text="Flat core<br>Steep wall gradient",
                    showarrow=False,
                    font=dict(size=10, color="red"),
                    bgcolor="rgba(255,255,255,0.8)",
                    row=1, col=1
                )
            
            # Update axes for velocity profile
            fig.update_xaxes(title_text="Velocity (m/s)", row=1, col=1, gridcolor='lightgray')
            fig.update_yaxes(title_text="Radial Position (r/R)", row=1, col=1, 
                           range=[-1.2, 1.2], gridcolor='lightgray')
        
        # --- 2. PARTICLE STREAMLINES ---
        if show_particle_paths:
            # Use the original file's approach for particle path generation
            # This cache prevents regenerating paths every interaction
            @st.cache_data
            def generate_particle_paths(n_particles, pipe_length, turb_intensity, turb_start_pos):
                """Generate particle paths with turbulence (from original file)"""
                paths = {}
                pipe_radius = 10  # Normalized units for visualization
                initial_y = np.linspace(-pipe_radius * 0.9, pipe_radius * 0.9, n_particles)
                
                for i in range(n_particles):
                    path = [(0, initial_y[i])]
                    for x_step in range(1, pipe_length):
                        _, last_y = path[-1]
                        perturbation = 0
                        
                        if x_step > turb_start_pos:
                            # Turbulence model: random perturbations
                            perturbation = np.random.normal(0, turb_intensity)
                        
                        new_y = np.clip(last_y + perturbation, -pipe_radius, pipe_radius)
                        path.append((x_step, new_y))
                    
                    paths[i] = np.array(path)
                return paths, pipe_radius
            
            # Determine turbulence parameters (matching original logic)
            pipe_length = 100
            n_particles_actual = n_particles if n_particles % 2 == 1 else n_particles + 1
            
            if Re < 2300:  # Laminar
                turb_intensity = 0
                turb_start_position = pipe_length + 1  # No turbulence
            elif Re <= 4000:  # Transitional
                trans_factor = (Re - 2300) / (4000 - 2300)
                turb_intensity = 0.1 + trans_factor * 0.4
                turb_start_position = pipe_length * (1 - trans_factor * 0.7)
            else:  # Turbulent
                # Increased base intensity for more visible turbulence
                turb_intensity = 0.8 + (Re - 4000) / 20000
                turb_intensity = min(turb_intensity, 2.5)  # Cap at reasonable value
                turb_start_position = 10
            
            # Generate particle paths
            particle_paths, pipe_radius = generate_particle_paths(
                n_particles_actual, pipe_length, turb_intensity, int(turb_start_position)
            )
            
            # Determine center particle for highlighting
            center_particle_idx = n_particles_actual // 2
            
            # Create color scheme
            colors = [f'hsl({int(h)}, 80%, 60%)' for h in np.linspace(0, 360, n_particles_actual, endpoint=False)]
            
            # Plot particle paths
            if use_static_view == "Static (full path)":
                # Show complete paths
                for i in range(n_particles_actual):
                    path = particle_paths[i]
                    
                    # Normalize to -1 to 1 range for consistency
                    x_data = path[:, 0] / pipe_length * 100
                    y_data = path[:, 1] / pipe_radius
                    
                    # Determine line properties
                    if highlight_center and i == center_particle_idx:
                        line_color = 'magenta'
                        line_width = 4
                    else:
                        if highlight_center:
                            line_color = 'rgba(200, 200, 200, 0.2)'  # Faded
                            line_width = 2
                        else:
                            line_color = colors[i]
                            line_width = 2
                    
                    fig.add_trace(
                        go.Scatter(
                            x=x_data,
                            y=y_data,
                            mode='lines',
                            line=dict(color=line_color, width=line_width),
                            name=f'Particle {i+1}',
                            showlegend=False,
                            hovertemplate='Position: %{y:.2f}<extra></extra>'
                        ),
                        row=2, col=1
                    )
            else:
                # Animated/developing view - show frames
                # For simplicity in static view, show progressive reveal
                for i in range(n_particles_actual):
                    path = particle_paths[i]
                    
                    # Show only part of the path (simulating animation frame)
                    reveal_fraction = 0.6  # Show 60% of path
                    n_points = int(len(path) * reveal_fraction)
                    
                    x_data = path[:n_points, 0] / pipe_length * 100
                    y_data = path[:n_points, 1] / pipe_radius
                    
                    fig.add_trace(
                        go.Scatter(
                            x=x_data,
                            y=y_data,
                            mode='lines',
                            line=dict(color=colors[i], width=2),
                            name=f'Particle {i+1}',
                            showlegend=False,
                            hovertemplate='Position: %{y:.2f}<extra></extra>'
                        ),
                        row=2, col=1
                    )
            
            # Add pipe walls
            fig.add_hline(y=1, line_dash="solid", line_color="black", line_width=3, row=2, col=1)
            fig.add_hline(y=-1, line_dash="solid", line_color="black", line_width=3, row=2, col=1)
            
            # Add flow regime annotation
            if Re < 2300:
                regime_text = "LAMINAR: Smooth, parallel streamlines"
                regime_color = "green"
            elif Re <= 4000:
                regime_text = "TRANSITIONAL: Developing turbulence"
                regime_color = "orange"
            else:
                regime_text = "TURBULENT: Chaotic, mixing flow"
                regime_color = "red"
            
            fig.add_annotation(
                x=50, y=1.15,
                text=f"<b>{regime_text}</b>",
                showarrow=False,
                font=dict(size=12, color=regime_color),
                row=2, col=1
            )
            
            # Update axes for streamlines
            fig.update_xaxes(title_text="Axial Distance", row=2, col=1, showgrid=False, range=[0, 100])
            fig.update_yaxes(title_text="Radial Position", row=2, col=1, range=[-1.3, 1.3], showgrid=False)
        
        # Update overall layout
        fig.update_layout(
            height=800,
            showlegend=False,
            plot_bgcolor='white',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Add result box at top of visualization (matching other modules' style)
        if Re < 2300:
            bg_color = "rgba(0, 150, 0, 0.9)"
            border_color = "darkgreen"
        elif Re <= 4000:
            bg_color = "rgba(200, 150, 0, 0.9)"
            border_color = "darkorange"
        else:
            bg_color = "rgba(200, 0, 0, 0.9)"
            border_color = "darkred"
        
        fig.add_annotation(
            x=0.5,
            y=1.02,
            xref="paper",
            yref="paper",
            text=f"<b>Re = {Re:,.0f} ({flow_regime} Flow)</b>",
            showarrow=False,
            font=dict(size=20, color="white"),
            bgcolor=bg_color,
            bordercolor=border_color,
            borderwidth=2,
            borderpad=8
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Caption
        caption_text = f"**{flow_regime} Flow** (Re = {Re:,.0f}). "
        if Re < 2300:
            caption_text += "Smooth parabolic velocity profile with parallel streamlines. No turbulent mixing."
        elif Re <= 4000:
            caption_text += "Transitional regime showing blend of laminar and turbulent characteristics."
        else:
            caption_text += "Flatter velocity profile with chaotic streamline mixing. Significant turbulent eddies."
        
        st.caption(caption_text)

with tab2:
    st.header("📚 Understanding Flow Regimes")
    
    col_edu1, col_edu2 = st.columns([1, 1])
    
    with col_edu1:
        st.markdown("""
        ### What Determines Flow Regime?
        
        The **Reynolds number** is the key parameter that determines whether flow is laminar or turbulent:
        """)
        
        st.latex(r'Re = \frac{\rho V D}{\mu} = \frac{\text{Inertial Forces}}{\text{Viscous Forces}}')
        
        st.markdown("""
        Where:
        - **ρ** = fluid density (kg/m³)
        - **V** = average velocity (m/s)
        - **D** = pipe diameter (m)
        - **μ** = dynamic viscosity (Pa·s)
        
        ### Physical Meaning of Reynolds Number
        
        The Reynolds number represents the **ratio of inertial forces to viscous forces**:
        
        - **Low Re**: Viscous forces dominate → Smooth, orderly flow (laminar)
        - **High Re**: Inertial forces dominate → Chaotic, mixing flow (turbulent)
        
        ### Critical Reynolds Numbers
        
        For flow in circular pipes:
        
        - **Re < 2,300**: Laminar flow (guaranteed)
        - **2,300 < Re < 4,000**: Transitional (unstable)
        - **Re > 4,000**: Turbulent flow (fully developed)
        
        The transition is not sharp - it depends on:
        - Pipe roughness
        - Entrance conditions
        - Flow disturbances
        - Vibrations
        """)
    
    with col_edu2:
        st.markdown("""
        ### Laminar Flow Characteristics
        
        **Velocity Profile:**
        - Parabolic (Poiseuille flow)
        - V_max = 2 × V_avg (at centerline)
        - Zero velocity at walls (no-slip condition)
        
        **Flow Structure:**
        - Fluid moves in parallel layers (laminae)
        - No mixing between layers
        - Smooth particle paths
        - Predictable and stable
        
        **Pressure Drop:**
        - Linear with velocity (f = 64/Re)
        - Relatively low energy loss
        - Easy to calculate analytically
        
        **Applications:**
        - Lubric oil systems
        - Blood flow in vessels
        - Microfluidic devices
        - High-viscosity fluids
        
        ### Turbulent Flow Characteristics
        
        **Velocity Profile:**
        - Flatter (power law, V^(1/7))
        - V_max ≈ 1.2 × V_avg
        - Steep velocity gradient near wall
        
        **Flow Structure:**
        - Chaotic, three-dimensional motion
        - Random velocity fluctuations (eddies)
        - Strong mixing between layers
        - Time-dependent
        
        **Pressure Drop:**
        - Approximately proportional to V² 
        - Higher energy loss than laminar
        - Empirical correlations needed
        
        **Applications:**
        - Most industrial piping
        - Water distribution
        - HVAC systems
        - Heat exchangers (enhanced heat transfer)
        """)
    
    st.markdown("---")
    
    st.markdown("### Detailed Comparison")
    
    comparison_data = {
        "Characteristic": [
            "Velocity Profile",
            "V_max / V_avg",
            "Flow Structure",
            "Mixing",
            "Stability",
            "Energy Loss",
            "Heat Transfer",
            "Friction Factor",
            "Entry Length"
        ],
        "Laminar (Re < 2300)": [
            "Parabolic",
            "2.0",
            "Parallel layers",
            "None (molecular only)",
            "Very stable",
            "Low (∝ V)",
            "Poor (conduction only)",
            "f = 64/Re",
            "L_e = 0.05×Re×D"
        ],
        "Turbulent (Re > 4000)": [
            "Flatter (power law)",
            "~1.2",
            "Chaotic eddies",
            "Strong (convective)",
            "Fluctuating",
            "High (∝ V²)",
            "Excellent (mixing)",
            "f = 0.316/Re^0.25",
            "L_e = 4.4×Re^(1/6)×D"
        ]
    }
    
    st.table(pd.DataFrame(comparison_data))
    
    st.markdown("---")
    
    st.markdown("### Common Misconceptions")
    
    misconception_col1, misconception_col2 = st.columns(2)
    
    with misconception_col1:
        st.error("""
        **❌ WRONG: "Turbulent flow is always bad"**
        
        Turbulence is often desirable!
        
        **✅ CORRECT:** Turbulent flow:
        - Enhances heat transfer (10-100× better than laminar)
        - Prevents settling of particles
        - Promotes mixing in reactors
        - Is unavoidable in most industrial systems
        """)
        
        st.error("""
        **❌ WRONG: "Higher velocity always means turbulent"**
        
        It depends on all parameters in Re!
        
        **✅ CORRECT:** Flow regime depends on:
        - Velocity (V) ✓
        - Diameter (D)
        - Density (ρ)
        - Viscosity (μ)
        
        Honey flowing fast can still be laminar due to high viscosity!
        """)
    
    with misconception_col2:
        st.error("""
        **❌ WRONG: "Re = 2300 is an exact boundary"**
        
        The transition is gradual and depends on conditions.
        
        **✅ CORRECT:**
        - Re = 2300 is for "disturbed" flow (normal pipes)
        - Carefully controlled flow can remain laminar up to Re ≈ 100,000!
        - Pipe roughness, bends, and disturbances trigger turbulence
        - Safe design: Use Re < 2000 for guaranteed laminar
        """)
        
        st.error("""
        **❌ WRONG: "All particles travel at the same speed"**
        
        Even in turbulent flow, there's a velocity distribution.
        
        **✅ CORRECT:**
        - Velocity varies across the pipe radius
        - Zero at walls (no-slip condition)
        - Maximum at centerline
        - Turbulent profile is flatter, but not uniform
        """)

with tab3:
    st.header("📋 Real-World Applications")
    
    st.markdown("""
    Understanding laminar vs turbulent flow is crucial across many engineering disciplines.
    """)
    
    app_col1, app_col2 = st.columns(2)
    
    with app_col1:
        st.markdown("""
        ### Laminar Flow Applications
        
        **1. Biomedical Engineering**
        - **Blood flow in vessels**: Most arteries and veins operate at Re < 1000 (laminar)
        - **Typical values**: Re = 100-1000 in large arteries, Re < 100 in capillaries
        - **Importance**: Laminar flow prevents cell damage, smooth wall shear stress
        - **Disease**: Turbulent flow in damaged vessels can cause problems
        
        **2. Microfluidics and Lab-on-Chip**
        - **Micro-channels**: D = 10-500 μm
        - **Typical Re**: 0.01-10 (extremely laminar)
        - **Advantages**: Predictable flow, precise control, no mixing
        - **Applications**: DNA sequencing, drug delivery, diagnostic devices
        
        **3. Lubrication Systems**
        - **Oil bearings**: High viscosity ensures laminar flow
        - **Typical Re**: 10-1000
        - **Purpose**: Smooth, predictable oil film
        - **Critical**: Avoid turbulence which increases friction
        
        **4. Food Processing**
        - **Honey, syrup handling**: High viscosity → laminar
        - **Typical Re**: 1-500
        - **Advantage**: Gentle handling prevents product damage
        - **Challenge**: High pumping power due to viscosity
        
        **5. Polymer Processing**
        - **Extrusion, molding**: Very high viscosity
        - **Typical Re**: 0.1-100
        - **Laminar flow**: Essential for quality (no mixing of different viscosities)
        
        ### Transitional Flow (Usually Avoided)
        
        **Challenges:**
        - Unpredictable pressure drop
        - Fluctuating heat transfer
        - Unstable operation
        - Difficult to model
        
        **Where it occurs:**
        - Startup/shutdown operations
        - Variable flow systems without proper design
        - Should be avoided in steady-state operation
        """)
    
    with app_col2:
        st.markdown("""
        ### Turbulent Flow Applications
        
        **6. Water Distribution Systems**
        - **Typical Re**: 50,000-500,000 (highly turbulent)
        - **Pipe sizes**: 50-1000 mm
        - **Velocities**: 1-3 m/s
        - **Advantage**: Self-cleaning (prevents sediment buildup)
        - **Challenge**: Higher pressure drop requires pumping power
        
        **7. HVAC and Ventilation**
        - **Air ducts**: Re = 10,000-100,000
        - **Purpose**: Mixing for uniform temperature
        - **Design**: Turbulent flow enhances heat transfer
        - **Standards**: ASHRAE guidelines assume turbulent flow
        
        **8. Heat Exchangers**
        - **Typical Re**: 10,000-100,000
        - **Why turbulent**: Heat transfer coefficient h ∝ Re^0.8
        - **Improvement**: Turbulent flow can be 10-100× better than laminar
        - **Trade-off**: Higher pressure drop vs better heat transfer
        
        **9. Chemical Reactors**
        - **Purpose**: Mixing of reactants
        - **Typical Re**: 20,000-200,000
        - **Turbulent mixing**: Ensures uniform concentration
        - **Critical**: Reaction rates depend on mixing
        
        **10. Oil and Gas Pipelines**
        - **Long-distance transport**
        - **Typical Re**: 100,000-1,000,000
        - **Pipe sizes**: 200-1000 mm
        - **Challenge**: Huge pressure drops over long distances
        - **Optimization**: Minimize Re while maintaining flow rate
        
        **11. Fire Protection Systems**
        - **Sprinkler systems**: Re = 30,000-100,000
        - **Fire hoses**: Re = 50,000-200,000
        - **High velocity**: Necessary for throw distance
        - **Always turbulent**: Design assumes turbulent flow
        
        **12. Irrigation Systems**
        - **Center pivot**: Re = 20,000-80,000
        - **Drip irrigation**: Can be laminar or turbulent depending on size
        - **Design consideration**: Filter requirements based on flow regime
        """)
    
    st.markdown("---")
    
    st.markdown("### Design Guidelines")
    
    guide_col1, guide_col2, guide_col3 = st.columns(3)
    
    with guide_col1:
        st.markdown("""
        #### For Laminar Flow
        
        **Maintain laminar if Re < 2000:**
        - Avoid disturbances
        - Smooth pipe entrance
        - Minimize bends
        - Use flow straighteners
        
        **Advantages:**
        - Lower pressure drop
        - Predictable behavior
        - Analytical solutions exist
        
        **Disadvantages:**
        - Poor heat transfer
        - No self-cleaning
        - Particle settling
        """)
    
    with guide_col2:
        st.markdown("""
        #### For Turbulent Flow
        
        **Ensure Re > 4000 for stability:**
        - Design for higher velocity
        - Use turbulence promoters
        - Accept higher pressure drop
        
        **Advantages:**
        - Excellent heat transfer
        - Good mixing
        - Self-cleaning
        
        **Disadvantages:**
        - Higher energy consumption
        - More complex modeling
        - Potential for noise/vibration
        """)
    
    with guide_col3:
        st.markdown("""
        #### Avoid Transitional
        
        **Don't operate at 2300 < Re < 4000:**
        - Unpredictable
        - Unstable
        - Hard to model
        
        **If unavoidable:**
        - Use conservative safety factors
        - Expect variations
        - Monitor closely
        
        **Better approach:**
        - Design for Re < 2000 (laminar)
        - Or Re > 5000 (turbulent)
        """)

# Quick calculator at bottom
st.markdown("---")
st.header("🧮 Quick Reynolds Number Calculator")

calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)

with calc_col1:
    calc_rho = st.number_input("Density ρ (kg/m³)", value=1000.0, step=10.0, key="calc_rho")
    calc_V = st.number_input("Velocity V (m/s)", value=1.0, step=0.1, key="calc_V")

with calc_col2:
    calc_D = st.number_input("Diameter D (mm)", value=50.0, step=1.0, key="calc_D") / 1000
    calc_mu = st.number_input("Viscosity μ (Pa·s)", value=0.001, step=0.0001, format="%.4f", key="calc_mu")

with calc_col3:
    calc_Re = (calc_rho * calc_V * calc_D) / calc_mu if calc_mu > 0 else 0
    calc_regime = "Laminar 🟢" if calc_Re < 2300 else ("Transitional 🟡" if calc_Re <= 4000 else "Turbulent 🔴")
    st.metric("Reynolds Number", f"{calc_Re:,.0f}")
    st.metric("Flow Regime", calc_regime)

with calc_col4:
    calc_Q = (np.pi * calc_D**2 / 4) * calc_V * 1000  # L/s
    calc_f = (64 / calc_Re) if calc_Re < 2300 else (0.316 / (calc_Re**0.25))
    st.metric("Flow Rate (L/s)", f"{calc_Q:.2f}")
    st.metric("Friction Factor", f"{calc_f:.5f}")

st.caption("💡 **Quick calculator**: Instantly compute Reynolds number and flow regime for any pipe flow configuration.")

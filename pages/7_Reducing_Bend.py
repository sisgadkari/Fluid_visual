import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Pipe Bend Momentum Analysis", layout="wide")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>🔄 Momentum Analysis of Reducing Pipe Bends</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
Explore how changes in fluid momentum create forces on pipe bends with changing diameter.
Understand the combined effects of direction change and velocity change through interactive visualization.
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# Create tabs for different aspects
tab1, tab2, tab3 = st.tabs(["🎯 Interactive Simulation", "📚 Understanding Momentum Forces", "📋 Real-World Applications"])

with tab1:
    # --- Main Layout ---
    col1, col2 = st.columns([2, 3])

    # --- Column 1: Inputs and Results ---
    with col1:
        st.header("🔬 Parameters")
        
        # --- Interactive Scenarios ---
        SCENARIOS = {
            "Custom...": {
                "D1": 20.0, "D2": 10.0, "theta": 45, "Q": 10.0, "p1": 200.0, "fluid": "Water",
                "desc": "Manually adjust all parameters below."
            },
            "Water Distribution 90° Elbow": {
                "D1": 15.0, "D2": 15.0, "theta": 90, "Q": 15.0, "p1": 300.0, "fluid": "Water",
                "desc": "Standard 90° pipe elbow: same diameter, right-angle turn. Common in municipal water systems."
            },
            "Industrial Reducer 45°": {
                "D1": 30.0, "D2": 15.0, "theta": 45, "Q": 25.0, "p1": 500.0, "fluid": "Water",
                "desc": "Reducing bend: 30cm to 15cm, 45° turn. High velocity change creates significant forces."
            },
            "HVAC Duct Transition": {
                "D1": 40.0, "D2": 30.0, "theta": 60, "Q": 0.5, "p1": 0.5, "fluid": "Air",
                "desc": "Air handling system: 40cm to 30cm, 60° turn. Low density but high volume flow."
            },
            "Oil Pipeline Bend": {
                "D1": 25.0, "D2": 20.0, "theta": 30, "Q": 20.0, "p1": 800.0, "fluid": "Oil",
                "desc": "Oil pipeline: 25cm to 20cm, gentle 30° turn. Higher density increases momentum forces."
            },
            "Fire Hydrant Branch": {
                "D1": 10.0, "D2": 6.5, "theta": 90, "Q": 8.0, "p1": 600.0, "fluid": "Water",
                "desc": "Fire protection system: 10cm main to 6.5cm branch at 90°. High pressure, rapid diameter change."
            }
        }
        
        scenario = st.selectbox("Select Application Scenario", list(SCENARIOS.keys()))
        selected = SCENARIOS[scenario]
        st.info(selected["desc"])
        
        st.subheader("Fluid Properties")
        fluid_type = st.selectbox("Select Fluid", ["Water", "Air", "Oil", "Custom"], 
                                  index=["Water", "Air", "Oil", "Custom"].index(selected["fluid"]) if selected["fluid"] in ["Water", "Air", "Oil"] else 0)
        
        if fluid_type == "Water":
            rho = 1000.0  # kg/m³
        elif fluid_type == "Air":
            rho = 1.2  # kg/m³
        elif fluid_type == "Oil":
            rho = 850.0  # kg/m³
        else:
            rho = st.number_input("Fluid Density ρ (kg/m³)", value=1000.0, min_value=0.1, step=10.0)
        
        st.caption(f"ρ = {rho:.1f} kg/m³")
        
        st.subheader("Pipe Geometry")
        c1, c2 = st.columns(2)
        with c1:
            D1_cm = st.slider("Inlet Diameter D₁ (cm)", 5.0, 100.0, selected["D1"], step=0.5,
                             help="Diameter of inlet pipe")
            D1 = D1_cm / 100  # Convert to meters
        with c2:
            D2_cm = st.slider("Outlet Diameter D₂ (cm)", 5.0, min(100.0, D1_cm), selected["D2"], step=0.5,
                             help="Diameter of outlet pipe (≤ inlet for reducing bend)")
            D2 = D2_cm / 100
        
        theta_deg = st.slider("Bend Angle θ (degrees)", 0, 180, selected["theta"], step=5,
                             help="Angle between inlet and outlet directions")
        theta = np.radians(theta_deg)
        
        st.subheader("Flow Conditions")
        c1, c2 = st.columns(2)
        with c1:
            Q_L_s = st.number_input("Flow Rate Q (L/s)", value=selected["Q"], min_value=0.1, step=0.5,
                                   help="Volumetric flow rate")
            Q = Q_L_s / 1000  # Convert to m³/s
        with c2:
            p1_gauge_kPa = st.number_input("Inlet Gauge Pressure p₁ (kPa)", value=selected["p1"], min_value=0.0, step=10.0,
                                          help="Gauge pressure at inlet")
            p1_gauge = p1_gauge_kPa * 1000  # Convert to Pa

        # --- Calculations ---
        # Areas
        A1 = np.pi * (D1/2)**2
        A2 = np.pi * (D2/2)**2
        
        # Velocities (continuity equation)
        U1 = Q / A1 if A1 > 0 else 0
        U2 = Q / A2 if A2 > 0 else 0
        
        # Mass flow rate
        m_dot = rho * Q
        
        # Outlet pressure (Bernoulli equation, neglecting elevation and losses)
        p2_gauge = p1_gauge + 0.5 * rho * (U1**2 - U2**2)
        p2_gauge_kPa = p2_gauge / 1000
        
        # Momentum equation for force on fluid
        # x-direction (horizontal, inlet direction)
        Fx_fluid = m_dot * (U2 * np.cos(theta) - U1) + p1_gauge * A1 - p2_gauge * A2 * np.cos(theta)
        
        # y-direction (perpendicular to inlet)
        Fy_fluid = m_dot * U2 * np.sin(theta) - p2_gauge * A2 * np.sin(theta)
        
        # Reaction force on pipe (Newton's third law)
        Rx = -Fx_fluid
        Ry = -Fy_fluid
        
        # Resultant force magnitude and direction
        R = np.sqrt(Rx**2 + Ry**2)
        phi = np.degrees(np.arctan2(Ry, Rx)) if Rx != 0 else (90 if Ry > 0 else -90)
        
        # Dynamic pressure
        q1 = 0.5 * rho * U1**2
        q2 = 0.5 * rho * U2**2
        
        # Reynolds number (assuming water viscosity μ = 0.001 Pa·s, or air μ = 1.8e-5 Pa·s)
        mu = 0.001 if fluid_type in ["Water", "Oil"] else 1.8e-5
        Re1 = (rho * U1 * D1) / mu if mu > 0 else 0
        Re2 = (rho * U2 * D2) / mu if mu > 0 else 0

        st.markdown("---")
        st.header("📈 Results Summary")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric(label="Resultant Force on Pipe (|R|)", value=f"{R:.1f} N",
                      help="Magnitude of total force that pipe must resist")
            st.metric(label="Force Direction (φ)", value=f"{phi:.1f}°",
                      help="Angle of resultant force from horizontal (inlet direction)")
        with col_r2:
            st.metric(label="Horizontal Component (Rₓ)", value=f"{Rx:.1f} N",
                      help="Force component in inlet direction")
            st.metric(label="Vertical Component (Rᵧ)", value=f"{Ry:.1f} N",
                      help="Force component perpendicular to inlet")
        
        col_r3, col_r4 = st.columns(2)
        with col_r3:
            st.metric(label="Inlet Velocity (U₁)", value=f"{U1:.2f} m/s",
                      help="Average velocity at inlet")
            st.metric(label="Outlet Velocity (U₂)", value=f"{U2:.2f} m/s",
                      help="Average velocity at outlet")
        with col_r4:
            st.metric(label="Mass Flow Rate (ṁ)", value=f"{m_dot:.2f} kg/s",
                      help="Mass of fluid passing through per second")
            st.metric(label="Outlet Pressure (p₂)", value=f"{p2_gauge_kPa:.1f} kPa",
                      help="Gauge pressure at outlet")
        
        st.markdown("---")
        st.header("🧮 Step-by-Step Calculation")
        
        with st.expander("📖 See Detailed Breakdown", expanded=False):
            st.markdown("### Momentum Analysis of Reducing Pipe Bend")
            
            st.markdown("#### Step 1: Calculate Pipe Areas")
            st.write("Cross-sectional areas from diameters:")
            st.latex(r'A = \pi \left(\frac{D}{2}\right)^2')
            st.write(f"\n**Inlet:**")
            st.write(f"A₁ = π × ({D1_cm/100}/2)² = π × ({D1/2:.4f})²")
            st.write(f"A₁ = **{A1:.6f} m²** = **{A1*10000:.2f} cm²**")
            
            st.write(f"\n**Outlet:**")
            st.write(f"A₂ = π × ({D2_cm/100}/2)² = π × ({D2/2:.4f})²")
            st.write(f"A₂ = **{A2:.6f} m²** = **{A2*10000:.2f} cm²**")
            
            area_ratio = A1 / A2 if A2 > 0 else 0
            st.write(f"\n**Area ratio**: A₁/A₂ = {area_ratio:.2f}")
            if area_ratio > 1:
                st.write(f"→ This is a **reducing bend** (converging)")
            elif area_ratio < 1:
                st.write(f"→ This is an **expanding bend** (diverging)")
            else:
                st.write(f"→ This is a **constant diameter bend**")
            
            st.markdown("#### Step 2: Apply Continuity Equation")
            st.write("For incompressible flow, volumetric flow rate is constant:")
            st.latex(r'Q = A_1 U_1 = A_2 U_2')
            st.write("Solving for velocities:")
            st.latex(r'U_1 = \frac{Q}{A_1} \quad , \quad U_2 = \frac{Q}{A_2}')
            
            st.write(f"\n**Calculations:**")
            st.write(f"Q = {Q_L_s} L/s = {Q:.6f} m³/s")
            st.write(f"\nU₁ = {Q:.6f} / {A1:.6f} = **{U1:.3f} m/s**")
            st.write(f"U₂ = {Q:.6f} / {A2:.6f} = **{U2:.3f} m/s**")
            
            velocity_ratio = U2 / U1 if U1 > 0 else 0
            st.write(f"\n**Velocity ratio**: U₂/U₁ = {velocity_ratio:.2f}")
            st.write(f"→ Velocity **increases by {((velocity_ratio-1)*100):.1f}%**" if velocity_ratio > 1 else f"→ Velocity **decreases by {((1-velocity_ratio)*100):.1f}%**")
            
            st.write(f"\n**Mass flow rate:**")
            st.latex(r'\dot{m} = \rho Q')
            st.write(f"ṁ = {rho} kg/m³ × {Q:.6f} m³/s = **{m_dot:.3f} kg/s**")
            
            st.markdown("#### Step 3: Apply Bernoulli Equation")
            st.write("Neglecting elevation change and friction losses:")
            st.latex(r'p_1 + \frac{1}{2}\rho U_1^2 = p_2 + \frac{1}{2}\rho U_2^2')
            st.write("Solving for outlet pressure:")
            st.latex(r'p_2 = p_1 + \frac{1}{2}\rho(U_1^2 - U_2^2)')
            
            st.write(f"\n**Calculation:**")
            st.write(f"p₂ = {p1_gauge_kPa} kPa + 0.5 × {rho} kg/m³ × ({U1:.3f}² - {U2:.3f}²) m²/s²")
            st.write(f"p₂ = {p1_gauge_kPa} + 0.5 × {rho} × ({U1**2:.3f} - {U2**2:.3f})")
            st.write(f"p₂ = {p1_gauge_kPa} + {0.5*rho*(U1**2 - U2**2)/1000:.2f}")
            st.write(f"p₂ = **{p2_gauge_kPa:.2f} kPa**")
            
            pressure_change = p2_gauge_kPa - p1_gauge_kPa
            if pressure_change < 0:
                st.write(f"\n→ Pressure **decreases by {abs(pressure_change):.2f} kPa** (acceleration)")
            elif pressure_change > 0:
                st.write(f"\n→ Pressure **increases by {pressure_change:.2f} kPa** (deceleration)")
            else:
                st.write(f"\n→ Pressure **remains constant** (no velocity change)")
            
            st.markdown("#### Step 4: Apply Momentum Equation")
            st.write("The momentum equation relates forces to momentum change:")
            st.latex(r'\vec{F} = \dot{m}(\vec{U}_2 - \vec{U}_1) + p_1 A_1 \vec{n}_1 + p_2 A_2 \vec{n}_2')
            
            st.write("\nWhere:")
            st.write("• **ṁ(U₂ - U₁)** = momentum flux change")
            st.write("• **p₁A₁n₁** = pressure force at inlet (pointing in flow direction)")
            st.write("• **p₂A₂n₂** = pressure force at outlet (pointing against flow direction)")
            
            st.write(f"\n**Breaking into components:**")
            
            st.write("\n**X-direction (horizontal, inlet direction):**")
            st.write("• U₁ₓ = U₁ (inlet horizontal)")
            st.write(f"• U₂ₓ = U₂ cos(θ) = {U2:.3f} × cos({theta_deg}°) = {U2*np.cos(theta):.3f} m/s")
            st.write(f"• Momentum flux: ṁ(U₂ₓ - U₁ₓ) = {m_dot:.3f} × ({U2*np.cos(theta):.3f} - {U1:.3f}) = {m_dot*(U2*np.cos(theta) - U1):.2f} N")
            st.write(f"• Pressure at inlet: p₁A₁ = {p1_gauge_kPa} × {A1*10000:.2f} = {p1_gauge*A1:.2f} N")
            st.write(f"• Pressure at outlet: p₂A₂cos(θ) = {p2_gauge_kPa} × {A2*10000:.2f} × cos({theta_deg}°) = {p2_gauge*A2*np.cos(theta):.2f} N")
            
            st.latex(r'F_x = \dot{m}(U_{2x} - U_{1x}) + p_1 A_1 - p_2 A_2 \cos\theta')
            st.write(f"Fₓ = {m_dot*(U2*np.cos(theta) - U1):.2f} + {p1_gauge*A1:.2f} - {p2_gauge*A2*np.cos(theta):.2f}")
            st.write(f"Fₓ = **{Fx_fluid:.2f} N** (force on fluid)")
            
            st.write("\n**Y-direction (vertical, perpendicular to inlet):**")
            st.write("• U₁ᵧ = 0 (inlet is horizontal)")
            st.write(f"• U₂ᵧ = U₂ sin(θ) = {U2:.3f} × sin({theta_deg}°) = {U2*np.sin(theta):.3f} m/s")
            st.write(f"• Momentum flux: ṁU₂ᵧ = {m_dot:.3f} × {U2*np.sin(theta):.3f} = {m_dot*U2*np.sin(theta):.2f} N")
            st.write(f"• Pressure at outlet: p₂A₂sin(θ) = {p2_gauge_kPa} × {A2*10000:.2f} × sin({theta_deg}°) = {p2_gauge*A2*np.sin(theta):.2f} N")
            
            st.latex(r'F_y = \dot{m}U_{2y} - p_2 A_2 \sin\theta')
            st.write(f"Fᵧ = {m_dot*U2*np.sin(theta):.2f} - {p2_gauge*A2*np.sin(theta):.2f}")
            st.write(f"Fᵧ = **{Fy_fluid:.2f} N** (force on fluid)")
            
            st.markdown("#### Step 5: Find Reaction Force on Pipe")
            st.write("By Newton's third law, the pipe exerts force F on fluid, so fluid exerts -F on pipe:")
            st.latex(r'\vec{R} = -\vec{F}')
            
            st.write(f"\n**Reaction components:**")
            st.write(f"Rₓ = -Fₓ = **{Rx:.2f} N**")
            st.write(f"Rᵧ = -Fᵧ = **{Ry:.2f} N**")
            
            st.write(f"\n**Resultant magnitude:**")
            st.latex(r'|R| = \sqrt{R_x^2 + R_y^2}')
            st.write(f"|R| = √({Rx:.2f}² + {Ry:.2f}²)")
            st.write(f"|R| = √({Rx**2:.2f} + {Ry**2:.2f})")
            st.write(f"|R| = **{R:.2f} N** = **{R/1000:.3f} kN**")
            
            st.write(f"\n**Direction:**")
            st.latex(r'\phi = \tan^{-1}\left(\frac{R_y}{R_x}\right)')
            st.write(f"φ = tan⁻¹({Ry:.2f}/{Rx:.2f})")
            st.write(f"φ = **{phi:.2f}°** from horizontal (inlet direction)")
            
            st.markdown("### Physical Interpretation")
            
            # Categorize force magnitude
            if R < 100:
                st.info(f"💡 **Small force** ({R:.1f} N ≈ {R/9.81:.1f} kg weight): Typical for small domestic pipes. Standard pipe supports adequate.")
            elif R < 1000:
                st.success(f"✅ **Moderate force** ({R:.1f} N ≈ {R/9.81:.1f} kg weight): Common in industrial systems. Requires proper anchoring.")
            elif R < 10000:
                st.warning(f"⚠️ **Large force** ({R:.1f} N ≈ {R/9.81:.1f} kg weight): Significant in large pipelines. Heavy-duty supports needed.")
            else:
                st.error(f"❗ **Very large force** ({R:.1f} N ≈ {R/9.81:.1f} kg weight): Major pipeline system. Professional structural design essential.")
            
            # Analyze contributions
            st.write(f"\n**Force contributions:**")
            momentum_contribution = m_dot * (U2 - U1) if theta_deg == 0 else m_dot * np.sqrt((U2*np.cos(theta) - U1)**2 + (U2*np.sin(theta))**2)
            pressure_contribution = np.sqrt((p1_gauge*A1 - p2_gauge*A2*np.cos(theta))**2 + (p2_gauge*A2*np.sin(theta))**2)
            
            st.write(f"• Momentum change: ≈{momentum_contribution:.1f} N")
            st.write(f"• Pressure forces: ≈{pressure_contribution:.1f} N")
            
            if momentum_contribution > pressure_contribution:
                st.write("→ **Momentum change dominates** (high velocity change or large diameter reduction)")
            else:
                st.write("→ **Pressure forces dominate** (high pressure or large areas)")
        
        st.markdown("---")
        st.header("🔍 Analysis Insights")
        
        with st.expander("💡 Parameter Effects on Force", expanded=False):
            st.markdown("**How each parameter affects the force on the pipe:**")
            
            st.markdown("#### 1. Effect of Bend Angle (θ)")
            st.write(f"• Current angle: **θ = {theta_deg}°**")
            st.write(f"• **Key relationship**: Both momentum and pressure forces have directional components")
            
            st.write("\n**Force at different angles (keeping other parameters constant):**")
            angles = [0, 30, 45, 60, 90, 120, 180]
            angle_data = []
            for angle in angles:
                angle_rad = np.deg2rad(angle)
                fx = m_dot * (U2 * np.cos(angle_rad) - U1) + p1_gauge * A1 - p2_gauge * A2 * np.cos(angle_rad)
                fy = m_dot * U2 * np.sin(angle_rad) - p2_gauge * A2 * np.sin(angle_rad)
                r = np.sqrt(fx**2 + fy**2)
                angle_data.append({
                    "Angle (°)": angle,
                    "Rₓ (N)": f"{-fx:.1f}",
                    "Rᵧ (N)": f"{-fy:.1f}",
                    "|R| (N)": f"{r:.1f}",
                    "Ratio": f"{r/R:.2f}" if R > 0 else "-"
                })
            st.table(pd.DataFrame(angle_data))
            
            st.success("✅ **Key insights**: \n• At 0° (straight pipe): Only x-component exists\n• At 90°: Maximum y-component\n• At 180° (U-turn): Maximum total force")
            
            st.markdown("#### 2. Effect of Diameter Ratio (D₂/D₁)")
            st.write(f"• Current ratio: **D₂/D₁ = {D2_cm/D1_cm:.3f}**")
            st.write(f"• Velocity ratio: **U₂/U₁ = {U2/U1:.3f}** (inverse of area ratio)")
            
            st.write("\n**Force for different diameter ratios:**")
            diameter_ratios = [0.5, 0.7, 0.85, 1.0]
            diameter_data = []
            for d_ratio in diameter_ratios:
                d2_temp = D1 * d_ratio
                a2_temp = np.pi * (d2_temp/2)**2
                u2_temp = Q / a2_temp if a2_temp > 0 else 0
                p2_temp = p1_gauge + 0.5 * rho * (U1**2 - u2_temp**2)
                fx = m_dot * (u2_temp * np.cos(theta) - U1) + p1_gauge * A1 - p2_temp * a2_temp * np.cos(theta)
                fy = m_dot * u2_temp * np.sin(theta) - p2_temp * a2_temp * np.sin(theta)
                r = np.sqrt(fx**2 + fy**2)
                diameter_data.append({
                    "D₂/D₁": f"{d_ratio:.2f}",
                    "U₂/U₁": f"{u2_temp/U1:.2f}",
                    "ΔP (kPa)": f"{(p2_temp - p1_gauge)/1000:.1f}",
                    "|R| (N)": f"{r:.1f}",
                    "vs current": f"{r/R:.2f}×" if R > 0 else "-"
                })
            st.table(pd.DataFrame(diameter_data))
            
            st.warning("⚠️ **Critical insight**: Smaller D₂/D₁ → Higher velocity change → More momentum force → Larger total force")
            
            st.markdown("#### 3. Effect of Flow Rate (Q)")
            st.write(f"• Current flow: **Q = {Q_L_s} L/s**")
            st.write(f"• **Relationship**: Force increases with Q because both ṁ and velocities increase")
            
            st.write("\n**Force at different flow rates:**")
            flow_rates = [Q_L_s * 0.5, Q_L_s * 0.75, Q_L_s, Q_L_s * 1.5, Q_L_s * 2.0]
            flow_data = []
            for q_temp in flow_rates:
                q_m3s = q_temp / 1000
                m_temp = rho * q_m3s
                u1_temp = q_m3s / A1
                u2_temp = q_m3s / A2
                p2_temp = p1_gauge + 0.5 * rho * (u1_temp**2 - u2_temp**2)
                fx = m_temp * (u2_temp * np.cos(theta) - u1_temp) + p1_gauge * A1 - p2_temp * A2 * np.cos(theta)
                fy = m_temp * u2_temp * np.sin(theta) - p2_temp * A2 * np.sin(theta)
                r = np.sqrt(fx**2 + fy**2)
                flow_data.append({
                    "Q (L/s)": f"{q_temp:.1f}",
                    "ṁ (kg/s)": f"{m_temp:.2f}",
                    "U₂ (m/s)": f"{u2_temp:.2f}",
                    "|R| (N)": f"{r:.1f}",
                    "Scaling": f"{r/R:.2f}×" if R > 0 else "-"
                })
            st.table(pd.DataFrame(flow_data))
            
            st.error("❗ **Important**: Force increases **faster** than flow rate (approximately as Q²) due to velocity-squared term in momentum!")
            
            st.markdown("#### 4. Effect of Inlet Pressure (p₁)")
            st.write(f"• Current pressure: **p₁ = {p1_gauge_kPa} kPa**")
            st.write(f"• **Note**: Pressure affects outlet pressure but momentum change depends mainly on velocities")
            
            st.write("\n**Force at different inlet pressures:**")
            pressures = [p1_gauge_kPa * 0.5, p1_gauge_kPa * 0.75, p1_gauge_kPa, p1_gauge_kPa * 1.5, p1_gauge_kPa * 2.0]
            pressure_data = []
            for p_temp in pressures:
                p_temp_pa = p_temp * 1000
                p2_temp = p_temp_pa + 0.5 * rho * (U1**2 - U2**2)
                fx = m_dot * (U2 * np.cos(theta) - U1) + p_temp_pa * A1 - p2_temp * A2 * np.cos(theta)
                fy = m_dot * U2 * np.sin(theta) - p2_temp * A2 * np.sin(theta)
                r = np.sqrt(fx**2 + fy**2)
                pressure_data.append({
                    "p₁ (kPa)": f"{p_temp:.0f}",
                    "p₂ (kPa)": f"{p2_temp/1000:.0f}",
                    "|R| (N)": f"{r:.1f}",
                    "vs current": f"{r/R:.2f}×" if R > 0 else "-"
                })
            st.table(pd.DataFrame(pressure_data))
            
            st.info("💡 **Insight**: Pressure has **moderate** effect on force. Momentum change often dominates in high-velocity systems.")

        with st.expander("⚙️ Design Considerations for Pipe Bends", expanded=False):
            st.markdown("**Engineering considerations for piping systems with bends:**")
            
            st.markdown("#### 1. Support and Anchoring Requirements")
            
            st.write("**A. Anchor Blocks**")
            st.write(f"• Required anchor capacity: ≥ {R*1.5:.0f} N (with SF = 1.5)")
            st.write(f"• Direction: {phi:.1f}° from inlet direction")
            st.write("• Typical anchor types:")
            if R < 500:
                st.write("  - Pipe clamps with brackets (light duty)")
                st.write("  - Wall-mounted supports")
            elif R < 5000:
                st.write("  - Concrete thrust blocks")
                st.write("  - Steel anchor frames")
            else:
                st.write("  - Large reinforced concrete blocks")
                st.write("  - Deep foundation systems")
            
            st.write("\n**B. Support Spacing**")
            st.write("Maximum unsupported span recommendations:")
            if D1_cm < 5:
                st.write("• Small pipe (< 5cm): 1-2 m spacing")
            elif D1_cm < 15:
                st.write("• Medium pipe (5-15cm): 2-4 m spacing")
            elif D1_cm < 40:
                st.write("• Large pipe (15-40cm): 4-6 m spacing")
            else:
                st.write("• Extra large pipe (> 40cm): 6-9 m spacing")
            
            st.markdown("#### 2. Bend Design Selection")
            
            st.write("**A. Standard vs Long Radius Bends**")
            st.write("\n**Standard radius:** R = 1.5D (more compact, higher pressure drop)")
            st.write("**Long radius:** R = 3D (lower pressure drop, easier flow)")
            st.write("**Extra long:** R = 5D (minimal pressure drop, large space)")
            
            st.write(f"\nFor your pipe (D₁ = {D1_cm:.1f} cm):")
            st.write(f"• Standard radius: R ≈ {D1_cm*1.5:.1f} cm")
            st.write(f"• Long radius: R ≈ {D1_cm*3:.1f} cm")
            
            st.write("\n**B. Mitered vs Smooth Bends**")
            st.write("• **Mitered** (welded sections): Lower cost, higher losses, higher forces")
            st.write("• **Smooth** (formed/cast): Higher cost, lower losses, lower forces")
            st.write(f"• For θ = {theta_deg}°: " + ("Smooth bend recommended" if theta_deg > 45 else "Either type acceptable"))
            
            st.markdown("#### 3. Pressure Loss Estimation")
            
            st.write("**Loss coefficient method:**")
            st.latex(r'\Delta p_{loss} = K \times \frac{1}{2}\rho U^2')
            
            # Estimate K based on angle (rough approximation)
            if theta_deg <= 45:
                K = 0.2
            elif theta_deg <= 90:
                K = 0.4
            else:
                K = 0.7
            
            pressure_loss = K * 0.5 * rho * U1**2 / 1000  # kPa
            st.write(f"\nFor {theta_deg}° bend: K ≈ {K}")
            st.write(f"Estimated pressure loss: Δp ≈ {pressure_loss:.2f} kPa")
            st.write(f"This is {pressure_loss/p1_gauge_kPa*100:.1f}% of inlet pressure")
            
            st.markdown("#### 4. Material and Wall Thickness")
            
            st.write("**Pressure-based wall thickness (Barlow's formula):**")
            st.latex(r't = \frac{pD}{2S \times E}')
            st.write("Where:")
            st.write("• p = design pressure (with safety factor)")
            st.write("• D = pipe diameter")
            st.write("• S = allowable stress (material dependent)")
            st.write("• E = weld joint efficiency")
            
            # Example calculation
            design_pressure = max(p1_gauge_kPa, p2_gauge_kPa) * 1.5  # 50% safety factor
            allowable_stress_mpa = 150  # Typical for carbon steel
            E = 1.0  # Seamless pipe
            
            t1_mm = (design_pressure * D1_cm * 10) / (2 * allowable_stress_mpa * E * 1000)
            t2_mm = (design_pressure * D2_cm * 10) / (2 * allowable_stress_mpa * E * 1000)
            
            st.write(f"\n**Example for carbon steel** (S = {allowable_stress_mpa} MPa):")
            st.write(f"• Inlet: t₁ ≥ {t1_mm:.2f} mm → Use Schedule 40 or higher")
            st.write(f"• Outlet: t₂ ≥ {t2_mm:.2f} mm")
            
            st.markdown("#### 5. Special Considerations")
            
            st.write("**A. Waterhammer Protection**")
            st.write("• Sudden valve closure can multiply forces by 10-100×")
            st.write("• Install surge protection: pressure relief valves, surge tanks")
            st.write(f"• For Q = {Q_L_s} L/s, consider surge analysis")
            
            st.write("\n**B. Thermal Expansion**")
            st.write("• Temperature changes cause expansion/contraction")
            st.write("• Provide expansion loops or joints")
            st.write("• Maintain flexibility in piping system")
            
            st.write("\n**C. Erosion and Corrosion**")
            if U2 > 3:
                st.write(f"• High outlet velocity ({U2:.2f} m/s) may cause erosion")
                st.write("• Consider erosion-resistant lining")
            st.write("• Regular inspection at bends (erosion-prone)")
            st.write("• Cathodic protection for buried pipes")

        with st.expander("📊 Flow Regime Analysis", expanded=False):
            st.markdown("**Flow characteristics and Reynolds numbers:**")
            
            st.write(f"**Reynolds numbers:**")
            st.write(f"• Inlet: Re₁ = {Re1:.0f}")
            st.write(f"• Outlet: Re₂ = {Re2:.0f}")
            
            st.write("\n**Flow regimes:**")
            
            # Inlet regime
            if Re1 < 2300:
                st.success(f"✅ **Inlet**: Laminar flow (Re < 2300)")
                st.write("• Smooth, predictable flow")
                st.write("• Lower friction losses")
            elif Re1 < 4000:
                st.warning(f"⚠️ **Inlet**: Transitional flow (2300 < Re < 4000)")
                st.write("• Unstable, may switch between laminar/turbulent")
                st.write("• Difficult to predict accurately")
            else:
                st.info(f"💡 **Inlet**: Turbulent flow (Re > 4000)")
                st.write("• Chaotic, mixing flow")
                st.write("• Higher friction losses")
            
            # Outlet regime
            if Re2 < 2300:
                st.success(f"✅ **Outlet**: Laminar flow (Re < 2300)")
            elif Re2 < 4000:
                st.warning(f"⚠️ **Outlet**: Transitional flow (2300 < Re < 4000)")
            else:
                st.info(f"💡 **Outlet**: Turbulent flow (Re > 4000)")
            
            st.write(f"\n**Dynamic pressures:**")
            st.write(f"• Inlet: q₁ = ½ρU₁² = {q1/1000:.2f} kPa")
            st.write(f"• Outlet: q₂ = ½ρU₂² = {q2/1000:.2f} kPa")
            st.write(f"• Change: Δq = {(q2-q1)/1000:.2f} kPa")
            
            st.write("\n**Velocity heads:**")
            h1 = U1**2 / (2 * 9.81)
            h2 = U2**2 / (2 * 9.81)
            st.write(f"• Inlet: h₁ = U₁²/(2g) = {h1:.2f} m")
            st.write(f"• Outlet: h₂ = U₂²/(2g) = {h2:.2f} m")

    # --- Column 2: Visualization ---
    with col2:
        st.header("🖼️ Visualization")

        fig = go.Figure()
        
        # Pipe bend geometry
        inlet_length = 0.8
        outlet_length = 0.8
        bend_radius = 0.8
        
        # Inlet section (horizontal, pointing right)
        inlet_x = [-inlet_length, 0]
        inlet_y_top = [D1/2, D1/2]
        inlet_y_bot = [-D1/2, -D1/2]
        
        # Bend section (reducing diameter)
        n_bend = 50
        bend_angles = np.linspace(0, theta, n_bend)
        D_bend = np.linspace(D1, D2, n_bend)
        
        x_centerline = bend_radius * np.sin(bend_angles)
        y_centerline = bend_radius * (1 - np.cos(bend_angles))
        
        x_bend_top, y_bend_top = [], []
        x_bend_bot, y_bend_bot = [], []
        
        for i in range(n_bend):
            normal_angle = bend_angles[i] + np.pi/2
            x_bend_top.append(x_centerline[i] + D_bend[i]/2 * np.cos(normal_angle))
            y_bend_top.append(y_centerline[i] + D_bend[i]/2 * np.sin(normal_angle))
            x_bend_bot.append(x_centerline[i] - D_bend[i]/2 * np.cos(normal_angle))
            y_bend_bot.append(y_centerline[i] - D_bend[i]/2 * np.sin(normal_angle))
        
        # Outlet section
        outlet_start_x = x_centerline[-1]
        outlet_start_y = y_centerline[-1]
        outlet_end_x = outlet_start_x + outlet_length * np.cos(theta)
        outlet_end_y = outlet_start_y + outlet_length * np.sin(theta)
        
        outlet_normal = theta + np.pi/2
        outlet_x_top = [outlet_start_x + D2/2 * np.cos(outlet_normal), 
                        outlet_end_x + D2/2 * np.cos(outlet_normal)]
        outlet_y_top = [outlet_start_y + D2/2 * np.sin(outlet_normal), 
                        outlet_end_y + D2/2 * np.sin(outlet_normal)]
        outlet_x_bot = [outlet_start_x - D2/2 * np.cos(outlet_normal), 
                        outlet_end_x - D2/2 * np.cos(outlet_normal)]
        outlet_y_bot = [outlet_start_y - D2/2 * np.sin(outlet_normal), 
                        outlet_end_y - D2/2 * np.sin(outlet_normal)]
        
        # Combine all sections for pipe walls
        x_top = inlet_x + x_bend_top + outlet_x_top
        y_top = inlet_y_top + y_bend_top + outlet_y_top
        
        x_bot = inlet_x + x_bend_bot + outlet_x_bot
        y_bot = inlet_y_bot + y_bend_bot + outlet_y_bot
        
        # Draw pipe walls
        fig.add_trace(go.Scatter(
            x=x_top, y=y_top, 
            mode='lines', 
            line=dict(color='black', width=3), 
            showlegend=False, 
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=x_bot, y=y_bot, 
            mode='lines', 
            line=dict(color='black', width=3), 
            showlegend=False, 
            hoverinfo='skip'
        ))
        
        # Fill pipe with fluid color
        x_fill = x_top + outlet_x_bot[::-1] + x_bend_bot[::-1] + inlet_x[::-1]
        y_fill = y_top + outlet_y_bot[::-1] + y_bend_bot[::-1] + inlet_y_bot[::-1]
        
        fluid_color = 'rgba(59, 130, 246, 0.5)' if fluid_type == "Water" else ('rgba(200, 200, 200, 0.3)' if fluid_type == "Air" else 'rgba(139, 69, 19, 0.5)')
        
        fig.add_trace(go.Scatter(
            x=x_fill, y=y_fill, 
            fill="toself", 
            fillcolor=fluid_color, 
            mode='none', 
            showlegend=False, 
            hoverinfo='skip'
        ))
        
        # Flow direction arrows
        fig.add_annotation(
            x=-inlet_length*0.7, y=0,
            ax=-inlet_length*0.7 - 0.25, ay=0,
            showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3, arrowcolor='darkblue'
        )
        
        arrow_x = outlet_start_x + outlet_length*0.5 * np.cos(theta)
        arrow_y = outlet_start_y + outlet_length*0.5 * np.sin(theta)
        fig.add_annotation(
            x=arrow_x, y=arrow_y,
            ax=arrow_x - 0.25*np.cos(theta), ay=arrow_y - 0.25*np.sin(theta),
            showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3, arrowcolor='darkblue'
        )
        
        # Labels
        fig.add_annotation(
            x=-inlet_length/2, y=D1/2+0.2,
            text=f"<b>D₁={D1_cm:.1f}cm</b><br>U₁={U1:.2f}m/s<br>p₁={p1_gauge_kPa:.0f}kPa",
            showarrow=False,
            font=dict(size=12),
            bgcolor="white",
            borderwidth=1,
            borderpad=3
        )
        
        outlet_label_x = outlet_start_x + outlet_length*0.5*np.cos(theta)
        outlet_label_y = outlet_start_y + outlet_length*0.5*np.sin(theta) + D2/2 + 0.25
        fig.add_annotation(
            x=outlet_label_x, y=outlet_label_y,
            text=f"<b>D₂={D2_cm:.1f}cm</b><br>U₂={U2:.2f}m/s<br>p₂={p2_gauge_kPa:.0f}kPa",
            showarrow=False,
            font=dict(size=12),
            bgcolor="white",
            borderwidth=1,
            borderpad=3
        )
        
        # Angle annotation
        if theta_deg > 5:  # Only show if bend angle is significant
            angle_arc_radius = bend_radius + D1/2 + 0.3
            fig.add_annotation(
                x=angle_arc_radius*np.sin(theta/2),
                y=angle_arc_radius*(1-np.cos(theta/2)) - 0.1,
                text=f"<b>θ={theta_deg}°</b>",
                showarrow=False,
                font=dict(size=14, color='red')
            )
        
        # Resultant force vector
        force_x_pos = (bend_radius + D1/2) * np.sin(theta/2) if theta_deg > 5 else 0.4
        force_y_pos = (bend_radius + D1/2) * (1 - np.cos(theta/2)) + 1.0 if theta_deg > 5 else 1.0
        force_length = 0.5
        
        phi_rad = np.radians(phi)
        force_arrow_x = force_x_pos + force_length * np.cos(phi_rad)
        force_arrow_y = force_y_pos + force_length * np.sin(phi_rad)
        
        fig.add_annotation(
            x=force_arrow_x, y=force_arrow_y,
            ax=force_x_pos, ay=force_y_pos,
            showarrow=True,
            arrowhead=3,
            arrowsize=2,
            arrowwidth=5,
            arrowcolor="red"
        )
        
        fig.add_annotation(
            x=force_arrow_x, y=force_arrow_y + 0.2,
            text=f"<b>R = {R/1000:.2f} kN</b><br><b>φ = {phi:.1f}°</b>",
            font=dict(color="red", size=16),
            showarrow=False
        )
        
        # Update layout
        all_x = x_top + x_bot
        all_y = y_top + y_bot
        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)
        
        padding_x = (x_max - x_min) * 0.3
        padding_y = (y_max - y_min) * 0.3
        
        fig.update_layout(
            xaxis=dict(
                range=[x_min - padding_x, x_max + padding_x],
                visible=False,
                scaleanchor="y",
                scaleratio=1
            ),
            yaxis=dict(
                range=[y_min - padding_y, y_max + padding_y + 1.0],
                visible=False
            ),
            plot_bgcolor='white',
            height=600,
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        # Add result box at top of visualization (matching other modules' style)
        fig.add_annotation(
            x=(x_min + x_max) / 2,
            y=y_max + padding_y + 0.5,
            text=f"<b>Resultant Force: {R/1000:.2f} kN at {phi:.1f}°</b>",
            showarrow=False,
            font=dict(size=20, color="white"),
            bgcolor="rgba(0, 100, 200, 0.9)",
            bordercolor="darkblue",
            borderwidth=2,
            borderpad=8
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Caption
        st.caption(
            f"Fluid flows through the reducing bend from D₁={D1_cm:.1f}cm to D₂={D2_cm:.1f}cm at angle θ={theta_deg}°. "
            f"The velocity increases from {U1:.2f} m/s to {U2:.2f} m/s due to the area reduction. "
            f"The red arrow shows the resultant force ({R/1000:.2f} kN at {phi:.1f}°) that the pipe supports must resist."
        )

with tab2:
    st.header("📚 Understanding Momentum Forces in Pipe Bends")
    
    col_edu1, col_edu2 = st.columns([1, 1])
    
    with col_edu1:
        st.markdown("""
        ### What Causes Forces on Pipe Bends?
        
        When fluid flows through a pipe bend, two main changes occur:
        
        1. **Direction change**: The fluid momentum vector changes direction
        2. **Velocity change**: If the diameter changes, the fluid accelerates or decelerates
        
        Both changes require forces, which the pipe must provide. By Newton's third law,
        the fluid exerts equal and opposite forces on the pipe.
        
        ### The Momentum Principle
        
        Newton's second law applied to fluid flow:
        """)
        
        st.latex(r'\vec{F} = \frac{d(m\vec{v})}{dt} = \dot{m}(\vec{U}_2 - \vec{U}_1)')
        
        st.markdown("""
        Where:
        - **F** = force on fluid (N)
        - **ṁ** = mass flow rate (kg/s)
        - **U₁, U₂** = inlet and outlet velocities (m/s)
        
        This is the **momentum flux change** - the rate of change of momentum passing through the control volume.
        
        ### Pressure Forces Also Matter
        
        In addition to momentum change, pressure forces act on the inlet and outlet:
        """)
        
        st.latex(r'\vec{F}_{total} = \dot{m}(\vec{U}_2 - \vec{U}_1) + p_1 A_1 \vec{n}_1 + p_2 A_2 \vec{n}_2')
        
        st.markdown("""
        The pressure forces push on the cross-sectional areas in the flow direction.
        """)
    
    with col_edu2:
        st.markdown("""
        ### Components of Force
        
        For a bend with angle θ, we resolve forces into components:
        
        **X-direction (inlet direction):**
        """)
        
        st.latex(r'F_x = \dot{m}(U_2\cos\theta - U_1) + p_1 A_1 - p_2 A_2\cos\theta')
        
        st.markdown("""
        **Y-direction (perpendicular):**
        """)
        
        st.latex(r'F_y = \dot{m}U_2\sin\theta - p_2 A_2\sin\theta')
        
        st.markdown("""
        ### Why Reducing Bends Are Special
        
        In a **reducing bend** (D₂ < D₁):
        
        1. **Velocity increases**: U₂ > U₁ (continuity equation)
        2. **Pressure decreases**: p₂ < p₁ (Bernoulli equation)
        3. **Forces increase**: Larger velocity change means more momentum force
        
        The velocity increase creates a "dynamic pressure" rise:
        """)
        
        st.latex(r'q = \frac{1}{2}\rho U^2')
        
        st.markdown("""
        This dynamic pressure converts to force through the momentum equation.
        
        ### Connection to Bernoulli's Equation
        
        Bernoulli's equation relates pressure to velocity:
        """)
        
        st.latex(r'p_1 + \frac{1}{2}\rho U_1^2 = p_2 + \frac{1}{2}\rho U_2^2')
        
        st.markdown("""
        We use this to find p₂, which then enters the momentum equation.
        """)
    
    st.markdown("---")
    
    st.markdown("### Key Concepts Explained")
    
    concept_col1, concept_col2, concept_col3 = st.columns(3)
    
    with concept_col1:
        st.markdown("""
        #### Mass Conservation
        
        **Continuity Equation:**
        """)
        st.latex(r'\dot{m} = \rho A_1 U_1 = \rho A_2 U_2')
        
        st.markdown("""
        - Mass flow rate is constant
        - If area decreases, velocity must increase
        - A₁/A₂ = U₂/U₁
        
        **Example:**
        - D₁ = 20 cm → A₁ = 314 cm²
        - D₂ = 10 cm → A₂ = 79 cm²
        - Ratio: A₁/A₂ = 4
        - Therefore: U₂ = 4×U₁
        """)
    
    with concept_col2:
        st.markdown("""
        #### Momentum Conservation
        
        **Momentum Equation:**
        """)
        st.latex(r'\vec{F} = \dot{m}\Delta\vec{U}')
        
        st.markdown("""
        - Force = mass flow × velocity change
        - Vector equation (direction matters)
        - Includes both magnitude and direction change
        
        **Key insight:**
        Even without diameter change, a 90° bend needs force to change flow direction!
        """)
    
    with concept_col3:
        st.markdown("""
        #### Energy Conservation
        
        **Bernoulli's Equation:**
        """)
        st.latex(r'p + \frac{1}{2}\rho U^2 = \text{const}')
        
        st.markdown("""
        - Total energy per unit volume is constant
        - Static pressure + dynamic pressure = constant
        - Velocity increase → pressure decrease
        
        **Trade-off:**
        Higher velocity means lower pressure, but higher dynamic force!
        """)
    
    st.markdown("---")
    
    st.markdown("### Common Misconceptions")
    
    misconception_col1, misconception_col2 = st.columns(2)
    
    with misconception_col1:
        st.error("""
        **❌ WRONG: "Force only depends on bend angle"**
        
        The angle affects direction, but magnitude depends on many factors.
        
        **✅ CORRECT:** Force depends on:
        - Bend angle θ (direction)
        - Diameter ratio D₂/D₁ (velocity change)
        - Flow rate Q (momentum flux)
        - Inlet pressure p₁ (pressure forces)
        - Fluid density ρ (momentum and pressure)
        """)
        
        st.error("""
        **❌ WRONG: "A straight reducer has no force"**
        
        Even without direction change, velocity change creates force.
        
        **✅ CORRECT:** A straight reducer (θ=0°) still has force due to:
        - Momentum change from U₁ to U₂
        - Pressure difference p₁ - p₂
        - Area difference A₁ - A₂
        """)
    
    with misconception_col2:
        st.error("""
        **❌ WRONG: "Higher pressure means higher force"**
        
        Pressure contributes to force, but isn't the only factor.
        
        **✅ CORRECT:** Force has two contributions:
        - Momentum flux: ṁΔU (often dominant in high-velocity systems)
        - Pressure: p₁A₁ - p₂A₂cosθ (important in high-pressure systems)
        """)
        
        st.error("""
        **❌ WRONG: "Force acts along the pipe"**
        
        The force isn't aligned with either inlet or outlet.
        
        **✅ CORRECT:** Resultant force has its own direction φ, which depends on:
        - Component balance between Rₓ and Rᵧ
        - Usually not aligned with pipe
        - Anchor must resist this specific direction
        """)

with tab3:
    st.header("📋 Real-World Applications")
    
    st.markdown("""
    Pipe bends with diameter changes are ubiquitous in fluid systems. Understanding
    the forces they create is essential for safe piping design and proper support.
    """)
    
    app_col1, app_col2 = st.columns(2)
    
    with app_col1:
        st.markdown("""
        ### Water Distribution Systems
        
        **1. Municipal Water Mains**
        - **Configuration**: 90° elbows, step reducers
        - **Typical sizes**: 150-600 mm diameter
        - **Pressures**: 400-800 kPa
        - **Forces**: 5-50 kN at major bends
        - **Anchoring**: Concrete thrust blocks required
        - **Key concern**: Waterhammer during valve operations
        
        **2. Building Plumbing**
        - **Configuration**: 90° elbows, tees with diameter changes
        - **Typical sizes**: 15-100 mm
        - **Pressures**: 300-600 kPa
        - **Forces**: 50-500 N
        - **Anchoring**: Pipe clamps and brackets
        - **Key concern**: Noise and vibration
        
        **3. Fire Protection Systems**
        - **Configuration**: Reducing elbows, sprinkler branches
        - **Typical sizes**: 65-200 mm mains, 15-25 mm branches
        - **Pressures**: 700-1200 kPa during operation
        - **Forces**: Can exceed 10 kN during testing
        - **Standards**: NFPA 13, 14 requirements
        - **Key concern**: Support during hydrostatic testing
        
        ### Industrial Process Piping
        
        **4. Chemical Plants**
        - **Fluids**: Various chemicals, oils, solvents
        - **Typical sizes**: 50-400 mm
        - **Pressures**: Wide range (100-10,000 kPa)
        - **Materials**: Stainless steel, lined pipes
        - **Special considerations**:
          - Corrosion-resistant anchors
          - Expansion loops for thermal growth
          - Vibration isolation
        
        **5. Steam Systems**
        - **Configuration**: Reducing elbows in distribution
        - **Typical sizes**: 50-300 mm
        - **Pressures**: 700-1500 kPa (low pressure steam)
        - **Temperature**: 150-200°C
        - **Forces**: Combined pressure + thermal expansion
        - **Key concern**: Thermal expansion forces can exceed momentum forces!
        
        **6. Oil and Gas Pipelines**
        - **Configuration**: Gentle bends, gradual reducers
        - **Typical sizes**: 200-1200 mm
        - **Pressures**: 5000-15,000 kPa
        - **Forces**: Can exceed 500 kN at major bends
        - **Anchoring**: Deep foundation systems, rock anchors
        - **Standards**: ASME B31.4 (liquid), B31.8 (gas)
        """)
    
    with app_col2:
        st.markdown("""
        ### HVAC and Air Handling
        
        **7. Duct Systems**
        - **Fluid**: Air (low density)
        - **Typical sizes**: 200-1000 mm
        - **Pressures**: 0.5-2.5 kPa (very low)
        - **Velocities**: 5-15 m/s
        - **Forces**: Usually small (< 100 N) due to low density
        - **Anchoring**: Light-duty hangers
        - **Key concern**: Noise transmission through duct walls
        
        **8. Fume Hoods and Exhaust**
        - **Configuration**: Reducing transitions to fan inlet
        - **Typical sizes**: 150-400 mm
        - **Velocities**: 10-20 m/s (high for air systems)
        - **Forces**: Momentum-dominated despite low pressure
        - **Key concern**: Vibration from fan interaction
        
        ### Power Generation
        
        **9. Cooling Water Systems**
        - **Configuration**: Large reducing bends to/from condensers
        - **Typical sizes**: 500-2000 mm
        - **Flow rates**: 10,000-100,000 L/s
        - **Forces**: Very large (100-1000 kN)
        - **Anchoring**: Massive concrete blocks on bedrock
        - **Key concern**: Seismic loads in earthquake zones
        
        **10. Boiler Feed Water**
        - **Configuration**: High-pressure reducers to boiler
        - **Pressures**: 10,000-30,000 kPa
        - **Temperatures**: 150-350°C
        - **Forces**: Extremely high
        - **Material**: Special alloy steel
        - **Key concern**: Creep at high temperature and pressure
        
        ### Marine Applications
        
        **11. Ship Piping Systems**
        - **Systems**: Seawater cooling, ballast, cargo
        - **Configuration**: Compact routing with many bends
        - **Special requirements**:
          - Corrosion-resistant (seawater)
          - Vibration-isolated (engine/propeller)
          - Shock-resistant (slamming loads)
        - **Anchoring**: Welded to ship structure
        
        **12. Offshore Platforms**
        - **Systems**: Process, injection, export pipelines
        - **Challenges**: Combined loads (weight + pressure + thermal + dynamic)
        - **Forces**: Can include wave-induced oscillations
        - **Design codes**: API RP 14E
        """)
    
    st.markdown("---")
    
    st.markdown("### Design Standards and Codes")
    
    code_col1, code_col2 = st.columns(2)
    
    with code_col1:
        st.markdown("""
        #### Piping Design Codes
        
        **ASME B31 Series** (Pressure Piping Codes):
        - **B31.1**: Power piping
        - **B31.3**: Process piping
        - **B31.4**: Pipeline transportation (liquid)
        - **B31.5**: Refrigeration piping
        - **B31.8**: Gas transmission and distribution
        - **B31.9**: Building services piping
        
        **Other Key Standards:**
        - **AWWA M11**: Steel water pipe design
        - **API 650/620**: Storage tank piping
        - **ISO 14692**: GRP piping systems
        """)
    
    with code_col2:
        st.markdown("""
        #### Support Design Guidelines
        
        **MSS SP-58**: Pipe hangers and supports
        
        **Typical Safety Factors:**
        - Permanent supports: 2.0-3.0
        - Temporary construction: 1.5-2.0
        - Seismic zones: Add 50% capacity
        - Impact loading: Add 100% capacity
        
        **Load Combinations:**
        - Dead load + fluid weight
        - Operating loads (momentum forces)
        - Thermal expansion
        - Wind/seismic (for exposed piping)
        - Waterhammer/surge
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Key Design Principles
    
    1. **Always calculate forces**: Don't assume bends don't need support
    2. **Anchor strategically**: Place anchors to resist resultant force direction
    3. **Allow for flexibility**: Provide expansion loops for thermal growth
    4. **Consider all loads**: Momentum + pressure + weight + thermal + dynamic
    5. **Protect against transients**: Install surge protection for waterhammer
    6. **Inspect regularly**: Bends are high-stress points prone to failure
    7. **Follow codes**: Use appropriate piping codes for your application
    """)

# Quick calculator at bottom
st.markdown("---")
st.header("🧮 Quick Force Calculator")

calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)

with calc_col1:
    calc_D1 = st.number_input("D₁ (cm)", value=20.0, step=1.0, key="calc_D1") / 100
    calc_D2 = st.number_input("D₂ (cm)", value=10.0, step=1.0, key="calc_D2") / 100

with calc_col2:
    calc_theta = st.number_input("θ (degrees)", value=45, step=5, key="calc_theta")
    calc_Q = st.number_input("Q (L/s)", value=10.0, step=1.0, key="calc_Q") / 1000

with calc_col3:
    calc_rho = st.number_input("ρ (kg/m³)", value=1000.0, step=100.0, key="calc_rho")
    calc_p1 = st.number_input("p₁ (kPa)", value=200.0, step=10.0, key="calc_p1") * 1000

with calc_col4:
    calc_A1 = np.pi * (calc_D1/2)**2
    calc_A2 = np.pi * (calc_D2/2)**2
    calc_U1 = calc_Q / calc_A1 if calc_A1 > 0 else 0
    calc_U2 = calc_Q / calc_A2 if calc_A2 > 0 else 0
    calc_m = calc_rho * calc_Q
    calc_p2 = calc_p1 + 0.5 * calc_rho * (calc_U1**2 - calc_U2**2)
    calc_theta_rad = np.deg2rad(calc_theta)
    calc_Fx = calc_m * (calc_U2 * np.cos(calc_theta_rad) - calc_U1) + calc_p1 * calc_A1 - calc_p2 * calc_A2 * np.cos(calc_theta_rad)
    calc_Fy = calc_m * calc_U2 * np.sin(calc_theta_rad) - calc_p2 * calc_A2 * np.sin(calc_theta_rad)
    calc_R = np.sqrt(calc_Fx**2 + calc_Fy**2)
    
    st.metric("Force |R| (N)", f"{calc_R:.1f}")
    st.metric("Force |R| (kN)", f"{calc_R/1000:.2f}")

st.caption("💡 **Quick calculator**: Instantly compute resultant force for any pipe bend configuration.")

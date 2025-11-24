import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Hydrostatic Force on Inclined Wall", layout="wide")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>📐 Hydrostatic Force on an Inclined Wall</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
Explore how inclination angle affects hydrostatic pressure distribution and forces on submerged inclined surfaces.
Understand the relationship between angle, depth, and resultant force through interactive visualization.
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# Create tabs for different aspects
tab1, tab2, tab3 = st.tabs(["🎯 Interactive Simulation", "📚 Understanding Inclined Surfaces", "📋 Real-World Applications"])

with tab1:
    # --- Main Layout ---
    col1, col2 = st.columns([2, 3])

    # --- Column 1: Inputs and Results ---
    with col1:
        st.header("🔬 Parameters")
        
        # --- Interactive Scenarios ---
        SCENARIOS = {
            "Custom...": {
                "L": 5.0, "w": 3.0, "theta": 45, "rho": 1000.0,
                "desc": "Manually adjust all parameters below."
            },
            "Dam Spillway (30°)": {
                "L": 20.0, "w": 30.0, "theta": 30, "rho": 1000.0,
                "desc": "Typical spillway: 30° slope, 20m length. Gentle incline for controlled overflow."
            },
            "Steep Canal Gate (60°)": {
                "L": 8.0, "w": 6.0, "theta": 60, "rho": 1000.0,
                "desc": "Canal control gate: 60° slope, 8m long. Steeper for irrigation control."
            },
            "Lock Gate (90°)": {
                "L": 12.0, "w": 15.0, "theta": 90, "rho": 1000.0,
                "desc": "Vertical lock gate: 90°, 12m high. Maximum depth, vertical orientation."
            },
            "Tank Bottom (15°)": {
                "L": 6.0, "w": 4.0, "theta": 15, "rho": 1000.0,
                "desc": "Sloped tank bottom: 15° for drainage, 6m length. Shallow angle."
            },
            "Reservoir Embankment (45°)": {
                "L": 25.0, "w": 100.0, "theta": 45, "rho": 1000.0,
                "desc": "Earth dam face: 45° slope (1V:1H), 25m length. Standard embankment angle."
            },
            "Ship Hull Section (70°)": {
                "L": 10.0, "w": 20.0, "theta": 70, "rho": 1025.0,
                "desc": "Ship hull plating: 70° from horizontal, seawater (ρ=1025). Nearly vertical."
            }
        }
        
        scenario = st.selectbox("Select Application Scenario", list(SCENARIOS.keys()))
        selected = SCENARIOS[scenario]
        st.info(selected["desc"])
        
        st.subheader("Wall Geometry")
        c1, c2 = st.columns(2)
        with c1:
            L = st.slider("Wall length, L (m)", 0.5, 30.0, selected["L"], step=0.5,
                         help="Length of inclined wall measured along the slope")
        with c2:
            w = st.slider("Wall width, w (m)", 0.5, 100.0, selected["w"], step=0.5,
                         help="Width of wall perpendicular to the page")
        
        theta_deg = st.slider("Inclination angle, θ (degrees)", 0, 90, selected["theta"], step=1,
                              help="Angle from horizontal: 0°=horizontal, 45°=diagonal, 90°=vertical")
        theta_rad = np.deg2rad(theta_deg)
        
        st.subheader("Fluid Properties")
        c1, c2 = st.columns(2)
        with c1:
            rho = st.number_input("Fluid density, ρ (kg/m³)", value=selected["rho"], step=10.0, format="%.1f",
                                 help="Water: 1000, Seawater: 1025")
        with c2:
            g = st.number_input("Gravity, g (m/s²)", value=9.81, format="%.2f",
                               help="Standard gravity: 9.81 m/s²")
        
        st.subheader("📊 Visualization Options")
        show_pressure_arrows = st.checkbox("Show Pressure Distribution", value=True,
                                         help="Toggle to visualize pressure acting perpendicular to inclined wall")
        
        if show_pressure_arrows:
            c1, c2 = st.columns(2)
            with c1:
                n_arrows = st.slider("Number of pressure arrows", 5, 20, 10, step=1)
            with c2:
                arrow_style = st.radio("Arrow style", 
                                     ["Perpendicular arrows", "Triangular arrows", "Force vectors"])
        
        show_gradient = st.checkbox("Show pressure gradient on wall", value=True,
                                   help="Shows color gradient indicating pressure intensity")

        # --- Calculations ---
        # Vertical depth (height) of the inclined wall
        h = L * np.sin(theta_rad)  # Vertical projection
        
        # Horizontal extent
        b = L * np.cos(theta_rad)  # Horizontal projection
        
        # Normal force (perpendicular to inclined surface)
        # This is derived from integrating pressure over the inclined area
        F_N = 0.5 * rho * g * w * L**2 * np.sin(theta_rad)
        F_N_kN = F_N / 1000
        
        # Horizontal and vertical components of force
        F_H = F_N * np.sin(theta_rad)  # Horizontal component
        F_V = F_N * np.cos(theta_rad)  # Vertical component
        F_H_kN = F_H / 1000
        F_V_kN = F_V / 1000
        
        # Center of pressure along the inclined surface
        s_cp = (2/3) * L  # Distance from top along the slope
        
        # Coordinates of center of pressure
        x_cp = s_cp * np.cos(theta_rad)
        y_cp = s_cp * np.sin(theta_rad)
        
        # Depth at center of pressure
        depth_cp = h - y_cp
        
        # Pressure at bottom (maximum)
        P_bottom = rho * g * h
        P_bottom_kPa = P_bottom / 1000
        
        # Average pressure
        P_avg = P_bottom / 2
        P_avg_kPa = P_avg / 1000
        
        # Wall area
        wall_area = L * w

        st.markdown("---")
        st.header("📈 Results Summary")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric(label="Normal Force (F_N)", value=f"{F_N_kN:,.2f} kN",
                      help="Total force acting perpendicular to the inclined surface")
            st.metric(label="Vertical Depth (h)", value=f"{h:.2f} m",
                      help=f"Vertical projection of wall = L × sin(θ) = {L:.2f} × sin({theta_deg}°)")
        with col_r2:
            st.metric(label="Horizontal Component (F_H)", value=f"{F_H_kN:,.2f} kN",
                      help="Horizontal component of normal force")
            st.metric(label="Vertical Component (F_V)", value=f"{F_V_kN:,.2f} kN",
                      help="Vertical component of normal force")
        
        col_r3, col_r4 = st.columns(2)
        with col_r3:
            st.metric(label="Max Pressure (at bottom)", value=f"{P_bottom_kPa:.2f} kPa",
                      help="Maximum pressure at deepest point")
            st.metric(label="Center of Pressure", value=f"{s_cp:.2f} m",
                      help=f"Distance from top along slope = (2/3) × {L:.2f} m")
        with col_r4:
            st.metric(label="Average Pressure", value=f"{P_avg_kPa:.2f} kPa",
                      help="Average pressure over wall = P_max / 2")
            st.metric(label="Wall Area", value=f"{wall_area:.1f} m²",
                      help="Wetted surface area")
        
        st.markdown("---")
        st.header("🧮 Step-by-Step Calculation")
        
        with st.expander("📖 See Detailed Breakdown", expanded=False):
            st.markdown("### Hydrostatic Force on Inclined Wall")
            
            st.markdown("#### Step 1: Understand the Geometry")
            st.write("For an inclined wall at angle θ from horizontal:")
            st.write(f"• **Wall length** (along slope): L = {L} m")
            st.write(f"• **Inclination angle**: θ = {theta_deg}°")
            st.write(f"• **Vertical depth**: h = L × sin(θ) = {L} × sin({theta_deg}°) = **{h:.2f} m**")
            st.write(f"• **Horizontal projection**: b = L × cos(θ) = {L} × cos({theta_deg}°) = **{b:.2f} m**")
            st.write(f"• **Wall width** (into page): w = {w} m")
            st.write(f"\n💡 The vertical depth h determines the maximum pressure, not the wall length L!")
            
            st.markdown("#### Step 2: Pressure Distribution on Inclined Surface")
            st.write("Pressure at any point depends on **vertical depth below the surface**, not distance along slope.")
            st.write("\nAt distance s along the slope from top:")
            st.latex(r'y = s \sin\theta')
            st.write("Depth below surface:")
            st.latex(r'd = h - y = h - s\sin\theta')
            st.write("Pressure at that point:")
            st.latex(r'P(s) = \rho g (h - s\sin\theta) = \rho g h - \rho g s \sin\theta')
            st.write(f"\n• At top (s = 0): P = ρgh = {P_bottom_kPa:.2f} kPa (maximum, deepest point)")
            st.write(f"• At bottom (s = L): P = ρg(h - L sin θ) = ρg(h - h) = 0 kPa (at surface)")
            st.write(f"\n**Note**: For inclined walls, pressure **decreases** along the slope from bottom to top!")
            
            st.markdown("#### Step 3: Calculate Normal Force")
            st.write("The normal force acts perpendicular to the inclined surface.")
            st.write("\nIntegrating pressure over the inclined area:")
            st.latex(r'F_N = \int_0^L P(s) \cdot w \, ds = \int_0^L \rho g (h - s\sin\theta) \cdot w \, ds')
            st.write("Evaluating the integral:")
            st.latex(r'F_N = w \rho g \left[hs - \frac{s^2\sin\theta}{2}\right]_0^L')
            st.latex(r'F_N = w \rho g \left(hL - \frac{L^2\sin\theta}{2}\right)')
            st.write("Since h = L sin θ:")
            st.latex(r'F_N = w \rho g \left(L^2\sin\theta - \frac{L^2\sin\theta}{2}\right) = \frac{1}{2}w \rho g L^2 \sin\theta')
            
            st.write(f"\n**Calculation:**")
            st.write(f"F_N = 0.5 × {w} m × {rho} kg/m³ × {g} m/s² × ({L} m)² × sin({theta_deg}°)")
            st.write(f"F_N = 0.5 × {w} × {rho} × {g} × {L**2:.2f} × {np.sin(theta_rad):.4f}")
            st.write(f"F_N = **{F_N:.0f} N** = **{F_N_kN:.2f} kN**")
            
            st.markdown("#### Step 4: Force Components")
            st.write("The normal force can be resolved into horizontal and vertical components:")
            st.latex(r'F_H = F_N \sin\theta \quad \text{(horizontal component)}')
            st.latex(r'F_V = F_N \cos\theta \quad \text{(vertical component)}')
            
            st.write(f"\n**Calculations:**")
            st.write(f"F_H = {F_N_kN:.2f} kN × sin({theta_deg}°) = **{F_H_kN:.2f} kN**")
            st.write(f"F_V = {F_N_kN:.2f} kN × cos({theta_deg}°) = **{F_V_kN:.2f} kN**")
            
            st.write(f"\n**Verification:**")
            st.write(f"√(F_H² + F_V²) = √({F_H_kN:.2f}² + {F_V_kN:.2f}²) = {np.sqrt(F_H_kN**2 + F_V_kN**2):.2f} kN ✓")
            
            st.markdown("#### Step 5: Locate Center of Pressure")
            st.write("For a triangular pressure distribution on an inclined surface:")
            st.latex(r's_{cp} = \frac{2}{3}L')
            st.write("This is measured along the slope from the top (deepest point).")
            
            st.write(f"\n**Calculation:**")
            st.write(f"s_cp = (2/3) × {L} m = **{s_cp:.2f} m** from top along slope")
            st.write(f"\n**Coordinates of center of pressure:**")
            st.write(f"x_cp = s_cp × cos(θ) = {s_cp:.2f} × cos({theta_deg}°) = {x_cp:.2f} m (horizontal)")
            st.write(f"y_cp = s_cp × sin(θ) = {s_cp:.2f} × sin({theta_deg}°) = {y_cp:.2f} m (vertical)")
            st.write(f"Depth at C.P. = h - y_cp = {h:.2f} - {y_cp:.2f} = **{depth_cp:.2f} m** below surface")
            
            st.markdown("#### Step 6: Special Cases and Insights")
            
            col_special1, col_special2 = st.columns(2)
            
            with col_special1:
                st.write("**Case 1: Vertical Wall (θ = 90°)**")
                st.write("• sin(90°) = 1")
                st.write("• h = L (full length is vertical)")
                st.write(f"• F_N = ½ρgwL² × 1 = ½ρgwL²")
                st.write("• This matches vertical wall formula!")
                
                st.write("\n**Case 2: Horizontal Surface (θ = 0°)**")
                st.write("• sin(0°) = 0")
                st.write("• h = 0 (no vertical depth)")
                st.write("• F_N = 0 (no hydrostatic force)")
                st.write("• Makes sense: no water depth!")
            
            with col_special2:
                st.write("**Case 3: 45° Inclination**")
                st.write("• sin(45°) = 0.707")
                st.write("• h = 0.707L")
                st.write("• F_N = ½ρgwL² × 0.707")
                st.write("• Force is ~70% of vertical wall")
                
                st.write("\n**Case 4: 30° Spillway**")
                st.write("• sin(30°) = 0.5")
                st.write("• h = 0.5L (half the slope length)")
                st.write("• F_N = ½ρgwL² × 0.5 = ¼ρgwL²")
                st.write("• Force is 25% of equivalent vertical")
            
            st.markdown("### Physical Interpretation")
            if theta_deg == 90:
                st.info("💡 **Vertical wall**: Maximum force for given length. Equivalent to straight wall case.")
            elif theta_deg >= 60:
                st.success(f"✅ **Steep inclination** ({theta_deg}°): Force is {F_N_kN:.2f} kN. Large vertical depth ({h:.2f}m) creates significant pressure.")
            elif theta_deg >= 30:
                st.warning(f"⚠️ **Moderate inclination** ({theta_deg}°): Force is {F_N_kN:.2f} kN. Depth is {h:.2f}m, about {(h/L)*100:.0f}% of wall length.")
            else:
                st.error(f"❗ **Shallow inclination** ({theta_deg}°): Force is {F_N_kN:.2f} kN. Small vertical depth ({h:.2f}m) means lower pressure despite long wall ({L}m).")
        
        st.markdown("---")
        st.header("🔍 Analysis Insights")
        
        with st.expander("💡 Effect of Inclination Angle", expanded=False):
            st.markdown("**How angle affects the hydrostatic force:**")
            
            st.markdown("#### 1. Force vs Angle Relationship")
            st.write(f"• Current angle: **θ = {theta_deg}°**")
            st.write(f"• **Key relationship**: F_N ∝ sin(θ)")
            st.latex(r'F_N = \frac{1}{2}\rho g w L^2 \sin\theta')
            
            # Create force vs angle table
            st.write("\n**Force at different angles (keeping L and w constant):**")
            angles = [0, 15, 30, 45, 60, 75, 90]
            angle_data = []
            for angle in angles:
                angle_rad = np.deg2rad(angle)
                f = 0.5 * rho * g * w * L**2 * np.sin(angle_rad) / 1000
                h_temp = L * np.sin(angle_rad)
                ratio = f / F_N_kN if F_N_kN > 0 else 0
                angle_data.append({
                    "Angle (°)": angle,
                    "sin(θ)": f"{np.sin(angle_rad):.3f}",
                    "Depth h (m)": f"{h_temp:.2f}",
                    "Force (kN)": f"{f:.2f}",
                    "Ratio to current": f"×{ratio:.3f}"
                })
            st.table(pd.DataFrame(angle_data))
            
            st.success("✅ **Key insight**: Increasing angle from 30° to 90° **doubles** the force (sin increases from 0.5 to 1.0)")
            
            st.markdown("#### 2. Why sin(θ) Appears in the Formula")
            st.write("**Two factors contribute:**")
            st.write(f"1. **Vertical depth**: h = L sin(θ)")
            st.write(f"   • Determines pressure magnitude")
            st.write(f"   • At θ={theta_deg}°: h = {h:.2f}m")
            st.write(f"\n2. **Effective area normal to pressure**")
            st.write(f"   • Pressure acts vertically")
            st.write(f"   • Effective area = wetted area × sin(θ)")
            st.write(f"\n**Combined effect**: Force ∝ h × area ∝ (L sin θ) × (Lw sin θ) ∝ sin²θ")
            st.write(f"**But**: Integration along slope gives final result ∝ sin θ")
            
            st.markdown("#### 3. Comparison: Same Depth vs Same Length")
            
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                st.write("**Scenario A: Same wall length L**")
                st.write(f"Keep L = {L}m constant, vary angle:")
                for angle in [30, 45, 60, 90]:
                    angle_rad = np.deg2rad(angle)
                    h_temp = L * np.sin(angle_rad)
                    f = 0.5 * rho * g * w * L**2 * np.sin(angle_rad) / 1000
                    st.write(f"• {angle}°: h={h_temp:.1f}m, F={f:.1f}kN")
                st.write("\n→ Steeper = more force")
            
            with col_comp2:
                st.write("**Scenario B: Same vertical depth h**")
                st.write(f"Keep h = {h:.2f}m constant:")
                for angle in [30, 45, 60, 90]:
                    angle_rad = np.deg2rad(angle)
                    L_temp = h / np.sin(angle_rad) if np.sin(angle_rad) > 0 else 0
                    f = 0.5 * rho * g * w * L_temp**2 * np.sin(angle_rad) / 1000
                    st.write(f"• {angle}°: L={L_temp:.1f}m, F={f:.1f}kN")
                st.write("\n→ More vertical = less length needed")
            
            st.markdown("#### 4. Force Components Analysis")
            st.write(f"**Current angle: θ = {theta_deg}°**")
            st.write(f"• Normal force: F_N = {F_N_kN:.2f} kN")
            st.write(f"• Horizontal component: F_H = {F_H_kN:.2f} kN ({(F_H_kN/F_N_kN*100):.1f}% of F_N)")
            st.write(f"• Vertical component: F_V = {F_V_kN:.2f} kN ({(F_V_kN/F_N_kN*100):.1f}% of F_N)")
            
            st.write("\n**Component distribution by angle:**")
            component_data = []
            for angle in [30, 45, 60, 90]:
                angle_rad = np.deg2rad(angle)
                fh_pct = np.sin(angle_rad) * 100
                fv_pct = np.cos(angle_rad) * 100
                component_data.append({
                    "Angle (°)": angle,
                    "F_H (% of F_N)": f"{fh_pct:.1f}%",
                    "F_V (% of F_N)": f"{fv_pct:.1f}%",
                    "Dominant": "Horizontal" if fh_pct > fv_pct else "Vertical"
                })
            st.table(pd.DataFrame(component_data))
            
            st.info("💡 **Design insight**: At 45°, horizontal and vertical components are equal. Below 45°, vertical dominates. Above 45°, horizontal dominates.")

        with st.expander("⚙️ Design Considerations for Inclined Surfaces", expanded=False):
            st.markdown("**Engineering design factors for inclined walls:**")
            
            st.markdown("#### 1. Structural Design Requirements")
            
            st.write("**A. Normal Force and Bending**")
            st.write(f"• Normal force F_N = {F_N_kN:.2f} kN")
            st.write(f"• Acts perpendicular to surface at center of pressure")
            st.write(f"• Creates bending moment in the wall structure")
            st.write(f"• Wall must be designed for combined normal stress and bending")
            
            st.write("\n**B. Component Forces for Foundation Design**")
            st.write(f"• Horizontal thrust: F_H = {F_H_kN:.2f} kN")
            st.write(f"  → Foundation must resist sliding")
            st.write(f"• Vertical component: F_V = {F_V_kN:.2f} kN")
            st.write(f"  → Adds to (or reduces) foundation loads")
            st.write(f"• Resultant creates moment about base")
            
            st.write("\n**C. Material Selection Based on Angle**")
            
            if theta_deg >= 70:
                st.success("✅ **Near-vertical** (70-90°):")
                st.write("• Similar to vertical walls")
                st.write("• Reinforced concrete most common")
                st.write("• Thickness: L/10 to L/12")
                st.write("• Heavy reinforcement near base")
            elif theta_deg >= 45:
                st.info("💡 **Moderate slope** (45-70°):")
                st.write("• Concrete or masonry with reinforcement")
                st.write("• Consider sliding resistance")
                st.write("• Drainage behind wall critical")
                st.write("• May use stepped construction")
            elif theta_deg >= 20:
                st.warning("⚠️ **Gentle slope** (20-45°):")
                st.write("• Earth embankment with facing")
                st.write("• Geotextile reinforcement")
                st.write("• Riprap or gabion protection")
                st.write("• Focus on erosion control")
            else:
                st.error("❗ **Very shallow** (< 20°):")
                st.write("• Essentially horizontal")
                st.write("• Uplift pressure may dominate")
                st.write("• Anchoring or weight needed")
                st.write("• Drainage most critical")
            
            st.markdown("#### 2. Stability Analysis")
            
            st.write("**A. Sliding Stability**")
            st.write("Must resist horizontal component:")
            st.latex(r'\text{Factor of Safety} = \frac{\text{Friction Force}}{\text{F}_H}')
            st.write(f"Required friction force ≥ 1.5 × {F_H_kN:.2f} = {F_H_kN*1.5:.2f} kN")
            st.write("\nMethods to increase sliding resistance:")
            st.write("• Increase normal load (self-weight, backfill)")
            st.write("• Deepen foundation (passive earth pressure)")
            st.write("• Add shear keys or anchors")
            st.write("• Roughen base interface")
            
            st.write("\n**B. Overturning Stability**")
            st.write("Moment analysis about toe:")
            st.write("• Overturning moment from hydrostatic force")
            st.write("• Resisting moment from wall weight")
            st.write("• Factor of safety typically 2.0-2.5")
            st.write(f"• Lower angles (like {theta_deg}°) reduce overturning risk")
            
            st.markdown("#### 3. Special Considerations for Inclined Walls")
            
            st.write("**A. Drainage and Seepage**")
            st.write("• Water can seep along inclined interface")
            st.write("• Install drainage layer (gravel, geotextile)")
            st.write("• Weep holes angled downward")
            st.write("• Prevent pressure buildup behind wall")
            
            st.write("\n**B. Construction Sequence**")
            st.write("• For slopes < 60°: may pour on slope")
            st.write("• For slopes ≥ 60°: vertical formwork")
            st.write("• Consider slip-forming for long structures")
            st.write("• Cure adequately before loading")
            
            st.write("\n**C. Surface Protection**")
            if theta_deg >= 60:
                st.write("• Smooth finish for flow control")
                st.write("• Coating for abrasion resistance")
            elif theta_deg >= 30:
                st.write("• Concrete lining or gunite")
                st.write("• May add surface texture")
            else:
                st.write("• Riprap or concrete blocks")
                st.write("• Vegetation for erosion control")
            
            st.write("\n**D. Joints and Movement**")
            st.write("• Expansion joints every 15-20m")
            st.write("• Contraction joints at 3-5m spacing")
            st.write("• Waterstops at all joints")
            st.write("• Monitor for differential settlement")

        with st.expander("📊 Pressure and Force Distribution", expanded=False):
            st.markdown("**Detailed analysis of pressure variation:**")
            
            # Create detailed pressure table along slope
            n_points = 11
            pressure_table = []
            for i in range(n_points):
                s = (i / (n_points - 1)) * L  # Distance along slope
                y = s * np.sin(theta_rad)  # Vertical position
                depth_below = h - y  # Depth below surface
                pressure = rho * g * depth_below
                pressure_kPa = pressure / 1000
                percent_max = (depth_below / h) * 100 if h > 0 else 0
                
                pressure_table.append({
                    "Position along slope (m)": f"{s:.2f}",
                    "Vertical height (m)": f"{y:.2f}",
                    "Depth below surface (m)": f"{depth_below:.2f}",
                    "Pressure (kPa)": f"{pressure_kPa:.2f}",
                    "% of max": f"{percent_max:.0f}%"
                })
            
            st.table(pd.DataFrame(pressure_table))
            
            st.write(f"\n**Key observations:**")
            st.write(f"• Pressure is maximum at **top** of slope (deepest point): {P_bottom_kPa:.2f} kPa")
            st.write(f"• Pressure is zero at **bottom** of slope (at water surface): 0 kPa")
            st.write(f"• Pressure decreases linearly along the slope")
            st.write(f"• Pressure gradient = {P_bottom_kPa/L:.2f} kPa per meter of slope length")
            st.write(f"• At center of pressure ({s_cp:.2f}m along slope): P = {rho*g*depth_cp/1000:.2f} kPa")

    # --- Column 2: Visualization ---
    with col2:
        st.header("🖼️ Visualization")
        
        # Add instructional message when arrows are hidden
        if not show_pressure_arrows:
            st.info("👆 Enable 'Show Pressure Distribution' to visualize how pressure acts on the inclined wall")

        fig = go.Figure()
        
        # --- Geometry Setup ---
        x0, y0 = 0, 0  # Top of wall (deepest point)
        x1, y1 = L * np.cos(theta_rad), L * np.sin(theta_rad)  # Bottom of wall (at surface)
        
        plot_width = max(L * 1.5, 8)
        plot_height = max(h * 1.5, 6)
        
        # 1. Draw water region (left side of wall only)
        water_points_x = [-plot_width/3]
        water_points_y = [0]
        n_wall_points = 50
        for i in range(n_wall_points + 1):
            frac = i / n_wall_points
            if frac * L * np.sin(theta_rad) <= h:
                water_points_x.append(frac * L * np.cos(theta_rad))
                water_points_y.append(frac * L * np.sin(theta_rad))
        water_points_x.extend([x1, -plot_width/3])
        water_points_y.extend([h, h])
        
        fig.add_trace(go.Scatter(
            x=water_points_x, y=water_points_y,
            fill="toself",
            fillcolor="rgba(0, 119, 182, 0.3)",
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # 2. Draw pressure gradient on wall if enabled
        if show_gradient:
            gradient_steps = 50
            for i in range(gradient_steps):
                s_start = i * L / gradient_steps
                s_end = (i + 1) * L / gradient_steps
                xs_start = s_start * np.cos(theta_rad)
                ys_start = s_start * np.sin(theta_rad)
                xs_end = s_end * np.cos(theta_rad)
                ys_end = s_end * np.sin(theta_rad)
                
                offset = 0.1
                perp_x = -np.sin(theta_rad) * offset
                perp_y = np.cos(theta_rad) * offset
                
                # Depth at midpoint
                s_mid = (s_start + s_end) / 2
                y_mid = s_mid * np.sin(theta_rad)
                depth_mid = h - y_mid
                
                opacity = 0.02 + 0.15 * (depth_mid / h) if h > 0 else 0.02
                
                grad_x = [xs_start, xs_end, xs_end + perp_x, xs_start + perp_x]
                grad_y = [ys_start, ys_end, ys_end + perp_y, ys_start + perp_y]
                
                fig.add_trace(go.Scatter(
                    x=grad_x, y=grad_y,
                    fill="toself",
                    fillcolor=f"rgba(255, 0, 0, {opacity})",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # 3. Draw the inclined wall
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode='lines',
            line=dict(color="black", width=8),
            name='Inclined Wall',
            showlegend=False
        ))
        
        # Add the horizontal base
        fig.add_trace(go.Scatter(
            x=[-plot_width/3, x0], y=[y0, y0],
            mode='lines',
            line=dict(color="black", width=8),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Wall label
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        wall_angle = np.degrees(np.arctan2(y1 - y0, x1 - x0))
        fig.add_annotation(
            x=mid_x, y=mid_y,
            text="<b>WALL</b>",
            showarrow=False,
            font=dict(size=14, color="white"),
            textangle=-wall_angle,
            bgcolor="black",
            borderpad=4
        )
        
        # 4. Draw pressure arrows if enabled
        if show_pressure_arrows:
            max_pressure = rho * g * h if h > 0 else 1
            arrow_max_length = min(2.5, plot_width * 0.3)
            
            if arrow_style == "Perpendicular arrows":
                for i in range(n_arrows):
                    frac = (i + 0.5) / n_arrows
                    s = frac * L
                    x_wall = s * np.cos(theta_rad)
                    y_wall = s * np.sin(theta_rad)
                    depth = h - y_wall
                    pressure = rho * g * depth if depth > 0 else 0
                    arrow_length = arrow_max_length * (pressure / max_pressure) if max_pressure > 0 else 0
                    
                    # Arrow direction (perpendicular to wall)
                    arrow_dx = -np.sin(theta_rad) * arrow_length
                    arrow_dy = np.cos(theta_rad) * arrow_length
                    
                    # Draw arrow shaft
                    fig.add_shape(
                        type="line",
                        x0=x_wall + arrow_dx, y0=y_wall + arrow_dy,
                        x1=x_wall - 0.02 * np.sin(theta_rad), y1=y_wall + 0.02 * np.cos(theta_rad),
                        line=dict(color="red", width=4)
                    )
                    
                    # Draw arrow head
                    head_size = 0.15
                    head_perp_x = np.cos(theta_rad) * head_size/2
                    head_perp_y = np.sin(theta_rad) * head_size/2
                    head_along_x = -np.sin(theta_rad) * head_size
                    head_along_y = np.cos(theta_rad) * head_size
                    
                    fig.add_trace(go.Scatter(
                        x=[x_wall + head_along_x - head_perp_x,
                           x_wall,
                           x_wall + head_along_x + head_perp_x],
                        y=[y_wall + head_along_y - head_perp_y,
                           y_wall,
                           y_wall + head_along_y + head_perp_y],
                        fill="toself",
                        fillcolor="red",
                        line=dict(color="red", width=0),
                        mode='lines',
                        showlegend=False,
                        hoverinfo='text',
                        text=f"Position: {s:.1f}m along slope<br>Depth: {depth:.2f}m<br>Pressure: {pressure/1000:.2f} kPa"
                    ))
            
            elif arrow_style == "Triangular arrows":
                for i in range(n_arrows):
                    frac = (i + 0.5) / n_arrows
                    s = frac * L
                    x_wall = s * np.cos(theta_rad)
                    y_wall = s * np.sin(theta_rad)
                    depth = h - y_wall
                    pressure = rho * g * depth if depth > 0 else 0
                    arrow_length = arrow_max_length * (pressure / max_pressure) if max_pressure > 0 else 0
                    
                    arrow_dx = -np.sin(theta_rad) * arrow_length
                    arrow_dy = np.cos(theta_rad) * arrow_length
                    
                    tri_width = 0.2
                    width_x = np.cos(theta_rad) * tri_width/2
                    width_y = np.sin(theta_rad) * tri_width/2
                    
                    fig.add_trace(go.Scatter(
                        x=[x_wall + arrow_dx - width_x,
                           x_wall,
                           x_wall + arrow_dx + width_x],
                        y=[y_wall + arrow_dy - width_y,
                           y_wall,
                           y_wall + arrow_dy + width_y],
                        fill="toself",
                        fillcolor="red",
                        line=dict(color="darkred", width=1),
                        mode='lines',
                        showlegend=False,
                        hoverinfo='text',
                        text=f"Position: {s:.1f}m<br>Depth: {depth:.2f}m<br>Pressure: {pressure/1000:.2f} kPa"
                    ))
            
            else:  # Force vectors
                for i in range(n_arrows):
                    frac = (i + 0.5) / n_arrows
                    s = frac * L
                    x_wall = s * np.cos(theta_rad)
                    y_wall = s * np.sin(theta_rad)
                    depth = h - y_wall
                    pressure = rho * g * depth if depth > 0 else 0
                    arrow_length = arrow_max_length * (pressure / max_pressure) if max_pressure > 0 else 0
                    
                    arrow_dx = -np.sin(theta_rad) * arrow_length
                    arrow_dy = np.cos(theta_rad) * arrow_length
                    
                    fig.add_trace(go.Scatter(
                        x=[x_wall + arrow_dx],
                        y=[y_wall + arrow_dy],
                        mode='markers',
                        marker=dict(size=8, color='red'),
                        showlegend=False,
                        hoverinfo='text',
                        text=f"Position: {s:.1f}m<br>Depth: {depth:.2f}m<br>Pressure: {pressure/1000:.2f} kPa"
                    ))
                    
                    fig.add_shape(
                        type="line",
                        x0=x_wall + arrow_dx, y0=y_wall + arrow_dy,
                        x1=x_wall - 0.02 * np.sin(theta_rad), y1=y_wall + 0.02 * np.cos(theta_rad),
                        line=dict(color="red", width=3)
                    )
        
        # 5. Fluid surface line
        fig.add_shape(
            type="line",
            x0=-plot_width/3, y0=h,
            x1=x1, y1=h,
            line=dict(color="#0077B6", width=3, dash="dash")
        )
        fig.add_annotation(
            x=-plot_width/6, y=h,
            text="Water Surface",
            showarrow=False,
            font=dict(color="#0077B6", size=14),
            xanchor="center",
            yshift=15
        )
        
        # 6. Center of pressure marker
        x_cp_plot = s_cp * np.cos(theta_rad)
        y_cp_plot = s_cp * np.sin(theta_rad)
        
        # Draw marker perpendicular to wall
        marker_length = 0.3
        cp_marker_dx = -np.sin(theta_rad) * marker_length
        cp_marker_dy = np.cos(theta_rad) * marker_length
        
        fig.add_shape(
            type="line",
            x0=x_cp_plot - cp_marker_dx, y0=y_cp_plot - cp_marker_dy,
            x1=x_cp_plot + cp_marker_dx, y1=y_cp_plot + cp_marker_dy,
            line=dict(color="green", width=3, dash="dot")
        )
        
        fig.add_annotation(
            x=x_cp_plot - cp_marker_dx, y=y_cp_plot - cp_marker_dy,
            text="C.P.",
            showarrow=False,
            font=dict(size=12, color="green", family="Arial Black"),
            xanchor="right"
        )
        
        # Add center of pressure annotation
        fig.add_annotation(
            x=x_cp_plot + cp_marker_dx*2, y=y_cp_plot + cp_marker_dy*2,
            text=f"Center of Pressure<br>{s_cp:.2f}m along slope<br>{depth_cp:.2f}m below surface",
            showarrow=True,
            arrowhead=2,
            arrowcolor="green",
            font=dict(size=10, color="green"),
            xanchor="left",
            ax=50, ay=-30
        )
        
        # 7. Angle indicator
        arc_radius = min(1.0, L * 0.2)
        arc_angles = np.linspace(0, theta_rad, 30)
        arc_x = arc_radius * np.cos(arc_angles)
        arc_y = arc_radius * np.sin(arc_angles)
        
        fig.add_trace(go.Scatter(
            x=arc_x, y=arc_y,
            mode='lines',
            line=dict(color="gray", width=2, dash="dot"),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_annotation(
            x=arc_radius * np.cos(theta_rad/2) * 1.3,
            y=arc_radius * np.sin(theta_rad/2) * 1.3,
            text=f"θ = {theta_deg}°",
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        
        # 8. Depth markers
        depth_markers = 5
        for i in range(1, depth_markers + 1):
            depth_mark = i * h / depth_markers
            fig.add_annotation(
                x=-plot_width/3 - 0.5, y=depth_mark,
                text=f"{depth_mark:.1f} m",
                showarrow=False,
                font=dict(size=10, color="gray"),
                xanchor="right"
            )
        
        # 9. Add resultant force arrow
        force_arrow_scale = min(2.0, plot_width * 0.25)
        force_arrow_dx = -np.sin(theta_rad) * force_arrow_scale
        force_arrow_dy = np.cos(theta_rad) * force_arrow_scale
        
        fig.add_annotation(
            x=x_cp_plot - cp_marker_dx*1.5, y=y_cp_plot - cp_marker_dy*1.5,
            ax=x_cp_plot - cp_marker_dx*1.5 - force_arrow_dx, ay=y_cp_plot - cp_marker_dy*1.5 - force_arrow_dy,
            text=f"F_N = {F_N_kN:.1f} kN",
            showarrow=True,
            arrowhead=2,
            arrowsize=2,
            arrowwidth=3,
            arrowcolor="darkgreen",
            font=dict(size=14, color="darkgreen", family="Arial Black")
        )
        
        # Update layout
        fig.update_xaxes(
            range=[-plot_width/2, plot_width/2],
            scaleanchor="y",
            scaleratio=1,
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=True,
            title="Horizontal Distance (m)"
        )
        fig.update_yaxes(
            range=[-0.5, plot_height],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=True,
            title="Vertical Distance (m)"
        )
        fig.update_layout(
            plot_bgcolor='white',
            margin=dict(l=10, r=10, t=20, b=10),
            height=600,
            showlegend=False,
            hovermode='closest'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Dynamic caption
        if show_pressure_arrows:
            st.caption(
                f"Red arrows show hydrostatic pressure acting perpendicular to the inclined wall (θ={theta_deg}°). "
                f"Pressure is maximum ({P_bottom_kPa:.2f} kPa) at the top (deepest point) and zero at the bottom (water surface). "
                f"The green marker shows the center of pressure at {s_cp:.2f}m along the slope. "
                f"Total normal force: {F_N_kN:.2f} kN."
            )
        else:
            st.caption(
                f"The inclined wall (θ={theta_deg}°, L={L}m) experiences hydrostatic pressure from water depth {h:.2f}m. "
                f"Total normal force: {F_N_kN:.2f} kN. "
                "Enable 'Show Pressure Distribution' to visualize the pressure variation."
            )

with tab2:
    st.header("📚 Understanding Hydrostatic Forces on Inclined Walls")
    
    col_edu1, col_edu2 = st.columns([1, 1])
    
    with col_edu1:
        st.markdown("""
        ### Why Inclination Matters
        
        Inclined walls are common in hydraulic structures like dams, spillways, canal gates, and ship hulls.
        The angle of inclination significantly affects:
        - Magnitude of hydrostatic force
        - Direction of force components
        - Structural design requirements
        - Stability considerations
        
        ### Key Difference from Vertical Walls
        
        For a vertical wall, the entire length contributes to vertical depth. For an inclined wall:
        """)
        
        st.latex(r'h = L \sin\theta')
        
        st.markdown("""
        Where:
        - **h** = vertical depth (m)
        - **L** = length along slope (m)
        - **θ** = angle from horizontal
        
        This means for the same wall length, a more vertical orientation creates greater depth and larger forces.
        
        ### Pressure Distribution
        
        Pressure still depends on **vertical depth** below the surface, not distance along the slope:
        """)
        
        st.latex(r'P = \rho g d')
        
        st.markdown("""
        where d is the vertical depth below the water surface at any point.
        
        For an inclined surface, pressure:
        - Is **maximum** at the top (deepest point)
        - Is **zero** at the bottom (at water surface)
        - Decreases **linearly** along the slope
        """)
    
    with col_edu2:
        st.markdown("""
        ### Calculating the Normal Force
        
        The force acting perpendicular to the inclined surface is:
        """)
        
        st.latex(r'F_N = \frac{1}{2}\rho g w L^2 \sin\theta')
        
        st.markdown("""
        This formula shows:
        - Force ∝ L² (quadratic with length)
        - Force ∝ sin θ (increases with angle)
        - Force ∝ w (linear with width)
        - Force ∝ ρ (linear with density)
        
        ### Force Components
        
        The normal force can be resolved into:
        """)
        
        st.latex(r'F_H = F_N \sin\theta \quad \text{(horizontal)}')
        st.latex(r'F_V = F_N \cos\theta \quad \text{(vertical)}')
        
        st.markdown("""
        These components are important for:
        - Foundation design (horizontal thrust)
        - Stability analysis (sliding, overturning)
        - Load distribution in structure
        
        ### Center of Pressure
        
        Located at 2/3 of the length from the top (deepest point):
        """)
        
        st.latex(r's_{cp} = \frac{2}{3}L')
        
        st.markdown("""
        Measured along the slope. This is where the resultant force acts perpendicular to the surface.
        """)
    
    st.markdown("---")
    
    st.markdown("### Effect of Angle: Key Comparisons")
    
    angle_col1, angle_col2, angle_col3 = st.columns(3)
    
    with angle_col1:
        st.markdown("""
        #### Shallow Angles (0°-30°)
        
        **Characteristics:**
        - Small vertical depth
        - Low hydrostatic force
        - Large horizontal extent
        - Vertical component dominates
        
        **Applications:**
        - Tank bottoms
        - Gentle spillways
        - Drainage channels
        
        **Design focus:**
        - Erosion control
        - Drainage
        - Uplift pressure
        """)
    
    with angle_col2:
        st.markdown("""
        #### Moderate Angles (30°-60°)
        
        **Characteristics:**
        - Moderate depth and force
        - Balanced components
        - Common in practice
        - Good structural efficiency
        
        **Applications:**
        - Dam faces
        - Canal gates
        - Embankment slopes
        
        **Design focus:**
        - Sliding stability
        - Reinforcement
        - Both components matter
        """)
    
    with angle_col3:
        st.markdown("""
        #### Steep Angles (60°-90°)
        
        **Characteristics:**
        - Large vertical depth
        - High hydrostatic force
        - Approaches vertical
        - Horizontal component dominates
        
        **Applications:**
        - Lock gates
        - Dock walls
        - Ship hulls
        
        **Design focus:**
        - Bending strength
        - Horizontal thrust
        - Overturning
        """)
    
    st.markdown("---")
    
    st.markdown("### Common Misconceptions")
    
    misconception_col1, misconception_col2 = st.columns(2)
    
    with misconception_col1:
        st.error("""
        **❌ WRONG: "Force depends on wall length L"**
        
        It's not just length - it's the combination of length and angle!
        
        **✅ CORRECT:** Force depends on L² × sin(θ). Two walls with same L but 
        different angles will have very different forces.
        
        Example: L=10m at 30° gives half the force of L=10m at 90°
        """)
        
        st.error("""
        **❌ WRONG: "Pressure is maximum at the bottom of the slope"**
        
        This confuses position along slope with depth below surface.
        
        **✅ CORRECT:** Pressure is maximum at the **top** of the inclined wall 
        (deepest point below water surface) and **zero** at the bottom (at water surface).
        """)
    
    with misconception_col2:
        st.error("""
        **❌ WRONG: "The force acts along the slope"**
        
        Force direction is often confused with slope direction.
        
        **✅ CORRECT:** The hydrostatic force acts **perpendicular** to the surface, 
        not along it. It can be resolved into horizontal and vertical components.
        """)
        
        st.error("""
        **❌ WRONG: "Steeper always means more force"**
        
        This is only true if length L is held constant.
        
        **✅ CORRECT:** If you want the same vertical depth h, a steeper wall 
        requires **shorter** length L, which can result in **less** force overall.
        """)

with tab3:
    st.header("📋 Real-World Applications")
    
    st.markdown("""
    Inclined surfaces subjected to hydrostatic pressure appear in many engineering applications.
    Understanding how angle affects force is crucial for safe and economical design.
    """)
    
    app_col1, app_col2 = st.columns(2)
    
    with app_col1:
        st.markdown("""
        ### Dam and Spillway Structures
        
        **1. Gravity Dam Upstream Face**
        - **Typical angle**: 60-90° (usually ~80°)
        - **Purpose**: Hold back reservoir water
        - **Design**: Near-vertical to minimize foundation size
        - **Forces**: Very large (10⁴-10⁸ kN)
        - **Key consideration**: Must resist sliding and overturning
        
        **2. Spillway Chute**
        - **Typical angle**: 25-40°
        - **Purpose**: Safely discharge flood water
        - **Design**: Gentle slope for controlled flow
        - **Forces**: Moderate (depends on depth over crest)
        - **Key consideration**: Erosion resistance, cavitation
        
        **3. Embankment Dam Face**
        - **Typical angle**: 30-45° (often 1V:2H or 1V:1.5H)
        - **Purpose**: Earth/rockfill dam upstream slope
        - **Material**: Earth with impermeable core or facing
        - **Forces**: Distributed through embankment
        - **Key consideration**: Slope stability, seepage control
        
        ### Canal and Navigation Structures
        
        **4. Canal Side Walls**
        - **Typical angle**: 30-60°
        - **Purpose**: Lined irrigation or navigation canals
        - **Material**: Concrete, shotcrete, or earth
        - **Forces**: 50-500 kN depending on depth
        - **Key consideration**: Minimize seepage, prevent erosion
        
        **5. Lock Gates**
        - **Typical angle**: 85-90° (nearly vertical)
        - **Purpose**: Control water level in navigation locks
        - **Design**: Hinged or sliding gates
        - **Forces**: Can exceed 10,000 kN for large locks
        - **Example**: Panama Canal locks (33.5m depth)
        - **Key consideration**: Gate sealing, operation loads
        
        **6. Sluice Gates and Radial Gates**
        - **Typical angle**: Variable (30-90°)
        - **Purpose**: Flow control in dams and canals
        - **Design**: Can be inclined or curved
        - **Forces**: Vary with gate position and head
        - **Key consideration**: Hydraulic loads during operation
        """)
    
    with app_col2:
        st.markdown("""
        ### Marine and Coastal Engineering
        
        **7. Ship Hulls**
        - **Typical angle**: 60-80° from horizontal
        - **Purpose**: Underwater portion of ship structure
        - **Material**: Steel or aluminum plating
        - **Forces**: Increase with draft (depth)
        - **Key consideration**: Hydrodynamic design, pressure distribution
        - **Note**: External pressure (opposite direction)
        
        **8. Dry Dock Caissons**
        - **Typical angle**: 70-90°
        - **Purpose**: Movable gates to close dry docks
        - **Design**: Large steel structures, floated into place
        - **Forces**: Can exceed 50,000 kN
        - **Key consideration**: Buoyancy control, sealing
        
        **9. Seawalls and Bulkheads**
        - **Typical angle**: 70-90°
        - **Purpose**: Protect shoreline from erosion
        - **Material**: Concrete, sheet pile, or rock
        - **Forces**: Hydrostatic + wave impact
        - **Key consideration**: Combined loading, scour protection
        
        ### Industrial and Storage Applications
        
        **10. Tank Sloped Bottoms**
        - **Typical angle**: 5-15°
        - **Purpose**: Drainage and sediment collection
        - **Material**: Steel or concrete
        - **Forces**: Relatively small
        - **Key consideration**: Complete drainage, cleaning access
        
        **11. Hopper Dredge Holds**
        - **Typical angle**: 45-60° sloped sides
        - **Purpose**: Self-unloading cargo holds
        - **Material**: Marine-grade steel
        - **Forces**: Vary with cargo and water
        - **Key consideration**: Material flow, structural integrity
        
        **12. Clarifier and Settling Tanks**
        - **Typical angle**: 45-60° for conical bottoms
        - **Purpose**: Wastewater treatment, sediment settling
        - **Design**: Sloped for sludge collection
        - **Forces**: Modest (shallow depths)
        - **Key consideration**: Sludge sliding, scraper loads
        """)
    
    st.markdown("---")
    
    st.markdown("### Design Standards and Codes")
    
    code_col1, code_col2 = st.columns(2)
    
    with code_col1:
        st.markdown("""
        #### For Dams and Hydraulic Structures
        
        - **USBR Design Standards**: Guidelines for dam slopes
        - **ICOLD Bulletins**: International dam engineering
        - **USACE Engineering Manuals**: Lock and dam design
        - **ASCE 7**: Load combinations including hydrostatic
        
        #### Typical Safety Factors
        
        - **Dams**: 3.0-5.0 (permanent, critical)
        - **Lock gates**: 2.5-3.5 (operational structures)
        - **Spillways**: 2.0-3.0 (flood design)
        - **Temporary cofferdams**: 1.5-2.0
        """)
    
    with code_col2:
        st.markdown("""
        #### For Marine Structures
        
        - **ABS/DNV Rules**: Ship structural design
        - **PIANC Guidelines**: Port and waterway structures
        - **BS 6349**: Maritime structures code
        
        #### For Industrial Tanks
        
        - **API 650**: Welded tanks for oil storage
        - **ACI 350**: Concrete liquid-containing structures
        - **AWWA D100**: Welded carbon steel tanks
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Key Design Principles for Inclined Walls
    
    1. **Angle Selection**: Balance structural efficiency with constructability
    2. **Stability Analysis**: Check sliding, overturning, and bearing capacity
    3. **Drainage**: Prevent pressure buildup behind inclined surfaces
    4. **Material Choice**: Match material properties to angle and loads
    5. **Construction**: Consider formwork, access, and quality control
    6. **Monitoring**: Install instrumentation for long-term performance
    """)

# Quick calculator at bottom
st.markdown("---")
st.header("🧮 Quick Force Calculator")

calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)

with calc_col1:
    calc_L = st.number_input("Length L (m)", value=5.0, step=0.5, key="calc_L")
    calc_w = st.number_input("Width w (m)", value=3.0, step=0.5, key="calc_w")

with calc_col2:
    calc_theta = st.number_input("Angle θ (degrees)", value=45, step=5, key="calc_theta")
    calc_rho = st.number_input("Density ρ (kg/m³)", value=1000.0, step=50.0, key="calc_rho")

with calc_col3:
    calc_theta_rad = np.deg2rad(calc_theta)
    calc_h = calc_L * np.sin(calc_theta_rad)
    calc_F_N = 0.5 * calc_rho * 9.81 * calc_w * calc_L**2 * np.sin(calc_theta_rad) / 1000
    st.metric("Normal Force (kN)", f"{calc_F_N:.2f}")
    st.metric("Vertical Depth (m)", f"{calc_h:.2f}")

with calc_col4:
    calc_F_H = calc_F_N * np.sin(calc_theta_rad)
    calc_F_V = calc_F_N * np.cos(calc_theta_rad)
    st.metric("Horizontal Comp (kN)", f"{calc_F_H:.2f}")
    st.metric("Vertical Comp (kN)", f"{calc_F_V:.2f}")

st.caption("💡 **Quick calculator**: Instantly compute forces for any inclined wall configuration.")

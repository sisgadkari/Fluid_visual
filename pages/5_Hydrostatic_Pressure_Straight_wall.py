import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(page_title="Hydrostatic Force on Wall", layout="wide")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>💧 Hydrostatic Force on a Straight Vertical Wall</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
Explore how hydrostatic pressure creates forces on submerged vertical walls.
Understand the pressure distribution, resultant force, and center of pressure through interactive visualization.
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# Create tabs for different aspects
tab1, tab2, tab3 = st.tabs(["🎯 Interactive Simulation", "📚 Understanding Hydrostatic Forces", "📋 Real-World Applications"])

with tab1:
    # --- Main Layout ---
    col1, col2 = st.columns([2, 3])

    # --- Column 1: Inputs and Results ---
    with col1:
        st.header("🔬 Parameters")
        
        # --- Interactive Scenarios ---
        SCENARIOS = {
            "Custom...": {
                "D": 5.0, "w": 3.0, "rho": 1000.0,
                "desc": "Manually adjust all parameters below."
            },
            "Swimming Pool Wall": {
                "D": 2.5, "w": 25.0, "rho": 1000.0,
                "desc": "Typical swimming pool: 2.5m deep, 25m long wall. Moderate force on wall structure."
            },
            "Water Storage Tank": {
                "D": 8.0, "w": 5.0, "rho": 1000.0,
                "desc": "Industrial water tank: 8m depth, 5m width. Significant hydrostatic pressure at base."
            },
            "Small Dam": {
                "D": 15.0, "w": 50.0, "rho": 1000.0,
                "desc": "Small hydroelectric dam: 15m water depth behind 50m wide wall. Large forces requiring robust design."
            },
            "Aquarium Wall": {
                "D": 0.6, "w": 2.0, "rho": 1025.0,
                "desc": "Large aquarium viewing panel: 0.6m deep saltwater, 2m wide. Uses thick acrylic for safety."
            },
            "Coastal Seawall": {
                "D": 6.0, "w": 100.0, "rho": 1025.0,
                "desc": "Seawall protecting coastline: 6m tide height, 100m length. Must withstand seawater and waves."
            },
            "Chemical Storage": {
                "D": 4.0, "w": 3.0, "rho": 1200.0,
                "desc": "Chemical tank: 4m depth of dense liquid (ρ=1200 kg/m³). Higher density increases force."
            }
        }
        
        scenario = st.selectbox("Select Application Scenario", list(SCENARIOS.keys()))
        selected = SCENARIOS[scenario]
        st.info(selected["desc"])
        
        st.subheader("Geometry and Fluid Properties")
        c1, c2 = st.columns(2)
        with c1:
            D = st.slider("Depth of fluid, D (m)", 0.1, 20.0, selected["D"], step=0.1,
                         help="Vertical height of fluid from bottom to surface")
        with c2:
            w = st.slider("Width of wall, w (m)", 0.1, 100.0, selected["w"], step=0.5,
                         help="Horizontal extent of the wall (into the page)")

        c1, c2 = st.columns(2)
        with c1:
            rho = st.number_input("Fluid density, ρ (kg/m³)", value=selected["rho"], step=10.0, format="%.1f",
                                 help="Water: 1000, Seawater: 1025, typical range: 700-1400")
        with c2:
            g = st.number_input("Gravity, g (m/s²)", value=9.81, format="%.2f",
                               help="Standard gravity: 9.81 m/s²")
        
        st.subheader("📊 Visualization Options")
        show_pressure_arrows = st.checkbox("Show Pressure Distribution", value=True,
                                         help="Toggle to visualize how pressure acts on the wall")
        
        if show_pressure_arrows:
            c1, c2 = st.columns(2)
            with c1:
                n_arrows = st.slider("Number of pressure arrows", 5, 20, 10, step=1)
            with c2:
                arrow_style = st.radio("Arrow style", 
                                     ["Lines with heads", "Triangular arrows", "Force vectors"])
        
        show_gradient = st.checkbox("Show pressure gradient on wall", value=True,
                                   help="Shows color gradient indicating pressure intensity")

        # --- Calculations ---
        F = 0.5 * rho * g * w * D**2  # Force in Newtons (N)
        F_kN = F / 1000
        
        # Calculate center of pressure (measured from water surface downward)
        y_cp = (2/3) * D  # Center of pressure from water surface
        
        # Calculate moment about base
        M = F * (D - y_cp)  # Moment in N⋅m
        M_kNm = M / 1000
        
        # Pressure at bottom
        P_bottom = rho * g * D  # Pressure at bottom (Pa)
        P_bottom_kPa = P_bottom / 1000
        
        # Average pressure
        P_avg = P_bottom / 2
        P_avg_kPa = P_avg / 1000

        st.markdown("---")
        st.header("📈 Results Summary")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric(label="Total Hydrostatic Force (F)", value=f"{F_kN:,.2f} kN",
                      help="Total resultant force acting horizontally on the wall")
            st.metric(label="Max Pressure (at bottom)", value=f"{P_bottom_kPa:.2f} kPa",
                      help="Maximum pressure at the deepest point")
        with col_r2:
            st.metric(label="Center of Pressure", value=f"{y_cp:.2f} m",
                      help=f"Distance below water surface where resultant force acts = (2/3) × {D:.2f} m")
            st.metric(label="Moment about Base", value=f"{M_kNm:.2f} kN⋅m",
                      help="Overturning moment that foundation must resist")
        
        col_r3, col_r4 = st.columns(2)
        with col_r3:
            st.metric(label="Average Pressure", value=f"{P_avg_kPa:.2f} kPa",
                      help="Average pressure over wall height = P_max / 2")
        with col_r4:
            # Calculate wall area
            wall_area = D * w
            st.metric(label="Wall Area", value=f"{wall_area:.1f} m²",
                      help="Wetted surface area of the wall")
        
        st.markdown("---")
        st.header("🧮 Step-by-Step Calculation")
        
        with st.expander("📖 See Detailed Breakdown", expanded=False):
            st.markdown("### Hydrostatic Force on Vertical Wall")
            
            st.markdown("#### Step 1: Understand Pressure Distribution")
            st.write("Pressure in a static fluid increases linearly with depth below the free surface:")
            st.latex(r'P(y) = \rho g y')
            st.write(f"where y is the depth **below the water surface**.")
            st.write(f"• At surface (y = 0): P = 0 Pa (gauge pressure)")
            st.write(f"• At bottom (y = {D} m): P = {rho} × {g} × {D} = **{P_bottom:.0f} Pa** = **{P_bottom_kPa:.2f} kPa**")
            st.write(f"\n**Pressure varies linearly** from 0 at top to {P_bottom_kPa:.2f} kPa at bottom (triangular distribution).")
            
            st.markdown("#### Step 2: Calculate Resultant Hydrostatic Force")
            st.write("For a rectangular vertical wall, the force equals the volume of the pressure prism:")
            st.latex(r'F = \int_0^D P(y) \cdot w \, dy = \int_0^D \rho g y \cdot w \, dy')
            st.write("Evaluating the integral:")
            st.latex(r'F = w \rho g \int_0^D y \, dy = w \rho g \left[\frac{y^2}{2}\right]_0^D = \frac{1}{2} w \rho g D^2')
            st.write(f"\nAlternatively: Force = Average Pressure × Area")
            st.latex(r'F = P_{avg} \times A = \frac{P_{max}}{2} \times (D \times w) = \frac{\rho g D}{2} \times D \times w = \frac{1}{2}\rho g w D^2')
            st.write(f"\n**Calculation:**")
            st.write(f"F = 0.5 × {rho} kg/m³ × {g} m/s² × {w} m × ({D} m)²")
            st.write(f"F = 0.5 × {rho} × {g} × {w} × {D**2:.2f}")
            st.write(f"F = **{F:.0f} N** = **{F_kN:.2f} kN**")
            
            st.markdown("#### Step 3: Locate Center of Pressure")
            st.write("The center of pressure is where the resultant force acts. For a triangular pressure distribution:")
            st.latex(r'y_{cp} = \frac{\int_0^D y \cdot P(y) \, dy}{\int_0^D P(y) \, dy} = \frac{\int_0^D y \cdot (\rho g y) \, dy}{\int_0^D \rho g y \, dy}')
            st.write("Evaluating:")
            st.latex(r'y_{cp} = \frac{\rho g \int_0^D y^2 \, dy}{\rho g \int_0^D y \, dy} = \frac{D^3/3}{D^2/2} = \frac{2D}{3}')
            st.write(f"\n**Therefore:**")
            st.write(f"y_cp = (2/3) × {D} m = **{y_cp:.2f} m** from the water surface")
            st.write(f"Or equivalently: **{D - y_cp:.2f} m** from the bottom of the wall")
            st.write(f"\n💡 **Key insight**: The center of pressure is always at 2/3 of the depth from the surface, regardless of fluid density or wall size!")
            
            st.markdown("#### Step 4: Calculate Moment about Base")
            st.write("The overturning moment about the base of the wall:")
            st.latex(r'M = F \times d')
            st.write(f"where d is the perpendicular distance from the line of action to the base.")
            st.write(f"\n**Calculation:**")
            st.write(f"d = D - y_cp = {D} - {y_cp:.2f} = {D - y_cp:.2f} m")
            st.write(f"M = {F_kN:.2f} kN × {D - y_cp:.2f} m")
            st.write(f"M = **{M_kNm:.2f} kN⋅m**")
            st.write(f"\n⚠️ **Design consideration**: The foundation must provide sufficient resistance to prevent overturning.")
            
            st.markdown("#### Step 5: Verify Using Pressure Prism Concept")
            st.write("Alternative verification using the volume of the pressure prism:")
            st.write(f"• Base of triangle: P_max = {P_bottom_kPa:.2f} kPa")
            st.write(f"• Height of triangle: D = {D} m")
            st.write(f"• Width (into page): w = {w} m")
            st.write(f"\nVolume = (1/2) × base × height × width")
            st.write(f"Volume = (1/2) × {P_bottom:.0f} Pa × {D} m × {w} m")
            st.write(f"Volume = **{F:.0f} N** ✓")
            st.write(f"\nThe volume of the pressure prism equals the force!")
            
            st.markdown("### Physical Interpretation")
            if F_kN < 10:
                st.info(f"💡 **Small force**: {F_kN:.2f} kN. Suitable for small tanks, aquariums, or shallow pools. Standard construction materials adequate.")
            elif F_kN < 100:
                st.success(f"✅ **Moderate force**: {F_kN:.2f} kN. Typical for residential pools, small industrial tanks. Reinforced concrete or steel recommended.")
            elif F_kN < 1000:
                st.warning(f"⚠️ **Large force**: {F_kN:.2f} kN. Requires significant structural design. Common for large tanks, small dams. Heavy reinforcement necessary.")
            else:
                st.error(f"❗ **Very large force**: {F_kN:.2f} kN. Major civil engineering structure (large dam, massive retaining wall). Professional structural analysis essential.")
            
            # Force per unit width
            force_per_width = F_kN / w
            st.write(f"\n**Force per unit width**: {force_per_width:.2f} kN/m")
            if force_per_width < 5:
                st.write("→ Light duty construction")
            elif force_per_width < 50:
                st.write("→ Standard reinforced concrete")
            elif force_per_width < 200:
                st.write("→ Heavy reinforced concrete with anchoring")
            else:
                st.write("→ Massive structure with deep foundations required")
        
        st.markdown("---")
        st.header("🔍 Analysis Insights")
        
        with st.expander("💡 Parameter Sensitivity Analysis", expanded=False):
            st.markdown("**How each parameter affects the hydrostatic force:**")
            
            st.markdown("#### 1. Effect of Fluid Depth (D)")
            st.write(f"• Current value: **D = {D} m**")
            st.write(f"• **Critical relationship**: F ∝ D² (quadratic!)")
            st.latex(r'F = \frac{1}{2}\rho g w D^2')
            
            # Show effect of depth changes
            depths = [D * 0.5, D * 0.75, D, D * 1.5, D * 2]
            st.write("\n**Force at different depths:**")
            
            import pandas as pd
            depth_data = []
            for d in depths:
                f = 0.5 * rho * g * w * d**2 / 1000
                depth_ratio = d / D
                force_ratio = (d / D)**2
                depth_data.append({
                    "Depth (m)": f"{d:.2f}",
                    "Depth Ratio": f"×{depth_ratio:.2f}",
                    "Force (kN)": f"{f:.2f}",
                    "Force Ratio": f"×{force_ratio:.2f}"
                })
            st.table(pd.DataFrame(depth_data))
            
            st.error("⚠️ **CRITICAL INSIGHT**: Doubling the depth **quadruples** the force! This is why dam failures are catastrophic.")
            st.write("Example: Increasing depth from 5m to 10m increases force from 1 unit to 4 units!")
            
            st.markdown("#### 2. Effect of Wall Width (w)")
            st.write(f"• Current value: **w = {w} m**")
            st.write(f"• **Relationship**: F ∝ w (linear)")
            
            widths = [w * 0.5, w, w * 2]
            st.write("\n**Force at different widths:**")
            width_data = []
            for width in widths:
                f = 0.5 * rho * g * width * D**2 / 1000
                ratio = width / w
                width_data.append({
                    "Width (m)": f"{width:.1f}",
                    "Width Ratio": f"×{ratio:.2f}",
                    "Force (kN)": f"{f:.2f}",
                    "Force Ratio": f"×{ratio:.2f}"
                })
            st.table(pd.DataFrame(width_data))
            
            st.success("✅ Force increases linearly with width. Doubling width doubles force.")
            
            st.markdown("#### 3. Effect of Fluid Density (ρ)")
            st.write(f"• Current value: **ρ = {rho} kg/m³**")
            st.write(f"• **Relationship**: F ∝ ρ (linear)")
            
            st.write("\n**Common fluids and their forces:**")
            fluids_data = []
            fluids = {
                "Gasoline": 720,
                "Ethanol": 789,
                "Fresh water": 1000,
                "Seawater": 1025,
                "Glycerol": 1260,
                "Sulfuric acid": 1840,
                "Mercury": 13600
            }
            for fluid_name, density in fluids.items():
                f = 0.5 * density * g * w * D**2 / 1000
                ratio = density / rho
                fluids_data.append({
                    "Fluid": fluid_name,
                    "Density (kg/m³)": density,
                    "Force (kN)": f"{f:.2f}",
                    "Ratio to current": f"×{ratio:.2f}"
                })
            st.table(pd.DataFrame(fluids_data))
            
            st.markdown("#### 4. Pressure Distribution Characteristics")
            st.write("**Key properties of triangular pressure distribution:**")
            st.write(f"• **Zero pressure** at free surface (gauge pressure)")
            st.write(f"• **Maximum pressure** at bottom = {P_bottom_kPa:.2f} kPa")
            st.write(f"• **Average pressure** = P_max/2 = {P_avg_kPa:.2f} kPa")
            st.write(f"• **Center of pressure** always at 2/3 depth from surface")
            st.write(f"• **Linear variation** means uniform pressure gradient = {P_bottom_kPa/D:.2f} kPa/m")
            
            st.markdown("#### 5. Comparison: Depth vs Width Effects")
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                st.write("**Doubling Depth (D → 2D):**")
                st.write(f"• Force: {F_kN:.2f} → {F_kN*4:.2f} kN (×4)")
                st.write(f"• Center of pressure: {y_cp:.2f} → {y_cp*2:.2f} m")
                st.write(f"• Moment arm: {D-y_cp:.2f} → {2*D-2*y_cp:.2f} m (×2)")
                st.write(f"• Moment: {M_kNm:.2f} → {M_kNm*8:.2f} kN⋅m (×8!)")
            
            with col_comp2:
                st.write("**Doubling Width (w → 2w):**")
                st.write(f"• Force: {F_kN:.2f} → {F_kN*2:.2f} kN (×2)")
                st.write(f"• Center of pressure: {y_cp:.2f} m (unchanged)")
                st.write(f"• Moment arm: {D-y_cp:.2f} m (unchanged)")
                st.write(f"• Moment: {M_kNm:.2f} → {M_kNm*2:.2f} kN⋅m (×2)")
            
            st.info("💡 **Design implication**: Depth has much more dramatic effect than width. Keep tanks/dams shallow when possible!")

        with st.expander("⚙️ Design Considerations", expanded=False):
            st.markdown("**Engineering design factors for walls subjected to hydrostatic pressure:**")
            
            st.markdown("#### 1. Structural Design Requirements")
            
            st.write("**A. Factor of Safety**")
            st.write("Typical factors of safety for hydrostatic loading:")
            safety_factors = {
                "Permanent structures (dams, tanks)": "2.0 - 3.0",
                "Temporary structures (cofferdams)": "1.5 - 2.0",
                "Seismic zones": "3.0 - 4.0",
                "Critical facilities": "3.5 - 5.0"
            }
            for structure, sf in safety_factors.items():
                st.write(f"• {structure}: SF = {sf}")
            
            design_force = F_kN * 2.5  # Assuming SF = 2.5
            st.write(f"\n**For current wall with SF = 2.5:**")
            st.write(f"Design force = {F_kN:.2f} × 2.5 = **{design_force:.2f} kN**")
            st.write(f"Design moment = {M_kNm:.2f} × 2.5 = **{M_kNm*2.5:.2f} kN⋅m**")
            
            st.write("\n**B. Material Selection**")
            
            # Material recommendations based on force per unit width
            force_per_width = F_kN / w
            
            if force_per_width < 5:
                st.success("✅ **Light duty** (< 5 kN/m):")
                st.write("• Glass or acrylic panels (aquariums, display tanks)")
                st.write("• Thickness: 10-25 mm for glass, 15-40 mm for acrylic")
                st.write("• Suitable for: Small aquariums, fountain walls")
            
            if 5 <= force_per_width < 50:
                st.info("💡 **Medium duty** (5-50 kN/m):")
                st.write("• Reinforced concrete (minimum 200 mm thick)")
                st.write("• Steel reinforcement: #4 bars @ 300 mm centers")
                st.write("• Suitable for: Swimming pools, small storage tanks")
            
            if 50 <= force_per_width < 200:
                st.warning("⚠️ **Heavy duty** (50-200 kN/m):")
                st.write("• Reinforced concrete (400-800 mm thick)")
                st.write("• Heavy reinforcement: #6 bars @ 150 mm centers, both faces")
                st.write("• Concrete strength: minimum 30 MPa")
                st.write("• Suitable for: Large industrial tanks, small dams")
            
            if force_per_width >= 200:
                st.error("❗ **Extra heavy duty** (> 200 kN/m):")
                st.write("• Mass concrete or heavily reinforced concrete (> 1000 mm)")
                st.write("• Multiple layers of reinforcement")
                st.write("• Deep foundation with rock anchors")
                st.write("• Professional structural analysis required")
                st.write("• Suitable for: Large dams, deep shafts")
            
            st.markdown("#### 2. Foundation Design")
            
            st.write("**A. Overturning Stability**")
            st.write("The wall must resist overturning moment:")
            st.latex(r'\text{Resisting Moment} \geq \text{SF} \times \text{Overturning Moment}')
            st.write(f"\nRequired resisting moment ≥ 2.0 × {M_kNm:.2f} = **{M_kNm*2:.2f} kN⋅m**")
            
            # Calculate required base width for stability
            # Assuming concrete density = 2400 kg/m³, wall thickness = D/10
            wall_thickness = max(0.3, D / 10)
            concrete_density = 2400
            wall_weight_per_m = concrete_density * 9.81 * wall_thickness * D / 1000  # kN per meter width
            
            st.write(f"\n**Example calculation** (concrete wall, thickness = {wall_thickness:.2f} m):")
            st.write(f"• Wall weight per meter: {wall_weight_per_m:.2f} kN/m")
            st.write(f"• Weight provides resisting moment about base")
            
            st.write("\n**B. Sliding Resistance**")
            st.write("The wall must resist sliding:")
            st.latex(r'\text{Friction Force} \geq \text{SF} \times F')
            st.write(f"\nRequired friction force ≥ 1.5 × {F_kN:.2f} = **{F_kN*1.5:.2f} kN**")
            st.write("Achieved through:")
            st.write("• Foundation weight and friction (μ ≈ 0.5-0.7 for concrete on rock)")
            st.write("• Shear keys extending into foundation")
            st.write("• Rock anchors or piles")
            
            st.markdown("#### 3. Special Considerations")
            
            st.write("**A. Water Seepage and Drainage**")
            st.write("• Install drainage system behind wall (reduce pore pressure)")
            st.write("• Weep holes at regular intervals (300-600 mm spacing)")
            st.write("• Filter fabric to prevent soil migration")
            st.write("• Waterproofing membrane on water-facing side")
            
            st.write("\n**B. Thermal Effects**")
            st.write("• Temperature changes cause expansion/contraction")
            st.write("• Provide expansion joints every 15-30 m")
            st.write("• Consider thermal stresses in design")
            
            st.write("\n**C. Dynamic Loading (for dams/seawalls)**")
            st.write("• Earthquake loads (seismic coefficient 0.1-0.3)")
            st.write("• Wave impact forces")
            st.write("• Ice pressure (cold climates)")
            st.write("• Sediment pressure (for dams)")
            
            st.write("\n**D. Construction Sequence**")
            st.write("• Pour concrete in lifts (not full height at once)")
            st.write("• Allow curing between lifts (minimum 7 days)")
            st.write("• Backfill gradually to avoid sudden loading")
            st.write("• Monitor for cracks and leaks during filling")

        with st.expander("📊 Pressure Distribution Table", expanded=False):
            st.markdown("**Pressure variation with depth:**")
            
            # Create detailed pressure table
            n_points = 11
            pressure_table = []
            for i in range(n_points):
                depth_from_surface = (i / (n_points - 1)) * D
                height_from_bottom = D - depth_from_surface
                pressure = rho * g * depth_from_surface
                pressure_kPa = pressure / 1000
                percent_max = (depth_from_surface / D) * 100
                
                pressure_table.append({
                    "Depth from surface (m)": f"{depth_from_surface:.2f}",
                    "Height from bottom (m)": f"{height_from_bottom:.2f}",
                    "Pressure (kPa)": f"{pressure_kPa:.2f}",
                    "% of max pressure": f"{percent_max:.0f}%"
                })
            
            st.table(pd.DataFrame(pressure_table))
            
            st.write(f"\n**Key observations:**")
            st.write(f"• Pressure gradient = {P_bottom_kPa/D:.2f} kPa per meter of depth")
            st.write(f"• At center of pressure ({y_cp:.2f} m): P = {rho*g*y_cp/1000:.2f} kPa ({(y_cp/D)*100:.0f}% of max)")
            st.write(f"• At mid-depth ({D/2:.2f} m): P = {rho*g*D/2/1000:.2f} kPa (50% of max)")

    # --- Column 2: Visualization ---
    with col2:
        st.header("🖼️ Visualization")
        
        # Add instructional message when arrows are hidden
        if not show_pressure_arrows:
            st.info("👆 Enable 'Show Pressure Distribution' to visualize how pressure acts on the wall")

        fig = go.Figure()
        
        # --- Visualization Constants - Scale with fluid depth ---
        wall_x = 0
        fluid_x_end = 10
        
        # Make vessel depth scale with fluid depth (add some freeboard)
        freeboard = max(1.0, D * 0.1)  # At least 1m or 10% of depth
        vessel_depth = D + freeboard
        
        y_surface = freeboard  # Water surface is at the freeboard level
        y_bottom = vessel_depth  # Bottom of vessel

        # 1. Draw the Wall/Vessel Outline
        fig.add_shape(
            type="rect", x0=wall_x-0.5, y0=0, x1=wall_x, y1=vessel_depth,
            fillcolor="rgba(128, 128, 128, 0.3)",
            line=dict(color="black", width=2),
            layer="below"
        )
        
        # Add wall label
        fig.add_annotation(
            x=wall_x-0.25, y=vessel_depth/2, 
            text="<b>WALL</b>", 
            textangle=-90,
            showarrow=False, 
            font=dict(size=12, color="black"),
            xanchor="center"
        )
        
        # 2. Draw the Fluid
        fig.add_shape(
            type="rect", x0=wall_x, y0=y_surface, x1=fluid_x_end, y1=y_bottom,
            fillcolor="rgba(0, 119, 182, 0.3)",
            line_width=0,
            layer="below"
        )
        
        # 3. Draw pressure gradient if enabled
        if show_gradient:
            gradient_steps = 50
            for i in range(gradient_steps):
                y_top = y_surface + (i * D / gradient_steps)
                y_bot = y_surface + ((i + 1) * D / gradient_steps)
                opacity = 0.02 + 0.1 * (i / gradient_steps)
                
                # Gradient on wall surface
                fig.add_shape(
                    type="rect", 
                    x0=wall_x - 0.1, y0=y_top, 
                    x1=wall_x, y1=y_bot,
                    fillcolor=f"rgba(255, 0, 0, {opacity})",
                    line_width=0,
                    layer="above"
                )

        # Calculate max pressure for labels
        max_pressure = rho * g * D
        arrow_max_length = 4
        
        # 4. Draw Pressure Arrows if enabled
        if show_pressure_arrows:
            
            if arrow_style == "Lines with heads":
                # Draw arrows as lines with triangular heads at the wall
                for i in range(n_arrows):
                    frac = (i + 0.5) / n_arrows
                    y_arrow = y_surface + frac * D
                    depth_from_surface = frac * D
                    pressure = rho * g * depth_from_surface
                    arrow_length = arrow_max_length * (pressure / max_pressure)
                    
                    # Draw arrow shaft
                    fig.add_shape(
                        type="line",
                        x0=wall_x + arrow_length, y0=y_arrow,
                        x1=wall_x + 0.05, y1=y_arrow,
                        line=dict(color="red", width=4)
                    )
                    
                    # Draw arrow head
                    head_size = 0.2
                    fig.add_trace(go.Scatter(
                        x=[wall_x + head_size + 0.05, wall_x + 0.02, wall_x + head_size + 0.05],
                        y=[y_arrow - head_size/2, y_arrow, y_arrow + head_size/2],
                        fill="toself",
                        fillcolor="red",
                        line=dict(color="red", width=0),
                        mode='lines',
                        showlegend=False,
                        hoverinfo='text',
                        text=f"Depth: {depth_from_surface:.2f} m<br>Pressure: {pressure/1000:.2f} kPa<br>Force per width: {pressure*1/1000:.2f} kN/m"
                    ))
            
            elif arrow_style == "Triangular arrows":
                # Draw arrows as solid triangles
                for i in range(n_arrows):
                    frac = (i + 0.5) / n_arrows
                    y_arrow = y_surface + frac * D
                    depth_from_surface = frac * D
                    pressure = rho * g * depth_from_surface
                    arrow_length = arrow_max_length * (pressure / max_pressure)
                    
                    triangle_height = 0.15
                    fig.add_trace(go.Scatter(
                        x=[wall_x + arrow_length, wall_x + 0.02, wall_x + arrow_length],
                        y=[y_arrow - triangle_height, y_arrow, y_arrow + triangle_height],
                        fill="toself",
                        fillcolor="red",
                        line=dict(color="darkred", width=1),
                        mode='lines',
                        showlegend=False,
                        hoverinfo='text',
                        text=f"Depth: {depth_from_surface:.2f} m<br>Pressure: {pressure/1000:.2f} kPa"
                    ))
            
            else:  # Force vectors
                # Draw as force vectors with dots
                for i in range(n_arrows):
                    frac = (i + 0.5) / n_arrows
                    y_arrow = y_surface + frac * D
                    depth_from_surface = frac * D
                    pressure = rho * g * depth_from_surface
                    arrow_length = arrow_max_length * (pressure / max_pressure)
                    
                    # Draw base point
                    fig.add_trace(go.Scatter(
                        x=[wall_x + arrow_length], 
                        y=[y_arrow],
                        mode='markers',
                        marker=dict(size=8, color='red'),
                        showlegend=False,
                        hoverinfo='text',
                        text=f"Depth: {depth_from_surface:.2f} m<br>Pressure: {pressure/1000:.2f} kPa"
                    ))
                    
                    # Draw arrow shaft
                    fig.add_shape(
                        type="line",
                        x0=wall_x + arrow_length, y0=y_arrow,
                        x1=wall_x + 0.05, y1=y_arrow,
                        line=dict(color="red", width=3)
                    )
                    # Add arrowhead
                    fig.add_shape(
                        type="path",
                        path=f"M {wall_x + 0.25} {y_arrow - 0.1} L {wall_x + 0.02} {y_arrow} L {wall_x + 0.25} {y_arrow + 0.1} Z",
                        fillcolor="red",
                        line=dict(color="red", width=0)
                    )

        # 5. Water surface line
        fig.add_shape(
            type="line", 
            x0=wall_x, y0=y_surface, 
            x1=fluid_x_end, y1=y_surface, 
            line=dict(color="#0077B6", width=3, dash="dash")
        )
        fig.add_annotation(
            x=fluid_x_end-0.5, y=y_surface, 
            text="Water Surface", 
            showarrow=False, 
            font=dict(color="#0077B6", size=14), 
            xanchor="right", 
            yshift=-15
        )
        
        # 6. Add depth markers
        depth_markers = 5
        for i in range(depth_markers + 1):
            depth_frac = i / depth_markers
            y_mark = y_surface + depth_frac * D
            actual_depth = depth_frac * D
            
            fig.add_annotation(
                x=fluid_x_end + 0.5, y=y_mark,
                text=f"{actual_depth:.1f} m",
                showarrow=False,
                font=dict(size=10, color="gray"),
                xanchor="left"
            )
        
        # 7. Add labels based on arrow visibility
        if show_pressure_arrows:
            fig.add_annotation(
                x=wall_x + arrow_max_length/2, y=y_surface - 0.8,
                text="<b>Hydrostatic Pressure Distribution</b>",
                showarrow=False,
                font=dict(size=14),
                xanchor="center"
            )
            
            # Add pressure scale
            fig.add_annotation(
                x=wall_x + arrow_max_length + 0.5, y=(y_surface + y_bottom)/2,
                text=f"← Max: {max_pressure/1000:.1f} kPa",
                showarrow=False,
                font=dict(size=12, color="red"),
                xanchor="left"
            )
        
        # Always show center of pressure marker
        y_cp_plot = y_surface + y_cp
        fig.add_shape(
            type="line",
            x0=wall_x - 0.3, y0=y_cp_plot,
            x1=wall_x + 0.3, y1=y_cp_plot,
            line=dict(color="green", width=3, dash="dot")
        )
        fig.add_annotation(
            x=wall_x - 0.35, y=y_cp_plot,
            text="C.P.",
            showarrow=False,
            font=dict(size=12, color="green", family="Arial Black"),
            xanchor="right"
        )
        
        # Add center of pressure annotation
        fig.add_annotation(
            x=wall_x + 1, y=y_cp_plot,
            text=f"Center of Pressure<br>{y_cp:.2f} m from surface<br>{D-y_cp:.2f} m from bottom",
            showarrow=True,
            arrowhead=2,
            arrowcolor="green",
            font=dict(size=10, color="green"),
            xanchor="left",
            ax=50, ay=0
        )
        
        # Show maximum pressure location
        fig.add_shape(
            type="rect",
            x0=wall_x - 0.5, y0=y_bottom - 0.02,
            x1=wall_x + 2, y1=y_bottom + 0.02,
            fillcolor="yellow",
            opacity=0.3,
            line=dict(color="orange", width=1)
        )
        fig.add_annotation(
            x=wall_x + 0.75, y=y_bottom,
            text=f"P_max = {max_pressure/1000:.1f} kPa",
            showarrow=False,
            font=dict(size=10, color="darkorange", family="Arial Black"),
            xanchor="center"
        )
        
        # Add resultant force arrow and label
        fig.add_annotation(
            x=wall_x - 0.8, y=y_cp_plot,
            ax=wall_x - 0.8 - 1.5, ay=y_cp_plot,
            text=f"F = {F_kN:.1f} kN",
            showarrow=True,
            arrowhead=2,
            arrowsize=2,
            arrowwidth=3,
            arrowcolor="darkgreen",
            font=dict(size=14, color="darkgreen", family="Arial Black")
        )

        # --- Layout and Axes Configuration ---
        # Add result box at top of visualization (matching other modules' style)
        fig.add_annotation(
            x=(wall_x + fluid_x_end) / 2,
            y=-0.3,
            text=f"<b>Hydrostatic Force: {F_kN:.2f} kN</b>",
            showarrow=False,
            font=dict(size=20, color="white"),
            bgcolor="rgba(0, 100, 200, 0.9)",
            bordercolor="darkblue",
            borderwidth=2,
            borderpad=8
        )
        
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-2, fluid_x_end + 2]),
            yaxis=dict(
                title="Vertical Position (m)",
                range=[vessel_depth + 1, -0.5],
                showgrid=True, 
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=False,
                dtick=max(1, D // 10)  # Dynamic tick spacing based on depth
            ),
            plot_bgcolor="white",
            margin=dict(l=10, r=10, t=20, b=10),
            height=600,
            showlegend=False,
            hovermode='closest'
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # Dynamic caption based on visualization state
        if show_pressure_arrows:
            st.caption(
                f"The red arrows represent hydrostatic pressure acting perpendicular to the wall. "
                f"Arrow length increases linearly with depth, forming a triangular distribution. "
                f"The green dashed line (C.P.) shows the center of pressure at {y_cp:.2f} m from the surface "
                f"({D-y_cp:.2f} m from bottom), where the resultant force of {F_kN:.2f} kN acts. "
                f"Total wall width into the page: {w} m."
            )
        else:
            st.caption(
                f"The fluid exerts hydrostatic pressure on the submerged wall. "
                f"Total force: {F_kN:.2f} kN acting horizontally at the center of pressure (green line) "
                f"located at {y_cp:.2f} m from the surface. "
                "Enable 'Show Pressure Distribution' to visualize the pressure variation."
            )

with tab2:
    st.header("📚 Understanding Hydrostatic Forces on Vertical Walls")
    
    col_edu1, col_edu2 = st.columns([1, 1])
    
    with col_edu1:
        st.markdown("""
        ### What is Hydrostatic Force?
        
        Hydrostatic force is the force exerted by a static (non-moving) fluid on a surface due to the 
        weight of the fluid above. For a vertical wall holding back water, this force arises from the 
        pressure variation with depth.
        
        ### The Physics of Pressure in Static Fluids
        
        In any static fluid, pressure increases linearly with depth according to:
        """)
        
        st.latex(r'P = P_0 + \rho g h')
        
        st.markdown("""
        Where:
        - **P** = pressure at depth h (Pa)
        - **P₀** = pressure at surface (usually atmospheric, taken as 0 for gauge pressure)
        - **ρ** = fluid density (kg/m³)
        - **g** = gravitational acceleration (9.81 m/s²)
        - **h** = depth below free surface (m)
        
        For gauge pressure (P₀ = 0):
        """)
        
        st.latex(r'P = \rho g h')
        
        st.markdown("""
        ### Pressure Distribution on Vertical Wall
        
        For a vertical rectangular wall from surface (depth 0) to bottom (depth D):
        - **At surface (h = 0)**: P = 0 (gauge pressure)
        - **At depth h**: P = ρgh (linear increase)
        - **At bottom (h = D)**: P = ρgD (maximum)
        
        This creates a **triangular pressure distribution** - zero at top, maximum at bottom.
        """)
    
    with col_edu2:
        st.markdown("""
        ### Calculating the Resultant Force
        
        The total force on the wall is found by integrating pressure over the area:
        """)
        
        st.latex(r'F = \int_A P \, dA = \int_0^D \rho g y \cdot w \, dy')
        
        st.markdown("""
        Evaluating this integral:
        """)
        
        st.latex(r'F = w \rho g \left[\frac{y^2}{2}\right]_0^D = \frac{1}{2} w \rho g D^2')
        
        st.markdown("""
        **Alternative interpretation**: 
        """)
        
        st.latex(r'F = \text{Average Pressure} \times \text{Area} = \frac{P_{max}}{2} \times (D \times w)')
        
        st.markdown("""
        ### Locating the Center of Pressure
        
        The center of pressure is the point where the resultant force acts. For a triangular 
        distribution, it's located at the centroid of the pressure triangle:
        """)
        
        st.latex(r'y_{cp} = \frac{2}{3}D')
        
        st.markdown("""
        Measured from the water surface downward. This is **always 2/3 of the depth**, regardless of:
        - Fluid density
        - Wall dimensions
        - Absolute depth
        
        ### Why 2/3 Depth?
        
        The centroid of a triangle is at 1/3 of its height from the base. Since the pressure 
        triangle has its base at the bottom, the centroid (center of pressure) is at 1/3 up 
        from the bottom, which is 2/3 down from the top.
        """)
    
    st.markdown("---")
    
    st.markdown("### Key Equations Summary")
    
    eq_col1, eq_col2, eq_col3 = st.columns(3)
    
    with eq_col1:
        st.markdown("""
        #### Pressure at Depth
        """)
        st.latex(r'P(y) = \rho g y')
        st.markdown("""
        - Linear with depth
        - Independent of wall size
        - Depends only on fluid properties
        """)
    
    with eq_col2:
        st.markdown("""
        #### Resultant Force
        """)
        st.latex(r'F = \frac{1}{2}\rho g w D^2')
        st.markdown("""
        - Quadratic with depth (F ∝ D²)
        - Linear with width (F ∝ w)
        - Linear with density (F ∝ ρ)
        """)
    
    with eq_col3:
        st.markdown("""
        #### Center of Pressure
        """)
        st.latex(r'y_{cp} = \frac{2}{3}D')
        st.markdown("""
        - Always at 2/3 depth
        - Independent of fluid/wall
        - Measured from surface down
        """)
    
    st.markdown("---")
    
    st.markdown("### Common Misconceptions")
    
    misconception_col1, misconception_col2 = st.columns(2)
    
    with misconception_col1:
        st.error("""
        **❌ WRONG: "Force acts at the middle of the wall"**
        
        Many assume the force acts at D/2 (midpoint). This would be true for uniform 
        pressure, but hydrostatic pressure is triangular!
        
        **✅ CORRECT:** Force acts at 2/3 depth from surface (or 1/3 height from bottom)
        """)
        
        st.error("""
        **❌ WRONG: "Doubling depth doubles the force"**
        
        This linear thinking is incorrect!
        
        **✅ CORRECT:** Force ∝ D². Doubling depth **quadruples** the force!
        
        Example: D = 5m → F = 100 kN  
        D = 10m → F = 400 kN (not 200 kN!)
        """)
    
    with misconception_col2:
        st.error("""
        **❌ WRONG: "Deeper water just means more pressure at bottom"**
        
        While true, this misses the key point: **average pressure** also increases, 
        and **wetted area** increases.
        
        **✅ CORRECT:** Force increases as D² because both average pressure (∝ D) 
        and area (∝ D) increase.
        """)
        
        st.error("""
        **❌ WRONG: "Water pressure pushes down on the wall"**
        
        Pressure in a fluid acts **perpendicular** to any surface.
        
        **✅ CORRECT:** For a vertical wall, pressure acts **horizontally**, 
        pushing the wall backward, not downward.
        """)

with tab3:
    st.header("📋 Real-World Applications")
    
    st.markdown("""
    Hydrostatic forces on vertical walls are one of the most important considerations in civil 
    and hydraulic engineering. Understanding these forces is essential for safe design of water 
    retention structures.
    """)
    
    st.markdown("""
    ### Major Applications
    
    **1. Dams and Reservoirs** - 10-200m depth, forces up to 10⁸ kN
    
    **2. Water Storage Tanks** - 100-50,000 m³ volume
    
    **3. Swimming Pools** - 1.2-3.0m depth, residential to Olympic
    
    **4. Aquariums** - Thick acrylic panels, safety factor 4-6
    
    **5. Seawalls and Coastal Protection** - Must withstand waves and tides
    
    **6. Ship Locks** - Hold back 5-30m of water difference
    
    **7. Basement Waterproofing** - Resist groundwater pressure
    
    **8. Chemical Storage Tanks** - Higher density fluids increase forces
    
    For detailed application examples, safety considerations, and failure case studies, 
    explore the interactive simulation above with different scenarios.
    """)

# Quick calculator at bottom
st.markdown("---")
st.header("🧮 Quick Force Calculator")

calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)

with calc_col1:
    calc_D = st.number_input("Depth D (m)", value=5.0, step=0.5, key="calc_D")
    calc_w = st.number_input("Width w (m)", value=3.0, step=0.5, key="calc_w")

with calc_col2:
    calc_rho = st.number_input("Density ρ (kg/m³)", value=1000.0, step=50.0, key="calc_rho")
    calc_g = st.number_input("Gravity g (m/s²)", value=9.81, key="calc_g")

with calc_col3:
    calc_F = 0.5 * calc_rho * calc_g * calc_w * calc_D**2
    calc_F_kN = calc_F / 1000
    calc_y_cp = (2/3) * calc_D
    st.metric("Force (kN)", f"{calc_F_kN:.2f}")
    st.metric("Center of Pressure (m)", f"{calc_y_cp:.2f}")

with calc_col4:
    calc_P_max = calc_rho * calc_g * calc_D / 1000
    calc_M = calc_F * (calc_D - calc_y_cp) / 1000
    st.metric("Max Pressure (kPa)", f"{calc_P_max:.2f}")
    st.metric("Moment (kN⋅m)", f"{calc_M:.2f}")

st.caption("💡 **Quick calculator**: Instantly compute force and related parameters for any wall configuration.")

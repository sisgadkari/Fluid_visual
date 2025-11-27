import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Capillary Rise Simulator")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>💧 Interactive Capillary Rise Simulator</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>Explore how surface tension causes liquids to rise or fall in small tubes. Adjust the parameters and watch the liquid level animate to its new height.</p>",
    unsafe_allow_html=True
)
st.markdown("---")

# Create tabs for different aspects
tab1, tab2, tab3 = st.tabs(["🎯 Interactive Simulation", "📚 Understanding Capillary Action", "📋 Real-World Applications"])

with tab1:
    # --- Initialize Session State ---
    if 'previous_h' not in st.session_state:
        st.session_state.previous_h = None

    # --- Layout ---
    col1, col2 = st.columns([1, 1])

    # --- Column 1: Input Controls ---
    with col1:
        st.header("🔬 Parameters")

        # --- Preset Fluid Options ---
        fluid_choice = st.selectbox(
            "Choose a preset fluid:",
            ("Water (20°C)", "Mercury (20°C)", "Ethanol (20°C)", "Glycerol (20°C)", "Acetone (20°C)", "Custom"),
            key="fluid_selector"
        )

        # Preset values
        FLUID_PROPERTIES = {
            "Water (20°C)":   {'sigma': 0.0728, 'rho': 998, 'color': 'rgba(100, 170, 255, 0.7)', 'theta': 0},
            "Mercury (20°C)": {'sigma': 0.485, 'rho': 13534, 'color': 'rgba(180, 180, 180, 0.7)', 'theta': 140},
            "Ethanol (20°C)": {'sigma': 0.0223, 'rho': 789, 'color': 'rgba(200, 150, 255, 0.7)', 'theta': 0},
            "Glycerol (20°C)": {'sigma': 0.063, 'rho': 1260, 'color': 'rgba(255, 200, 150, 0.7)', 'theta': 19},
            "Acetone (20°C)": {'sigma': 0.0237, 'rho': 784, 'color': 'rgba(255, 180, 200, 0.7)', 'theta': 0},
        }
        
        if fluid_choice == "Custom":
            st.subheader("Custom Fluid Properties")
            sigma = st.slider("Surface Tension (σ) [N/m]", 0.01, 0.5, 0.0728, 0.001, format="%.4f")
            rho = st.number_input("Liquid Density (ρ) [kg/m³]", value=998)
            liquid_color = 'rgba(100, 170, 255, 0.7)'
        else:
            properties = FLUID_PROPERTIES[fluid_choice]
            sigma = properties['sigma']
            rho = properties['rho']
            liquid_color = properties['color']
            st.info(f"Loaded properties for **{fluid_choice}**.")
            st.markdown(f"**Surface Tension (σ):** `{sigma}` N/m")
            st.markdown(f"**Liquid Density (ρ):** `{rho}` kg/m³")

        st.subheader("Tube and Angle Properties")
        theta_deg = st.slider("Contact Angle (θ) [degrees]", 0, 180, 90,
                             help="0° = perfect wetting, 90° = neutral, >90° = non-wetting")
        d_mm = st.slider("Capillary Diameter (d) [mm]", 0.1, 10.0, 1.0, 0.1,
                        help="Smaller diameter = greater capillary rise")
        
        d_m = d_mm / 1000
        g = 9.81
        theta_rad = np.deg2rad(theta_deg)

        # --- Calculation ---
        if d_m > 0 and rho > 0:
            h = (4 * sigma * np.cos(theta_rad)) / (rho * g * d_m)
        else:
            h = 0
        
        h_mm = h * 1000
        
        st.markdown("---")
        st.header("📈 Results")
        st.metric(label="Calculated Capillary Rise (h)", value=f"{h_mm:.2f} mm")
        
        # Provide context based on result
        if h_mm > 0:
            st.success(f"✅ Liquid rises {h_mm:.2f} mm due to wetting (θ < 90°)")
        elif h_mm < 0:
            st.warning(f"⚠️ Liquid depresses {abs(h_mm):.2f} mm due to non-wetting (θ > 90°)")
        else:
            st.info("💡 Neutral wetting at θ = 90° - no rise or depression")
        
        st.latex(r'''\Large h = \frac{4 \sigma \cos(\theta)}{\rho g d}''')
        
        # Show step-by-step calculation
        with st.expander("📖 See Step-by-Step Calculation", expanded=False):
            st.markdown("### Detailed Calculation Steps")
            
            st.markdown("#### Step 1: Given Parameters")
            st.write(f"• Surface tension: σ = {sigma} N/m")
            st.write(f"• Contact angle: θ = {theta_deg}°")
            st.write(f"• Liquid density: ρ = {rho} kg/m³")
            st.write(f"• Tube diameter: d = {d_mm} mm = {d_m} m")
            st.write(f"• Gravity: g = {g} m/s²")
            
            st.markdown("#### Step 2: Apply Capillary Rise Equation")
            st.latex(r'h = \frac{4\sigma\cos(\theta)}{\rho g d}')
            
            st.markdown("#### Step 3: Calculate cos(θ)")
            cos_theta = np.cos(theta_rad)
            st.write(f"cos({theta_deg}°) = {cos_theta:.4f}")
            
            st.markdown("#### Step 4: Calculate Numerator")
            numerator = 4 * sigma * cos_theta
            st.write(f"Numerator = 4 × {sigma} × {cos_theta:.4f}")
            st.write(f"Numerator = {numerator:.6f} N/m")
            
            st.markdown("#### Step 5: Calculate Denominator")
            denominator = rho * g * d_m
            st.write(f"Denominator = {rho} × {g} × {d_m}")
            st.write(f"Denominator = {denominator:.4f} kg/s²")
            
            st.markdown("#### Step 6: Final Result")
            st.write(f"h = {numerator:.6f} / {denominator:.4f}")
            st.write(f"h = {h:.6f} m")
            st.write(f"**h = {h_mm:.2f} mm**")
            
            if theta_deg < 90:
                st.success("✅ Positive height → Liquid rises (wetting)")
            elif theta_deg > 90:
                st.warning("⚠️ Negative height → Liquid depresses (non-wetting)")
            else:
                st.info("💡 Zero height → Neutral (no capillary effect)")

    # --- Column 2: Visualization ---
    with col2:
        st.header("🖼️ Visualization")
        plot_placeholder = st.empty()

        # This function creates the plot for a given instantaneous height
        def generate_plot(instant_h=0):
            tube_radius_vis = d_mm / 2
            h_vis_target = h * 1000
            max_y_val = max(abs(h_vis_target), 5)
            plot_y_range = [-max_y_val * 0.5, max_y_val * 1.5]
            plot_height = plot_y_range[1]
            beaker_radius = 15
            beaker_bottom = min(-5, h_vis_target - 2)

            fig = go.Figure()
            line_color = liquid_color.replace('0.7', '1')

            # 1. Draw beaker and liquid
            fig.add_shape(type="line", x0=-beaker_radius, y0=beaker_bottom, x1=-beaker_radius, y1=0, line=dict(color="grey", width=2))
            fig.add_shape(type="line", x0=beaker_radius, y0=beaker_bottom, x1=beaker_radius, y1=0, line=dict(color="grey", width=2))
            fig.add_shape(type="line", x0=-beaker_radius, y0=beaker_bottom, x1=beaker_radius, y1=beaker_bottom, line=dict(color="grey", width=2))
            
            # Liquid around the tube
            fig.add_trace(go.Scatter(x=[-beaker_radius, -tube_radius_vis, -tube_radius_vis, -beaker_radius], y=[beaker_bottom, beaker_bottom, 0, 0], fill='toself', fillcolor=liquid_color, mode='none'))
            fig.add_trace(go.Scatter(x=[tube_radius_vis, beaker_radius, beaker_radius, tube_radius_vis], y=[beaker_bottom, beaker_bottom, 0, 0], fill='toself', fillcolor=liquid_color, mode='none'))

            # 2. Draw tube and meniscus
            fig.add_shape(type="line", x0=-tube_radius_vis, y0=beaker_bottom, x1=-tube_radius_vis, y1=plot_height, line=dict(color="darkgrey", width=3))
            fig.add_shape(type="line", x0=tube_radius_vis, y0=beaker_bottom, x1=tube_radius_vis, y1=plot_height, line=dict(color="darkgrey", width=3))

            meniscus_x = np.linspace(-tube_radius_vis, tube_radius_vis, 100)
            curvature_direction = -1 if theta_deg < 90 else 1
            meniscus_y = instant_h - curvature_direction * (meniscus_x**2 / (tube_radius_vis * 2)) * np.tan(np.deg2rad(90 - theta_deg if theta_deg < 90 else theta_deg - 90)) if tube_radius_vis > 0 else instant_h
            if tube_radius_vis > 0:
                meniscus_y -= (meniscus_y[-1] - instant_h)
            
            x_fill = np.concatenate([meniscus_x, [tube_radius_vis, -tube_radius_vis]])
            y_fill = np.concatenate([meniscus_y, [beaker_bottom, beaker_bottom]])
            fig.add_trace(go.Scatter(x=x_fill, y=y_fill, fill='toself', fillcolor=liquid_color, mode='none', hoverinfo='none'))
            fig.add_trace(go.Scatter(x=meniscus_x, y=meniscus_y, mode='lines', line=dict(color=line_color), hoverinfo='none'))

            # Position the annotation dynamically based on the tube radius
            annotation_base_x = tube_radius_vis + 1.5
            fig.add_annotation(x=annotation_base_x, y=instant_h / 2, ax=annotation_base_x, ay=0, text="", showarrow=True, arrowhead=3, arrowwidth=2, arrowcolor="black")
            fig.add_annotation(x=annotation_base_x + 0.5, y=instant_h / 2, text=f"h = {instant_h:.2f} mm", showarrow=False, font=dict(size=28), xanchor='left')

            fig.update_layout(
                xaxis=dict(range=[-25, 25], showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(range=[beaker_bottom - 1, plot_y_range[1]], zeroline=False, title_text="Height (mm)"),
                showlegend=False, height=600, plot_bgcolor='white'
            )
            return fig

        # --- Main Visualization and Animation Logic ---
        h_vis_target = h * 1000
        start_h = st.session_state.previous_h
        end_h = h_vis_target
        
        # On the very first run, start_h is None. Set it to the target to prevent animation.
        if start_h is None:
            start_h = end_h

        # Animate if the height has changed.
        if not np.isclose(start_h, end_h):
            animation_steps = 15
            for i in range(animation_steps + 1):
                intermediate_h = start_h + (end_h - start_h) * (i / animation_steps)
                fig = generate_plot(intermediate_h)
                plot_placeholder.plotly_chart(fig, use_container_width=True)
                time.sleep(0.03)
        else:
            fig = generate_plot(end_h)
            plot_placeholder.plotly_chart(fig, use_container_width=True)
        
        # Always update the previous height for the next run
        st.session_state.previous_h = end_h

with tab2:
    st.header("📚 Understanding Capillary Action")
    
    col_edu1, col_edu2 = st.columns([1, 1])
    
    with col_edu1:
        st.markdown("""
        ### What is Capillary Action?
        
        **Capillary action** (or capillarity) is the ability of a liquid to flow in narrow spaces without 
        the assistance of external forces. It occurs when adhesive forces (liquid-to-solid) are stronger 
        than cohesive forces (liquid-to-liquid).
        
        ### The Physics Behind It
        
        **Surface Tension:**
        - Molecules at a liquid surface experience unbalanced forces
        - Creates a "skin" that resists external force
        - Measured in N/m (force per unit length)
        
        **Contact Angle (θ):**
        - Angle between liquid surface and solid surface
        - θ < 90°: Liquid wets the surface (adhesion > cohesion)
        - θ = 90°: Neutral wetting
        - θ > 90°: Liquid doesn't wet surface (cohesion > adhesion)
        
        ### The Capillary Rise Equation
        """)
        
        st.latex(r'h = \frac{4\sigma\cos(\theta)}{\rho g d}')
        
        st.markdown("""
        Where:
        - **h** = Height of liquid column (m)
        - **σ** = Surface tension (N/m)
        - **θ** = Contact angle (degrees)
        - **ρ** = Liquid density (kg/m³)
        - **g** = Gravitational acceleration (9.81 m/s²)
        - **d** = Tube diameter (m)
        
        ### Key Relationships
        
        **Height is proportional to:**
        - Surface tension (↑σ → ↑h)
        - Contact angle through cos(θ) (↑θ from 0° → ↓h)
        
        **Height is inversely proportional to:**
        - Density (↑ρ → ↓h)
        - Tube diameter (↑d → ↓h) - **Most dramatic effect!**
        """)
    
    with col_edu2:
        st.markdown("""
        ### Force Balance
        
        At equilibrium, upward and downward forces balance:
        
        **Upward force (Surface Tension):**
        """)
        st.latex(r'F_{up} = \sigma \cdot \pi d \cdot \cos(\theta)')
        
        st.markdown("""
        Acts along the perimeter where liquid touches tube wall.
        
        **Downward force (Weight):**
        """)
        st.latex(r'F_{down} = \rho g V = \rho g \cdot \frac{\pi d^2}{4} \cdot h')
        
        st.markdown("""
        Weight of the liquid column that has been lifted.
        
        **At Equilibrium:**
        """)
        st.latex(r'F_{up} = F_{down}')
        
        st.markdown("""
        Solving this gives us the capillary rise equation!
        
        ### Wetting vs Non-Wetting
        
        | Property | Wetting (θ < 90°) | Non-Wetting (θ > 90°) |
        |----------|-------------------|----------------------|
        | Example | Water in glass | Mercury in glass |
        | Meniscus | Concave (curves down) | Convex (curves up) |
        | Rise/Depression | Rises (h > 0) | Depresses (h < 0) |
        | cos(θ) | Positive | Negative |
        | Adhesion | Strong | Weak |
        
        ### Common Misconceptions
        
        **❌ "Capillary action requires gravity"**
        
        **✅ CORRECT:** Capillary action works in zero gravity! The Young-Laplace 
        equation (ΔP = 2σ/r) creates pressure differences that pull liquid into narrow 
        spaces even without gravity.
        
        **❌ "Larger tubes have stronger capillary action"**
        
        **✅ CORRECT:** Smaller diameter tubes show MUCH stronger effects. 
        Halving the diameter doubles the height!
        
        **❌ "All liquids behave the same way"**
        
        **✅ CORRECT:** Different liquids have vastly different:
        - Surface tensions (water: 0.073 N/m, mercury: 0.485 N/m)
        - Contact angles (water: 0°, mercury: 140°)
        - Densities (water: 1000 kg/m³, mercury: 13,534 kg/m³)
        
        ### Temperature Effects
        
        Surface tension **decreases** with temperature:
        - Water at 0°C: σ = 0.076 N/m
        - Water at 20°C: σ = 0.073 N/m
        - Water at 100°C: σ = 0.059 N/m
        
        Therefore: **Hot liquids show reduced capillary rise**
        """)

with tab3:
    st.header("📋 Real-World Applications")
    
    st.markdown("""
    Capillary action is everywhere in nature and technology! Here are major applications:
    """)
    
    app_col1, app_col2 = st.columns(2)
    
    with app_col1:
        st.markdown("""
        ### Biological Systems
        
        **1. Plant Xylem**
        - **Tube diameter**: 10-200 µm
        - **Height**: Up to 100+ meters in tall trees!
        - **Mechanism**: Capillary action + transpiration pull
        - **Key insight**: Extremely narrow vessels enable water transport 
          from roots to leaves without a pump
        
        **2. Blood Capillaries**
        - **Diameter**: 5-10 µm (smallest blood vessels)
        - **Function**: Nutrient/gas exchange
        - **Capillary action**: Helps distribute blood through tiny vessels
        
        **3. Soil-Plant Water Movement**
        - **Soil pores**: 1-100 µm
        - **Process**: Water moves from soil into plant roots via capillarity
        
        ### Industrial Applications
        
        **4. Paper Towels & Absorbents**
        - **Fiber spacing**: 10-100 µm
        - **Mechanism**: Network of tiny channels wicks liquid rapidly
        - **Applications**: Paper towels, diapers, medical dressings
        
        **5. Inkjet Printing**
        - **Nozzle diameter**: 10-50 µm
        - **Function**: Capillary action helps control ink droplet formation
        
        **6. Heat Pipes**
        - **Wick structure**: 1-100 µm pores
        - **Function**: Capillary action returns condensed fluid to heat source
        - **Applications**: CPU cooling, spacecraft thermal management
        """)
    
    with app_col2:
        st.markdown("""
        ### Scientific & Medical Applications
        
        **7. Thin Layer Chromatography (TLC)**
        - **Mechanism**: Capillary action pulls solvent up silica gel plate
        - **Pore size**: 2-100 nm
        - **Use**: Separating chemical mixtures
        
        **8. Microfluidics**
        - **Channel width**: 10-500 µm
        - **Applications**: Lab-on-a-chip devices, blood glucose monitors
        
        **9. Wicking Fabrics**
        - **Fiber spacing**: 5-50 µm
        - **Function**: Pull sweat away from skin
        - **Materials**: Synthetic microfibers
        
        ### Other Applications
        
        **10. Oil Recovery**
        - **Rock pores**: 0.1-100 µm
        - **Challenge**: Oil trapped in tiny pores by capillary forces
        
        **11. Rising Damp in Buildings**
        - **Problem**: Water rises through concrete/brick pores
        - **Height**: Can reach 1-2 meters above ground
        
        **12. Candle Wicks**
        - **Function**: Continuously delivers fuel to flame via capillary action
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Typical Capillary Rise Values
    
    | Fluid | Tube Diameter | Approximate Rise |
    |-------|--------------|------------------|
    | Water | 1 mm | 30 mm |
    | Water | 0.1 mm | 300 mm (30 cm!) |
    | Water | 0.01 mm (10 µm) | 3000 mm (3 m!) |
    | Mercury | 1 mm | -19 mm (depression) |
    | Ethanol | 1 mm | 12 mm |
    
    **Key insight:** The 1/d relationship means 10× smaller diameter → 10× greater rise!
    """)

st.markdown("---")
st.info("💡 **Tip**: Try experimenting with different fluids and tube diameters in the Interactive Simulation tab to see these principles in action!")

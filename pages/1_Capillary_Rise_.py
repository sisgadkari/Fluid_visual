import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Capillary Rise Simulator")

# --- Initialize Session State ---
if 'previous_h' not in st.session_state:
    st.session_state.previous_h = None

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

        # Preset values for [surface tension (N/m), density (kg/m³), color, typical contact angle]
        FLUID_PROPERTIES = {
            "Water (20°C)":   {'sigma': 0.0728, 'rho': 998, 'color': 'rgba(100, 170, 255, 0.7)', 'theta': 0, 'desc': 'Wets glass strongly, rises in tubes'},
            "Mercury (20°C)": {'sigma': 0.485, 'rho': 13534, 'color': 'rgba(180, 180, 180, 0.7)', 'theta': 140, 'desc': 'Does not wet glass, depresses in tubes'},
            "Ethanol (20°C)": {'sigma': 0.0223, 'rho': 789, 'color': 'rgba(200, 150, 255, 0.7)', 'theta': 0, 'desc': 'Low surface tension, good wetting'},
            "Glycerol (20°C)": {'sigma': 0.063, 'rho': 1260, 'color': 'rgba(255, 200, 150, 0.7)', 'theta': 19, 'desc': 'Viscous, moderate wetting'},
            "Acetone (20°C)": {'sigma': 0.0237, 'rho': 784, 'color': 'rgba(255, 180, 200, 0.7)', 'theta': 0, 'desc': 'Very low surface tension'},
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
            st.info(f"**{fluid_choice}**: {properties['desc']}")
            st.markdown(f"**Surface Tension (σ):** `{sigma}` N/m")
            st.markdown(f"**Liquid Density (ρ):** `{rho}` kg/m³")

        st.subheader("Tube and Angle Properties")
        theta_deg = st.slider("Contact Angle (θ) [degrees]", 0, 180, 
                             properties.get('theta', 90) if fluid_choice != "Custom" else 90,
                             help="0° = perfect wetting, 90° = neutral, >90° = non-wetting")
        d_mm = st.slider("Capillary Diameter (d) [mm]", 0.1, 10.0, 1.0, 0.1,
                        help="Smaller diameter = greater capillary rise")
        
        # Visualization options
        col_vis1, col_vis2 = st.columns(2)
        with col_vis1:
            show_forces = st.checkbox("Show Force Balance", value=False)
        with col_vis2:
            show_comparison = st.checkbox("Show Scale Reference", value=True)
        
        d_m = d_mm / 1000
        g = 9.81
        theta_rad = np.deg2rad(theta_deg)

        # --- Calculation ---
        if d_m > 0 and rho > 0:
            h = (4 * sigma * np.cos(theta_rad)) / (rho * g * d_m)
        else:
            h = 0
        
        # Additional calculations
        h_mm = h * 1000
        
        # Adhesive force (upward)
        circumference = np.pi * d_m
        F_adhesive = sigma * circumference * np.cos(theta_rad)
        
        # Weight of liquid column (downward)
        if h > 0:
            volume = np.pi * (d_m/2)**2 * abs(h)
            mass = rho * volume
            F_weight = mass * g
        else:
            F_weight = 0
            volume = 0
        
        # Pressure difference
        delta_P = 2 * sigma * np.cos(theta_rad) / (d_m/2)
        delta_P_Pa = delta_P
        
        st.markdown("---")
        st.header("📊 Results Summary")
        
        # Main result with interpretation
        if h > 0:
            rise_direction = "⬆️ Rise (liquid climbs up)"
            result_color = "normal"
        elif h < 0:
            rise_direction = "⬇️ Depression (liquid pushed down)"
            result_color = "inverse"
        else:
            rise_direction = "➡️ No change"
            result_color = "off"
        
        st.metric(label="Capillary Rise (h)", value=f"{h_mm:.2f} mm", 
                 delta=rise_direction, delta_color=result_color)
        
        # Additional metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("In meters", f"{h:.4f} m")
        with col_m2:
            st.metric("In cm", f"{h*100:.2f} cm")
        with col_m3:
            st.metric("In inches", f"{h*39.37:.3f} in")
        
        st.markdown("---")
        st.header("🧮 Step-by-Step Calculation")
        
        with st.expander("📖 See Detailed Breakdown", expanded=False):
            st.markdown("### Fundamental Equation")
            st.markdown("The capillary rise is determined by balancing surface tension forces with gravitational forces:")
            st.latex(r'h = \frac{4 \sigma \cos(\theta)}{\rho g d}')
            
            st.markdown("### Step 1: Calculate Surface Tension Force")
            st.markdown("The upward force due to surface tension acts along the contact line (perimeter):")
            st.latex(r'F_{adhesive} = \sigma \times \text{perimeter} \times \cos(\theta)')
            st.write(f"Perimeter = π × d = π × {d_mm} mm = {circumference*1000:.3f} mm")
            st.write(f"F_adhesive = {sigma} × {circumference:.6f} × cos({theta_deg}°)")
            st.write(f"F_adhesive = **{F_adhesive*1e6:.4f} µN** (microNewtons)")
            
            st.markdown("### Step 2: Calculate Weight of Liquid Column")
            st.markdown("The downward force is the weight of the liquid column:")
            st.latex(r'F_{weight} = \rho \times g \times V = \rho \times g \times \frac{\pi d^2}{4} \times h')
            if h != 0:
                st.write(f"Volume = π × (d/2)² × |h| = {volume*1e9:.4f} mm³")
                st.write(f"Mass = ρ × V = {rho} × {volume:.9f} = {mass*1e6:.4f} mg")
                st.write(f"F_weight = {mass*1e6:.4f} mg × {g} m/s² = **{F_weight*1e6:.4f} µN**")
            else:
                st.write("No liquid column (h = 0)")
            
            st.markdown("### Step 3: Force Balance")
            st.markdown("At equilibrium, upward surface tension force equals downward weight:")
            st.latex(r'F_{adhesive} = F_{weight}')
            st.write(f"{F_adhesive*1e6:.4f} µN ≈ {F_weight*1e6:.4f} µN")
            
            if abs(F_adhesive - F_weight) < 1e-10:
                st.success("✅ Forces are balanced!")
            
            st.markdown("### Step 4: Solve for Height")
            st.markdown("Rearranging the force balance equation:")
            st.latex(r'h = \frac{4 \sigma \cos(\theta)}{\rho g d}')
            st.write(f"h = (4 × {sigma} × cos({theta_deg}°)) / ({rho} × {g} × {d_m})")
            st.write(f"h = **{h:.6f} m** = **{h_mm:.2f} mm**")
            
            st.markdown("### Step 5: Pressure Interpretation")
            st.markdown("The capillary rise creates a pressure difference:")
            st.latex(r'\Delta P = \frac{2\sigma \cos(\theta)}{r} = \rho g h')
            st.write(f"ΔP = (2 × {sigma} × cos({theta_deg}°)) / {d_m/2}")
            st.write(f"ΔP = **{delta_P_Pa:.2f} Pa**")
            
            # Physical interpretation
            st.markdown("### Physical Interpretation")
            if h > 0:
                st.success(f"✅ **Capillary Rise**: The liquid climbs {h_mm:.2f} mm due to adhesive forces exceeding cohesive forces.")
                st.info("The contact angle < 90° indicates the liquid 'wets' the tube material. Surface tension pulls the liquid upward along the tube wall.")
            elif h < 0:
                st.warning(f"⚠️ **Capillary Depression**: The liquid is pushed down {abs(h_mm):.2f} mm below the reservoir level.")
                st.info("The contact angle > 90° indicates the liquid does NOT wet the tube material. Cohesive forces dominate, creating a depression.")
            else:
                st.info("ℹ️ No capillary action occurs. Contact angle = 90° represents neutral wetting.")
        
        st.markdown("---")
        st.header("🔍 Analysis Insights")
        
        with st.expander("💡 Parameter Sensitivity Analysis", expanded=False):
            st.markdown("**How each parameter affects capillary rise:**")
            
            # Surface tension effect
            st.markdown("#### 1. Surface Tension (σ)")
            st.write(f"• Current value: {sigma} N/m")
            st.write(f"• Effect: h ∝ σ (directly proportional)")
            if sigma > 0.05:
                st.info("💡 High surface tension (like mercury) can produce large effects even with poor wetting.")
            else:
                st.info("💡 Low surface tension requires good wetting (low θ) for significant capillary rise.")
            
            # Density effect
            st.markdown("#### 2. Liquid Density (ρ)")
            st.write(f"• Current value: {rho} kg/m³")
            st.write(f"• Effect: h ∝ 1/ρ (inversely proportional)")
            if rho > 5000:
                st.warning("⚠️ High density (like mercury) results in smaller capillary effects for the same surface tension.")
            else:
                st.success("✅ Lower density liquids show more pronounced capillary action.")
            
            # Contact angle effect
            st.markdown("#### 3. Contact Angle (θ)")
            st.write(f"• Current value: {theta_deg}°")
            st.write(f"• Effect: h ∝ cos(θ)")
            
            cos_theta = np.cos(theta_rad)
            st.write(f"• cos({theta_deg}°) = {cos_theta:.3f}")
            
            if theta_deg < 45:
                st.success("✅ Excellent wetting: Strong capillary rise expected")
            elif theta_deg < 90:
                st.info("💡 Good wetting: Moderate capillary rise")
            elif theta_deg == 90:
                st.warning("⚠️ Neutral: No capillary action (cos(90°) = 0)")
            else:
                st.error("❌ Non-wetting: Capillary depression occurs (cos(θ) < 0)")
            
            # Diameter effect
            st.markdown("#### 4. Tube Diameter (d)")
            st.write(f"• Current value: {d_mm} mm")
            st.write(f"• Effect: h ∝ 1/d (inversely proportional)")
            
            # Calculate rise for different diameters
            d_half = d_m / 2
            h_half = (4 * sigma * np.cos(theta_rad)) / (rho * g * d_half)
            
            st.write(f"• If diameter halved to {d_mm/2:.2f} mm: h would be **{h_half*1000:.2f} mm** (doubled)")
            st.info("💡 **Key insight**: Capillary effects are MUCH more pronounced in narrow tubes. This is why paper towels (tiny pores) wick water so effectively.")

        with st.expander("⚖️ Force Balance Visualization", expanded=False):
            st.markdown("**Understanding the equilibrium:**")
            
            col_force1, col_force2 = st.columns(2)
            
            with col_force1:
                st.markdown("#### Upward Forces")
                st.write(f"**Surface Tension Component:**")
                st.write(f"• Force: {F_adhesive*1e6:.4f} µN")
                st.write(f"• Acts along: Contact line (perimeter)")
                st.write(f"• Direction: Vertical component upward")
                st.write(f"• Magnitude depends on: σ, d, cos(θ)")
                
                if theta_deg < 90:
                    st.success("✅ Positive vertical component → Pulls liquid up")
                elif theta_deg > 90:
                    st.warning("⚠️ Negative vertical component → Pushes liquid down")
            
            with col_force2:
                st.markdown("#### Downward Forces")
                st.write(f"**Gravitational Weight:**")
                st.write(f"• Force: {F_weight*1e6:.4f} µN")
                st.write(f"• Acts on: Entire liquid column")
                st.write(f"• Direction: Vertically downward")
                st.write(f"• Magnitude depends on: ρ, g, volume (∝ d²h)")
                
                if h != 0:
                    st.info(f"💡 Liquid column height: {abs(h_mm):.2f} mm")

            st.markdown("---")
            st.markdown("**Energy Perspective:**")
            st.write("At equilibrium, the system minimizes total energy:")
            st.write("• **Surface energy**: Increases with liquid-gas interface area")
            st.write("• **Gravitational potential energy**: Increases with height")
            st.write("• **Adhesive energy**: Decreases with liquid-solid contact")
            st.info("The final height represents the balance where total energy is minimized.")

        with st.expander("🎯 Practical Implications", expanded=False):
            st.markdown("**What this means in real applications:**")
            
            # Time to equilibrium
            st.markdown("#### Time to Reach Equilibrium")
            
            # Estimate using Washburn equation (simplified)
            if h > 0 and rho > 0:
                viscosity_estimate = 0.001  # Pa·s, approximate for water
                if fluid_choice == "Glycerol (20°C)":
                    viscosity_estimate = 1.5
                elif fluid_choice == "Mercury (20°C)":
                    viscosity_estimate = 0.00155
                
                # Washburn time constant: t ∝ η·h/(σ·cos(θ))
                time_constant = (8 * viscosity_estimate * abs(h)) / (sigma * abs(np.cos(theta_rad))) if np.cos(theta_rad) != 0 else float('inf')
                
                st.write(f"• **Estimated rise time**: ~{time_constant:.2f} seconds")
                st.caption(f"(Assuming viscosity ≈ {viscosity_estimate*1000:.1f} mPa·s)")
                
                if time_constant < 1:
                    st.success("⚡ Very fast - nearly instantaneous")
                elif time_constant < 10:
                    st.info("💡 Fast - observable in real-time")
                else:
                    st.warning("⏱️ Slow - may take significant time")
            
            # Maximum theoretical height
            st.markdown("#### Theoretical Limits")
            
            # Calculate for minimum practical diameter (0.01 mm = 10 µm)
            d_min = 0.00001  # 10 µm
            h_max = (4 * sigma * abs(np.cos(theta_rad))) / (rho * g * d_min) if theta_deg != 90 else 0
            
            st.write(f"• **Maximum possible rise** (d = 10 µm): {h_max*100:.2f} cm")
            st.caption("This explains why capillary action can lift water meters high in plant stems!")
            
            # Pressure requirement
            st.markdown("#### Pressure Required to Prevent Rise")
            st.write(f"• **Pressure needed**: {delta_P_Pa:.2f} Pa = {delta_P_Pa/1000:.4f} kPa")
            st.write(f"• **Equivalent water column**: {delta_P_Pa/(rho*g)*1000:.2f} mm")
            
            if delta_P_Pa < 100:
                st.info("💡 Very small pressure - capillary effects dominate over gravity at this scale")
            else:
                st.warning("⚠️ Significant pressure - consider in system design")

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
            fig.add_trace(go.Scatter(x=meniscus_x, y=meniscus_y, mode='lines', line=dict(color=line_color, width=2), hoverinfo='none'))

            # Position the annotation dynamically based on the tube radius
            annotation_base_x = tube_radius_vis + 1.5
            fig.add_annotation(x=annotation_base_x, y=instant_h / 2, ax=annotation_base_x, ay=0, text="", showarrow=True, arrowhead=3, arrowwidth=2, arrowcolor="black")
            fig.add_annotation(x=annotation_base_x + 0.5, y=instant_h / 2, text=f"h = {instant_h:.2f} mm", showarrow=False, font=dict(size=20), xanchor='left')

            # Show forces if enabled
            if show_forces and instant_h != 0:
                # Surface tension force arrows
                arrow_y = instant_h * 0.8
                fig.add_annotation(
                    x=-tube_radius_vis, y=arrow_y, ax=-tube_radius_vis-3, ay=arrow_y+3,
                    showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="red"
                )
                fig.add_annotation(
                    x=tube_radius_vis, y=arrow_y, ax=tube_radius_vis+3, ay=arrow_y+3,
                    showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="red"
                )
                fig.add_annotation(x=tube_radius_vis+5, y=arrow_y+3, text="Surface<br>Tension", 
                                 showarrow=False, font=dict(size=10, color="red"))
                
                # Weight arrow
                if instant_h > 0:
                    fig.add_annotation(
                        x=0, y=instant_h/2, ax=0, ay=instant_h/2-3,
                        showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="blue"
                    )
                    fig.add_annotation(x=-tube_radius_vis-5, y=instant_h/2-3, text="Weight", 
                                     showarrow=False, font=dict(size=10, color="blue"))
            
            # Show comparison scale if enabled
            if show_comparison:
                # Add reference markers
                reference_heights = [1, 5, 10, 20, 50] if abs(h_vis_target) < 100 else [10, 50, 100, 200]
                for ref_h in reference_heights:
                    if beaker_bottom < ref_h < plot_height:
                        fig.add_shape(type="line", x0=beaker_radius+1, y0=ref_h, 
                                    x1=beaker_radius+2, y1=ref_h, 
                                    line=dict(color="gray", width=1, dash="dot"))
                        fig.add_annotation(x=beaker_radius+3, y=ref_h, text=f"{ref_h} mm", 
                                         showarrow=False, font=dict(size=9, color="gray"), xanchor="left")

            # Contact angle indicator
            if theta_deg != 90:
                angle_x = tube_radius_vis * 0.7
                angle_annotation_y = instant_h + 2
                fig.add_annotation(x=angle_x, y=angle_annotation_y, 
                                 text=f"θ = {theta_deg}°", 
                                 showarrow=False, font=dict(size=12, color="darkblue"),
                                 bgcolor="rgba(255,255,255,0.8)", bordercolor="blue", borderwidth=1)

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
        # If height hasn't changed, just draw the static plot.
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
        
        Capillary action (or capillarity) is the ability of a liquid to flow in narrow spaces without 
        the assistance of external forces like gravity. It occurs when **adhesive forces** between the 
        liquid and solid surface exceed **cohesive forces** within the liquid.
        
        ### The Physics Behind It
        
        Three key forces determine capillary behavior:
        
        1. **Surface Tension (σ)**: The energy per unit area at the liquid-air interface. Creates a 
           "skin" on the liquid surface that wants to minimize area.
        
        2. **Adhesion**: Attraction between liquid molecules and the solid surface (tube wall). 
           Pulls liquid up the wall.
        
        3. **Cohesion**: Attraction between liquid molecules themselves. Holds the liquid together 
           as a continuous column.
        
        ### The Fundamental Equation
        """)
        
        st.latex(r'h = \frac{4 \sigma \cos(\theta)}{\rho g d}')
        
        st.markdown("""
        Where:
        - **h** = height of capillary rise (m)
        - **σ** = surface tension (N/m)
        - **θ** = contact angle (degrees)
        - **ρ** = liquid density (kg/m³)
        - **g** = gravitational acceleration (9.81 m/s²)
        - **d** = tube diameter (m)
        """)
    
    with col_edu2:
        st.markdown("""
        ### Contact Angle: The Key Parameter
        
        The contact angle determines whether a liquid wets a surface:
        
        | Contact Angle | Behavior | Example |
        |--------------|----------|---------|
        | **θ < 10°** | Perfect wetting | Water on clean glass |
        | **10° < θ < 90°** | Partial wetting | Water on plastic |
        | **θ = 90°** | Neutral | Theoretical boundary |
        | **90° < θ < 150°** | Non-wetting | Mercury on glass |
        | **θ > 150°** | Superhydrophobic | Water on lotus leaf |
        
        ### Wetting vs. Non-Wetting
        
        **Wetting (θ < 90°):**
        - Adhesive forces > Cohesive forces
        - Liquid "climbs" the wall
        - Forms **concave meniscus** (curves down)
        - Results in **capillary rise** (h > 0)
        - Example: Water in glass tube
        
        **Non-Wetting (θ > 90°):**
        - Cohesive forces > Adhesive forces
        - Liquid "avoids" the wall
        - Forms **convex meniscus** (curves up)
        - Results in **capillary depression** (h < 0)
        - Example: Mercury in glass tube
        """)
    
    st.markdown("---")
    
    st.markdown("### The Meniscus Shape")
    
    meniscus_col1, meniscus_col2, meniscus_col3 = st.columns(3)
    
    with meniscus_col1:
        st.markdown("""
        #### Concave Meniscus (θ < 90°)
        
        - **Shape**: Curves downward
        - **Pressure**: Lower inside meniscus
        - **Effect**: Pulls liquid upward
        - **Common in**: Water, alcohols, acetone
        - **Curve radius**: Related to contact angle
        
        The curvature creates a pressure difference:
        """)
        st.latex(r'\Delta P = \frac{2\sigma \cos(\theta)}{r}')
        st.caption("This pressure difference drives the capillary rise")
    
    with meniscus_col2:
        st.markdown("""
        #### Flat Meniscus (θ = 90°)
        
        - **Shape**: Perfectly flat
        - **Pressure**: Equal on both sides
        - **Effect**: No capillary action
        - **Rare**: Theoretical ideal case
        - **Indication**: Perfect balance
        
        When cos(90°) = 0:
        """)
        st.latex(r'h = 0')
        st.caption("No driving force for liquid movement")
    
    with meniscus_col3:
        st.markdown("""
        #### Convex Meniscus (θ > 90°)
        
        - **Shape**: Curves upward
        - **Pressure**: Higher inside meniscus
        - **Effect**: Pushes liquid downward
        - **Common in**: Mercury, some oils
        - **Behavior**: Avoids solid contact
        
        Negative cos(θ) gives:
        """)
        st.latex(r'h < 0')
        st.caption("Results in capillary depression")
    
    st.markdown("---")
    
    st.markdown("### Scale Effects: Why Size Matters")
    
    scale_col1, scale_col2 = st.columns(2)
    
    with scale_col1:
        st.markdown("""
        #### Relationship: h ∝ 1/d
        
        Capillary rise is **inversely proportional** to tube diameter. This has profound implications:
        
        **Small Tubes (d < 1 mm):**
        - Very large capillary effects
        - Can lift liquids meters high
        - Dominates over gravity
        - Examples: Paper towels, soil, plant xylem
        
        **Medium Tubes (1 mm < d < 10 mm):**
        - Observable capillary rise
        - Centimeters to tens of cm
        - Laboratory demonstrations
        - Examples: Glass capillary tubes
        
        **Large Tubes (d > 10 mm):**
        - Minimal capillary effects
        - Millimeters or less
        - Gravity dominates
        - Examples: Drinking straws, pipes
        """)
    
    with scale_col2:
        st.markdown("""
        #### Practical Examples by Scale
        
        | Diameter | Rise (Water) | Application |
        |----------|--------------|-------------|
        | **10 µm** | ~3 m | Plant xylem vessels |
        | **100 µm** | ~30 cm | Paper towel pores |
        | **1 mm** | ~3 cm | Laboratory capillary |
        | **1 cm** | ~0.3 mm | Drinking straw |
        | **10 cm** | ~0.03 mm | Water pipe |
        
        **Key Insight:**
        
        This inverse relationship explains why:
        - Trees can pull water 100m+ high
        - Sponges and towels wick water
        - Soil retains water in tiny pores
        - Oil lamps work without pumps
        - Insects can walk on water
        """)
    
    st.markdown("---")
    
    st.markdown("### Energy Perspective")
    
    st.markdown("""
    Capillary action can be understood through energy minimization:
    
    **Three competing energy terms:**
    
    1. **Surface Energy** (E_surface = σ × Area): 
       - Increases with liquid-air interface area
       - System wants to minimize this
    
    2. **Adhesive Energy** (E_adhesive < 0):
       - Negative energy from liquid-solid contact
       - System wants to maximize this (good wetting)
    
    3. **Gravitational Potential Energy** (E_gravity = mgh):
       - Increases with liquid column height
       - System wants to minimize this
    
    **At equilibrium:**
    """)
    
    st.latex(r'\frac{dE_{total}}{dh} = 0')
    
    st.markdown("""
    The system finds the height where total energy is minimum, balancing these three contributions.
    
    **For good wetting (θ < 90°):**
    - Adhesive energy gain > Gravitational energy cost
    - Net benefit to rising until forces balance
    - Result: Capillary rise
    
    **For poor wetting (θ > 90°):**
    - Adhesive energy is small or negative
    - System minimizes liquid-solid contact
    - Result: Capillary depression
    """)

with tab3:
    st.header("📋 Real-World Applications")
    
    st.markdown("""
    Capillary action is fundamental to countless natural and technological processes. Understanding 
    it is essential for applications ranging from biology to industrial processes.
    """)
    
    app_col1, app_col2 = st.columns(2)
    
    with app_col1:
        st.markdown("""
        ### Biological Systems
        
        **1. Plant Water Transport**
        - **Mechanism**: Xylem vessels (10-200 µm diameter)
        - **Rise**: Can lift water 100+ meters in tall trees
        - **Combined with**: Transpiration pull and root pressure
        - **Critical for**: Nutrient delivery, photosynthesis
        - **Without it**: Plants couldn't grow tall
        
        *Example: A redwood tree lifts water 115m high, partly through capillary action in xylem vessels as small as 20 µm*
        
        **2. Fluid Movement in Tissues**
        - **Capillaries**: Blood vessels (5-10 µm diameter)
        - **Function**: Delivers oxygen, nutrients to cells
        - **Mechanism**: Combination of pressure and capillary forces
        - **Disease connection**: Capillary damage affects tissue health
        
        **3. Tear Film Maintenance**
        - **Location**: Surface of the eye
        - **Mechanism**: Capillary action in tear meniscus
        - **Function**: Keeps eye lubricated and clear
        - **Size scale**: ~100 µm tear film thickness
        
        **4. Insect Water Collection**
        - **Insects**: Many collect water through mouthparts
        - **Mechanism**: Grooves act as capillary channels
        - **Benefit**: Can drink from tiny water sources
        - **Example**: Desert beetles harvest fog on textured shells
        """)
    
    with app_col2:
        st.markdown("""
        ### Industrial & Daily Applications
        
        **5. Wicking in Textiles**
        - **Paper towels**: Network of cellulose fibers (10-100 µm)
        - **Sponges**: Porous structure with mm-scale channels
        - **Athletic wear**: Engineered fiber spacing for sweat wicking
        - **Diapers**: Super-absorbent polymers + capillary channels
        
        **6. Oil Lamps & Candles**
        - **Mechanism**: Fuel wicks through porous wick material
        - **Wick design**: Optimized pore size for steady fuel flow
        - **No pump needed**: Passive fuel delivery to flame
        - **History**: Used for thousands of years
        
        **7. Ink & Writing Instruments**
        - **Fountain pens**: Controlled ink flow through capillary feed
        - **Felt-tip markers**: Porous tip wicks ink from reservoir
        - **Ballpoint pens**: Capillary gaps control ink release
        - **Quill pens**: Natural capillary channels in feathers
        
        **8. Chromatography**
        - **Paper chromatography**: Solvent rises through paper
        - **Thin-layer chromatography (TLC)**: Precise separation
        - **Pore size**: Determines separation resolution
        - **Applications**: Analytical chemistry, forensics
        """)
    
    st.markdown("---")
    
    st.markdown("### Construction & Civil Engineering")
    
    construction_col1, construction_col2 = st.columns(2)
    
    with construction_col1:
        st.markdown("""
        **9. Moisture Rise in Buildings**
        - **Problem**: Water wicks up through porous materials
        - **Typical height**: 0.5-1.5 m above ground in bricks
        - **Pore sizes**: 0.1-100 µm in concrete, mortar
        - **Consequences**: Structural damage, mold, corrosion
        - **Solution**: Damp-proof courses, waterproof membranes
        
        **10. Soil Water Retention**
        - **Mechanism**: Capillary forces hold water in soil pores
        - **Pore sizes**: Clay (< 2 µm), silt (2-50 µm), sand (50-2000 µm)
        - **Plant access**: Root hair diameter ~10 µm
        - **Agriculture**: Critical for drought resistance
        - **Engineering**: Foundation design must account for this
        """)
    
    with construction_col2:
        st.markdown("""
        **11. Concrete Curing**
        - **Importance**: Proper moisture essential for strength
        - **Capillary pores**: 10-100 nm in cement paste
        - **Water retention**: Capillary forces keep concrete moist
        - **Problem**: Rapid drying causes cracks
        - **Solution**: Wet curing maintains capillary water
        
        **12. Paint & Coating Application**
        - **Flow**: Paint must wet surface through capillary action
        - **Coverage**: Depends on contact angle with substrate
        - **Penetration**: Into porous surfaces via capillarity
        - **Drying**: Capillary forces affect film formation
        - **Quality**: Poor wetting leads to defects
        """)
    
    st.markdown("---")
    
    st.markdown("### Laboratory & Analytical Techniques")
    
    lab_col1, lab_col2 = st.columns(2)
    
    with lab_col1:
        st.markdown("""
        **13. Microfluidics**
        - **Devices**: Lab-on-a-chip systems
        - **Channel size**: 10-500 µm
        - **Advantages**: No external pumps needed
        - **Applications**: Medical diagnostics, DNA analysis
        - **Design**: Engineered surface chemistry controls flow
        
        **14. Capillary Electrophoresis**
        - **Separation**: Based on charge and size
        - **Capillary diameter**: 25-100 µm
        - **Length**: 20-100 cm
        - **Applications**: Protein analysis, DNA sequencing
        - **Advantage**: Minimal sample volume needed
        """)
    
    with lab_col2:
        st.markdown("""
        **15. Medical Diagnostics**
        - **Blood glucose strips**: Capillary fill with 0.5 µL sample
        - **Pregnancy tests**: Urine wicks along test strip
        - **Lateral flow assays**: COVID-19 rapid tests
        - **Advantages**: Fast, cheap, no equipment needed
        - **Mechanism**: Designed pore network for controlled flow
        
        **16. Fuel Cells**
        - **Water management**: Must wick away product water
        - **GDL (gas diffusion layer)**: Porous ~10 µm fiber mat
        - **Problem**: Water flooding reduces performance
        - **Solution**: Engineered wettability gradients
        """)
    
    st.markdown("---")
    
    st.markdown("### Advanced Materials & Nanotechnology")
    
    st.markdown("""
    **17. Superhydrophobic Surfaces**
    - **Contact angle**: θ > 150° (water beads up)
    - **Examples**: Lotus leaf, water-repellent fabrics
    - **Structure**: Micro/nano texture + low-energy coating
    - **Applications**: Self-cleaning surfaces, anti-icing
    - **Mechanism**: Trapped air prevents wetting
    
    **18. Heat Pipes & Cooling**
    - **Working fluid**: Wicks through porous structure
    - **Wick**: Sintered metal, grooves, or mesh (10-100 µm pores)
    - **Function**: Passive heat transfer device
    - **Applications**: Laptop cooling, spacecraft thermal control
    - **Advantage**: No moving parts, highly reliable
    
    **19. 3D Printing**
    - **Binder jetting**: Liquid binder wicks into powder
    - **SLA resin**: Must wet layer surface properly
    - **Inkjet**: Precise droplet placement requires controlled wetting
    - **Quality**: Contact angle affects layer adhesion
    """)
    
    st.markdown("---")
    
    st.markdown("### Environmental & Agriculture")
    
    env_col1, env_col2 = st.columns(2)
    
    with env_col1:
        st.markdown("""
        **20. Oil Spill Cleanup**
        - **Sorbent materials**: Engineered for oil (hydrophobic)
        - **Selectivity**: Absorb oil, repel water (θ_water > 90°)
        - **Capacity**: Can absorb 20-70× their weight
        - **Examples**: Polypropylene fibers, modified cellulose
        
        **21. Groundwater Movement**
        - **Capillary fringe**: Zone above water table
        - **Height**: 10 cm (gravel) to >1 m (clay)
        - **Contamination**: Pollutants can wick above water table
        - **Modeling**: Essential for predicting contaminant spread
        """)
    
    with env_col2:
        st.markdown("""
        **22. Irrigation Systems**
        - **Drip irrigation**: Controlled water delivery
        - **Wicking beds**: Self-watering planters
        - **Capillary mat**: Greenhouse watering systems
        - **Efficiency**: Reduces water waste compared to flooding
        
        **23. Atmospheric Water Harvesting**
        - **Fog nets**: Capture water droplets from fog
        - **Surface design**: Wettability patterns guide droplets
        - **Desert applications**: Provides water in arid regions
        - **Biomimicry**: Inspired by desert beetles, cacti
        """)
    
    st.markdown("---")
    
    st.markdown("### Design Considerations")
    
    st.info("""
    **When Designing Systems Involving Capillary Action:**
    
    1. **Choose appropriate materials**: Consider surface energy and contact angles
    2. **Optimize pore/channel size**: Balance flow rate vs. capillary pressure
    3. **Account for temperature**: Surface tension decreases ~0.15% per °C for water
    4. **Consider contamination**: Surfactants drastically reduce surface tension
    5. **Test with actual fluids**: Contact angle varies with fluid composition
    6. **Factor in aging**: Surface properties change over time (oxidation, fouling)
    7. **Model numerically**: Complex geometries require computational fluid dynamics
    8. **Validate experimentally**: Always test prototypes with target fluids
    """)
    
    st.markdown("---")
    
    st.markdown("### Famous Historical Examples")
    
    history_col1, history_col2, history_col3 = st.columns(3)
    
    with history_col1:
        st.markdown("""
        #### Leonardo da Vinci (1500s)
        - First observed capillary rise
        - Documented in notebooks
        - Couldn't explain mechanism
        - Attributed to "natural philosophy"
        """)
    
    with history_col2:
        st.markdown("""
        #### Thomas Young (1805)
        - Derived contact angle equation
        - Related to surface energies
        - Foundation of wetting theory
        - Still used today
        """)
    
    with history_col3:
        st.markdown("""
        #### Pierre-Simon Laplace (1806)
        - Young-Laplace equation
        - Relates pressure to curvature
        - Explained meniscus shape
        - Universal principle
        """)

# Add comparison tool
st.markdown("---")
st.header("🔬 Capillary Rise Comparison Tool")

st.markdown("Compare capillary rise for different tube diameters with the same liquid:")

comp_col1, comp_col2, comp_col3, comp_col4 = st.columns(4)

with comp_col1:
    comp_sigma = st.number_input("Surface Tension σ (N/m)", value=0.0728, format="%.4f", key="comp_sigma")
    comp_rho = st.number_input("Density ρ (kg/m³)", value=998.0, key="comp_rho")

with comp_col2:
    comp_theta = st.number_input("Contact Angle θ (°)", value=0, min_value=0, max_value=180, key="comp_theta")
    comp_g = st.number_input("Gravity g (m/s²)", value=9.81, format="%.2f", key="comp_g")

with comp_col3:
    st.markdown("### Small Tube")
    d_small = 0.5  # mm
    h_small = (4 * comp_sigma * np.cos(np.deg2rad(comp_theta))) / (comp_rho * comp_g * d_small/1000)
    st.metric(f"d = {d_small} mm", f"{h_small*100:.2f} cm")
    st.caption(f"{h_small*1000:.1f} mm")

with comp_col4:
    st.markdown("### Large Tube")
    d_large = 5.0  # mm
    h_large = (4 * comp_sigma * np.cos(np.deg2rad(comp_theta))) / (comp_rho * comp_g * d_large/1000)
    st.metric(f"d = {d_large} mm", f"{h_large*100:.2f} cm")
    st.caption(f"{h_large*1000:.1f} mm")

ratio = h_small / h_large if h_large != 0 else 0
st.info(f"💡 **Height ratio**: The smaller tube ({d_small} mm) produces **{ratio:.1f}× higher** capillary rise than the larger tube ({d_large} mm)")

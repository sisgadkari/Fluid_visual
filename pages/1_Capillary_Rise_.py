import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Capillary Rise Simulator")

# --- Initialize Session State ---
if 'previous_h' not in st.session_state:
    st.session_state.previous_h = None
if 'previous_theta' not in st.session_state:
    st.session_state.previous_theta = 90  # Always start from neutral (90°)

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
    col1, col2 = st.columns([2, 3])

    # --- Column 1: Input Controls ---
    with col1:
        st.header("🔬 Parameters")

        # --- Interactive Scenarios ---
        SCENARIOS = {
            "Custom...": {
                "sigma": 0.0728, "rho": 998, "theta": 90, "d_mm": 1.0,
                "color": 'rgba(100, 170, 255, 0.7)',
                "desc": "Manually adjust all parameters below."
            },
            "Water in Glass Tube": {
                "sigma": 0.0728, "rho": 998, "theta": 0, "d_mm": 1.0,
                "color": 'rgba(100, 170, 255, 0.7)',
                "desc": "Classic demonstration: water perfectly wets glass (θ ≈ 0°), showing strong capillary rise."
            },
            "Mercury in Glass Tube": {
                "sigma": 0.485, "rho": 13534, "theta": 140, "d_mm": 1.0,
                "color": 'rgba(180, 180, 180, 0.9)',
                "desc": "Mercury doesn't wet glass (θ ≈ 140°), causing capillary depression instead of rise."
            },
            "Ethanol in Glass": {
                "sigma": 0.0223, "rho": 789, "theta": 0, "d_mm": 1.0,
                "color": 'rgba(200, 150, 255, 0.7)',
                "desc": "Ethanol has lower surface tension than water, resulting in less capillary rise."
            },
            "Water in Fine Capillary": {
                "sigma": 0.0728, "rho": 998, "theta": 0, "d_mm": 0.1,
                "color": 'rgba(100, 170, 255, 0.7)',
                "desc": "Very narrow tube (0.1 mm) shows dramatic capillary rise - demonstrates 1/d relationship."
            },
            "Blood in Capillary Tube": {
                "sigma": 0.058, "rho": 1060, "theta": 0, "d_mm": 0.5,
                "color": 'rgba(180, 40, 40, 0.7)',
                "desc": "Medical application: blood sample collection in capillary tubes for testing."
            },
            "Oil in Metal Tube": {
                "sigma": 0.032, "rho": 920, "theta": 30, "d_mm": 2.0,
                "color": 'rgba(200, 180, 50, 0.7)',
                "desc": "Lubricating oil in metal bearing - partial wetting with moderate contact angle."
            },
            "Solder on Copper (Wetting)": {
                "sigma": 0.50, "rho": 7000, "theta": 20, "d_mm": 0.5,
                "color": 'rgba(192, 192, 192, 0.8)',
                "desc": "Molten solder wets clean copper surfaces - important for electronics manufacturing."
            }
        }
        
        scenario_choice = st.selectbox("Interactive 'What-If' Scenarios", options=list(SCENARIOS.keys()))
        selected_scenario = SCENARIOS[scenario_choice]
        st.info(selected_scenario["desc"])

        # --- Fluid Properties ---
        st.subheader("Fluid Properties")
        
        if scenario_choice == "Custom...":
            sigma = st.slider("Surface Tension (σ) [N/m]", 0.01, 0.6, 0.0728, 0.001, format="%.4f",
                            help="Surface tension of the liquid")
            rho = st.number_input("Liquid Density (ρ) [kg/m³]", value=998, min_value=1, step=10,
                                 help="Density of the liquid")
            liquid_color = 'rgba(100, 170, 255, 0.7)'
        else:
            sigma = selected_scenario["sigma"]
            rho = selected_scenario["rho"]
            liquid_color = selected_scenario["color"]
            col_prop1, col_prop2 = st.columns(2)
            with col_prop1:
                st.metric("Surface Tension (σ)", f"{sigma} N/m")
            with col_prop2:
                st.metric("Liquid Density (ρ)", f"{rho} kg/m³")

        st.subheader("Tube and Contact Properties")
        
        if scenario_choice == "Custom...":
            theta_deg = st.slider("Contact Angle (θ) [degrees]", 0, 180, 90,
                                 help="0° = perfect wetting, 90° = neutral, >90° = non-wetting")
            d_mm = st.slider("Capillary Diameter (d) [mm]", 0.1, 10.0, 1.0, 0.1,
                            help="Smaller diameter = greater capillary rise")
        else:
            theta_deg = st.slider("Contact Angle (θ) [degrees]", 0, 180, selected_scenario["theta"],
                                 help="0° = perfect wetting, 90° = neutral, >90° = non-wetting")
            d_mm = st.slider("Capillary Diameter (d) [mm]", 0.1, 10.0, selected_scenario["d_mm"], 0.1,
                            help="Smaller diameter = greater capillary rise")
        
        # Temperature effect on surface tension (for liquids)
        if scenario_choice != "Custom..." and "Mercury" not in scenario_choice and "Solder" not in scenario_choice:
            temp_c = st.slider("Temperature (°C)", 0, 100, 20,
                              help="Temperature affects surface tension")
            # Approximate temperature correction for surface tension
            # Surface tension typically decreases ~0.1-0.2% per °C
            temp_factor = 1 - 0.002 * (temp_c - 20)
            sigma_adjusted = sigma * temp_factor
            if abs(sigma_adjusted - sigma) > 0.0001:
                st.caption(f"Temperature-adjusted σ: {sigma_adjusted:.4f} N/m")
                sigma = sigma_adjusted
        
        d_m = d_mm / 1000
        g = 9.81
        theta_rad = np.deg2rad(theta_deg)

        # --- Calculation ---
        if d_m > 0 and rho > 0:
            h = (4 * sigma * np.cos(theta_rad)) / (rho * g * d_m)
        else:
            h = 0
        
        h_mm = h * 1000
        h_cm = h * 100
        h_inches = h * 39.3701
        
        # Calculate forces
        F_surface_tension = sigma * np.pi * d_m * np.cos(theta_rad)  # Upward force
        F_weight = rho * g * (np.pi * d_m**2 / 4) * abs(h)  # Weight of liquid column
        
        # Calculate pressure difference at meniscus (Young-Laplace)
        if d_m > 0:
            delta_P = 4 * sigma * np.cos(theta_rad) / d_m
            delta_P_kPa = delta_P / 1000
        else:
            delta_P = 0
            delta_P_kPa = 0
        
        st.markdown("---")
        st.header("📊 Results Summary")
        
        # Main result
        st.metric(label="Capillary Rise (h)", value=f"{h_mm:.2f} mm",
                 delta=f"{h_cm:.3f} cm" if abs(h_cm) > 0.001 else None)
        
        # Additional units
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("In meters", f"{h:.6f} m")
        with col_r2:
            st.metric("In inches", f"{h_inches:.4f} in")
        
        # Provide context based on result
        if h_mm > 0:
            st.success(f"✅ Liquid rises {h_mm:.2f} mm due to wetting (θ < 90°)")
        elif h_mm < 0:
            st.warning(f"⚠️ Liquid depresses {abs(h_mm):.2f} mm due to non-wetting (θ > 90°)")
        else:
            st.info("💡 Neutral wetting at θ = 90° - no rise or depression")
        
        st.markdown("---")
        st.header("🧮 Step-by-Step Calculation")
        
        with st.expander("📖 See Detailed Breakdown", expanded=False):
            st.markdown("### Capillary Rise Equation")
            st.latex(r'h = \frac{4 \sigma \cos(\theta)}{\rho g d}')
            
            st.markdown("### Step 1: Given Parameters")
            st.write(f"• Surface tension: σ = {sigma:.4f} N/m")
            st.write(f"• Contact angle: θ = {theta_deg}°")
            st.write(f"• Liquid density: ρ = {rho} kg/m³")
            st.write(f"• Tube diameter: d = {d_mm} mm = {d_m:.6f} m")
            st.write(f"• Gravity: g = {g} m/s²")
            
            st.markdown("### Step 2: Calculate cos(θ)")
            cos_theta = np.cos(theta_rad)
            st.latex(rf'\cos({theta_deg}°) = {cos_theta:.4f}')
            
            st.markdown("### Step 3: Calculate Numerator")
            numerator = 4 * sigma * cos_theta
            st.write(f"Numerator = 4 × σ × cos(θ)")
            st.write(f"Numerator = 4 × {sigma:.4f} × {cos_theta:.4f}")
            st.write(f"Numerator = **{numerator:.6f} N/m**")
            
            st.markdown("### Step 4: Calculate Denominator")
            denominator = rho * g * d_m
            st.write(f"Denominator = ρ × g × d")
            st.write(f"Denominator = {rho} × {g} × {d_m:.6f}")
            st.write(f"Denominator = **{denominator:.4f} N/m³**")
            
            st.markdown("### Step 5: Final Result")
            st.write(f"h = {numerator:.6f} / {denominator:.4f}")
            st.write(f"h = **{h:.6f} m** = **{h_mm:.2f} mm**")
            
            # Physical interpretation
            st.markdown("### Physical Interpretation")
            if theta_deg < 90:
                st.success("✅ Positive height → Liquid rises (adhesive forces dominate)")
            elif theta_deg > 90:
                st.warning("⚠️ Negative height → Liquid depresses (cohesive forces dominate)")
            else:
                st.info("💡 Zero height → Forces balanced (no net capillary effect)")
        
        st.markdown("---")
        st.header("🔍 Analysis Insights")
        
        with st.expander("💡 Force & Pressure Analysis", expanded=False):
            st.markdown("**Force Balance:**")
            st.write(f"• Surface tension force (upward): {F_surface_tension*1000:.4f} mN")
            st.write(f"• Weight of liquid column: {F_weight*1000:.4f} mN")
            
            st.markdown("**Pressure at Meniscus (Young-Laplace):**")
            st.latex(r'\Delta P = \frac{4\sigma\cos(\theta)}{d}')
            st.write(f"• Pressure difference: {delta_P:.2f} Pa = {delta_P_kPa:.4f} kPa")
            
            if theta_deg < 90:
                st.info("💡 Pressure inside the meniscus is LOWER than atmospheric - this draws liquid up.")
            elif theta_deg > 90:
                st.info("💡 Pressure inside the meniscus is HIGHER than atmospheric - this pushes liquid down.")
        
        with st.expander("🎯 Sensitivity Analysis", expanded=False):
            st.markdown("**How changes affect capillary rise:**")
            
            # Calculate sensitivities
            h_half_diameter = (4 * sigma * np.cos(theta_rad)) / (rho * g * (d_m/2)) * 1000  # mm
            h_double_diameter = (4 * sigma * np.cos(theta_rad)) / (rho * g * (d_m*2)) * 1000  # mm
            h_double_sigma = (4 * (sigma*2) * np.cos(theta_rad)) / (rho * g * d_m) * 1000  # mm
            h_half_sigma = (4 * (sigma/2) * np.cos(theta_rad)) / (rho * g * d_m) * 1000  # mm
            
            st.write(f"**Current rise:** {h_mm:.2f} mm")
            st.write(f"• If diameter halved (d = {d_mm/2:.2f} mm): h = {h_half_diameter:.2f} mm (2× rise)")
            st.write(f"• If diameter doubled (d = {d_mm*2:.2f} mm): h = {h_double_diameter:.2f} mm (½ rise)")
            st.write(f"• If surface tension doubled: h = {h_double_sigma:.2f} mm")
            st.write(f"• If surface tension halved: h = {h_half_sigma:.2f} mm")
            
            st.markdown("**Key insight:** Diameter has the most dramatic effect due to inverse relationship!")
        
        with st.expander("🎯 Design Considerations", expanded=False):
            st.markdown("**Application Suitability:**")
            
            if abs(h_mm) < 1:
                st.warning("⚠️ Very small capillary effect - may be difficult to observe or utilize")
            elif abs(h_mm) < 10:
                st.info("💡 Moderate capillary rise - suitable for most laboratory demonstrations")
            elif abs(h_mm) < 100:
                st.success("✅ Strong capillary effect - excellent for practical applications")
            else:
                st.success("✅ Very strong capillary rise - consider if this is practical for your tube length")
            
            st.markdown("**Practical Limits:**")
            st.write(f"• Tube must be at least **{abs(h_mm):.1f} mm** tall to observe full effect")
            st.write(f"• For accurate measurement, tube should be **{abs(h_mm)*1.5:.1f} mm** or taller")
            
            # Bond number (ratio of gravitational to surface tension forces)
            Bo = (rho * g * d_m**2) / sigma if sigma > 0 else 0
            st.markdown(f"**Bond Number:** Bo = {Bo:.4f}")
            if Bo < 1:
                st.info("💡 Bo < 1: Surface tension dominates - capillary effects are significant")
            else:
                st.warning("⚠️ Bo > 1: Gravity dominates - capillary effects less significant")

    # --- Column 2: Visualization ---
    with col2:
        st.header("🖼️ Visualization")
        
        # Visualization controls
        vis_col1, vis_col2, vis_col3 = st.columns(3)
        with vis_col1:
            show_forces = st.checkbox("Show Forces", value=False)
        with vis_col2:
            show_dimensions = st.checkbox("Show Dimensions", value=True)
        with vis_col3:
            show_result_label = st.checkbox("Show Result Label", value=True)
        
        plot_placeholder = st.empty()

        # This function creates the plot for a given instantaneous height and theta
        def generate_plot(instant_h=0, instant_theta=90):
            tube_radius_vis = d_mm / 2
            h_vis_target = h * 1000
            max_y_val = max(abs(h_vis_target), 10)
            plot_y_range = [-max_y_val * 0.3, max_y_val * 1.8]
            plot_height = plot_y_range[1]
            beaker_radius = 15
            beaker_bottom = min(-5, h_vis_target - 2)

            fig = go.Figure()
            line_color = liquid_color.replace('0.7', '1').replace('0.8', '1').replace('0.9', '1')

            # 1. Draw beaker and liquid
            fig.add_shape(type="line", x0=-beaker_radius, y0=beaker_bottom, x1=-beaker_radius, y1=0, line=dict(color="grey", width=2))
            fig.add_shape(type="line", x0=beaker_radius, y0=beaker_bottom, x1=beaker_radius, y1=0, line=dict(color="grey", width=2))
            fig.add_shape(type="line", x0=-beaker_radius, y0=beaker_bottom, x1=beaker_radius, y1=beaker_bottom, line=dict(color="grey", width=2))
            
            # Liquid around the tube
            fig.add_trace(go.Scatter(x=[-beaker_radius, -tube_radius_vis, -tube_radius_vis, -beaker_radius], y=[beaker_bottom, beaker_bottom, 0, 0], fill='toself', fillcolor=liquid_color, mode='none', hoverinfo='none'))
            fig.add_trace(go.Scatter(x=[tube_radius_vis, beaker_radius, beaker_radius, tube_radius_vis], y=[beaker_bottom, beaker_bottom, 0, 0], fill='toself', fillcolor=liquid_color, mode='none', hoverinfo='none'))

            # 2. Draw tube and meniscus (using instant_theta for animation)
            fig.add_shape(type="line", x0=-tube_radius_vis, y0=beaker_bottom, x1=-tube_radius_vis, y1=plot_height, line=dict(color="darkgrey", width=3))
            fig.add_shape(type="line", x0=tube_radius_vis, y0=beaker_bottom, x1=tube_radius_vis, y1=plot_height, line=dict(color="darkgrey", width=3))

            meniscus_x = np.linspace(-tube_radius_vis, tube_radius_vis, 100)
            curvature_direction = -1 if instant_theta < 90 else 1
            meniscus_y = instant_h - curvature_direction * (meniscus_x**2 / (tube_radius_vis * 2)) * np.tan(np.deg2rad(90 - instant_theta if instant_theta < 90 else instant_theta - 90)) if tube_radius_vis > 0 else instant_h
            if tube_radius_vis > 0:
                meniscus_y -= (meniscus_y[-1] - instant_h)
            
            x_fill = np.concatenate([meniscus_x, [tube_radius_vis, -tube_radius_vis]])
            y_fill = np.concatenate([meniscus_y, [beaker_bottom, beaker_bottom]])
            fig.add_trace(go.Scatter(x=x_fill, y=y_fill, fill='toself', fillcolor=liquid_color, mode='none', hoverinfo='none'))
            fig.add_trace(go.Scatter(x=meniscus_x, y=meniscus_y, mode='lines', line=dict(color=line_color), hoverinfo='none'))

            # 3. Annotations and dimensions
            if show_dimensions:
                # Datum line at liquid surface
                fig.add_shape(type="line", x0=-beaker_radius, y0=0, x1=beaker_radius, y1=0, 
                             line=dict(color="black", width=1, dash="dash"))
                fig.add_annotation(x=beaker_radius + 1, y=0, text="Datum", showarrow=False, xanchor="left", font=dict(size=12))
                
                # Height dimension line
                annotation_base_x = tube_radius_vis + 2
                if instant_h != 0:
                    fig.add_shape(type="line", x0=annotation_base_x, y0=0, x1=annotation_base_x, y1=instant_h, 
                                 line=dict(color="black", width=1))
                    # Tick marks
                    fig.add_shape(type="line", x0=annotation_base_x - 0.5, y0=0, x1=annotation_base_x + 0.5, y1=0, 
                                 line=dict(color="black", width=1))
                    fig.add_shape(type="line", x0=annotation_base_x - 0.5, y0=instant_h, x1=annotation_base_x + 0.5, y1=instant_h, 
                                 line=dict(color="black", width=1))
                
                fig.add_annotation(x=annotation_base_x + 1, y=instant_h / 2, text=f"h = {instant_h:.2f} mm", 
                                  showarrow=False, font=dict(size=16), xanchor='left')
                
                # Diameter annotation
                fig.add_annotation(x=0, y=beaker_bottom - 1, text=f"d = {d_mm:.1f} mm", 
                                  showarrow=False, font=dict(size=12))
            
            # 4. Force arrows (if enabled)
            if show_forces and instant_h != 0:
                # Surface tension force (upward arrows at tube walls)
                arrow_scale = min(5, max(2, abs(instant_h) / 5))
                if instant_theta < 90:
                    # Upward arrows for wetting
                    fig.add_annotation(x=-tube_radius_vis, y=instant_h, ax=-tube_radius_vis, ay=instant_h + arrow_scale,
                                      showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="green")
                    fig.add_annotation(x=tube_radius_vis, y=instant_h, ax=tube_radius_vis, ay=instant_h + arrow_scale,
                                      showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="green")
                    fig.add_annotation(x=-tube_radius_vis - 3, y=instant_h + arrow_scale/2, text="F_σ", 
                                      showarrow=False, font=dict(size=12, color="green"))
                elif instant_theta > 90:
                    # Downward arrows for non-wetting
                    fig.add_annotation(x=-tube_radius_vis, y=instant_h, ax=-tube_radius_vis, ay=instant_h - arrow_scale,
                                      showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="red")
                    fig.add_annotation(x=tube_radius_vis, y=instant_h, ax=tube_radius_vis, ay=instant_h - arrow_scale,
                                      showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="red")
                    fig.add_annotation(x=-tube_radius_vis - 3, y=instant_h - arrow_scale/2, text="F_σ", 
                                      showarrow=False, font=dict(size=12, color="red"))
            
            # 5. Result label at top (if enabled)
            if show_result_label:
                result_text = f"<b>Capillary Rise: {instant_h:.2f} mm</b>"
                if instant_h < 0:
                    result_text = f"<b>Capillary Depression: {abs(instant_h):.2f} mm</b>"
                
                fig.add_annotation(
                    x=0,
                    y=plot_y_range[1] * 0.9,
                    text=result_text,
                    showarrow=False,
                    font=dict(size=20, color="white"),
                    bgcolor="rgba(0, 100, 200, 0.9)" if instant_h >= 0 else "rgba(200, 100, 0, 0.9)",
                    bordercolor="darkblue" if instant_h >= 0 else "darkorange",
                    borderwidth=2,
                    borderpad=8
                )

            fig.update_layout(
                xaxis=dict(range=[-25, 25], showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(range=[beaker_bottom - 3, plot_y_range[1]], zeroline=False, title_text="Height (mm)"),
                showlegend=False, height=600, plot_bgcolor='white',
                margin=dict(t=20, b=20, l=40, r=20)
            )
            return fig

        # --- Main Visualization and Animation Logic ---
        h_vis_target = h * 1000
        end_h = h_vis_target
        end_theta = theta_deg
        
        # Always start from 90° (neutral position) for the first frame
        start_h = st.session_state.previous_h
        start_theta = st.session_state.previous_theta
        
        # On the very first run, start from neutral (90°, h=0)
        if start_h is None:
            start_h = 0  # Start from zero height (neutral)
            start_theta = 90  # Start from 90° contact angle

        # Animate if either height or theta has changed
        if not (np.isclose(start_h, end_h) and np.isclose(start_theta, end_theta)):
            animation_steps = 20
            for i in range(animation_steps + 1):
                progress = i / animation_steps
                intermediate_h = start_h + (end_h - start_h) * progress
                intermediate_theta = start_theta + (end_theta - start_theta) * progress
                fig = generate_plot(intermediate_h, intermediate_theta)
                plot_placeholder.plotly_chart(fig, use_container_width=True)
                time.sleep(0.025)
        else:
            fig = generate_plot(end_h, end_theta)
            plot_placeholder.plotly_chart(fig, use_container_width=True)
        
        # Always update the previous values for the next run
        st.session_state.previous_h = end_h
        st.session_state.previous_theta = end_theta

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
    
    st.markdown("### Safety Considerations")
    
    safety_col1, safety_col2, safety_col3 = st.columns(3)
    
    with safety_col1:
        st.markdown("""
        #### Mercury Handling
        
        **Hazards:**
        - Toxic vapor inhalation
        - Skin contact absorption
        - Environmental contamination
        
        **Precautions:**
        - Use in well-ventilated areas
        - Wear appropriate PPE
        - Use spill containment trays
        - Proper disposal procedures
        - Consider alternatives (Galinstan)
        """)
    
    with safety_col2:
        st.markdown("""
        #### Glass Capillary Tubes
        
        **Risks:**
        - Breakage and cuts
        - Sharp edges
        - Small fragments
        
        **Safety Measures:**
        - Handle with care
        - Fire-polish ends
        - Use tube holders
        - Dispose in sharps container
        - Wear safety glasses
        """)
    
    with safety_col3:
        st.markdown("""
        #### Chemical Fluids
        
        **Considerations:**
        - Check MSDS for each fluid
        - Proper ventilation
        - Appropriate containers
        - Spill procedures
        - First aid knowledge
        
        **Common Safe Alternatives:**
        - Water (with dye for visibility)
        - Vegetable oils
        - Food coloring solutions
        """)
    
    st.markdown("---")
    
    st.markdown("### Practical Measurement Tips")
    
    st.info("""
    **For Accurate Capillary Rise Measurements:**
    
    1. **Clean the tube**: Contamination drastically affects contact angle - clean with appropriate solvent
    2. **Vertical alignment**: Ensure tube is perfectly vertical using a spirit level
    3. **Temperature control**: Note the temperature as it affects surface tension
    4. **Allow equilibration**: Wait for the liquid level to stabilize (can take minutes for viscous fluids)
    5. **Read at meniscus bottom**: For wetting liquids, read at the lowest point of the curved surface
    6. **Multiple readings**: Take several measurements and average them
    7. **Tube diameter verification**: Measure actual diameter; nominal values may vary
    8. **Fresh surfaces**: For reactive systems, use fresh tube surfaces
    """)
    
    st.markdown("---")
    
    st.markdown("### Typical Capillary Rise Values")
    
    st.markdown("""
    | Fluid | Tube Diameter | Approximate Rise |
    |-------|--------------|------------------|
    | Water | 1 mm | 30 mm |
    | Water | 0.1 mm | 300 mm (30 cm!) |
    | Water | 0.01 mm (10 µm) | 3000 mm (3 m!) |
    | Mercury | 1 mm | -10 mm (depression) |
    | Ethanol | 1 mm | 12 mm |
    | Blood | 0.5 mm | ~22 mm |
    
    **Key insight:** The 1/d relationship means 10× smaller diameter → 10× greater rise!
    """)
    
    st.markdown("---")
    
    st.markdown("### Modern Measurement Alternatives")
    
    st.markdown("""
    While capillary rise observation is classic, modern alternatives include:
    
    | Technology | Advantages | When to Use |
    |-----------|-----------|-------------|
    | **Wilhelmy Plate** | Direct surface tension measurement, high accuracy | When precise σ values needed |
    | **Du Noüy Ring** | Classic method, well-established | Teaching, standard measurements |
    | **Pendant Drop** | Non-contact, small sample volumes | When sample is limited or reactive |
    | **Sessile Drop** | Direct contact angle measurement | When θ is the primary interest |
    | **Capillary Pressure** | Dynamic measurements possible | Porous media studies |
    
    However, **capillary rise observation is still valuable** for:
    - Teaching fundamental concepts (visual understanding)
    - Quick qualitative assessments
    - Situations where simplicity matters
    - Historical/reference comparisons
    """)

# --- Quick Comparison Tool ---
st.markdown("---")
st.header("🔧 Quick Comparison Calculator")

calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)

with calc_col1:
    st.markdown("**Input Parameters**")
    calc_sigma = st.number_input("Surface Tension σ (N/m)", value=0.0728, format="%.4f", key="calc_sigma")
    calc_theta = st.number_input("Contact Angle θ (°)", value=0, min_value=0, max_value=180, key="calc_theta")

with calc_col2:
    st.markdown("**Fluid & Tube**")
    calc_rho = st.number_input("Density ρ (kg/m³)", value=998, key="calc_rho")
    calc_d = st.number_input("Diameter d (mm)", value=1.0, format="%.2f", key="calc_d")

with calc_col3:
    st.markdown("**Results**")
    calc_theta_rad = np.deg2rad(calc_theta)
    calc_d_m = calc_d / 1000
    if calc_d_m > 0 and calc_rho > 0:
        calc_h = (4 * calc_sigma * np.cos(calc_theta_rad)) / (calc_rho * 9.81 * calc_d_m)
        calc_h_mm = calc_h * 1000
    else:
        calc_h_mm = 0
    
    st.metric("Capillary Rise (mm)", f"{calc_h_mm:.2f}")
    st.metric("Capillary Rise (cm)", f"{calc_h_mm/10:.3f}")

with calc_col4:
    st.markdown("**Quick Reference**")
    # Compare with different diameters
    for d_ref in [0.1, 0.5, 1.0, 2.0, 5.0]:
        d_ref_m = d_ref / 1000
        if d_ref_m > 0 and calc_rho > 0:
            h_ref = (4 * calc_sigma * np.cos(calc_theta_rad)) / (calc_rho * 9.81 * d_ref_m) * 1000
            st.caption(f"d = {d_ref} mm → h = {h_ref:.1f} mm")

st.caption("💡 **Tip**: Use this calculator to quickly compare capillary rise for different fluid/tube combinations.")

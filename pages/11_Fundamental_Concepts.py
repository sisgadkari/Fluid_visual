import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Fundamental Concepts in Fluid Mechanics")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>📖 Fundamental Concepts in Fluid Mechanics</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>Master the essential building blocks of fluid mechanics. These concepts form the foundation for understanding fluid behavior in engineering applications.</p>",
    unsafe_allow_html=True
)
st.markdown("---")

# Create main tabs for different fundamental concepts
main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6, main_tab7, main_tab8, main_tab9 = st.tabs([
    "🍯 Viscosity", 
    "💧 Surface Tension", 
    "⚓ Buoyancy & Stability", 
    "🌊 Bernoulli Principle",
    "🔀 Types of Flow",
    "🔬 Continuum Assumption",
    "⚖️ Continuity Equation",
    "📐 Boundary Layer",
    "📏 Dimensional Analysis"
])

# =====================================================
# TAB 1: VISCOSITY
# =====================================================
with main_tab1:
    st.markdown("<h2 style='text-align: center;'>🍯 Understanding Viscosity</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 16px;'>Explore how fluids resist flow and deformation. Visualize the difference between honey and water.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # SECTION 1: INTERACTIVE SIMULATION
    st.markdown("### 🎯 Interactive Simulation")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("🔬 Parameters")
        
        # --- Preset Fluid Options ---
        st.markdown("**Select a Fluid**")
        fluid_choice = st.selectbox(
            "Choose a fluid to explore:",
            ("Water (20°C)", "Honey", "Motor Oil (SAE 30)", "Glycerol", "Mercury", "Air", "Blood", "Maple Syrup", "Custom"),
            key="visc_fluid_selector"
        )
        
        # Preset values: dynamic viscosity (Pa·s), density (kg/m³), color
        FLUID_PROPERTIES = {
            "Water (20°C)":      {'mu': 0.001, 'rho': 998, 'color': 'rgba(100, 170, 255, 0.7)', 'description': 'Low viscosity - flows easily'},
            "Honey":             {'mu': 2.0, 'rho': 1420, 'color': 'rgba(255, 193, 7, 0.8)', 'description': 'Very high viscosity - flows slowly'},
            "Motor Oil (SAE 30)": {'mu': 0.2, 'rho': 880, 'color': 'rgba(139, 69, 19, 0.7)', 'description': 'Medium-high viscosity - lubricant'},
            "Glycerol":          {'mu': 1.5, 'rho': 1260, 'color': 'rgba(200, 200, 220, 0.7)', 'description': 'High viscosity - thick and syrupy'},
            "Mercury":           {'mu': 0.00155, 'rho': 13534, 'color': 'rgba(180, 180, 180, 0.9)', 'description': 'Low viscosity despite high density'},
            "Air":               {'mu': 0.0000181, 'rho': 1.2, 'color': 'rgba(200, 230, 255, 0.3)', 'description': 'Very low viscosity - gas'},
            "Blood":             {'mu': 0.004, 'rho': 1060, 'color': 'rgba(220, 20, 60, 0.7)', 'description': 'Non-Newtonian fluid'},
            "Maple Syrup":       {'mu': 0.15, 'rho': 1370, 'color': 'rgba(210, 105, 30, 0.8)', 'description': 'Medium viscosity - sweet and sticky'},
        }
        
        if fluid_choice == "Custom":
            st.markdown("**Custom Fluid Properties**")
            mu = st.slider("Dynamic Viscosity (μ) [Pa·s]", 0.0001, 5.0, 0.1, 0.0001, format="%.4f", key="visc_mu")
            rho = st.number_input("Density (ρ) [kg/m³]", value=1000, min_value=1, max_value=20000, key="visc_rho")
            fluid_color = 'rgba(100, 170, 255, 0.7)'
            fluid_desc = "Custom fluid"
        else:
            properties = FLUID_PROPERTIES[fluid_choice]
            mu = properties['mu']
            rho = properties['rho']
            fluid_color = properties['color']
            fluid_desc = properties['description']
            
            st.success(f"**{fluid_choice}**: {fluid_desc}")
            st.markdown(f"**Dynamic Viscosity (μ):** `{mu}` Pa·s")
            st.markdown(f"**Density (ρ):** `{rho}` kg/m³")
        
        # Calculate kinematic viscosity
        nu = mu / rho  # m²/s
        
        st.markdown("---")
        st.markdown("**Calculated Properties**")
        
        col_calc1, col_calc2 = st.columns(2)
        with col_calc1:
            st.metric("Dynamic Viscosity (μ)", f"{mu:.4f} Pa·s")
        with col_calc2:
            st.metric("Kinematic Viscosity (ν)", f"{nu:.2e} m²/s")
        
        st.markdown("---")
        st.markdown("**Flow Conditions**")
        
        # Shear rate for visualization
        shear_rate = st.slider("Shear Rate (du/dy) [1/s]", 1, 1000, 100, 10,
                               help="Rate of change of velocity with distance", key="visc_shear")
        
        # Calculate shear stress
        tau = mu * shear_rate  # Pa
        
        st.metric("Shear Stress (τ)", f"{tau:.2f} Pa")
        
        # Viscosity comparison info box
        st.markdown("---")
        st.info(f"""
        **Quick Comparison:**
        - Water: 0.001 Pa·s (reference)
        - Your fluid is **{mu/0.001:.0f}x** more viscous than water
        """)
    
    # --- Column 2: Visualization ---
    with col2:
        st.subheader("🖼️ Visualization")
        
        # Create visualization tabs
        viz_tab1, viz_tab2 = st.tabs(["🍯 Falling Ball", "🌊 Fluid Flow"])
        
        with viz_tab1:
            # --- Falling Ball Viscometer Simulation with Animation ---
            st.markdown("#### Falling Ball Viscometer - Animated")
            
            # Ball material selection
            st.markdown("**Select Ball Material:**")
            ball_col1, ball_col2 = st.columns(2)
            
            BALL_MATERIALS = {
                "Steel": {'rho': 7800, 'color': 'rgba(120, 120, 130, 0.95)', 'name': 'Steel'},
                "Iron": {'rho': 7874, 'color': 'rgba(90, 90, 100, 0.95)', 'name': 'Iron'},
                "Aluminum": {'rho': 2700, 'color': 'rgba(180, 180, 190, 0.95)', 'name': 'Aluminum'},
                "Plastic (PVC)": {'rho': 1400, 'color': 'rgba(200, 200, 220, 0.9)', 'name': 'PVC'},
                "Rubber": {'rho': 1100, 'color': 'rgba(50, 50, 50, 0.95)', 'name': 'Rubber'},
                "Glass": {'rho': 2500, 'color': 'rgba(200, 220, 255, 0.7)', 'name': 'Glass'},
                "Wood (Oak)": {'rho': 750, 'color': 'rgba(180, 130, 80, 0.95)', 'name': 'Oak'},
                "Copper": {'rho': 8960, 'color': 'rgba(184, 115, 51, 0.95)', 'name': 'Copper'},
            }
            
            with ball_col1:
                ball_choice = st.selectbox("Ball Material", list(BALL_MATERIALS.keys()), key="visc_ball")
            
            with ball_col2:
                ball_radius_mm = st.slider("Ball Radius (mm)", 1.0, 10.0, 5.0, 0.5, key="visc_radius")
            
            ball_props = BALL_MATERIALS[ball_choice]
            rho_ball = ball_props['rho']
            ball_color = ball_props['color']
            ball_radius = ball_radius_mm / 1000  # Convert to meters
            
            # Display ball properties
            st.info(f"**{ball_choice}**: Density = {rho_ball} kg/m³ | Radius = {ball_radius_mm} mm")
            
            # Check if ball will float or sink
            if rho_ball < rho:
                st.warning(f"⚠️ This ball will **FLOAT**! Ball density ({rho_ball} kg/m³) < Fluid density ({rho} kg/m³)")
                will_sink = False
            else:
                st.success(f"✓ Ball will **SINK**. Ball density ({rho_ball} kg/m³) > Fluid density ({rho} kg/m³)")
                will_sink = True
            
            # Calculate terminal velocity (Stokes' law)
            if mu > 0 and will_sink:
                v_terminal = (2 * ball_radius**2 * (rho_ball - rho) * 9.81) / (9 * mu)
                v_terminal = max(0.0001, min(v_terminal, 50))
            elif mu > 0 and not will_sink:
                v_terminal = (2 * ball_radius**2 * (rho - rho_ball) * 9.81) / (9 * mu)
                v_terminal = max(0.0001, min(v_terminal, 50))
            else:
                v_terminal = 50
            
            # Container dimensions
            container_width = 6
            container_height = 12
            ball_viz_radius = 0.4
            
            real_container_height = 0.20
            fall_distance = real_container_height - 2 * (ball_radius)
            
            if v_terminal > 0:
                time_to_sink = fall_distance / v_terminal
            else:
                time_to_sink = float('inf')
            
            # Display terminal velocity and time
            v_col1, v_col2, v_col3 = st.columns(3)
            with v_col1:
                st.metric("Terminal Velocity", f"{v_terminal:.6f} m/s")
            with v_col2:
                st.metric("In cm/s", f"{v_terminal * 100:.4f} cm/s")
            with v_col3:
                if time_to_sink < 10000:
                    st.metric("Time to Sink/Rise", f"{time_to_sink:.6f} s")
                else:
                    st.metric("Time to Sink/Rise", "Very long!")
            
            # Animation parameters
            animation_time = max(0.5, min(30.0, time_to_sink))
            
            if animation_time < 1:
                n_frames = 30
            elif animation_time < 5:
                n_frames = 60
            elif animation_time < 15:
                n_frames = 90
            else:
                n_frames = 120
            
            frame_duration_ms = (animation_time * 1000) / n_frames
            
            start_y = container_height - ball_viz_radius - 0.3
            end_y = ball_viz_radius
            
            if not will_sink:
                start_y = ball_viz_radius + 0.3
                end_y = container_height - ball_viz_radius - 0.3
            
            positions = []
            for i in range(n_frames):
                progress = i / (n_frames - 1)
                if will_sink:
                    pos = start_y - (start_y - end_y) * progress
                else:
                    pos = start_y + (end_y - start_y) * progress
                positions.append(pos)
            
            frames = []
            for i, ball_y in enumerate(positions):
                frame_data = []
                theta_circle = np.linspace(0, 2*np.pi, 30)
                ball_x = container_width/2 + ball_viz_radius * np.cos(theta_circle)
                ball_y_circle = ball_y + ball_viz_radius * np.sin(theta_circle)
                
                frame_data.append(go.Scatter(
                    x=ball_x, y=ball_y_circle,
                    fill='toself', fillcolor=ball_color,
                    line=dict(color='black', width=2),
                    mode='lines',
                    showlegend=False
                ))
                
                frames.append(go.Frame(data=frame_data, name=str(i)))
            
            fig3 = go.Figure()
            
            fig3.add_shape(type="rect", x0=-0.2, y0=0, x1=0, y1=container_height,
                          fillcolor="rgba(200, 220, 255, 0.5)", line=dict(color="darkblue", width=2))
            fig3.add_shape(type="rect", x0=container_width, y0=0, x1=container_width+0.2, y1=container_height,
                          fillcolor="rgba(200, 220, 255, 0.5)", line=dict(color="darkblue", width=2))
            fig3.add_shape(type="rect", x0=-0.2, y0=-0.3, x1=container_width+0.2, y1=0,
                          fillcolor="rgba(150, 150, 160, 0.8)", line=dict(color="black", width=2))
            
            fig3.add_shape(type="rect", x0=0, y0=0, x1=container_width, y1=container_height,
                          fillcolor=fluid_color, line_width=0, layer="below")
            
            fig3.add_shape(type="line", x0=0, y0=container_height, x1=container_width, y1=container_height,
                          line=dict(color="darkblue", width=3))
            
            theta_circle = np.linspace(0, 2*np.pi, 30)
            ball_x_init = container_width/2 + ball_viz_radius * np.cos(theta_circle)
            ball_y_init = positions[0] + ball_viz_radius * np.sin(theta_circle)
            
            fig3.add_trace(go.Scatter(
                x=ball_x_init, y=ball_y_init,
                fill='toself', fillcolor=ball_color,
                line=dict(color='black', width=2),
                mode='lines',
                showlegend=False,
                name='Ball'
            ))
            
            fig3.frames = frames
            
            fig3.add_annotation(x=container_width + 1, y=container_height/2,
                              text=f"<b>{fluid_choice}</b><br>μ = {mu:.4f} Pa·s",
                              showarrow=False, font=dict(size=11, color="darkblue"),
                              bgcolor="rgba(255,255,255,0.9)", borderpad=5)
            
            fig3.add_annotation(x=container_width/2, y=container_height + 0.5,
                              text=f"<b>{ball_choice} Ball</b><br>ρ = {rho_ball} kg/m³",
                              showarrow=False, font=dict(size=11),
                              bgcolor="rgba(255,255,255,0.9)", borderpad=5)
            
            if will_sink:
                fig3.add_annotation(x=container_width/2, y=container_height - 3,
                                  text="⬇️ SINKING", showarrow=False,
                                  font=dict(size=14, color="darkred"))
            else:
                fig3.add_annotation(x=container_width/2, y=3,
                                  text="⬆️ FLOATING UP", showarrow=False,
                                  font=dict(size=14, color="darkgreen"))
            
            fig3.add_annotation(
                x=container_width/2, y=-1.0,
                text=f"<b>V_terminal = {v_terminal:.4f} m/s ({v_terminal*100:.2f} cm/s)</b>",
                showarrow=False,
                font=dict(size=14, color="white"),
                bgcolor="rgba(0, 100, 200, 0.9)",
                bordercolor="darkblue",
                borderwidth=2,
                borderpad=8
            )
            
            fig3.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        showactive=False,
                        y=1.15,
                        x=0.5,
                        xanchor="center",
                        buttons=[
                            dict(label="▶ Drop Ball",
                                 method="animate",
                                 args=[None, {
                                     "frame": {"duration": frame_duration_ms, "redraw": True},
                                     "fromcurrent": True,
                                     "transition": {"duration": 0}
                                 }]),
                            dict(label="⏸ Pause",
                                 method="animate",
                                 args=[[None], {
                                     "frame": {"duration": 0, "redraw": False},
                                     "mode": "immediate",
                                     "transition": {"duration": 0}
                                 }]),
                            dict(label="🔄 Reset",
                                 method="animate",
                                 args=[[str(0)], {
                                     "frame": {"duration": 0, "redraw": True},
                                     "mode": "immediate",
                                     "transition": {"duration": 0}
                                 }])
                        ]
                    )
                ],
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, 
                          range=[-1, container_width+2.5]),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, 
                          range=[-1.8, container_height+1.5],
                          scaleanchor="x", scaleratio=1),
                height=550,
                showlegend=False,
                plot_bgcolor='white',
                margin=dict(t=80)
            )
            
            st.plotly_chart(fig3, use_container_width=True)
            
            st.caption(f"""
            **Stokes' Law**: V_terminal = (2r²Δρg) / (9μ) where Δρ = |ρ_ball - ρ_fluid|
            
            **Container height**: {real_container_height*100:.0f} cm | **Fall distance**: {fall_distance*100:.2f} cm
            """)
        
        with viz_tab2:
            # --- Parallel Plate Flow Visualization ---
            st.markdown("#### Couette Flow (Fluid Between Parallel Plates)")
            
            fig = go.Figure()
            
            plate_length = 10
            plate_gap = 2
            
            fig.add_shape(type="rect", x0=0, y0=plate_gap, x1=plate_length, y1=plate_gap+0.3,
                         fillcolor="rgba(100,100,100,0.8)", line=dict(color="black", width=2))
            fig.add_annotation(x=plate_length/2, y=plate_gap+0.5, text="<b>Moving Plate (V)</b>",
                             showarrow=False, font=dict(size=12))
            
            fig.add_shape(type="rect", x0=0, y0=-0.3, x1=plate_length, y1=0,
                         fillcolor="rgba(100,100,100,0.8)", line=dict(color="black", width=2))
            fig.add_annotation(x=plate_length/2, y=-0.5, text="<b>Stationary Plate</b>",
                             showarrow=False, font=dict(size=12))
            
            fig.add_shape(type="rect", x0=0, y0=0, x1=plate_length, y1=plate_gap,
                         fillcolor=fluid_color, line=dict(color="blue", width=1))
            
            n_arrows = 8
            max_arrow_length = 2.5 - (mu / 3)
            max_arrow_length = max(0.5, max_arrow_length)
            
            for i in range(n_arrows + 1):
                y_pos = i * plate_gap / n_arrows
                velocity_fraction = y_pos / plate_gap
                arrow_length = velocity_fraction * max_arrow_length
                
                if arrow_length > 0.1:
                    fig.add_annotation(
                        x=2 + arrow_length, y=y_pos,
                        ax=2, ay=y_pos,
                        showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2,
                        arrowcolor="darkblue"
                    )
            
            y_profile = np.linspace(0, plate_gap, 20)
            x_profile = 2 + (y_profile / plate_gap) * max_arrow_length
            fig.add_trace(go.Scatter(x=x_profile, y=y_profile, mode='lines',
                                    line=dict(color='red', width=3, dash='dash'),
                                    name='Velocity Profile'))
            
            fig.add_annotation(x=7, y=plate_gap/2, 
                             text=f"<b>τ = μ × (du/dy)</b><br>τ = {tau:.2f} Pa",
                             showarrow=False, font=dict(size=14, color="darkred"),
                             bgcolor="rgba(255,255,255,0.9)", bordercolor="red", borderwidth=2)
            
            resistance_text = "High resistance" if mu > 0.1 else "Low resistance" if mu < 0.01 else "Medium resistance"
            fig.add_annotation(x=plate_length/2, y=plate_gap/2,
                             text=f"<b>{resistance_text}</b>",
                             showarrow=False, font=dict(size=16, color="white"),
                             bgcolor=fluid_color.replace('0.7', '0.9').replace('0.8', '0.95'))
            
            fig.update_layout(
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-1, plate_length+1]),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-1, plate_gap+1]),
                height=350,
                showlegend=False,
                plot_bgcolor='white',
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            fig.add_annotation(
                x=plate_length/2, y=plate_gap+1.0,
                text=f"<b>Shear Stress: {tau:.2f} Pa</b>",
                showarrow=False,
                font=dict(size=18, color="white"),
                bgcolor="rgba(0, 100, 200, 0.9)",
                bordercolor="darkblue",
                borderwidth=2,
                borderpad=8
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption("""
            **Couette Flow**: When one plate moves relative to another, the fluid between them experiences shear.
            Higher viscosity fluids resist this shearing motion more strongly.
            """)
    
    st.markdown("---")
    
    # SECTION 2: THEORY & CONCEPTS
    st.markdown("### 📚 Theory & Concepts")
    
    col_theory1, col_theory2 = st.columns([1, 1])
    
    with col_theory1:
        st.markdown("""
        #### What is Viscosity?
        
        **Viscosity** is a measure of a fluid's resistance to deformation or flow. Think of it as the "thickness" or "stickiness" of a fluid.
        
        - **High viscosity**: Honey, motor oil, glycerol (flows slowly)
        - **Low viscosity**: Water, air, alcohol (flows easily)
        
        #### Newton's Law of Viscosity
        
        For **Newtonian fluids**, the shear stress is directly proportional to the shear rate:
        """)
        
        st.latex(r'\tau = \mu \frac{du}{dy}')
        
        st.markdown("""
        Where:
        - **τ** (tau) = Shear stress [Pa or N/m²]
        - **μ** (mu) = Dynamic viscosity [Pa·s]
        - **du/dy** = Velocity gradient (shear rate) [1/s]
        """)
    
    with col_theory2:
        st.markdown("""
        #### Two Types of Viscosity
        
        **1. Dynamic (Absolute) Viscosity (μ)**
        - Measures the force required to move one layer of fluid past another
        - Units: Pa·s (SI) or Poise (P) where 1 Pa·s = 10 P
        
        **2. Kinematic Viscosity (ν)**
        - Dynamic viscosity divided by density
        """)
        
        st.latex(r'\nu = \frac{\mu}{\rho}')
        
        st.markdown("""
        - Units: m²/s (SI) or Stokes (St)
        
        > **Fun Fact**: Kinematic viscosity is used in the Reynolds number calculation!
        """)
    
    st.markdown("---")
    
    # Viscosity comparison table
    st.markdown("#### 📊 Viscosity of Common Fluids at 20°C")
    
    col_table1, col_table2 = st.columns(2)
    
    with col_table1:
        st.markdown("""
        | Fluid | μ (Pa·s) | Relative to Water |
        |-------|----------|-------------------|
        | Air | 1.81 × 10⁻⁵ | 0.018× |
        | Water | 1.00 × 10⁻³ | 1× (reference) |
        | Blood | 3-4 × 10⁻³ | 3-4× |
        | Olive Oil | 8.4 × 10⁻² | 84× |
        | Motor Oil | 0.1 - 0.3 | 100-300× |
        """)
    
    with col_table2:
        st.markdown("""
        | Fluid | μ (Pa·s) | Relative to Water |
        |-------|----------|-------------------|
        | Maple Syrup | 0.15 | 150× |
        | Honey | 2 - 10 | 2,000-10,000× |
        | Glycerol | 1.5 | 1,500× |
        | Peanut Butter | ~250 | 250,000× |
        | Pitch (tar) | 2.3 × 10⁸ | 230 billion× |
        """)

# =====================================================
# TAB 2: SURFACE TENSION
# =====================================================
with main_tab2:
    st.markdown("<h2 style='text-align: center;'>💧 Understanding Surface Tension</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 16px;'>Discover why water forms droplets, how insects walk on water, and the molecular forces at fluid interfaces.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # SECTION 1: THEORY & CONCEPTS
    st.markdown("### 📚 Theory & Concepts")
    
    col_st_theory1, col_st_theory2 = st.columns([1, 1])
    
    
    with col_st_theory1:
        st.markdown("""
        #### What is Surface Tension?
        
        **Surface tension** is the tendency of liquid surfaces to shrink to the minimum possible area. 
        It's caused by the cohesive forces between liquid molecules.
        
        - Molecules inside the liquid are pulled equally in all directions
        - Molecules at the surface have no neighbors above, creating a net inward force
        - This creates a "skin" effect on the liquid surface
        
        #### The Physical Meaning
        
        Surface tension explains why:
        - Water forms droplets rather than spreading infinitely
        - Small insects can walk on water
        - Soap bubbles are spherical
        - A needle can float on water if placed carefully
        """)
        
        st.latex(r'\gamma = \frac{F}{L}')
        
        st.markdown("""
        Where:
        - **γ** (gamma) = Surface tension [N/m or J/m²]
        - **F** = Force along the surface [N]
        - **L** = Length over which force acts [m]
        """)
    
    with col_st_theory2:
        st.markdown("""
        #### Key Equations
        
        **Capillary Rise (Jurin's Law)**
        """)
        
        st.latex(r'h = \frac{2\gamma \cos\theta}{\rho g r}')
        
        st.markdown("""
        **Pressure Inside a Droplet (Young-Laplace)**
        """)
        
        st.latex(r'\Delta P = \frac{2\gamma}{r}')
        
        st.markdown("""
        **Pressure Inside a Bubble (2 surfaces)**
        """)
        
        st.latex(r'\Delta P = \frac{4\gamma}{r}')
        
        st.markdown("""
        #### Factors Affecting Surface Tension
        
        - **Temperature**: ↑ Temperature → ↓ Surface tension
        - **Surfactants**: Reduce surface tension (soap, detergents)
        - **Impurities**: Generally decrease surface tension
        - **Salts**: Can increase surface tension slightly
        """)
    
    st.markdown("---")
    
    # Surface tension comparison table
    st.markdown("#### 📊 Surface Tension of Common Liquids at 20°C")
    
    col_st_table1, col_st_table2 = st.columns(2)
    
    with col_st_table1:
        st.markdown("""
        | Liquid | γ (N/m) | Relative to Water |
        |--------|---------|-------------------|
        | Acetone | 0.025 | 0.34× |
        | Ethanol | 0.022 | 0.30× |
        | Soap Solution | 0.025 | 0.34× |
        | Olive Oil | 0.032 | 0.44× |
        | Glycerol | 0.064 | 0.88× |
        """)
    
    with col_st_table2:
        st.markdown("""
        | Liquid | γ (N/m) | Relative to Water |
        |--------|---------|-------------------|
        | Water | 0.0728 | 1× (reference) |
        | Blood | 0.058 | 0.80× |
        | Mercury | 0.485 | 6.66× |
        | Liquid Helium | 0.00012 | 0.002× |
        | Molten Glass | ~0.3 | 4.1× |
        """)
    
    st.info("""
    **Why does soap reduce surface tension?**
    
    Soap molecules are **surfactants** - they have a water-loving (hydrophilic) head and a water-fearing (hydrophobic) tail.
    At the surface, they insert themselves between water molecules, reducing the cohesive forces and thus the surface tension.
    This is why soapy water spreads more easily and creates bubbles!
    """)
    
    st.markdown("---")
    
    # Engineering Applications
    st.markdown("### 📋 Engineering Applications")
    
    col_st_app1, col_st_app2 = st.columns([1, 1])
    
    with col_st_app1:
        st.markdown("""
        #### Industrial Applications
        
        **🖨️ Inkjet Printing**
        - Surface tension controls droplet formation
        - Critical for print quality and resolution
        
        **🧪 Lab-on-a-Chip Devices**
        - Capillary forces drive fluid flow
        - No pumps needed in microchannels
        
        **🛢️ Oil Recovery**
        - Surfactants reduce interfacial tension
        - Helps release oil from rock pores
        
        **🎨 Coating & Painting**
        - Controls wetting and spreading
        - Prevents defects like crawling and dewetting
        """)
    
    with col_st_app2:
        st.markdown("""
        #### Natural Phenomena
        
        **🕷️ Water Striders**
        - Insects exploit surface tension to walk on water
        - Their legs are hydrophobic (high contact angle)
        - *Try the simulation above with "Water Strider" object!*
        
        **🪡 Floating Needle Trick**
        - A steel needle can float if placed gently
        - Surface tension supports ~1000× more than buoyancy alone
        
        **🫧 Soap Bubbles**
        - Minimize surface area (spherical shape)
        - Two surfaces = 4γ/r pressure
        
        **💧 Morning Dew**
        - Water condenses as droplets on surfaces
        - Shape depends on surface wettability
        """)
    
    st.success("""
    **Dimensionless Numbers Involving Surface Tension:**
    
    - **Weber Number (We)** = ρV²L/γ — Ratio of inertia to surface tension
    - **Capillary Number (Ca)** = μV/γ — Ratio of viscous forces to surface tension
    - **Bond Number (Bo)** = ρgL²/γ — Ratio of gravitational to surface tension forces
    """)

# =====================================================
# TAB 3: BUOYANCY AND STABILITY
# =====================================================
with main_tab3:
    st.markdown("<h2 style='text-align: center;'>⚓ Buoyancy and Stability</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 16px;'>Understand why objects float or sink, and explore the stability of floating bodies through Archimedes' Principle.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # SECTION 1: INTERACTIVE SIMULATION
    st.markdown("### 🎯 Interactive Simulation")
    
    col_b1, col_b2 = st.columns([2, 3])
    
    with col_b1:
        st.subheader("🔬 Parameters")
        
        # --- Fluid Selection ---
        st.markdown("**Select the Fluid**")
        fluid_buoy = st.selectbox(
            "Choose the surrounding fluid:",
            ("Water (Fresh)", "Seawater", "Oil", "Mercury", "Glycerol", "Custom"),
            key="buoy_fluid_selector"
        )
        
        FLUID_BUOY_PROPERTIES = {
            "Water (Fresh)": {'rho': 1000, 'color': 'rgba(100, 170, 255, 0.6)', 'name': 'Fresh Water'},
            "Seawater":      {'rho': 1025, 'color': 'rgba(70, 150, 220, 0.6)', 'name': 'Seawater'},
            "Oil":           {'rho': 850, 'color': 'rgba(200, 180, 100, 0.6)', 'name': 'Oil'},
            "Mercury":       {'rho': 13546, 'color': 'rgba(180, 180, 180, 0.8)', 'name': 'Mercury'},
            "Glycerol":      {'rho': 1260, 'color': 'rgba(200, 200, 220, 0.6)', 'name': 'Glycerol'},
        }
        
        if fluid_buoy == "Custom":
            rho_fluid = st.slider("Fluid Density (kg/m³)", 500, 15000, 1000, 10, key="buoy_fluid_rho")
            fluid_color_buoy = 'rgba(100, 170, 255, 0.6)'
        else:
            rho_fluid = FLUID_BUOY_PROPERTIES[fluid_buoy]['rho']
            fluid_color_buoy = FLUID_BUOY_PROPERTIES[fluid_buoy]['color']
            st.info(f"**{fluid_buoy}**: ρ = {rho_fluid} kg/m³")
        
        st.markdown("---")
        st.markdown("**Object Properties**")
        
        # Object selection
        object_buoy = st.selectbox(
            "Choose an object:",
            ("Wooden Block", "Steel Cube", "Ice Cube", "Aluminum Block", "Cork", "Concrete Block", "Custom"),
            key="buoy_object_selector"
        )
        
        OBJECT_BUOY_PROPERTIES = {
            "Wooden Block":    {'rho': 600, 'color': 'rgba(180, 130, 80, 0.95)', 'name': 'Wood (Oak)'},
            "Steel Cube":      {'rho': 7850, 'color': 'rgba(120, 120, 130, 0.95)', 'name': 'Steel'},
            "Ice Cube":        {'rho': 917, 'color': 'rgba(200, 230, 255, 0.7)', 'name': 'Ice'},
            "Aluminum Block":  {'rho': 2700, 'color': 'rgba(180, 180, 190, 0.95)', 'name': 'Aluminum'},
            "Cork":            {'rho': 240, 'color': 'rgba(210, 180, 140, 0.95)', 'name': 'Cork'},
            "Concrete Block":  {'rho': 2400, 'color': 'rgba(150, 150, 150, 0.95)', 'name': 'Concrete'},
        }
        
        if object_buoy == "Custom":
            rho_object = st.slider("Object Density (kg/m³)", 100, 10000, 1000, 10, key="buoy_obj_rho")
            object_color_buoy = 'rgba(150, 150, 150, 0.95)'
        else:
            rho_object = OBJECT_BUOY_PROPERTIES[object_buoy]['rho']
            object_color_buoy = OBJECT_BUOY_PROPERTIES[object_buoy]['color']
        
        # Object dimensions
        obj_side = st.slider("Object side length (cm)", 5, 30, 15, 1, key="buoy_side")
        obj_side_m = obj_side / 100  # Convert to meters
        
        # Calculations
        g = 9.81
        V_object = obj_side_m ** 3  # Volume of cube in m³
        m_object = rho_object * V_object  # Mass of object
        W_object = m_object * g  # Weight of object
        
        # Determine floating condition
        if rho_object < rho_fluid:
            # Object floats - calculate submerged fraction
            fraction_submerged = rho_object / rho_fluid
            V_submerged = fraction_submerged * V_object
            F_buoyancy = rho_fluid * g * V_submerged
            status = "FLOATS"
            status_color = "green"
        elif rho_object > rho_fluid:
            # Object sinks - fully submerged
            fraction_submerged = 1.0
            V_submerged = V_object
            F_buoyancy = rho_fluid * g * V_submerged
            status = "SINKS"
            status_color = "red"
        else:
            # Neutrally buoyant
            fraction_submerged = 1.0
            V_submerged = V_object
            F_buoyancy = rho_fluid * g * V_submerged
            status = "NEUTRALLY BUOYANT"
            status_color = "orange"
        
        st.markdown("---")
        st.markdown("**Results**")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Object Weight (W)", f"{W_object:.2f} N")
            st.metric("Object Density", f"{rho_object} kg/m³")
        with col_res2:
            st.metric("Buoyancy Force (Fᵦ)", f"{F_buoyancy:.2f} N")
            st.metric("Fluid Density", f"{rho_fluid} kg/m³")
        
        if status == "FLOATS":
            st.success(f"✓ **{status}!** {fraction_submerged*100:.1f}% submerged")
        elif status == "SINKS":
            st.error(f"✗ **{status}!** W > Fᵦ (when fully submerged)")
        else:
            st.warning(f"⚖ **{status}!** W = Fᵦ exactly")
        
        # Apparent weight for sinking objects
        if rho_object > rho_fluid:
            apparent_weight = W_object - F_buoyancy
            st.info(f"**Apparent Weight in Fluid:** {apparent_weight:.2f} N ({apparent_weight/W_object*100:.1f}% of actual weight)")
    
    with col_b2:
        st.subheader("🖼️ Visualization")
        
        # Create buoyancy visualization
        fig_buoy = go.Figure()
        
        # Container dimensions
        container_width = 10
        container_height = 12
        fluid_level = 9
        
        # Object visualization size
        obj_viz_size = 2
        obj_x_center = container_width / 2
        
        # Calculate object position based on floating/sinking
        if status == "FLOATS":
            # Object floats - position based on submerged fraction
            submerged_height = obj_viz_size * fraction_submerged
            obj_bottom = fluid_level - submerged_height
            obj_top = obj_bottom + obj_viz_size
        elif status == "SINKS":
            # Object at bottom
            obj_bottom = 0.5
            obj_top = obj_bottom + obj_viz_size
        else:
            # Neutrally buoyant - in middle of fluid
            obj_bottom = fluid_level / 2 - obj_viz_size / 2
            obj_top = obj_bottom + obj_viz_size
        
        # Draw container
        fig_buoy.add_shape(type="rect", x0=0, y0=0, x1=container_width, y1=container_height,
                          fillcolor="rgba(200, 220, 255, 0.1)", line=dict(color="darkblue", width=3))
        
        # Draw fluid
        fig_buoy.add_shape(type="rect", x0=0.1, y0=0.1, x1=container_width-0.1, y1=fluid_level,
                          fillcolor=fluid_color_buoy, line_width=0)
        
        # Draw fluid surface line
        fig_buoy.add_shape(type="line", x0=0.1, y0=fluid_level, x1=container_width-0.1, y1=fluid_level,
                          line=dict(color="darkblue", width=3))
        
        # Draw the object
        fig_buoy.add_shape(type="rect",
                          x0=obj_x_center - obj_viz_size/2, y0=obj_bottom,
                          x1=obj_x_center + obj_viz_size/2, y1=obj_top,
                          fillcolor=object_color_buoy,
                          line=dict(color="black", width=2))
        
        # Draw force arrows
        obj_center_y = (obj_bottom + obj_top) / 2
        
        # Weight arrow (pointing down) - RED
        arrow_scale = 1.5
        weight_arrow_length = min(2.5, W_object / 50 * arrow_scale)
        fig_buoy.add_annotation(
            x=obj_x_center, y=obj_center_y - weight_arrow_length,
            ax=obj_x_center, ay=obj_center_y,
            showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3,
            arrowcolor="red"
        )
        fig_buoy.add_annotation(x=obj_x_center - 0.8, y=obj_center_y - weight_arrow_length - 0.3,
                               text="<b>W</b>", showarrow=False, font=dict(size=16, color="red"))
        
        # Buoyancy arrow (pointing up) - GREEN
        buoy_arrow_length = min(2.5, F_buoyancy / 50 * arrow_scale)
        fig_buoy.add_annotation(
            x=obj_x_center, y=obj_center_y + buoy_arrow_length,
            ax=obj_x_center, ay=obj_center_y,
            showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3,
            arrowcolor="green"
        )
        fig_buoy.add_annotation(x=obj_x_center + 0.8, y=obj_center_y + buoy_arrow_length + 0.3,
                               text="<b>F<sub>B</sub></b>", showarrow=False, font=dict(size=16, color="green"))
        
        # Pressure arrows on submerged portion (small blue arrows)
        if obj_bottom < fluid_level:
            # Bottom pressure (larger, pointing up)
            for dx in [-0.6, 0, 0.6]:
                fig_buoy.add_annotation(
                    x=obj_x_center + dx, y=obj_bottom + 0.4,
                    ax=obj_x_center + dx, ay=obj_bottom - 0.1,
                    showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2,
                    arrowcolor="blue", opacity=0.6
                )
            
            # Top pressure (smaller, pointing down) - only if submerged
            submerged_top = min(obj_top, fluid_level)
            if submerged_top > obj_bottom + 0.5:
                for dx in [-0.6, 0, 0.6]:
                    fig_buoy.add_annotation(
                        x=obj_x_center + dx, y=submerged_top - 0.4,
                        ax=obj_x_center + dx, ay=submerged_top + 0.1,
                        showarrow=True, arrowhead=2, arrowsize=0.8, arrowwidth=1.5,
                        arrowcolor="lightblue", opacity=0.6
                    )
        
        # Labels
        fig_buoy.add_annotation(x=container_width/2, y=container_height + 0.8,
                               text=f"<b>{object_buoy}</b> in <b>{fluid_buoy}</b>",
                               showarrow=False, font=dict(size=14))
        
        # Status box
        status_bg = "rgba(0, 150, 0, 0.9)" if status == "FLOATS" else "rgba(200, 0, 0, 0.9)" if status == "SINKS" else "rgba(200, 150, 0, 0.9)"
        fig_buoy.add_annotation(
            x=container_width/2, y=container_height + 1.8,
            text=f"<b>{status}</b>",
            showarrow=False,
            font=dict(size=18, color="white"),
            bgcolor=status_bg,
            bordercolor="black",
            borderwidth=2,
            borderpad=8
        )
        
        # Depth markers
        fig_buoy.add_annotation(x=-0.8, y=fluid_level, text="Surface", showarrow=False, 
                               font=dict(size=10, color="darkblue"))
        
        # Force comparison text
        force_text = f"W = {W_object:.1f} N<br>F<sub>B</sub> = {F_buoyancy:.1f} N"
        fig_buoy.add_annotation(x=container_width + 1.5, y=container_height/2,
                               text=force_text, showarrow=False,
                               font=dict(size=12), align="left",
                               bgcolor="rgba(255,255,255,0.9)", borderpad=5)
        
        fig_buoy.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-2, container_width+3]),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-1, container_height+3],
                      scaleanchor="x", scaleratio=1),
            height=550,
            showlegend=False,
            plot_bgcolor='white',
            margin=dict(t=20, b=20)
        )
        
        st.plotly_chart(fig_buoy, use_container_width=True)
        
        st.caption("""
        **Archimedes' Principle**: F_B = ρ_fluid × g × V_submerged
        
        - **Blue arrows**: Hydrostatic pressure forces (larger at bottom due to greater depth)
        - **Green arrow (F_B)**: Net buoyancy force (acts upward at centre of buoyancy)
        - **Red arrow (W)**: Weight of object (acts downward at centre of gravity)
        """)
    
    st.markdown("---")
    
    # SECTION 2: THEORY & CONCEPTS
    st.markdown("### 📚 Theory & Concepts")
    
    col_buoy_theory1, col_buoy_theory2 = st.columns([1, 1])
    
    with col_buoy_theory1:
        st.markdown("""
        #### Archimedes' Principle
        
        When an object is submerged (fully or partially) in a fluid, it experiences an upward **buoyancy force** equal to the weight of the fluid displaced.
        """)
        
        st.latex(r'F_B = \rho_{fluid} \cdot g \cdot V_{submerged}')
        
        st.markdown("""
        This principle was discovered by Archimedes (287-212 BC) and explains why objects float or sink.
        
        #### Origin of Buoyancy
        
        The buoyancy force arises from the **pressure difference** between the top and bottom of a submerged object:
        
        - Pressure increases with depth: p = ρgh
        - Bottom surface experiences higher pressure than top
        - Net upward force = F_B
        """)
        
        st.latex(r'F_B = p_2 A - p_1 A = \rho g h_2 A - \rho g h_1 A = \rho g V')
        
    with col_buoy_theory2:
        st.markdown("""
        #### Floating Condition
        
        For an object to float, the buoyancy force must balance its weight:
        """)
        
        st.latex(r'W = F_B \implies \rho_{object} \cdot V_{object} = \rho_{fluid} \cdot V_{submerged}')
        
        st.markdown("""
        **Fraction submerged** for a floating object:
        """)
        
        st.latex(r'\frac{V_{submerged}}{V_{object}} = \frac{\rho_{object}}{\rho_{fluid}}')
        
        st.markdown("""
        #### Sink, Float, or Neutral?
        
        | Condition | Result |
        |-----------|--------|
        | ρ_object < ρ_fluid | **Floats** (partially submerged) |
        | ρ_object > ρ_fluid | **Sinks** (W > F_B even when fully submerged) |
        | ρ_object = ρ_fluid | **Neutrally buoyant** (suspended in fluid) |
        
        > **Example**: Ice (ρ = 917 kg/m³) floats in water (ρ = 1000 kg/m³) with about 91.7% submerged!
        """)
    
    st.markdown("---")
    
    # SECTION 3: STABILITY
    st.markdown("### ⚖️ Stability of Floating & Submerged Bodies")
    
    col_stab1, col_stab2 = st.columns([1, 1])
    
    with col_stab1:
        st.markdown("""
        #### Stability of Submerged Bodies
        
        For a **fully submerged** body, stability depends on the relative positions of:
        
        - **CG** (Centre of Gravity): Where weight acts
        - **CB** (Centre of Buoyancy): Centroid of displaced volume
        
        | Configuration | Stability |
        |--------------|-----------|
        | CG below CB | **Stable** ✓ (self-righting) |
        | CG above CB | **Unstable** ✗ (will capsize) |
        | CG at CB | **Neutral** (no tendency either way) |
        
        > **Think of a submarine**: Ballast tanks are positioned to keep CG below CB for stability.
        """)
        
    with col_stab2:
        st.markdown("""
        #### Stability of Floating Bodies
        
        Floating bodies are more complex because the **CB moves** when the body tilts!
        
        The key concept is the **Metacentre (M)**:
        - M is where the line of action of buoyancy force intersects the centreline
        - **Metacentric Height (GM)** = distance from G to M
        
        | Configuration | Stability |
        |--------------|-----------|
        | M above CG (GM > 0) | **Stable** ✓ |
        | M below CG (GM < 0) | **Unstable** ✗ |
        | M at CG (GM = 0) | **Neutral** |
        
        > **Ships** are designed with positive GM. Wider ships are generally more stable!
        """)
    
    st.info("""
    **Why can ships have CG above CB and still be stable?**
    
    When a ship tilts, the shape of the submerged volume changes, causing CB to shift sideways. 
    If the metacentre M (intersection of the new buoyancy line with the centreline) is above CG, 
    a **restoring moment** is created that rights the ship. This is why the metacentric height GM 
    is the critical stability parameter for floating vessels, not just the CG-CB relationship.
    """)
    
    st.markdown("---")
    
    # Practical Applications
    st.markdown("### 📋 Engineering Applications")
    
    col_app1, col_app2 = st.columns([1, 1])
    
    with col_app1:
        st.markdown("""
        #### Marine & Naval Engineering
        
        **🚢 Ship Design**
        - Hull shape optimized for stability (GM > 0)
        - Ballast systems to adjust CG position
        - Load distribution to maintain stability
        
        **🛥️ Submarines**
        - Ballast tanks for depth control
        - Trim tanks for pitch adjustment
        - CG kept below CB for stability
        
        **🏊 Life Jackets & Buoys**
        - Low-density materials (foam, air)
        - Designed to keep head above water
        """)
        
    with col_app2:
        st.markdown("""
        #### Industrial Applications
        
        **⚗️ Hydrometers**
        - Measure fluid density by floating depth
        - Used in brewing, batteries, milk testing
        
        **🎈 Hot Air Balloons**
        - Heated air is less dense than cold air
        - Buoyancy in atmosphere (same principle!)
        
        **🛢️ Oil-Water Separation**
        - Oil floats on water (ρ_oil < ρ_water)
        - Used in spill cleanup and refineries
        
        **⚓ Offshore Platforms**
        - Semi-submersibles use buoyancy
        - Tension-leg platforms anchored against buoyancy
        """)
    
    st.success("""
    **Key Equations Summary:**
    
    - **Buoyancy Force**: F_B = ρ_fluid × g × V_submerged
    - **Floating Condition**: ρ_object × V_object = ρ_fluid × V_submerged  
    - **Fraction Submerged**: V_sub/V_total = ρ_object/ρ_fluid
    - **Apparent Weight**: W_apparent = W - F_B = (ρ_object - ρ_fluid) × g × V
    """)

# =====================================================
# TAB 4: BERNOULLI PRINCIPLE
# =====================================================
with main_tab4:
    st.markdown("<h2 style='text-align: center;'>🌊 The Bernoulli Principle</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 16px;'>Explore the fundamental relationship between pressure, velocity, and elevation in flowing fluids.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # SECTION 1: INTERACTIVE SIMULATION
    st.markdown("### 🎯 Interactive Simulation - Venturi Effect")
    
    col_bern1, col_bern2 = st.columns([2, 3])
    
    with col_bern1:
        st.subheader("🔬 Parameters")
        
        st.markdown("**Pipe Configuration**")
        
        # Inlet parameters
        D1 = st.slider("Inlet Diameter D₁ (cm)", 5, 20, 10, 1, key="bern_D1")
        D2 = st.slider("Throat Diameter D₂ (cm)", 2, 15, 5, 1, key="bern_D2")
        
        # Ensure D2 < D1
        if D2 >= D1:
            st.warning("⚠️ Throat diameter should be smaller than inlet!")
            D2 = D1 - 1
        
        st.markdown("---")
        st.markdown("**Flow Conditions**")
        
        # Inlet velocity
        U1 = st.slider("Inlet Velocity U₁ (m/s)", 0.5, 10.0, 2.0, 0.1, key="bern_U1")
        
        # Fluid selection
        fluid_bern = st.selectbox(
            "Select Fluid:",
            ("Water", "Air", "Oil", "Custom"),
            key="bern_fluid"
        )
        
        FLUID_BERN = {
            "Water": {'rho': 1000, 'name': 'Water'},
            "Air": {'rho': 1.2, 'name': 'Air'},
            "Oil": {'rho': 850, 'name': 'Oil'},
        }
        
        if fluid_bern == "Custom":
            rho_bern = st.number_input("Fluid Density (kg/m³)", value=1000, min_value=1, max_value=15000, key="bern_rho")
        else:
            rho_bern = FLUID_BERN[fluid_bern]['rho']
        
        # Reference elevation
        z1 = st.slider("Inlet Elevation z₁ (m)", 0.0, 5.0, 1.0, 0.1, key="bern_z1")
        z2 = st.slider("Throat Elevation z₂ (m)", 0.0, 5.0, 1.0, 0.1, key="bern_z2")
        
        # Inlet pressure (gauge)
        p1_kpa = st.slider("Inlet Pressure p₁ (kPa gauge)", 0, 500, 100, 10, key="bern_p1")
        p1 = p1_kpa * 1000  # Convert to Pa
        
        st.markdown("---")
        
        # Calculations using continuity and Bernoulli
        # Convert diameters to meters
        D1_m = D1 / 100
        D2_m = D2 / 100
        
        # Areas
        A1 = np.pi * (D1_m/2)**2
        A2 = np.pi * (D2_m/2)**2
        
        # Continuity: A1*U1 = A2*U2
        U2 = U1 * (A1 / A2)
        
        # Volume flow rate
        Q = A1 * U1  # m³/s
        
        # Bernoulli: p1/ρ + U1²/2 + gz1 = p2/ρ + U2²/2 + gz2
        # Solve for p2:
        g = 9.81
        p2 = p1 + 0.5 * rho_bern * (U1**2 - U2**2) + rho_bern * g * (z1 - z2)
        
        # Calculate heads
        pressure_head_1 = p1 / (rho_bern * g)
        velocity_head_1 = U1**2 / (2 * g)
        elevation_head_1 = z1
        total_head_1 = pressure_head_1 + velocity_head_1 + elevation_head_1
        
        pressure_head_2 = p2 / (rho_bern * g)
        velocity_head_2 = U2**2 / (2 * g)
        elevation_head_2 = z2
        total_head_2 = pressure_head_2 + velocity_head_2 + elevation_head_2
        
        st.markdown("**Results**")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("**Inlet (1)**")
            st.metric("Velocity U₁", f"{U1:.2f} m/s")
            st.metric("Pressure p₁", f"{p1/1000:.1f} kPa")
        with col_r2:
            st.markdown("**Throat (2)**")
            st.metric("Velocity U₂", f"{U2:.2f} m/s")
            st.metric("Pressure p₂", f"{p2/1000:.1f} kPa")
        
        st.metric("Volume Flow Rate Q", f"{Q*1000:.2f} L/s")
        
        # Pressure change indicator
        delta_p = p2 - p1
        if delta_p < 0:
            st.success(f"✓ Pressure **drops** by {abs(delta_p)/1000:.1f} kPa at throat (velocity increases!)")
        else:
            st.info(f"Pressure **increases** by {delta_p/1000:.1f} kPa at throat")
        
        # Check for cavitation (water only)
        if fluid_bern == "Water" and p2 < -100000:  # Below -100 kPa gauge (absolute ~ 0)
            st.error("⚠️ **Cavitation Warning!** Pressure at throat may go below vapor pressure!")
    
    with col_bern2:
        st.subheader("🖼️ Visualization")
        
        # Create Venturi tube visualization
        fig_bern = go.Figure()
        
        # Pipe dimensions for visualization
        pipe_length = 12
        inlet_length = 4
        throat_length = 4
        outlet_length = 4
        
        # Scale factors for visualization
        inlet_radius = D1 / 10  # Scale to reasonable size
        throat_radius = D2 / 10
        
        # Create pipe outline
        # Top wall
        x_top = [0, inlet_length, inlet_length + throat_length/3, 
                inlet_length + 2*throat_length/3, inlet_length + throat_length, pipe_length]
        y_top = [inlet_radius, inlet_radius, throat_radius, 
                throat_radius, inlet_radius, inlet_radius]
        
        # Bottom wall (mirror)
        x_bottom = x_top
        y_bottom = [-y for y in y_top]
        
        # Draw pipe walls
        fig_bern.add_trace(go.Scatter(x=x_top, y=y_top, mode='lines',
                                      line=dict(color='darkblue', width=4), showlegend=False))
        fig_bern.add_trace(go.Scatter(x=x_bottom, y=y_bottom, mode='lines',
                                      line=dict(color='darkblue', width=4), showlegend=False))
        
        # Fill pipe interior
        x_fill = x_top + x_bottom[::-1]
        y_fill = y_top + y_bottom[::-1]
        fig_bern.add_trace(go.Scatter(x=x_fill, y=y_fill, fill='toself',
                                      fillcolor='rgba(100, 170, 255, 0.3)',
                                      line=dict(width=0), showlegend=False))
        
        # Flow arrows (more arrows in throat due to higher velocity)
        # Inlet arrows
        for y_pos in np.linspace(-inlet_radius*0.6, inlet_radius*0.6, 3):
            fig_bern.add_annotation(
                x=2, y=y_pos, ax=0.5, ay=y_pos,
                showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2,
                arrowcolor="blue"
            )
        
        # Throat arrows (longer to show higher velocity)
        arrow_scale = U2/U1
        for y_pos in np.linspace(-throat_radius*0.5, throat_radius*0.5, 3):
            fig_bern.add_annotation(
                x=inlet_length + throat_length/2 + 0.8*arrow_scale, y=y_pos,
                ax=inlet_length + throat_length/2 - 0.5, ay=y_pos,
                showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2,
                arrowcolor="red"
            )
        
        # Outlet arrows
        for y_pos in np.linspace(-inlet_radius*0.6, inlet_radius*0.6, 3):
            fig_bern.add_annotation(
                x=pipe_length - 0.5, y=y_pos, ax=pipe_length - 2, ay=y_pos,
                showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2,
                arrowcolor="blue"
            )
        
        # Pressure indicators (manometer tubes)
        manometer_height_1 = min(3, pressure_head_1 / 2)  # Scale for visualization
        manometer_height_2 = min(3, max(-2, pressure_head_2 / 2))
        
        # Inlet manometer
        fig_bern.add_shape(type="line", x0=2, y0=inlet_radius, x1=2, y1=inlet_radius + 2.5,
                          line=dict(color="gray", width=2))
        fig_bern.add_shape(type="rect", x0=1.8, y0=inlet_radius, x1=2.2, y1=inlet_radius + manometer_height_1,
                          fillcolor="rgba(100, 170, 255, 0.8)", line=dict(width=1))
        fig_bern.add_annotation(x=2, y=inlet_radius + 2.8, text=f"p₁={p1/1000:.0f} kPa",
                               showarrow=False, font=dict(size=10))
        
        # Throat manometer
        throat_x = inlet_length + throat_length/2
        fig_bern.add_shape(type="line", x0=throat_x, y0=throat_radius, x1=throat_x, y1=throat_radius + 2.5,
                          line=dict(color="gray", width=2))
        if manometer_height_2 > 0:
            fig_bern.add_shape(type="rect", x0=throat_x-0.2, y0=throat_radius, 
                              x1=throat_x+0.2, y1=throat_radius + manometer_height_2,
                              fillcolor="rgba(100, 170, 255, 0.8)", line=dict(width=1))
        fig_bern.add_annotation(x=throat_x, y=throat_radius + 2.8, text=f"p₂={p2/1000:.0f} kPa",
                               showarrow=False, font=dict(size=10, color="red" if p2 < p1 else "black"))
        
        # Labels
        fig_bern.add_annotation(x=1, y=-inlet_radius - 0.8, text=f"D₁={D1} cm<br>U₁={U1:.1f} m/s",
                               showarrow=False, font=dict(size=11))
        fig_bern.add_annotation(x=throat_x, y=-throat_radius - 1.0, text=f"D₂={D2} cm<br>U₂={U2:.1f} m/s",
                               showarrow=False, font=dict(size=11, color="red"))
        fig_bern.add_annotation(x=pipe_length - 1, y=-inlet_radius - 0.8, text="Outlet",
                               showarrow=False, font=dict(size=11))
        
        # Title
        fig_bern.add_annotation(x=pipe_length/2, y=inlet_radius + 4,
                               text="<b>Venturi Tube - Bernoulli Principle</b>",
                               showarrow=False, font=dict(size=14))
        
        fig_bern.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-1, pipe_length+1]),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, 
                      range=[-inlet_radius - 2, inlet_radius + 5], scaleanchor="x", scaleratio=1),
            height=400,
            showlegend=False,
            plot_bgcolor='white',
            margin=dict(t=20, b=20)
        )
        
        st.plotly_chart(fig_bern, use_container_width=True)
        
        # Energy head bar chart
        st.markdown("#### Energy Head Breakdown")
        
        fig_heads = go.Figure()
        
        locations = ['Inlet (1)', 'Throat (2)']
        
        fig_heads.add_trace(go.Bar(
            name='Pressure Head (p/ρg)', x=locations,
            y=[pressure_head_1, pressure_head_2],
            marker_color='steelblue'
        ))
        fig_heads.add_trace(go.Bar(
            name='Velocity Head (U²/2g)', x=locations,
            y=[velocity_head_1, velocity_head_2],
            marker_color='coral'
        ))
        fig_heads.add_trace(go.Bar(
            name='Elevation Head (z)', x=locations,
            y=[elevation_head_1, elevation_head_2],
            marker_color='seagreen'
        ))
        
        fig_heads.update_layout(
            barmode='stack',
            yaxis_title='Head (m)',
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            margin=dict(t=50, b=20)
        )
        
        # Add total head line
        fig_heads.add_hline(y=total_head_1, line_dash="dash", line_color="red",
                           annotation_text=f"Total Head = {total_head_1:.2f} m")
        
        st.plotly_chart(fig_heads, use_container_width=True)
        
        st.caption("""
        **Key Insight**: As velocity increases in the throat, pressure decreases to keep total head constant.
        This is the Venturi effect - the basis for many flow measurement devices!
        """)
    
    st.markdown("---")
    
    # SECTION 2: THEORY & CONCEPTS
    st.markdown("### 📚 Theory & Concepts")
    
    col_bern_theory1, col_bern_theory2 = st.columns([1, 1])
    
    with col_bern_theory1:
        st.markdown("""
        #### The Bernoulli Equation
        
        Derived from conservation of energy along a streamline for **steady, incompressible, inviscid flow**:
        """)
        
        st.latex(r'\frac{p}{\rho} + \frac{U^2}{2} + gz = \text{Constant}')
        
        st.markdown("""
        Or in terms of **Head** (dividing by g):
        """)
        
        st.latex(r'\frac{p}{\rho g} + \frac{U^2}{2g} + z = \text{Total Head}')
        
        st.markdown("""
        #### The Three Energy Terms
        
        | Term | Name | Physical Meaning |
        |------|------|------------------|
        | p/ρg | **Pressure Head** | Energy from fluid pressure |
        | U²/2g | **Velocity Head** | Kinetic energy of flow |
        | z | **Elevation Head** | Potential energy (gravity) |
        
        > **Total Head** remains constant along a streamline (ideal flow)
        """)
        
    with col_bern_theory2:
        st.markdown("""
        #### Continuity Equation
        
        Conservation of mass for incompressible flow:
        """)
        
        st.latex(r'A_1 U_1 = A_2 U_2 = Q = \text{Constant}')
        
        st.markdown("""
        This means:
        - **Smaller area → Higher velocity**
        - **Larger area → Lower velocity**
        
        #### Combining Continuity & Bernoulli
        
        Between two points on a streamline:
        """)
        
        st.latex(r'\frac{p_1}{\rho g} + \frac{U_1^2}{2g} + z_1 = \frac{p_2}{\rho g} + \frac{U_2^2}{2g} + z_2')
        
        st.markdown("""
        #### Key Assumptions
        
        Bernoulli equation is valid when:
        - ✓ **Steady flow** (no time variation)
        - ✓ **Incompressible fluid** (constant ρ)
        - ✓ **Inviscid flow** (no friction losses)
        - ✓ **Along a streamline**
        - ✓ **No heat transfer or work**
        """)
    
    st.markdown("---")
    
    # Alternative forms
    st.markdown("### 📐 Alternative Forms of Bernoulli Equation")
    
    col_form1, col_form2, col_form3 = st.columns(3)
    
    with col_form1:
        st.markdown("**Specific Energy Form**")
        st.markdown("*(J/kg)*")
        st.latex(r'\frac{p}{\rho} + \frac{U^2}{2} + gz = \text{Constant}')
        
    with col_form2:
        st.markdown("**Head Form**")
        st.markdown("*(m)*")
        st.latex(r'\frac{p}{\rho g} + \frac{U^2}{2g} + z = \text{Constant}')
        
    with col_form3:
        st.markdown("**Pressure Form**")
        st.markdown("*(N/m² or Pa)*")
        st.latex(r'p + \frac{\rho U^2}{2} + \rho gz = \text{Constant}')
    
    st.markdown("---")
    
    # Engineering Applications
    st.markdown("### 📋 Engineering Applications")
    
    col_app1, col_app2 = st.columns([1, 1])
    
    with col_app1:
        st.markdown("""
        #### Flow Measurement
        
        **📏 Venturi Meter**
        - Measures flow rate from pressure difference
        - Low energy loss, high accuracy
        - Used in water and gas pipelines
        
        **📏 Orifice Plate**
        - Simpler than Venturi, lower cost
        - Higher pressure loss
        - Common in industrial processes
        
        **📏 Pitot Tube**
        - Measures local velocity
        - Used in aircraft (airspeed indicator)
        - Stagnation pressure vs static pressure
        """)
        
    with col_app2:
        st.markdown("""
        #### Other Applications
        
        **✈️ Aircraft Wings (Lift)**
        - Air flows faster over curved top surface
        - Lower pressure above → upward lift force
        
        **⛽ Carburetors**
        - Venturi effect draws fuel into airstream
        - Mixing of air and fuel
        
        **🚿 Aspirators & Atomizers**
        - Low pressure region draws in secondary fluid
        - Used in spray bottles, lab equipment
        
        **🏗️ Building Aerodynamics**
        - Wind acceleration between buildings
        - Pressure differences on structures
        """)
    
    st.info("""
    **The Venturi Effect in Action:**
    
    When fluid flows through a constriction:
    1. **Continuity**: Area decreases → Velocity increases
    2. **Bernoulli**: Velocity increases → Pressure decreases
    
    This pressure drop is used in Venturi meters, carburetors, aspirators, and even explains 
    how airplane wings generate lift!
    """)
    
    st.success("""
    **Key Equations Summary:**
    
    - **Continuity**: A₁U₁ = A₂U₂ (mass conservation)
    - **Bernoulli**: p/ρg + U²/2g + z = Total Head (energy conservation)
    - **Velocity from Continuity**: U₂ = U₁(A₁/A₂) = U₁(D₁/D₂)²
    - **Mass Flow Rate**: ṁ = ρAU = ρQ
    """)

# =====================================================
# TAB 5: TYPES OF FLOW
# =====================================================
with main_tab5:
    st.markdown("<h2 style='text-align: center;'>🔀 Types of Flow</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 16px;'>Understanding the different classifications of fluid flow and their characteristics.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Interactive Visualization Section
    st.markdown("### 🎯 Interactive Flow Visualization")
    
    col_flow1, col_flow2 = st.columns([2, 3])
    
    with col_flow1:
        st.subheader("🔬 Flow Classification")
        
        # Flow type selection
        flow_classification = st.selectbox(
            "Select Flow Classification to Explore:",
            ("Steady vs Unsteady", "Uniform vs Non-uniform", "Laminar vs Turbulent", "1D vs 2D vs 3D"),
            key="flow_type_selector"
        )
        
        if flow_classification == "Steady vs Unsteady":
            flow_mode = st.radio("Select Flow Type:", ["Steady Flow", "Unsteady Flow"], key="steady_radio")
            
            st.markdown("---")
            if flow_mode == "Steady Flow":
                st.success("""
                **Steady Flow**: Properties at any point do NOT change with time.
                
                Mathematically: ∂(property)/∂t = 0
                
                **Examples:**
                - Water from a tap at constant opening
                - Flow in pipes at constant pump speed
                - River flow (approximately)
                """)
            else:
                st.warning("""
                **Unsteady Flow**: Properties at a point CHANGE with time.
                
                Mathematically: ∂(property)/∂t ≠ 0
                
                **Examples:**
                - Filling/draining a tank
                - Pump startup/shutdown
                - Tidal flows
                - Pulsating blood flow
                """)
                
        elif flow_classification == "Uniform vs Non-uniform":
            flow_mode = st.radio("Select Flow Type:", ["Uniform Flow", "Non-uniform Flow"], key="uniform_radio")
            
            st.markdown("---")
            if flow_mode == "Uniform Flow":
                st.success("""
                **Uniform Flow**: Properties do NOT change with position at a given time.
                
                Mathematically: ∂(property)/∂s = 0
                
                **Examples:**
                - Flow in a constant-diameter pipe (fully developed)
                - Wide river with constant cross-section
                """)
            else:
                st.warning("""
                **Non-uniform Flow**: Properties CHANGE with position.
                
                Mathematically: ∂(property)/∂s ≠ 0
                
                **Examples:**
                - Flow through a nozzle or diffuser
                - Flow around obstacles
                - River with varying width/depth
                """)
                
        elif flow_classification == "Laminar vs Turbulent":
            Re = st.slider("Reynolds Number (Re)", 100, 10000, 2000, 100, key="Re_slider")
            
            st.markdown("---")
            if Re < 2300:
                flow_mode = "Laminar"
                st.success(f"""
                **Laminar Flow** (Re = {Re} < 2300)
                
                - Smooth, orderly fluid motion
                - Fluid moves in parallel layers
                - Viscous forces dominate
                - Predictable behavior
                """)
            elif Re > 4000:
                flow_mode = "Turbulent"
                st.error(f"""
                **Turbulent Flow** (Re = {Re} > 4000)
                
                - Chaotic, irregular motion
                - Eddies and vortices present
                - Inertial forces dominate
                - Enhanced mixing
                """)
            else:
                flow_mode = "Transitional"
                st.warning(f"""
                **Transitional Flow** (Re = {Re})
                
                2300 < Re < 4000
                
                - Intermittent turbulent bursts
                - Unpredictable behavior
                - Sensitive to disturbances
                """)
        else:  # 1D vs 2D vs 3D
            flow_mode = st.radio("Select Flow Dimension:", ["1D Flow", "2D Flow", "3D Flow"], key="dim_radio")
            
            st.markdown("---")
            if flow_mode == "1D Flow":
                st.success("""
                **One-Dimensional Flow**
                
                Properties vary in ONE direction only.
                
                u = u(x), v = 0, w = 0
                
                **Examples:**
                - Fully developed pipe flow (average velocity)
                - Flow in long channels
                """)
            elif flow_mode == "2D Flow":
                st.info("""
                **Two-Dimensional Flow**
                
                Properties vary in TWO directions.
                
                u = u(x,y), v = v(x,y), w = 0
                
                **Examples:**
                - Flow over a long cylinder
                - Flow between parallel plates
                - Wind over a building (plan view)
                """)
            else:
                st.warning("""
                **Three-Dimensional Flow**
                
                Properties vary in ALL directions.
                
                u = u(x,y,z), v = v(x,y,z), w = w(x,y,z)
                
                **Examples:**
                - Flow around a sphere
                - Flow in complex geometries
                - Atmospheric flows
                """)
    
    with col_flow2:
        st.subheader("🖼️ Visualization")
        
        fig_flow = go.Figure()
        
        if flow_classification == "Steady vs Unsteady":
            # Create pipe visualization with streamlines
            if flow_mode == "Steady Flow":
                # Steady flow - parallel streamlines
                for y_pos in np.linspace(0.2, 0.8, 5):
                    x_line = np.linspace(0, 10, 50)
                    y_line = np.ones_like(x_line) * y_pos
                    fig_flow.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines',
                                                  line=dict(color='blue', width=2), showlegend=False))
                    # Add arrows
                    for x_arr in [2, 5, 8]:
                        fig_flow.add_annotation(x=x_arr+0.3, y=y_pos, ax=x_arr, ay=y_pos,
                                               showarrow=True, arrowhead=2, arrowsize=1.5,
                                               arrowwidth=2, arrowcolor='blue')
                
                fig_flow.add_annotation(x=5, y=0.95, text="<b>Steady Flow: Constant velocity at each point</b>",
                                       showarrow=False, font=dict(size=14))
            else:
                # Unsteady flow - varying streamlines with time indication
                times = [0.3, 0.5, 0.7]
                colors = ['lightblue', 'blue', 'darkblue']
                for i, (t, color) in enumerate(zip(times, colors)):
                    for y_pos in np.linspace(0.2, 0.8, 4):
                        x_line = np.linspace(0, 10, 50)
                        amplitude = 0.05 * (i + 1)
                        y_line = y_pos + amplitude * np.sin(x_line * 2 + i)
                        fig_flow.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines',
                                                      line=dict(color=color, width=2), 
                                                      name=f't = {i+1}s', showlegend=(y_pos == 0.5)))
                
                fig_flow.add_annotation(x=5, y=0.95, text="<b>Unsteady Flow: Velocity changes with time</b>",
                                       showarrow=False, font=dict(size=14))
        
        elif flow_classification == "Uniform vs Non-uniform":
            if flow_mode == "Uniform Flow":
                # Uniform pipe
                fig_flow.add_shape(type="rect", x0=0, y0=0.2, x1=10, y1=0.8,
                                  fillcolor="rgba(200,220,255,0.3)", line=dict(color="black", width=2))
                
                for y_pos in np.linspace(0.3, 0.7, 4):
                    for x_arr in [1, 3, 5, 7, 9]:
                        fig_flow.add_annotation(x=x_arr+0.5, y=y_pos, ax=x_arr, ay=y_pos,
                                               showarrow=True, arrowhead=2, arrowsize=1.5,
                                               arrowwidth=2, arrowcolor='blue')
                
                fig_flow.add_annotation(x=5, y=0.95, text="<b>Uniform: Same velocity everywhere</b>",
                                       showarrow=False, font=dict(size=14))
            else:
                # Converging pipe (non-uniform)
                # Draw converging section
                x_pipe = [0, 4, 6, 10, 10, 6, 4, 0, 0]
                y_pipe = [0.2, 0.2, 0.35, 0.35, 0.65, 0.65, 0.8, 0.8, 0.2]
                fig_flow.add_trace(go.Scatter(x=x_pipe, y=y_pipe, fill="toself",
                                             fillcolor="rgba(200,220,255,0.3)", 
                                             line=dict(color="black", width=2), showlegend=False))
                
                # Arrows - longer in narrow section
                for x_arr, length in [(1, 0.3), (3, 0.35), (5, 0.5), (7, 0.6), (9, 0.6)]:
                    y_center = 0.5
                    fig_flow.add_annotation(x=x_arr+length, y=y_center, ax=x_arr, ay=y_center,
                                           showarrow=True, arrowhead=2, arrowsize=1.5,
                                           arrowwidth=2, arrowcolor='blue')
                
                fig_flow.add_annotation(x=5, y=0.95, text="<b>Non-uniform: Velocity changes with position</b>",
                                       showarrow=False, font=dict(size=14))
        
        elif flow_classification == "Laminar vs Turbulent":
            # Create pipe
            fig_flow.add_shape(type="rect", x0=0, y0=0.1, x1=10, y1=0.9,
                              fillcolor="rgba(200,220,255,0.3)", line=dict(color="black", width=2))
            
            if flow_mode == "Laminar":
                # Smooth parallel streamlines
                for y_pos in np.linspace(0.2, 0.8, 7):
                    x_line = np.linspace(0, 10, 100)
                    y_line = np.ones_like(x_line) * y_pos
                    fig_flow.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines',
                                                  line=dict(color='blue', width=1.5), showlegend=False))
                
                fig_flow.add_annotation(x=5, y=0.95, text="<b>Laminar: Smooth, parallel layers</b>",
                                       showarrow=False, font=dict(size=14, color="green"))
            elif flow_mode == "Turbulent":
                # Chaotic streamlines
                np.random.seed(42)
                for y_start in np.linspace(0.2, 0.8, 6):
                    x_line = np.linspace(0, 10, 100)
                    y_line = y_start + 0.1 * np.cumsum(np.random.randn(100)) / 15
                    y_line = np.clip(y_line, 0.15, 0.85)
                    fig_flow.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines',
                                                  line=dict(color='red', width=1), showlegend=False))
                
                fig_flow.add_annotation(x=5, y=0.95, text="<b>Turbulent: Chaotic, irregular motion</b>",
                                       showarrow=False, font=dict(size=14, color="red"))
            else:
                # Transitional - mix of both
                np.random.seed(42)
                for i, y_start in enumerate(np.linspace(0.2, 0.8, 6)):
                    x_line = np.linspace(0, 10, 100)
                    if i % 2 == 0:
                        y_line = np.ones_like(x_line) * y_start
                        color = 'blue'
                    else:
                        y_line = y_start + 0.05 * np.cumsum(np.random.randn(100)) / 15
                        y_line = np.clip(y_line, 0.15, 0.85)
                        color = 'orange'
                    fig_flow.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines',
                                                  line=dict(color=color, width=1.5), showlegend=False))
                
                fig_flow.add_annotation(x=5, y=0.95, text="<b>Transitional: Intermittent behavior</b>",
                                       showarrow=False, font=dict(size=14, color="orange"))
        
        else:  # 1D, 2D, 3D visualization
            if flow_mode == "1D Flow":
                # Simple pipe with single direction arrows
                fig_flow.add_shape(type="rect", x0=0, y0=0.3, x1=10, y1=0.7,
                                  fillcolor="rgba(200,220,255,0.3)", line=dict(color="black", width=2))
                
                for x_arr in [1, 3, 5, 7, 9]:
                    fig_flow.add_annotation(x=x_arr+0.6, y=0.5, ax=x_arr, ay=0.5,
                                           showarrow=True, arrowhead=2, arrowsize=1.5,
                                           arrowwidth=3, arrowcolor='blue')
                
                fig_flow.add_annotation(x=5, y=0.85, text="<b>1D: u = u(x) only</b>",
                                       showarrow=False, font=dict(size=14))
                fig_flow.add_annotation(x=5, y=0.15, text="x →",
                                       showarrow=False, font=dict(size=12))
                
            elif flow_mode == "2D Flow":
                # Flow over obstacle showing 2D velocity field
                theta = np.linspace(0, np.pi, 30)
                x_cyl = 5 + 0.8 * np.cos(theta)
                y_cyl = 0.5 + 0.8 * np.sin(theta)
                fig_flow.add_trace(go.Scatter(x=x_cyl, y=y_cyl, fill="toself",
                                             fillcolor="gray", line=dict(color="black", width=2),
                                             showlegend=False))
                
                # Streamlines around cylinder
                for y_start in [0.2, 0.35, 0.65, 0.8]:
                    x_line = np.linspace(0, 10, 50)
                    if y_start < 0.5:
                        y_line = y_start - 0.15 * np.exp(-((x_line - 5)**2) / 2)
                    else:
                        y_line = y_start + 0.15 * np.exp(-((x_line - 5)**2) / 2)
                    fig_flow.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines',
                                                  line=dict(color='blue', width=1.5), showlegend=False))
                
                fig_flow.add_annotation(x=5, y=0.95, text="<b>2D: u = u(x,y), v = v(x,y)</b>",
                                       showarrow=False, font=dict(size=14))
                
            else:  # 3D
                # Show coordinate system and indicate 3D nature
                fig_flow.add_trace(go.Scatter(x=[1, 9], y=[0.5, 0.5], mode='lines+markers',
                                             line=dict(color='red', width=3), name='x', showlegend=True))
                fig_flow.add_trace(go.Scatter(x=[5, 5], y=[0.1, 0.9], mode='lines+markers',
                                             line=dict(color='green', width=3), name='y', showlegend=True))
                # Z direction indicated by circles (coming out of page)
                for x, y in [(3, 0.3), (7, 0.7), (5, 0.5)]:
                    fig_flow.add_trace(go.Scatter(x=[x], y=[y], mode='markers',
                                                  marker=dict(size=20, color='blue', 
                                                             symbol='circle-open', line=dict(width=3)),
                                                  showlegend=False))
                    fig_flow.add_trace(go.Scatter(x=[x], y=[y], mode='markers',
                                                  marker=dict(size=5, color='blue'),
                                                  showlegend=False))
                
                fig_flow.add_annotation(x=5, y=0.95, text="<b>3D: u, v, w all vary with x, y, z</b>",
                                       showarrow=False, font=dict(size=14))
                fig_flow.add_annotation(x=5.3, y=0.5, text="z (out)", showarrow=False, font=dict(size=10, color='blue'))
        
        fig_flow.update_layout(
            xaxis=dict(range=[0, 10], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, 1], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
            height=400,
            margin=dict(t=20, b=20, l=20, r=20),
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_flow, use_container_width=True)
    
    st.markdown("---")
    
    # Theory Section
    st.markdown("### 📚 Theory & Concepts")
    
    col_theory1, col_theory2 = st.columns(2)
    
    with col_theory1:
        st.markdown("""
        #### Classification Summary
        
        | Classification | Criterion | Types |
        |---------------|-----------|-------|
        | **Time Dependence** | ∂/∂t | Steady / Unsteady |
        | **Spatial Variation** | ∂/∂s | Uniform / Non-uniform |
        | **Flow Regime** | Reynolds Number | Laminar / Turbulent |
        | **Dimensionality** | Velocity components | 1D / 2D / 3D |
        | **Compressibility** | Mach Number | Incompressible / Compressible |
        
        #### Reynolds Number
        """)
        
        st.latex(r'Re = \frac{\rho U L}{\mu} = \frac{U L}{\nu} = \frac{\text{Inertial Forces}}{\text{Viscous Forces}}')
        
        st.markdown("""
        **Critical Values (pipe flow):**
        - Re < 2300: Laminar
        - 2300 < Re < 4000: Transitional
        - Re > 4000: Turbulent
        """)
    
    with col_theory2:
        st.markdown("""
        #### Streamlines, Pathlines & Streaklines
        
        **Streamline**: Line tangent to velocity vector at an instant
        - Snapshot of flow field
        - No flow crosses a streamline
        
        **Pathline**: Path traced by a single fluid particle over time
        - Lagrangian description
        - Like tracking a leaf in a stream
        
        **Streakline**: Line connecting all particles that passed through a point
        - Like dye injection
        - What we see in flow visualization
        
        > **For steady flow**: All three are identical!
        """)
    
    st.info("""
    **Practical Implications:**
    
    - **Steady vs Unsteady**: Determines if time derivatives can be neglected in governing equations
    - **Uniform vs Non-uniform**: Affects pressure and velocity distribution calculations
    - **Laminar vs Turbulent**: Completely changes friction factor correlations and mixing behavior
    - **Dimensionality**: Determines complexity of analysis (1D is simplest, 3D most complex)
    """)

# =====================================================
# TAB 6: CONTINUUM ASSUMPTION
# =====================================================
with main_tab6:
    st.markdown("<h2 style='text-align: center;'>🔬 The Continuum Assumption</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 16px;'>Understanding when we can treat fluids as continuous media rather than discrete molecules.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Interactive Section
    st.markdown("### 🎯 Interactive Exploration")
    
    col_cont1, col_cont2 = st.columns([2, 3])
    
    with col_cont1:
        st.subheader("🔬 Parameters")
        
        st.markdown("**Select Application:**")
        application = st.selectbox(
            "Choose a scenario:",
            ("Air at Sea Level", "Air at 30 km Altitude", "Vacuum Chamber", "Microfluidic Channel", "Blood in Capillary", "Custom"),
            key="continuum_app"
        )
        
        CONTINUUM_SCENARIOS = {
            "Air at Sea Level":      {'L': 0.01, 'lambda': 6.8e-8, 'desc': 'Normal atmospheric conditions'},
            "Air at 30 km Altitude": {'L': 0.01, 'lambda': 1e-5, 'desc': 'High altitude, low pressure'},
            "Vacuum Chamber":        {'L': 0.01, 'lambda': 1e-3, 'desc': 'Low pressure vacuum system'},
            "Microfluidic Channel":  {'L': 10e-6, 'lambda': 6.8e-8, 'desc': '10 μm channel width'},
            "Blood in Capillary":    {'L': 8e-6, 'lambda': 1e-9, 'desc': '8 μm capillary diameter'},
        }
        
        if application == "Custom":
            L = st.number_input("Characteristic Length L (m)", value=0.01, format="%.2e", key="cont_L")
            lambda_mfp = st.number_input("Mean Free Path λ (m)", value=6.8e-8, format="%.2e", key="cont_lambda")
            desc = "Custom configuration"
        else:
            scenario = CONTINUUM_SCENARIOS[application]
            L = scenario['L']
            lambda_mfp = scenario['lambda']
            desc = scenario['desc']
            
            st.info(f"**{application}**: {desc}")
            st.markdown(f"**Characteristic Length (L):** `{L:.2e}` m")
            st.markdown(f"**Mean Free Path (λ):** `{lambda_mfp:.2e}` m")
        
        # Calculate Knudsen number
        Kn = lambda_mfp / L
        
        st.markdown("---")
        st.markdown("### 📊 Results")
        
        st.metric("Knudsen Number (Kn)", f"{Kn:.2e}")
        
        # Regime classification
        if Kn < 0.001:
            regime = "Continuum"
            color = "green"
            st.success(f"""
            ✓ **{regime} Flow** (Kn < 0.001)
            
            Navier-Stokes equations valid.
            Standard fluid mechanics applies.
            """)
        elif Kn < 0.1:
            regime = "Slip Flow"
            color = "yellow"
            st.warning(f"""
            ⚠ **{regime}** (0.001 < Kn < 0.1)
            
            Navier-Stokes with slip boundary conditions.
            Velocity slip at walls.
            """)
        elif Kn < 10:
            regime = "Transition"
            color = "orange"
            st.warning(f"""
            ⚠ **{regime} Regime** (0.1 < Kn < 10)
            
            Neither continuum nor free molecular.
            Requires kinetic theory or DSMC.
            """)
        else:
            regime = "Free Molecular"
            color = "red"
            st.error(f"""
            ✗ **{regime} Flow** (Kn > 10)
            
            Continuum assumption breaks down.
            Molecule-surface interactions dominate.
            """)
    
    with col_cont2:
        st.subheader("🖼️ Visualization")
        
        # Create visualization showing molecular vs continuum view
        fig_cont = make_subplots(rows=1, cols=2, subplot_titles=("Molecular View", "Continuum View"))
        
        # Left plot: Molecular view
        np.random.seed(42)
        n_molecules = 100
        mol_x = np.random.uniform(0, 10, n_molecules)
        mol_y = np.random.uniform(0, 10, n_molecules)
        
        fig_cont.add_trace(go.Scatter(
            x=mol_x, y=mol_y, mode='markers',
            marker=dict(size=8, color='blue', opacity=0.6),
            name='Molecules'
        ), row=1, col=1)
        
        # Add sample volume box
        fig_cont.add_shape(type="rect", x0=3, y0=3, x1=7, y1=7,
                         line=dict(color="red", width=2, dash="dash"),
                         row=1, col=1)
        fig_cont.add_annotation(x=5, y=7.5, text="Sample Volume δV", showarrow=False,
                               font=dict(color="red"), row=1, col=1)
        
        # Right plot: Continuum view - smooth field
        x_grid = np.linspace(0, 10, 20)
        y_grid = np.linspace(0, 10, 20)
        X, Y = np.meshgrid(x_grid, y_grid)
        
        # Smooth density field
        rho = 1 + 0.2 * np.sin(X/3) * np.cos(Y/3)
        
        fig_cont.add_trace(go.Contour(
            x=x_grid, y=y_grid, z=rho,
            colorscale='Blues', showscale=False,
            contours=dict(showlines=False),
            name='Density Field'
        ), row=1, col=2)
        
        fig_cont.update_layout(height=400, showlegend=False)
        fig_cont.update_xaxes(showticklabels=False, showgrid=False)
        fig_cont.update_yaxes(showticklabels=False, showgrid=False)
        
        st.plotly_chart(fig_cont, use_container_width=True)
        
        # Knudsen number scale
        st.markdown("#### Knudsen Number Scale")
        
        fig_kn = go.Figure()
        
        # Create scale bar
        kn_ranges = [
            (0, 0.25, "Continuum", "green"),
            (0.25, 0.5, "Slip Flow", "yellow"),
            (0.5, 0.75, "Transition", "orange"),
            (0.75, 1.0, "Free Molecular", "red")
        ]
        
        for x0, x1, label, col in kn_ranges:
            fig_kn.add_shape(type="rect", x0=x0, y0=0, x1=x1, y1=1,
                           fillcolor=col, opacity=0.6, line_width=0)
            fig_kn.add_annotation(x=(x0+x1)/2, y=0.5, text=label, showarrow=False,
                                 font=dict(size=10, color="black"))
        
        # Mark current Kn position
        if Kn < 0.001:
            kn_pos = Kn / 0.001 * 0.25
        elif Kn < 0.1:
            kn_pos = 0.25 + (np.log10(Kn) - np.log10(0.001)) / (np.log10(0.1) - np.log10(0.001)) * 0.25
        elif Kn < 10:
            kn_pos = 0.5 + (np.log10(Kn) - np.log10(0.1)) / (np.log10(10) - np.log10(0.1)) * 0.25
        else:
            kn_pos = min(0.95, 0.75 + 0.25 * min(1, (Kn - 10) / 100))
        
        fig_kn.add_trace(go.Scatter(x=[kn_pos], y=[0.5], mode='markers',
                                    marker=dict(size=20, color='black', symbol='triangle-down'),
                                    name=f'Kn = {Kn:.2e}'))
        
        fig_kn.update_layout(
            height=100,
            xaxis=dict(range=[0, 1], showticklabels=False, showgrid=False),
            yaxis=dict(range=[0, 1], showticklabels=False, showgrid=False),
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False
        )
        
        st.plotly_chart(fig_kn, use_container_width=True)
        st.caption(f"Current position: Kn = {Kn:.2e} → **{regime}**")
    
    st.markdown("---")
    
    # Theory Section
    st.markdown("### 📚 Theory & Concepts")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("""
        #### What is the Continuum Assumption?
        
        We treat a fluid as a **continuous medium** rather than discrete molecules when:
        - The sample volume contains enough molecules for statistical averaging
        - Molecular fluctuations are negligible compared to bulk properties
        
        #### Knudsen Number Definition
        """)
        
        st.latex(r'Kn = \frac{\lambda}{L}')
        
        st.markdown("""
        Where:
        - **λ** = Mean free path (average distance between molecular collisions)
        - **L** = Characteristic length of the flow (pipe diameter, channel width, etc.)
        
        #### Mean Free Path
        """)
        
        st.latex(r'\lambda = \frac{k_B T}{\sqrt{2} \pi d^2 p}')
        
        st.markdown("""
        Where:
        - k_B = Boltzmann constant
        - T = Temperature
        - d = Molecular diameter
        - p = Pressure
        """)
    
    with col_t2:
        st.markdown("""
        #### Flow Regimes
        
        | Kn Range | Regime | Analysis Method |
        |----------|--------|-----------------|
        | < 0.001 | **Continuum** | Navier-Stokes equations |
        | 0.001 - 0.1 | **Slip Flow** | N-S with slip BC |
        | 0.1 - 10 | **Transition** | DSMC, Kinetic theory |
        | > 10 | **Free Molecular** | Molecular dynamics |
        
        #### Typical Mean Free Paths
        
        | Condition | λ (approximate) |
        |-----------|-----------------|
        | Air at STP | 68 nm |
        | Air at 100 km | 0.1 m |
        | Water | 0.3 nm |
        | Vacuum (10⁻⁶ Pa) | 60 m |
        
        #### Why It Matters
        
        - **Microfluidics**: Small L → larger Kn → slip effects
        - **High altitude**: Low pressure → larger λ → rarefied flow
        - **Vacuum systems**: Very large λ → molecular flow
        """)
    
    st.info("""
    **Key Insight:** The continuum assumption allows us to define fluid properties like density, velocity, and pressure 
    at a "point" — which is actually a small volume containing many molecules, but small compared to the system size.
    
    Without this assumption, we would need to track individual molecules — computationally impossible for most engineering applications!
    """)

# =====================================================
# TAB 7: CONTINUITY EQUATION
# =====================================================
with main_tab7:
    st.markdown("<h2 style='text-align: center;'>⚖️ Continuity Equation (Conservation of Mass)</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 16px;'>Mass cannot be created or destroyed - explore how this principle governs fluid flow.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Interactive Section
    st.markdown("### 🎯 Interactive Simulation")
    
    col_ce1, col_ce2 = st.columns([2, 3])
    
    with col_ce1:
        st.subheader("🔬 Parameters")
        
        st.markdown("**Pipe Configuration**")
        
        # Inlet conditions
        D1 = st.slider("Inlet Diameter D₁ (cm)", 5, 30, 20, 1, key="ce_D1")
        U1 = st.slider("Inlet Velocity U₁ (m/s)", 0.5, 10.0, 2.0, 0.1, key="ce_U1")
        
        st.markdown("---")
        
        # Outlet conditions
        D2 = st.slider("Outlet Diameter D₂ (cm)", 2, 25, 10, 1, key="ce_D2")
        
        # Fluid properties
        st.markdown("**Fluid Properties**")
        fluid_type = st.selectbox("Fluid:", ["Water (incompressible)", "Air (assume incompressible)"], key="ce_fluid")
        
        if fluid_type == "Water (incompressible)":
            rho = 1000
        else:
            rho = 1.2
        
        # Calculations
        D1_m = D1 / 100
        D2_m = D2 / 100
        
        A1 = np.pi * (D1_m/2)**2
        A2 = np.pi * (D2_m/2)**2
        
        # From continuity: A1*U1 = A2*U2
        U2 = U1 * A1 / A2
        
        # Volume flow rate
        Q = A1 * U1  # m³/s
        Q_lpm = Q * 60000  # liters per minute
        
        # Mass flow rate
        m_dot = rho * Q  # kg/s
        
        st.markdown("---")
        st.markdown("### 📊 Results")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("Inlet Area A₁", f"{A1*10000:.2f} cm²")
            st.metric("Inlet Velocity U₁", f"{U1:.2f} m/s")
        with col_r2:
            st.metric("Outlet Area A₂", f"{A2*10000:.2f} cm²")
            st.metric("Outlet Velocity U₂", f"{U2:.2f} m/s")
        
        st.markdown("---")
        
        st.metric("Volume Flow Rate Q", f"{Q*1000:.3f} L/s ({Q_lpm:.1f} L/min)")
        st.metric("Mass Flow Rate ṁ", f"{m_dot:.3f} kg/s")
        
        # Area ratio effect
        area_ratio = A1 / A2
        st.info(f"""
        **Area Ratio (A₁/A₂)**: {area_ratio:.2f}
        
        The outlet velocity is **{area_ratio:.2f}x** the inlet velocity!
        """)
        
        if D2 < D1:
            st.success("✓ **Converging pipe**: Velocity increases, pressure decreases")
        elif D2 > D1:
            st.warning("⚠ **Diverging pipe**: Velocity decreases, pressure increases")
        else:
            st.info("= **Constant diameter**: Velocity remains the same")
    
    with col_ce2:
        st.subheader("🖼️ Visualization")
        
        fig_ce = go.Figure()
        
        # Draw converging/diverging pipe
        pipe_length = 10
        transition_start = 3
        transition_end = 7
        
        # Scale diameters for visualization
        h1 = D1 / 30 * 2  # Scale to max height of 2
        h2 = D2 / 30 * 2
        
        # Upper pipe wall
        x_upper = [0, transition_start, transition_end, pipe_length]
        y_upper = [h1/2, h1/2, h2/2, h2/2]
        
        # Lower pipe wall
        x_lower = [0, transition_start, transition_end, pipe_length]
        y_lower = [-h1/2, -h1/2, -h2/2, -h2/2]
        
        # Fill pipe
        fig_ce.add_trace(go.Scatter(
            x=x_upper + x_lower[::-1] + [x_upper[0]],
            y=y_upper + y_lower[::-1] + [y_upper[0]],
            fill="toself",
            fillcolor="rgba(200, 220, 255, 0.4)",
            line=dict(color="black", width=2),
            showlegend=False
        ))
        
        # Flow arrows - size proportional to velocity
        arrow_positions = [1, 5, 9]
        arrow_heights = [0, 0, 0]
        
        for i, x_pos in enumerate(arrow_positions):
            if x_pos < transition_start:
                vel = U1
                arrow_length = 0.8
            elif x_pos > transition_end:
                vel = U2
                arrow_length = 0.8 * (U2/U1)
            else:
                # In transition
                frac = (x_pos - transition_start) / (transition_end - transition_start)
                vel = U1 + frac * (U2 - U1)
                arrow_length = 0.8 * (vel/U1)
            
            # Scale arrow length
            arrow_length = min(1.5, max(0.3, arrow_length))
            
            fig_ce.add_annotation(
                x=x_pos + arrow_length, y=0,
                ax=x_pos, ay=0,
                showarrow=True, arrowhead=2, arrowsize=1.5,
                arrowwidth=3, arrowcolor='blue'
            )
            
            # Velocity label
            fig_ce.add_annotation(
                x=x_pos + arrow_length/2, y=-0.4,
                text=f"U={vel:.1f}",
                showarrow=False, font=dict(size=10, color='blue')
            )
        
        # Dimension labels
        fig_ce.add_annotation(x=0.5, y=h1/2 + 0.2, text=f"D₁={D1}cm", showarrow=False, font=dict(size=12))
        fig_ce.add_annotation(x=9.5, y=h2/2 + 0.2, text=f"D₂={D2}cm", showarrow=False, font=dict(size=12))
        
        # Section markers
        fig_ce.add_shape(type="line", x0=1, y0=-h1/2-0.3, x1=1, y1=h1/2+0.3,
                        line=dict(color="red", width=2, dash="dash"))
        fig_ce.add_annotation(x=1, y=h1/2+0.5, text="Section 1", showarrow=False, font=dict(color="red"))
        
        fig_ce.add_shape(type="line", x0=9, y0=-h2/2-0.3, x1=9, y1=h2/2+0.3,
                        line=dict(color="red", width=2, dash="dash"))
        fig_ce.add_annotation(x=9, y=h2/2+0.5, text="Section 2", showarrow=False, font=dict(color="red"))
        
        # Flow rate indicator
        fig_ce.add_annotation(
            x=5, y=-1.5,
            text=f"<b>Q = A₁U₁ = A₂U₂ = {Q*1000:.3f} L/s (constant)</b>",
            showarrow=False, font=dict(size=14, color="green"),
            bgcolor="rgba(200, 255, 200, 0.8)",
            bordercolor="green", borderwidth=2, borderpad=5
        )
        
        fig_ce.update_layout(
            xaxis=dict(range=[-0.5, 10.5], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[-2, 2], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
            height=350,
            margin=dict(t=20, b=20, l=20, r=20),
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_ce, use_container_width=True)
        
        # Show equation verification
        st.markdown("#### ✓ Verification: Conservation of Mass")
        
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            st.markdown("**Inlet (1)**")
            st.latex(rf'A_1 U_1 = {A1:.6f} \times {U1:.2f}')
            st.latex(rf'= {A1*U1:.6f} \text{{ m³/s}}')
        with col_v2:
            st.markdown("**Equals**")
            st.markdown("")
            st.markdown("<h1 style='text-align: center;'>=</h1>", unsafe_allow_html=True)
        with col_v3:
            st.markdown("**Outlet (2)**")
            st.latex(rf'A_2 U_2 = {A2:.6f} \times {U2:.2f}')
            st.latex(rf'= {A2*U2:.6f} \text{{ m³/s}}')
    
    st.markdown("---")
    
    # Theory Section
    st.markdown("### 📚 Theory & Concepts")
    
    col_th1, col_th2 = st.columns(2)
    
    with col_th1:
        st.markdown("""
        #### The Continuity Equation
        
        **Integral Form** (for a control volume):
        """)
        
        st.latex(r'\frac{\partial}{\partial t} \int_{CV} \rho \, dV + \int_{CS} \rho \mathbf{U} \cdot d\mathbf{A} = 0')
        
        st.markdown("""
        **Differential Form**:
        """)
        
        st.latex(r'\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{U}) = 0')
        
        st.markdown("""
        **For Steady, Incompressible Flow**:
        """)
        
        st.latex(r'A_1 U_1 = A_2 U_2 = Q = \text{constant}')
        
        st.markdown("""
        Or in terms of mass flow rate:
        """)
        
        st.latex(r'\dot{m} = \rho A U = \text{constant}')
    
    with col_th2:
        st.markdown("""
        #### Key Relationships
        
        **Velocity-Area Relationship**:
        """)
        
        st.latex(r'U_2 = U_1 \frac{A_1}{A_2} = U_1 \left(\frac{D_1}{D_2}\right)^2')
        
        st.markdown("""
        **For circular pipes**:
        - Area: A = πD²/4
        - Diameter ratio squared gives velocity ratio
        
        #### Implications
        
        | Geometry | Area | Velocity | Pressure* |
        |----------|------|----------|-----------|
        | Converging | ↓ | ↑ | ↓ |
        | Diverging | ↑ | ↓ | ↑ |
        | Constant | = | = | = |
        
        *From Bernoulli equation
        
        #### Multiple Inlets/Outlets
        """)
        
        st.latex(r'\sum \dot{m}_{in} = \sum \dot{m}_{out}')
    
    st.success("""
    **Key Takeaways:**
    
    1. Mass is conserved — what flows in must flow out (steady state)
    2. Volume flow rate Q = AU is constant for incompressible flow
    3. Smaller area → Higher velocity (and vice versa)
    4. This principle is fundamental to understanding Venturi meters, nozzles, diffusers, and pipe networks
    """)

# =====================================================
# TAB 8: BOUNDARY LAYER CONCEPT
# =====================================================
with main_tab8:
    st.markdown("<h2 style='text-align: center;'>📐 Boundary Layer Concept</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 16px;'>Understanding how viscous effects are confined to a thin region near solid surfaces.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Interactive Section
    st.markdown("### 🎯 Interactive Simulation")
    
    col_bl1, col_bl2 = st.columns([2, 3])
    
    with col_bl1:
        st.subheader("🔬 Parameters")
        
        st.markdown("**Flow Conditions**")
        U_inf = st.slider("Freestream Velocity U∞ (m/s)", 1.0, 50.0, 10.0, 0.5, key="bl_U")
        
        st.markdown("**Fluid Selection**")
        bl_fluid = st.selectbox("Choose fluid:", 
                                ["Air (20°C)", "Water (20°C)", "Oil (SAE 30)", "Custom"],
                                key="bl_fluid")
        
        BL_FLUIDS = {
            "Air (20°C)":    {'nu': 1.5e-5, 'rho': 1.2},
            "Water (20°C)":  {'nu': 1.0e-6, 'rho': 998},
            "Oil (SAE 30)":  {'nu': 3.0e-4, 'rho': 880},
        }
        
        if bl_fluid == "Custom":
            nu_bl = st.number_input("Kinematic Viscosity ν (m²/s)", value=1.5e-5, format="%.2e", key="bl_nu")
            rho_bl = st.number_input("Density ρ (kg/m³)", value=1.2, key="bl_rho")
        else:
            nu_bl = BL_FLUIDS[bl_fluid]['nu']
            rho_bl = BL_FLUIDS[bl_fluid]['rho']
            st.info(f"ν = {nu_bl:.2e} m²/s, ρ = {rho_bl} kg/m³")
        
        st.markdown("**Position Along Plate**")
        x_pos = st.slider("Distance from leading edge x (m)", 0.01, 2.0, 0.5, 0.01, key="bl_x")
        
        # Calculations
        # Reynolds number at position x
        Re_x = U_inf * x_pos / nu_bl
        
        # Boundary layer thickness (Blasius solution for laminar)
        if Re_x > 0:
            delta_laminar = 5.0 * x_pos / np.sqrt(Re_x)  # Laminar BL thickness
        else:
            delta_laminar = 0
        
        # Critical Reynolds number for transition
        Re_crit = 5e5
        
        # Determine flow regime
        if Re_x < Re_crit:
            regime = "Laminar"
            delta = delta_laminar
            delta_formula = "5x/√(Re_x)"
        else:
            regime = "Turbulent"
            # Turbulent BL thickness (approximate)
            delta = 0.37 * x_pos / (Re_x ** 0.2)
            delta_formula = "0.37x/(Re_x)^0.2"
        
        st.markdown("---")
        st.markdown("### 📊 Results")
        
        st.metric("Local Reynolds Number Re_x", f"{Re_x:.2e}")
        
        if regime == "Laminar":
            st.success(f"✓ **{regime} Boundary Layer** (Re_x < 5×10⁵)")
        else:
            st.warning(f"⚠ **{regime} Boundary Layer** (Re_x > 5×10⁵)")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("BL Thickness δ", f"{delta*1000:.3f} mm")
        with col_res2:
            st.metric("δ/x ratio", f"{delta/x_pos*100:.3f}%")
        
        st.caption(f"Using: δ = {delta_formula}")
        
        # Wall shear stress (laminar)
        if regime == "Laminar" and Re_x > 0:
            tau_w = 0.332 * rho_bl * U_inf**2 / np.sqrt(Re_x)
            C_f = 0.664 / np.sqrt(Re_x)
            st.metric("Wall Shear Stress τ_w", f"{tau_w:.3f} Pa")
            st.metric("Local Skin Friction Coeff. C_f", f"{C_f:.6f}")
    
    with col_bl2:
        st.subheader("🖼️ Visualization")
        
        # Create boundary layer visualization
        fig_bl = go.Figure()
        
        # Plate surface
        fig_bl.add_shape(type="rect", x0=0, y0=-0.1, x1=10, y1=0,
                        fillcolor="gray", line=dict(color="black", width=2))
        
        # Generate boundary layer profile
        x_plate = np.linspace(0.1, 10, 100)
        
        # BL thickness along plate (scaled for visualization)
        Re_x_arr = U_inf * (x_plate * x_pos / 10) / nu_bl
        Re_x_arr = np.maximum(Re_x_arr, 1)  # Avoid division by zero
        
        # Laminar region
        delta_arr = np.where(Re_x_arr < Re_crit,
                            5.0 * (x_plate * x_pos / 10) / np.sqrt(Re_x_arr),
                            0.37 * (x_plate * x_pos / 10) / (Re_x_arr ** 0.2))
        
        # Scale for visualization
        delta_viz = delta_arr / delta_arr.max() * 2 if delta_arr.max() > 0 else delta_arr
        
        # Boundary layer edge
        fig_bl.add_trace(go.Scatter(
            x=x_plate, y=delta_viz,
            mode='lines', line=dict(color='blue', width=3),
            name='Boundary Layer Edge (δ)'
        ))
        
        # Fill boundary layer region
        fig_bl.add_trace(go.Scatter(
            x=np.concatenate([x_plate, x_plate[::-1]]),
            y=np.concatenate([delta_viz, np.zeros_like(delta_viz)]),
            fill='toself', fillcolor='rgba(100, 170, 255, 0.3)',
            line=dict(width=0), showlegend=False, name='Boundary Layer'
        ))
        
        # Freestream arrows
        for x_arr in [1, 4, 7]:
            fig_bl.add_annotation(
                x=x_arr + 1, y=2.5,
                ax=x_arr, ay=2.5,
                showarrow=True, arrowhead=2, arrowsize=1.5,
                arrowwidth=2, arrowcolor='darkblue'
            )
        fig_bl.add_annotation(x=5, y=2.8, text=f"U∞ = {U_inf} m/s", showarrow=False,
                             font=dict(size=12, color='darkblue'))
        
        # Velocity profile at selected position
        x_profile = x_pos / (2.0/10) * 10  # Scale position
        x_profile = min(9.5, max(0.5, x_profile))
        
        # Get delta at this position
        idx = int(x_profile / 10 * 99)
        delta_at_x = delta_viz[min(idx, len(delta_viz)-1)]
        
        # Draw velocity profile
        y_profile = np.linspace(0, delta_at_x * 1.2, 20)
        # Blasius-like profile
        eta = y_profile / max(delta_at_x, 0.01)
        u_profile = U_inf * np.minimum(1, 2*eta - eta**2)  # Parabolic approximation
        
        u_scaled = u_profile / U_inf * 1.5  # Scale for visualization
        
        fig_bl.add_trace(go.Scatter(
            x=x_profile + u_scaled, y=y_profile,
            mode='lines', line=dict(color='red', width=2),
            name='Velocity Profile u(y)'
        ))
        
        # Mark measurement point
        fig_bl.add_trace(go.Scatter(
            x=[x_profile], y=[0],
            mode='markers', marker=dict(size=10, color='red', symbol='triangle-up'),
            name=f'x = {x_pos} m'
        ))
        
        # Labels
        fig_bl.add_annotation(x=0.5, y=-0.3, text="Leading Edge", showarrow=False, font=dict(size=10))
        fig_bl.add_annotation(x=x_profile, y=delta_at_x + 0.3, text=f"δ = {delta*1000:.2f} mm",
                             showarrow=True, arrowhead=2, ay=delta_at_x + 0.8)
        
        # No-slip condition annotation
        fig_bl.add_annotation(x=x_profile + 0.1, y=0.1, text="u = 0 (no-slip)",
                             showarrow=False, font=dict(size=9, color='gray'))
        
        fig_bl.update_layout(
            xaxis=dict(range=[-0.5, 11], showgrid=False, zeroline=False, 
                      showticklabels=False, title="Distance along plate"),
            yaxis=dict(range=[-0.5, 3.5], showgrid=False, zeroline=False, 
                      showticklabels=False, title="Distance from surface"),
            height=400,
            margin=dict(t=20, b=40, l=20, r=20),
            plot_bgcolor='white',
            legend=dict(x=0.7, y=0.95)
        )
        
        st.plotly_chart(fig_bl, use_container_width=True)
    
    st.markdown("---")
    
    # Theory Section
    st.markdown("### 📚 Theory & Concepts")
    
    col_blt1, col_blt2 = st.columns(2)
    
    with col_blt1:
        st.markdown("""
        #### What is the Boundary Layer?
        
        A thin region near a solid surface where **viscous effects are significant**.
        
        - Outside: Flow behaves as **inviscid** (Bernoulli applies)
        - Inside: **Viscous forces** are important, velocity varies from 0 to U∞
        
        #### The No-Slip Condition
        
        At a solid surface, the fluid velocity equals the surface velocity:
        """)
        
        st.latex(r'u(y=0) = 0 \text{ (for stationary surface)}')
        
        st.markdown("""
        #### Boundary Layer Thickness δ
        
        Defined as the distance where u = 0.99 U∞
        
        **Laminar (Blasius solution)**:
        """)
        
        st.latex(r'\delta = \frac{5x}{\sqrt{Re_x}}')
        
        st.markdown("""
        **Turbulent (approximate)**:
        """)
        
        st.latex(r'\delta = \frac{0.37x}{Re_x^{0.2}}')
    
    with col_blt2:
        st.markdown("""
        #### Laminar vs Turbulent Boundary Layer
        
        | Property | Laminar | Turbulent |
        |----------|---------|-----------|
        | **Re_x range** | < 5×10⁵ | > 5×10⁵ |
        | **Profile shape** | Parabolic | Fuller |
        | **Wall shear** | Lower | Higher |
        | **Thickness growth** | ~ x^0.5 | ~ x^0.8 |
        | **Mixing** | Poor | Enhanced |
        
        #### Other Thickness Definitions
        
        **Displacement thickness δ*** (mass flow deficit):
        """)
        
        st.latex(r'\delta^* = \int_0^\infty \left(1 - \frac{u}{U_\infty}\right) dy')
        
        st.markdown("""
        **Momentum thickness θ** (momentum deficit):
        """)
        
        st.latex(r'\theta = \int_0^\infty \frac{u}{U_\infty}\left(1 - \frac{u}{U_\infty}\right) dy')
    
    st.info("""
    **Engineering Significance:**
    
    - **Drag**: Skin friction drag comes from wall shear stress in the boundary layer
    - **Heat Transfer**: Thermal boundary layer controls convective heat transfer
    - **Flow Separation**: Adverse pressure gradients can cause BL separation → increased drag, stall
    - **Design**: Aircraft wings, turbine blades, heat exchangers all require BL analysis
    """)

# =====================================================
# TAB 9: DIMENSIONAL ANALYSIS
# =====================================================
with main_tab9:
    st.markdown("<h2 style='text-align: center;'>📏 Dimensional Analysis</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 16px;'>Using dimensions to derive relationships and create dimensionless groups for scaling and similitude.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Interactive Section
    st.markdown("### 🎯 Interactive Exploration")
    
    col_da1, col_da2 = st.columns([1, 1])
    
    with col_da1:
        st.subheader("🔬 Common Dimensionless Numbers")
        
        # Calculator for dimensionless numbers
        st.markdown("**Calculate Dimensionless Numbers**")
        
        # Input parameters
        st.markdown("*Enter flow parameters:*")
        
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            U_da = st.number_input("Velocity U (m/s)", value=2.0, min_value=0.01, key="da_U")
            L_da = st.number_input("Length L (m)", value=0.1, min_value=0.001, key="da_L")
            rho_da = st.number_input("Density ρ (kg/m³)", value=1000.0, key="da_rho")
        with col_in2:
            mu_da = st.number_input("Dyn. Viscosity μ (Pa·s)", value=0.001, format="%.4f", key="da_mu")
            sigma_da = st.number_input("Surface Tension σ (N/m)", value=0.072, format="%.4f", key="da_sigma")
            g_da = st.number_input("Gravity g (m/s²)", value=9.81, key="da_g")
        
        # Calculate dimensionless numbers
        nu_da = mu_da / rho_da
        
        Re = rho_da * U_da * L_da / mu_da
        Fr = U_da / np.sqrt(g_da * L_da)
        We = rho_da * U_da**2 * L_da / sigma_da
        Eu = 101325 / (rho_da * U_da**2)  # Using atmospheric pressure as reference
        
        st.markdown("---")
        st.markdown("### 📊 Calculated Values")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.metric("Reynolds Number (Re)", f"{Re:.2e}")
            st.caption("Inertia / Viscous forces")
            
            st.metric("Froude Number (Fr)", f"{Fr:.3f}")
            st.caption("Inertia / Gravity forces")
        
        with col_res2:
            st.metric("Weber Number (We)", f"{We:.2e}")
            st.caption("Inertia / Surface tension")
            
            st.metric("Euler Number (Eu)", f"{Eu:.3f}")
            st.caption("Pressure / Inertia forces")
        
        # Interpretation
        st.markdown("---")
        st.markdown("**Flow Regime Interpretation:**")
        
        if Re < 2300:
            st.success(f"Re = {Re:.0f} → **Laminar flow** (Re < 2300)")
        elif Re < 4000:
            st.warning(f"Re = {Re:.0f} → **Transitional flow** (2300 < Re < 4000)")
        else:
            st.error(f"Re = {Re:.0f} → **Turbulent flow** (Re > 4000)")
        
        if Fr < 1:
            st.info(f"Fr = {Fr:.2f} → **Subcritical flow** (Fr < 1) - Gravity dominates")
        else:
            st.info(f"Fr = {Fr:.2f} → **Supercritical flow** (Fr > 1) - Inertia dominates")
    
    with col_da2:
        st.subheader("📋 Dimensionless Numbers Reference")
        
        # Table of common dimensionless numbers
        st.markdown("""
        | Number | Symbol | Definition | Physical Meaning |
        |--------|--------|------------|------------------|
        | **Reynolds** | Re | ρUL/μ | Inertia / Viscous |
        | **Froude** | Fr | U/√(gL) | Inertia / Gravity |
        | **Weber** | We | ρU²L/σ | Inertia / Surface tension |
        | **Euler** | Eu | Δp/(ρU²) | Pressure / Inertia |
        | **Mach** | Ma | U/c | Flow / Sound speed |
        | **Strouhal** | St | fL/U | Oscillation / Flow |
        | **Prandtl** | Pr | ν/α | Momentum / Thermal diffusivity |
        | **Nusselt** | Nu | hL/k | Convection / Conduction |
        | **Grashof** | Gr | gβΔTL³/ν² | Buoyancy / Viscous |
        """)
        
        st.markdown("---")
        st.markdown("#### 🎯 Applications by Dimensionless Number")
        
        with st.expander("Reynolds Number (Re) - Most Important!"):
            st.markdown("""
            **Used for:**
            - Predicting laminar vs turbulent flow
            - Pipe flow correlations
            - Drag coefficient correlations
            - Scale model testing
            
            **Critical Values:**
            - Pipe flow: Re_crit ≈ 2300
            - Flat plate: Re_crit ≈ 5×10⁵
            - Sphere: Re_crit ≈ 2×10⁵
            """)
        
        with st.expander("Froude Number (Fr)"):
            st.markdown("""
            **Used for:**
            - Open channel flow
            - Ship hull design
            - Spillway design
            - Wave phenomena
            
            **Critical Values:**
            - Fr < 1: Subcritical (tranquil)
            - Fr = 1: Critical
            - Fr > 1: Supercritical (rapid)
            """)
        
        with st.expander("Weber Number (We)"):
            st.markdown("""
            **Used for:**
            - Droplet formation
            - Spray dynamics
            - Bubble behavior
            - Capillary flows
            
            **When important:** We >> 1 means surface tension negligible
            """)
    
    st.markdown("---")
    
    # Buckingham Pi Theorem Section
    st.markdown("### 📚 Buckingham Pi Theorem")
    
    col_pi1, col_pi2 = st.columns(2)
    
    with col_pi1:
        st.markdown("""
        #### The Theorem
        
        If a physical problem involves **n** variables and **k** fundamental dimensions (M, L, T, θ), 
        then the problem can be described by **(n - k)** independent dimensionless groups (π groups).
        """)
        
        st.latex(r'\text{Number of } \Pi \text{ groups} = n - k')
        
        st.markdown("""
        #### Fundamental Dimensions
        
        | Dimension | Symbol | SI Unit |
        |-----------|--------|---------|
        | Mass | M | kg |
        | Length | L | m |
        | Time | T | s |
        | Temperature | θ | K |
        
        #### Example: Drag on a Sphere
        
        Variables: F_D, ρ, U, D, μ (n = 5)
        
        Dimensions: M, L, T (k = 3)
        
        π groups: 5 - 3 = **2**
        """)
    
    with col_pi2:
        st.markdown("""
        #### Procedure
        
        1. **List all variables** affecting the phenomenon
        2. **Express dimensions** of each variable in M, L, T, θ
        3. **Select k repeating variables** (must include all dimensions)
        4. **Form π groups** by combining remaining variables with repeating variables
        5. **Write the functional relationship** between π groups
        
        #### Sphere Drag Result
        """)
        
        st.latex(r'\Pi_1 = \frac{F_D}{\rho U^2 D^2} = C_D \quad \text{(Drag coefficient)}')
        
        st.latex(r'\Pi_2 = \frac{\rho U D}{\mu} = Re \quad \text{(Reynolds number)}')
        
        st.markdown("""
        **Functional relationship:**
        """)
        
        st.latex(r'C_D = f(Re)')
        
        st.markdown("""
        This tells us drag coefficient depends **only** on Reynolds number!
        """)
    
    st.markdown("---")
    
    # Similitude Section
    st.markdown("### 🔄 Similitude and Model Testing")
    
    col_sim1, col_sim2 = st.columns(2)
    
    with col_sim1:
        st.markdown("""
        #### Types of Similarity
        
        **Geometric Similarity**
        - Model and prototype have same shape
        - All length ratios equal: L_r = L_m/L_p
        
        **Kinematic Similarity**
        - Velocity ratios equal at corresponding points
        - Same flow patterns
        
        **Dynamic Similarity**
        - Force ratios equal at corresponding points
        - **Requires equal dimensionless numbers**
        """)
    
    with col_sim2:
        st.markdown("""
        #### Scaling Laws
        
        For complete dynamic similarity, match the relevant dimensionless numbers:
        
        | Application | Match This Number |
        |-------------|-------------------|
        | Pipe flow, aircraft | Reynolds (Re) |
        | Ship hulls, spillways | Froude (Fr) |
        | High-speed flow | Mach (Ma) |
        | Droplets, bubbles | Weber (We) |
        
        #### The Challenge
        
        Often **impossible to match all numbers** simultaneously!
        
        → Use **dominant phenomenon** to select which number to match
        """)
    
    st.success("""
    **Key Takeaways:**
    
    1. **Dimensional analysis** reduces the number of variables needed to describe a problem
    2. **Dimensionless numbers** allow comparison across different scales and fluids
    3. **Buckingham Pi Theorem** provides a systematic way to find dimensionless groups
    4. **Model testing** requires matching the relevant dimensionless numbers for valid scaling
    5. **Reynolds number** is the most important dimensionless number in fluid mechanics
    """)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 20px; font-size: 0.9em;'>
    <p>🎓 Developed for Chemical Engineering Students</p>
    <p>University of Surrey | School of Chemistry and Chemical Engineering</p>
</div>
""", unsafe_allow_html=True)

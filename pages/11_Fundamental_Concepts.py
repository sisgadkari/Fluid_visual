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
main_tab1, main_tab2 = st.tabs(["🍯 Viscosity", "💧 Surface Tension"])

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
    
    # SECTION 1: INTERACTIVE SIMULATION
    st.markdown("### 🎯 Interactive Simulation")
    
    col_st1, col_st2 = st.columns([2, 3])
    
    with col_st1:
        st.subheader("🔬 Parameters")
        
        # --- Preset Liquid Options ---
        st.markdown("**Select a Liquid**")
        liquid_choice = st.selectbox(
            "Choose a liquid to explore:",
            ("Water (20°C)", "Ethanol", "Mercury", "Acetone", "Glycerol", "Soap Solution", "Olive Oil", "Custom"),
            key="st_liquid_selector"
        )
        
        # Preset values: surface tension (N/m), density (kg/m³), contact angle with glass
        LIQUID_PROPERTIES = {
            "Water (20°C)":    {'gamma': 0.0728, 'rho': 998, 'theta': 20, 'color': 'rgba(100, 170, 255, 0.7)', 'description': 'High surface tension - forms droplets'},
            "Ethanol":         {'gamma': 0.022, 'rho': 789, 'theta': 0, 'color': 'rgba(200, 200, 255, 0.5)', 'description': 'Low surface tension - spreads easily'},
            "Mercury":         {'gamma': 0.485, 'rho': 13534, 'theta': 140, 'color': 'rgba(180, 180, 180, 0.9)', 'description': 'Very high surface tension - forms beads'},
            "Acetone":         {'gamma': 0.025, 'rho': 784, 'theta': 0, 'color': 'rgba(220, 220, 240, 0.4)', 'description': 'Low surface tension - evaporates quickly'},
            "Glycerol":        {'gamma': 0.064, 'rho': 1260, 'theta': 30, 'color': 'rgba(200, 200, 220, 0.7)', 'description': 'Moderate surface tension - viscous'},
            "Soap Solution":   {'gamma': 0.025, 'rho': 1000, 'theta': 10, 'color': 'rgba(150, 200, 255, 0.5)', 'description': 'Reduced surface tension - surfactant effect'},
            "Olive Oil":       {'gamma': 0.032, 'rho': 920, 'theta': 15, 'color': 'rgba(200, 180, 100, 0.6)', 'description': 'Low surface tension - spreads on water'},
        }
        
        if liquid_choice == "Custom":
            st.markdown("**Custom Liquid Properties**")
            gamma = st.slider("Surface Tension (γ) [N/m]", 0.01, 0.5, 0.072, 0.001, format="%.3f", key="st_gamma")
            rho_st = st.number_input("Density (ρ) [kg/m³]", value=1000, min_value=1, max_value=20000, key="st_rho")
            theta = st.slider("Contact Angle (θ) [degrees]", 0, 180, 20, 5, key="st_theta")
            liquid_color = 'rgba(100, 170, 255, 0.7)'
            liquid_desc = "Custom liquid"
        else:
            properties = LIQUID_PROPERTIES[liquid_choice]
            gamma = properties['gamma']
            rho_st = properties['rho']
            theta = properties['theta']
            liquid_color = properties['color']
            liquid_desc = properties['description']
            
            st.success(f"**{liquid_choice}**: {liquid_desc}")
            st.markdown(f"**Surface Tension (γ):** `{gamma}` N/m")
            st.markdown(f"**Density (ρ):** `{rho_st}` kg/m³")
            st.markdown(f"**Contact Angle (θ):** `{theta}`°")
        
        st.markdown("---")
        st.markdown("**Floating Object Parameters**")
        
        # Object selection for floating demonstration
        object_choice = st.selectbox(
            "Select object to float:",
            ("Steel Needle", "Paper Clip", "Water Strider", "Small Coin", "Razor Blade", "Custom"),
            key="st_object_selector"
        )
        
        # Object properties: mass per unit length (kg/m), width (m), density (kg/m³)
        OBJECT_PROPERTIES = {
            "Steel Needle":   {'mass_per_length': 0.0003, 'width': 0.0008, 'rho_obj': 7800, 'description': 'Classic demonstration'},
            "Paper Clip":     {'mass_per_length': 0.001, 'width': 0.001, 'rho_obj': 7800, 'description': 'Office experiment'},
            "Water Strider":  {'mass_per_length': 0.00001, 'width': 0.002, 'rho_obj': 1100, 'description': 'Nature\'s design - 6 legs'},
            "Small Coin":     {'mass_per_length': 0.025, 'width': 0.018, 'rho_obj': 8900, 'description': 'Heavy - needs high γ'},
            "Razor Blade":    {'mass_per_length': 0.002, 'width': 0.02, 'rho_obj': 7800, 'description': 'Flat and thin'},
        }
        
        if object_choice == "Custom":
            mass_per_length = st.slider("Mass per length (g/m)", 0.1, 50.0, 1.0, 0.1, key="st_mass") / 1000
            obj_width = st.slider("Object width (mm)", 0.5, 30.0, 2.0, 0.5, key="st_width") / 1000
            rho_obj = 7800
            obj_desc = "Custom object"
        else:
            obj_props = OBJECT_PROPERTIES[object_choice]
            mass_per_length = obj_props['mass_per_length']
            obj_width = obj_props['width']
            rho_obj = obj_props['rho_obj']
            obj_desc = obj_props['description']
            st.caption(f"*{obj_desc}*")
        
        # Calculate if object can float
        # Surface tension force (both sides): F_st = 2 * γ * L * cos(θ)
        # Weight per unit length: W = m/L * g
        # For floating: 2γcos(θ) ≥ (m/L)g
        
        g = 9.81
        theta_rad = np.radians(theta)
        
        # Maximum supportable weight per unit length
        max_weight_per_length = 2 * gamma * np.cos(theta_rad) if theta < 90 else 0
        actual_weight_per_length = mass_per_length * g
        
        # Safety factor (how much margin before sinking)
        if max_weight_per_length > 0:
            safety_factor = max_weight_per_length / actual_weight_per_length
        else:
            safety_factor = 0
        
        can_float = safety_factor >= 1.0
        
        st.markdown("---")
        st.markdown("**Results**")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Max Support Force", f"{max_weight_per_length*1000:.3f} mN/m")
        with col_res2:
            st.metric("Object Weight", f"{actual_weight_per_length*1000:.3f} mN/m")
        
        if can_float:
            st.success(f"✓ **FLOATS!** Safety factor: {safety_factor:.2f}x")
        else:
            st.error(f"✗ **SINKS!** Need {1/safety_factor:.1f}x more surface tension")
        
        # Surface tension comparison
        st.markdown("---")
        st.info(f"""
        **Quick Comparison:**
        - Water: 0.0728 N/m (reference)
        - Your liquid is **{gamma/0.0728:.2f}x** the surface tension of water
        """)
    
    with col_st2:
        st.subheader("🖼️ Visualization")
        
        # Create visualization tabs
        st_viz_tab1, st_viz_tab2 = st.tabs(["🪡 Floating Object", "💧 Droplet Shape"])
        
        with st_viz_tab1:
            st.markdown("#### Floating Needle / Water Strider Demonstration")
            
            # Create floating object visualization
            fig_float = go.Figure()
            
            # Container dimensions
            container_width = 10
            container_height = 6
            water_level = 3.5
            
            # Draw container
            fig_float.add_shape(type="rect", x0=0, y0=0, x1=container_width, y1=container_height,
                              fillcolor="rgba(200, 220, 255, 0.2)", line=dict(color="darkblue", width=3))
            
            # Draw liquid
            fig_float.add_shape(type="rect", x0=0.1, y0=0.1, x1=container_width-0.1, y1=water_level,
                              fillcolor=liquid_color, line_width=0)
            
            # Object dimensions for visualization
            obj_viz_width = 3
            obj_viz_height = 0.15
            obj_x_center = container_width / 2
            
            if can_float:
                # Object floats - show surface depression
                depression_depth = 0.3 * (1 - safety_factor) if safety_factor < 2 else 0.05
                depression_depth = max(0.05, min(0.4, depression_depth))
                obj_y = water_level - depression_depth
                
                # Draw depressed water surface (meniscus on both sides)
                # Left side meniscus
                meniscus_x_left = np.linspace(0.1, obj_x_center - obj_viz_width/2, 30)
                meniscus_y_left = water_level - depression_depth * np.exp(-2 * (meniscus_x_left - (obj_x_center - obj_viz_width/2))**2)
                
                # Right side meniscus
                meniscus_x_right = np.linspace(obj_x_center + obj_viz_width/2, container_width - 0.1, 30)
                meniscus_y_right = water_level - depression_depth * np.exp(-2 * (meniscus_x_right - (obj_x_center + obj_viz_width/2))**2)
                
                # Draw the curved water surface
                fig_float.add_trace(go.Scatter(
                    x=np.concatenate([meniscus_x_left, [obj_x_center - obj_viz_width/2]]),
                    y=np.concatenate([meniscus_y_left, [obj_y]]),
                    mode='lines', line=dict(color='darkblue', width=3),
                    showlegend=False
                ))
                fig_float.add_trace(go.Scatter(
                    x=np.concatenate([[obj_x_center + obj_viz_width/2], meniscus_x_right]),
                    y=np.concatenate([[obj_y], meniscus_y_right]),
                    mode='lines', line=dict(color='darkblue', width=3),
                    showlegend=False
                ))
                
                # Draw the floating object
                if object_choice == "Water Strider":
                    # Draw water strider with legs
                    body_x = [obj_x_center - 0.3, obj_x_center + 0.3, obj_x_center + 0.2, obj_x_center - 0.2]
                    body_y = [obj_y + 0.3, obj_y + 0.3, obj_y + 0.5, obj_y + 0.5]
                    fig_float.add_trace(go.Scatter(x=body_x + [body_x[0]], y=body_y + [body_y[0]],
                                                  fill='toself', fillcolor='rgba(80, 60, 40, 0.9)',
                                                  line=dict(color='black', width=2), mode='lines', showlegend=False))
                    
                    # Draw 6 legs (3 on each side)
                    leg_positions = [-1.2, 0, 1.2]
                    for lp in leg_positions:
                        # Left legs
                        fig_float.add_trace(go.Scatter(
                            x=[obj_x_center + lp*0.2, obj_x_center - 1.5 + lp*0.3],
                            y=[obj_y + 0.35, obj_y - 0.05],
                            mode='lines', line=dict(color='black', width=2), showlegend=False
                        ))
                        # Foot dimple on left
                        fig_float.add_trace(go.Scatter(
                            x=[obj_x_center - 1.5 + lp*0.3], y=[obj_y - 0.05],
                            mode='markers', marker=dict(size=6, color='black'), showlegend=False
                        ))
                        # Right legs
                        fig_float.add_trace(go.Scatter(
                            x=[obj_x_center + lp*0.2, obj_x_center + 1.5 - lp*0.3],
                            y=[obj_y + 0.35, obj_y - 0.05],
                            mode='lines', line=dict(color='black', width=2), showlegend=False
                        ))
                        # Foot dimple on right
                        fig_float.add_trace(go.Scatter(
                            x=[obj_x_center + 1.5 - lp*0.3], y=[obj_y - 0.05],
                            mode='markers', marker=dict(size=6, color='black'), showlegend=False
                        ))
                else:
                    # Draw needle/paper clip as a rectangle
                    fig_float.add_shape(type="rect",
                                       x0=obj_x_center - obj_viz_width/2, y0=obj_y,
                                       x1=obj_x_center + obj_viz_width/2, y1=obj_y + obj_viz_height,
                                       fillcolor="rgba(180, 180, 190, 0.95)",
                                       line=dict(color="black", width=2))
                
                # Force arrows showing surface tension
                arrow_length = 0.8
                arrow_y = obj_y - 0.1
                
                # Left surface tension arrow (pointing up-left)
                fig_float.add_annotation(
                    x=obj_x_center - obj_viz_width/2 - 0.3, y=arrow_y + arrow_length,
                    ax=obj_x_center - obj_viz_width/2 - 0.1, ay=arrow_y,
                    showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3,
                    arrowcolor="green"
                )
                # Right surface tension arrow (pointing up-right)
                fig_float.add_annotation(
                    x=obj_x_center + obj_viz_width/2 + 0.3, y=arrow_y + arrow_length,
                    ax=obj_x_center + obj_viz_width/2 + 0.1, ay=arrow_y,
                    showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3,
                    arrowcolor="green"
                )
                
                # Weight arrow (pointing down)
                fig_float.add_annotation(
                    x=obj_x_center, y=obj_y - 0.8,
                    ax=obj_x_center, ay=obj_y + obj_viz_height/2,
                    showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3,
                    arrowcolor="red"
                )
                
                # Labels
                fig_float.add_annotation(x=obj_x_center - obj_viz_width/2 - 0.8, y=arrow_y + arrow_length + 0.2,
                                        text="<b>F<sub>γ</sub></b>", showarrow=False, font=dict(size=14, color="green"))
                fig_float.add_annotation(x=obj_x_center + obj_viz_width/2 + 0.8, y=arrow_y + arrow_length + 0.2,
                                        text="<b>F<sub>γ</sub></b>", showarrow=False, font=dict(size=14, color="green"))
                fig_float.add_annotation(x=obj_x_center + 0.4, y=obj_y - 0.9,
                                        text="<b>W</b>", showarrow=False, font=dict(size=14, color="red"))
                
                # Status
                status_color = "rgba(0, 150, 0, 0.9)"
                status_text = f"FLOATING! (Safety factor: {safety_factor:.2f}x)"
                
            else:
                # Object sinks
                obj_y = 0.5  # At bottom
                
                # Flat water surface
                fig_float.add_shape(type="line", x0=0.1, y0=water_level, x1=container_width-0.1, y1=water_level,
                                  line=dict(color="darkblue", width=3))
                
                # Draw sunken object
                fig_float.add_shape(type="rect",
                                   x0=obj_x_center - obj_viz_width/2, y0=obj_y,
                                   x1=obj_x_center + obj_viz_width/2, y1=obj_y + obj_viz_height,
                                   fillcolor="rgba(180, 180, 190, 0.95)",
                                   line=dict(color="black", width=2))
                
                # Sinking arrow
                fig_float.add_annotation(
                    x=obj_x_center, y=obj_y + 1.5,
                    ax=obj_x_center, ay=obj_y + 0.5,
                    showarrow=True, arrowhead=2, arrowsize=2, arrowwidth=3,
                    arrowcolor="red"
                )
                
                status_color = "rgba(200, 0, 0, 0.9)"
                status_text = f"SINKS! (Need {1/safety_factor:.1f}x more γ)"
            
            # Status box
            fig_float.add_annotation(
                x=container_width/2, y=container_height + 0.8,
                text=f"<b>{status_text}</b>",
                showarrow=False,
                font=dict(size=16, color="white"),
                bgcolor=status_color,
                bordercolor="black",
                borderwidth=2,
                borderpad=8
            )
            
            # Object label
            fig_float.add_annotation(x=container_width/2, y=container_height + 1.6,
                                    text=f"<b>{object_choice}</b> on <b>{liquid_choice}</b>",
                                    showarrow=False, font=dict(size=14))
            
            fig_float.update_layout(
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-0.5, container_width+0.5]),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-0.5, container_height+2.2],
                          scaleanchor="x", scaleratio=1),
                height=500,
                showlegend=False,
                plot_bgcolor='white',
                margin=dict(t=20, b=20)
            )
            
            st.plotly_chart(fig_float, use_container_width=True)
            
            st.caption("""
            **Force Balance for Floating**: 2γL cos(θ) ≥ W
            
            - **F<sub>γ</sub>** (green): Surface tension force pulling upward along contact line
            - **W** (red): Weight of the object pulling downward
            - The object floats when surface tension forces exceed weight!
            """)
        
        with st_viz_tab2:
            st.markdown("#### Droplet on Surface")
            
            # Create droplet visualization
            fig_drop = go.Figure()
            
            # Surface
            fig_drop.add_shape(type="rect", x0=-5, y0=-0.5, x1=5, y1=0,
                             fillcolor="rgba(150, 150, 150, 0.8)", line=dict(color="black", width=2))
            
            # Create droplet shape based on contact angle
            droplet_radius = 2
            
            if theta < 90:
                # Wetting - flattened droplet
                spread = 1 + (90 - theta) / 90  # More spread for lower angles
                height = droplet_radius / spread
                
                # Elliptical droplet
                t = np.linspace(0, np.pi, 50)
                drop_x = droplet_radius * spread * np.cos(t)
                drop_y = height * np.sin(t)
                
            else:
                # Non-wetting - beaded droplet
                squeeze = 1 + (theta - 90) / 90  # More spherical for higher angles
                width = droplet_radius / squeeze
                height = droplet_radius * squeeze * 0.8
                
                t = np.linspace(0, np.pi, 50)
                drop_x = width * np.cos(t)
                drop_y = height * np.sin(t)
            
            fig_drop.add_trace(go.Scatter(
                x=drop_x, y=drop_y,
                fill='toself', fillcolor=liquid_color,
                line=dict(color='darkblue', width=2),
                mode='lines',
                showlegend=False
            ))
            
            # Contact angle indicator
            angle_arc_r = 1.5
            angle_t = np.linspace(0, np.radians(theta), 20)
            angle_x = -droplet_radius * (spread if theta < 90 else 1/squeeze) + angle_arc_r * np.cos(angle_t)
            angle_y = angle_arc_r * np.sin(angle_t)
            
            fig_drop.add_trace(go.Scatter(x=angle_x, y=angle_y, mode='lines',
                                         line=dict(color='red', width=2, dash='dash'),
                                         showlegend=False))
            
            fig_drop.add_annotation(
                x=-droplet_radius * (spread if theta < 90 else 1/squeeze) + 1.8,
                y=0.5,
                text=f"<b>θ = {theta}°</b>",
                showarrow=False,
                font=dict(size=14, color="red")
            )
            
            # Labels
            wetting_status = "Wetting (Hydrophilic)" if theta < 90 else "Non-wetting (Hydrophobic)"
            fig_drop.add_annotation(x=0, y=-1.2, text=f"<b>{wetting_status}</b>",
                                  showarrow=False, font=dict(size=14, color="darkblue"))
            
            fig_drop.add_annotation(x=0, y=max(drop_y)+0.8, text=f"<b>{liquid_choice}</b>",
                                  showarrow=False, font=dict(size=14))
            
            fig_drop.update_layout(
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-5, 5]),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-2, 5],
                          scaleanchor="x", scaleratio=1),
                height=400,
                showlegend=False,
                plot_bgcolor='white',
                margin=dict(t=20, b=20)
            )
            
            st.plotly_chart(fig_drop, use_container_width=True)
            
            st.caption("""
            **Contact Angle (θ)** determines how a liquid spreads on a surface:
            - θ < 90°: Liquid wets/spreads on the surface
            - θ > 90°: Liquid beads up on the surface
            """)
    
    st.markdown("---")
    
    # SECTION 2: THEORY & CONCEPTS
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

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 20px; font-size: 0.9em;'>
    <p>🎓 Developed for Chemical Engineering Students</p>
    <p>University of Surrey | School of Chemistry and Chemical Engineering</p>
</div>
""", unsafe_allow_html=True)

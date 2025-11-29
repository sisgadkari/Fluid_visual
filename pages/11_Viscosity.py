import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Understanding Viscosity")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>🍯 Understanding Viscosity</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>Explore how fluids resist flow and deformation. Visualize the difference between honey and water, and understand why viscosity matters in engineering.</p>",
    unsafe_allow_html=True
)
st.markdown("---")

# Create tabs for different aspects
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Interactive Simulation", "📚 Theory & Concepts", "🔬 Viscosity Types", "📋 Engineering Applications"])

# =====================================================
# TAB 1: INTERACTIVE SIMULATION
# =====================================================
with tab1:
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.header("🔬 Parameters")
        
        # --- Preset Fluid Options ---
        st.subheader("Select a Fluid")
        fluid_choice = st.selectbox(
            "Choose a fluid to explore:",
            ("Water (20°C)", "Honey", "Motor Oil (SAE 30)", "Glycerol", "Mercury", "Air", "Blood", "Maple Syrup", "Custom"),
            key="fluid_selector"
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
            st.subheader("Custom Fluid Properties")
            mu = st.slider("Dynamic Viscosity (μ) [Pa·s]", 0.0001, 5.0, 0.1, 0.0001, format="%.4f")
            rho = st.number_input("Density (ρ) [kg/m³]", value=1000, min_value=1, max_value=20000)
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
        st.subheader("Calculated Properties")
        
        col_calc1, col_calc2 = st.columns(2)
        with col_calc1:
            st.metric("Dynamic Viscosity (μ)", f"{mu:.4f} Pa·s")
        with col_calc2:
            st.metric("Kinematic Viscosity (ν)", f"{nu:.2e} m²/s")
        
        st.markdown("---")
        st.subheader("Flow Conditions")
        
        # Shear rate for visualization
        shear_rate = st.slider("Shear Rate (du/dy) [1/s]", 1, 1000, 100, 10,
                               help="Rate of change of velocity with distance")
        
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
        st.header("🖼️ Visualization")
        
        # Create visualization tabs
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["🌊 Fluid Flow", "📊 Velocity Profile", "🍯 Falling Ball"])
        
        with viz_tab1:
            # --- Parallel Plate Flow Visualization ---
            st.markdown("#### Couette Flow (Fluid Between Parallel Plates)")
            
            fig = go.Figure()
            
            # Plate dimensions
            plate_length = 10
            plate_gap = 2
            
            # Top plate (moving)
            fig.add_shape(type="rect", x0=0, y0=plate_gap, x1=plate_length, y1=plate_gap+0.3,
                         fillcolor="rgba(100,100,100,0.8)", line=dict(color="black", width=2))
            fig.add_annotation(x=plate_length/2, y=plate_gap+0.5, text="<b>Moving Plate (V)</b>",
                             showarrow=False, font=dict(size=12))
            
            # Bottom plate (stationary)
            fig.add_shape(type="rect", x0=0, y0=-0.3, x1=plate_length, y1=0,
                         fillcolor="rgba(100,100,100,0.8)", line=dict(color="black", width=2))
            fig.add_annotation(x=plate_length/2, y=-0.5, text="<b>Stationary Plate</b>",
                             showarrow=False, font=dict(size=12))
            
            # Fluid between plates
            fig.add_shape(type="rect", x0=0, y0=0, x1=plate_length, y1=plate_gap,
                         fillcolor=fluid_color, line=dict(color="blue", width=1))
            
            # Velocity profile arrows (linear for Couette flow)
            n_arrows = 8
            max_arrow_length = 2.5 - (mu / 3)  # Shorter arrows for more viscous fluids
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
            
            # Add velocity profile line
            y_profile = np.linspace(0, plate_gap, 20)
            x_profile = 2 + (y_profile / plate_gap) * max_arrow_length
            fig.add_trace(go.Scatter(x=x_profile, y=y_profile, mode='lines',
                                    line=dict(color='red', width=3, dash='dash'),
                                    name='Velocity Profile'))
            
            # Shear stress indicator
            fig.add_annotation(x=7, y=plate_gap/2, 
                             text=f"<b>τ = μ × (du/dy)</b><br>τ = {tau:.2f} Pa",
                             showarrow=False, font=dict(size=14, color="darkred"),
                             bgcolor="rgba(255,255,255,0.9)", bordercolor="red", borderwidth=2)
            
            # Add "High viscosity = more resistance" annotation
            resistance_text = "High resistance" if mu > 0.1 else "Low resistance" if mu < 0.01 else "Medium resistance"
            fig.add_annotation(x=plate_length/2, y=plate_gap/2,
                             text=f"<b>{resistance_text}</b>",
                             showarrow=False, font=dict(size=16, color="white"),
                             bgcolor=fluid_color.replace('0.7', '0.9').replace('0.8', '0.95'))
            
            fig.update_layout(
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-1, plate_length+1]),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-1, plate_gap+1]),
                height=400,
                showlegend=False,
                plot_bgcolor='white',
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            # Result box
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
            Higher viscosity fluids resist this shearing motion more strongly, requiring more force to maintain the same velocity.
            """)
        
        with viz_tab2:
            # --- Velocity Profile Comparison ---
            st.markdown("#### Velocity Profile in Pipe Flow")
            
            fig2 = go.Figure()
            
            # Pipe radius
            R = 1.0
            
            # Calculate velocity profile for laminar flow (Hagen-Poiseuille)
            r = np.linspace(-R, R, 100)
            
            # Normalize velocity based on viscosity (inverse relationship)
            v_max = 1 / (mu * 10 + 0.1)  # Normalized max velocity
            v_max = min(v_max, 2)  # Cap at 2
            
            v = v_max * (1 - (r/R)**2)  # Parabolic profile
            
            # Draw pipe walls
            fig2.add_shape(type="line", x0=0, y0=R, x1=3, y1=R,
                          line=dict(color="black", width=4))
            fig2.add_shape(type="line", x0=0, y0=-R, x1=3, y1=-R,
                          line=dict(color="black", width=4))
            
            # Fill pipe with fluid color
            fig2.add_shape(type="rect", x0=0, y0=-R, x1=3, y1=R,
                          fillcolor=fluid_color, line_width=0, layer="below")
            
            # Velocity profile
            fig2.add_trace(go.Scatter(x=v, y=r, mode='lines', fill='tozerox',
                                     fillcolor='rgba(255,100,100,0.3)',
                                     line=dict(color='red', width=3),
                                     name='Velocity Profile'))
            
            # Add velocity arrows
            n_arrows = 7
            for i in range(n_arrows):
                r_pos = -R + (i + 0.5) * 2 * R / n_arrows
                v_at_r = v_max * (1 - (r_pos/R)**2)
                if v_at_r > 0.05:
                    fig2.add_annotation(
                        x=v_at_r, y=r_pos,
                        ax=0, ay=r_pos,
                        showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2,
                        arrowcolor="darkblue"
                    )
            
            # Annotations
            fig2.add_annotation(x=v_max/2, y=0, text=f"<b>V_max</b>",
                              showarrow=True, ay=-30, font=dict(size=12, color="red"))
            
            fig2.add_annotation(x=-0.3, y=0, text="<b>Centerline</b>",
                              showarrow=False, font=dict(size=10), textangle=-90)
            
            # Result box
            fig2.add_annotation(
                x=1.0, y=R+0.4,
                text=f"<b>μ = {mu:.4f} Pa·s | Flow {'Slow' if mu > 0.1 else 'Fast'}</b>",
                showarrow=False,
                font=dict(size=16, color="white"),
                bgcolor="rgba(0, 100, 200, 0.9)",
                bordercolor="darkblue",
                borderwidth=2,
                borderpad=8
            )
            
            fig2.update_layout(
                xaxis=dict(title="Velocity", showgrid=True, gridcolor='rgba(0,0,0,0.1)', range=[-0.5, max(2.5, v_max+0.5)]),
                yaxis=dict(title="Radial Position (r/R)", showgrid=True, gridcolor='rgba(0,0,0,0.1)', range=[-1.5, 1.7]),
                height=400,
                showlegend=False,
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            st.caption("""
            **Pipe Flow**: In laminar flow, the velocity profile is parabolic. Maximum velocity occurs at the center,
            while velocity is zero at the walls (no-slip condition). Higher viscosity = slower flow for the same pressure drop.
            """)
        
        with viz_tab3:
            # --- Falling Ball Viscometer Simulation ---
            st.markdown("#### Falling Ball Viscometer")
            
            fig3 = go.Figure()
            
            # Container
            container_width = 4
            container_height = 10
            
            # Draw container
            fig3.add_shape(type="rect", x0=0, y0=0, x1=container_width, y1=container_height,
                          fillcolor=fluid_color, line=dict(color="black", width=3))
            
            # Ball position (based on viscosity - higher viscosity = ball higher up = slower fall)
            # Terminal velocity is inversely proportional to viscosity
            ball_radius = 0.3
            rho_ball = 7800  # Steel ball density
            
            # Calculate terminal velocity (Stokes' law)
            if mu > 0:
                v_terminal = (2 * ball_radius**2 * (rho_ball - rho) * 9.81) / (9 * mu)
                v_terminal = max(0.001, min(v_terminal, 100))  # Clamp values
            else:
                v_terminal = 100
            
            # Ball position (simulate where ball would be after some time)
            # Higher viscosity = ball hasn't fallen as far
            fall_distance = min(container_height - 2, v_terminal * 0.5)
            ball_y = container_height - 1 - fall_distance
            ball_y = max(1, ball_y)
            
            # Draw ball
            fig3.add_shape(type="circle",
                          x0=container_width/2 - ball_radius, y0=ball_y - ball_radius,
                          x1=container_width/2 + ball_radius, y1=ball_y + ball_radius,
                          fillcolor="rgba(100,100,100,0.9)", line=dict(color="black", width=2))
            
            # Velocity arrow
            arrow_length = min(2, v_terminal / 10)
            if arrow_length > 0.1:
                fig3.add_annotation(
                    x=container_width/2, y=ball_y - ball_radius - arrow_length,
                    ax=container_width/2, ay=ball_y - ball_radius,
                    showarrow=True, arrowhead=2, arrowsize=2, arrowwidth=3,
                    arrowcolor="red"
                )
            
            # Labels
            fig3.add_annotation(x=container_width/2, y=ball_y,
                              text="<b>Ball</b>", showarrow=False,
                              font=dict(size=10, color="white"))
            
            fig3.add_annotation(x=container_width + 0.5, y=container_height/2,
                              text=f"<b>{fluid_choice}</b>", showarrow=False,
                              font=dict(size=12), textangle=-90)
            
            # Terminal velocity annotation
            fig3.add_annotation(x=container_width/2, y=0.5,
                              text=f"<b>V_terminal ≈ {v_terminal:.3f} m/s</b>",
                              showarrow=False, font=dict(size=12, color="darkblue"),
                              bgcolor="rgba(255,255,255,0.9)")
            
            # Result box
            fig3.add_annotation(
                x=container_width/2, y=container_height + 0.8,
                text=f"<b>Higher μ = Slower Fall</b>",
                showarrow=False,
                font=dict(size=16, color="white"),
                bgcolor="rgba(0, 100, 200, 0.9)",
                bordercolor="darkblue",
                borderwidth=2,
                borderpad=8
            )
            
            fig3.update_layout(
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-1, container_width+2]),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-0.5, container_height+1.5]),
                height=500,
                showlegend=False,
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig3, use_container_width=True)
            
            st.caption(f"""
            **Falling Ball Viscometer**: A ball falls through the fluid under gravity. The terminal velocity depends on viscosity.
            Using Stokes' Law: V = (2r²(ρ_ball - ρ_fluid)g) / (9μ). For this fluid, V_terminal ≈ {v_terminal:.4f} m/s.
            """)

# =====================================================
# TAB 2: THEORY & CONCEPTS
# =====================================================
with tab2:
    st.header("📚 Understanding Viscosity")
    
    col_theory1, col_theory2 = st.columns([1, 1])
    
    with col_theory1:
        st.markdown("""
        ### What is Viscosity?
        
        **Viscosity** is a measure of a fluid's resistance to deformation or flow. Think of it as the "thickness" or "stickiness" of a fluid.
        
        - **High viscosity**: Honey, motor oil, glycerol (flows slowly)
        - **Low viscosity**: Water, air, alcohol (flows easily)
        
        ### The Physical Meaning
        
        When you stir a cup of water vs. a jar of honey, you immediately feel the difference. 
        The honey resists your stirring motion much more than water does. This resistance is viscosity!
        
        ### Newton's Law of Viscosity
        
        For **Newtonian fluids**, the shear stress is directly proportional to the shear rate:
        """)
        
        st.latex(r'\tau = \mu \frac{du}{dy}')
        
        st.markdown("""
        Where:
        - **τ** (tau) = Shear stress [Pa or N/m²]
        - **μ** (mu) = Dynamic viscosity [Pa·s or kg/(m·s)]
        - **du/dy** = Velocity gradient (shear rate) [1/s]
        
        This equation is fundamental to fluid mechanics and is analogous to Hooke's Law for solids!
        """)
    
    with col_theory2:
        st.markdown("""
        ### Two Types of Viscosity
        
        #### 1. Dynamic (Absolute) Viscosity (μ)
        - Measures the force required to move one layer of fluid past another
        - Units: Pa·s (SI) or Poise (P) where 1 Pa·s = 10 P
        - Also expressed in centipoise (cP): 1 cP = 0.001 Pa·s
        
        #### 2. Kinematic Viscosity (ν)
        - Dynamic viscosity divided by density
        - Represents the fluid's resistance to flow under gravity
        """)
        
        st.latex(r'\nu = \frac{\mu}{\rho}')
        
        st.markdown("""
        Where:
        - **ν** (nu) = Kinematic viscosity [m²/s]
        - **μ** = Dynamic viscosity [Pa·s]
        - **ρ** = Density [kg/m³]
        
        - Units: m²/s (SI) or Stokes (St) where 1 St = 10⁻⁴ m²/s
        - Also expressed in centistokes (cSt): 1 cSt = 10⁻⁶ m²/s
        
        > **Fun Fact**: Kinematic viscosity is used in the Reynolds number calculation, making it crucial for determining flow regimes!
        """)
    
    st.markdown("---")
    
    # Viscosity comparison table
    st.markdown("### 📊 Viscosity of Common Fluids at 20°C")
    
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
    
    st.info("""
    **The Pitch Drop Experiment**: The University of Queensland has been running an experiment since 1927 where pitch (a highly viscous material) 
    slowly drips through a funnel. Only 9 drops have fallen in nearly 100 years! This demonstrates extreme viscosity.
    """)

# =====================================================
# TAB 3: VISCOSITY TYPES
# =====================================================
with tab3:
    st.header("🔬 Types of Fluid Behavior")
    
    col_type1, col_type2 = st.columns([1, 1])
    
    with col_type1:
        st.markdown("""
        ### Newtonian vs Non-Newtonian Fluids
        
        #### Newtonian Fluids
        - Viscosity remains **constant** regardless of shear rate
        - Linear relationship between shear stress and shear rate
        - Examples: Water, air, most oils, honey, glycerol
        
        #### Non-Newtonian Fluids
        - Viscosity **changes** with shear rate or time
        - More complex behavior
        - Very common in industrial applications!
        """)
        
        st.markdown("""
        ### Types of Non-Newtonian Behavior
        
        **1. Shear-Thinning (Pseudoplastic)**
        - Viscosity decreases with increasing shear rate
        - Examples: Ketchup, paint, blood, polymer solutions
        - *"The harder you stir, the easier it flows"*
        
        **2. Shear-Thickening (Dilatant)**
        - Viscosity increases with increasing shear rate
        - Examples: Cornstarch in water (oobleck), wet sand
        - *"The harder you push, the more it resists"*
        
        **3. Bingham Plastic**
        - Requires minimum stress (yield stress) before flowing
        - Examples: Toothpaste, mayonnaise, drilling mud
        - *"Won't flow until you push hard enough"*
        """)
    
    with col_type2:
        # Create a plot showing different fluid behaviors
        fig_types = go.Figure()
        
        shear_rate = np.linspace(0, 100, 100)
        
        # Newtonian
        tau_newtonian = 0.5 * shear_rate
        
        # Shear-thinning (power law n < 1)
        tau_thinning = 2 * shear_rate**0.5
        
        # Shear-thickening (power law n > 1)
        tau_thickening = 0.05 * shear_rate**1.5
        
        # Bingham plastic
        tau_bingham = 20 + 0.3 * shear_rate
        
        fig_types.add_trace(go.Scatter(x=shear_rate, y=tau_newtonian, mode='lines',
                                       name='Newtonian', line=dict(color='blue', width=3)))
        fig_types.add_trace(go.Scatter(x=shear_rate, y=tau_thinning, mode='lines',
                                       name='Shear-Thinning', line=dict(color='green', width=3)))
        fig_types.add_trace(go.Scatter(x=shear_rate, y=tau_thickening, mode='lines',
                                       name='Shear-Thickening', line=dict(color='red', width=3)))
        fig_types.add_trace(go.Scatter(x=shear_rate, y=tau_bingham, mode='lines',
                                       name='Bingham Plastic', line=dict(color='purple', width=3)))
        
        fig_types.update_layout(
            title="<b>Shear Stress vs Shear Rate for Different Fluid Types</b>",
            xaxis_title="Shear Rate (du/dy) [1/s]",
            yaxis_title="Shear Stress (τ) [Pa]",
            height=400,
            legend=dict(x=0.02, y=0.98),
            plot_bgcolor='rgba(240,248,255,0.5)'
        )
        
        st.plotly_chart(fig_types, use_container_width=True)
        
        st.markdown("""
        ### Temperature Effects
        
        Viscosity is **strongly affected by temperature**:
        
        - **Liquids**: Viscosity **decreases** as temperature increases
          - Molecules move faster, reducing intermolecular forces
          - Example: Cold honey is much thicker than warm honey
        
        - **Gases**: Viscosity **increases** as temperature increases
          - Faster molecules collide more frequently
          - Opposite behavior to liquids!
        
        For liquids, the Arrhenius equation often applies:
        """)
        
        st.latex(r'\mu = A \cdot e^{E_a / RT}')
        
        st.markdown("""
        Where E_a is the activation energy for viscous flow.
        """)

# =====================================================
# TAB 4: ENGINEERING APPLICATIONS
# =====================================================
with tab4:
    st.header("📋 Engineering Applications of Viscosity")
    
    col_app1, col_app2 = st.columns([1, 1])
    
    with col_app1:
        st.markdown("""
        ### Why Viscosity Matters in Chemical Engineering
        
        #### 1. Pump Selection & Sizing
        - Higher viscosity = more power required
        - Affects pump efficiency and selection
        - Critical for pipeline design
        
        #### 2. Heat Transfer
        - Viscosity affects convective heat transfer
        - Appears in Prandtl number: Pr = μCp/k
        - Influences boundary layer thickness
        
        #### 3. Mixing Operations
        - Determines impeller selection
        - Affects mixing time and power consumption
        - Critical for reactor design
        
        #### 4. Coating & Painting
        - Controls film thickness
        - Affects surface finish quality
        - Important for spray applications
        """)
        
        st.markdown("""
        ### Key Dimensionless Numbers Involving Viscosity
        
        **Reynolds Number** - Flow regime indicator
        """)
        st.latex(r'Re = \frac{\rho V D}{\mu} = \frac{V D}{\nu}')
        
        st.markdown("""
        **Prandtl Number** - Heat transfer characteristic
        """)
        st.latex(r'Pr = \frac{\mu C_p}{k} = \frac{\nu}{\alpha}')
        
        st.markdown("""
        **Schmidt Number** - Mass transfer characteristic
        """)
        st.latex(r'Sc = \frac{\mu}{\rho D_{AB}} = \frac{\nu}{D_{AB}}')
    
    with col_app2:
        st.markdown("""
        ### Industrial Examples
        
        #### 🛢️ Petroleum Industry
        - Crude oil viscosity affects extraction and transport
        - Pipeline heating to reduce viscosity
        - Fuel injector design for engines
        
        #### 🍫 Food Industry
        - Chocolate tempering and viscosity control
        - Sauce consistency and mouthfeel
        - Beverage processing
        
        #### 💊 Pharmaceutical Industry
        - Injectable drug formulations
        - Cream and ointment consistency
        - Syrup medications
        
        #### 🏗️ Construction
        - Concrete flow properties
        - Paint and coating application
        - Adhesive performance
        
        #### 🚗 Automotive
        - Engine oil grades (SAE ratings)
        - Transmission fluids
        - Brake fluid performance
        """)
        
        st.success("""
        **SAE Oil Grades Explained:**
        - **SAE 30**: Single-grade oil (viscosity at 100°C)
        - **SAE 5W-30**: Multi-grade oil
          - "5W" = Winter viscosity (at -30°C)
          - "30" = Summer viscosity (at 100°C)
        - Lower W number = better cold-start performance
        """)
    
    st.markdown("---")
    
    # Interactive application example
    st.markdown("### 🧮 Quick Calculator: Pipe Flow Pressure Drop")
    
    calc_col1, calc_col2, calc_col3 = st.columns(3)
    
    with calc_col1:
        pipe_D = st.number_input("Pipe Diameter (m)", value=0.05, min_value=0.001, max_value=1.0, format="%.3f")
        pipe_L = st.number_input("Pipe Length (m)", value=10.0, min_value=0.1, max_value=1000.0)
    
    with calc_col2:
        flow_Q = st.number_input("Flow Rate (m³/s)", value=0.001, min_value=0.0001, max_value=1.0, format="%.4f")
        fluid_mu = st.number_input("Viscosity (Pa·s)", value=0.001, min_value=0.00001, max_value=10.0, format="%.5f")
    
    with calc_col3:
        fluid_rho = st.number_input("Density (kg/m³)", value=1000.0, min_value=1.0, max_value=20000.0)
    
    # Calculate
    A_pipe = np.pi * (pipe_D/2)**2
    V_pipe = flow_Q / A_pipe
    Re_pipe = (fluid_rho * V_pipe * pipe_D) / fluid_mu
    
    # Laminar flow pressure drop (Hagen-Poiseuille)
    if Re_pipe < 2300:
        delta_P = (128 * fluid_mu * pipe_L * flow_Q) / (np.pi * pipe_D**4)
        flow_type = "Laminar"
    else:
        # Turbulent - use Blasius correlation for friction factor
        f = 0.316 / Re_pipe**0.25
        delta_P = f * (pipe_L / pipe_D) * (fluid_rho * V_pipe**2 / 2)
        flow_type = "Turbulent"
    
    st.markdown("---")
    
    result_col1, result_col2, result_col3, result_col4 = st.columns(4)
    
    with result_col1:
        st.metric("Velocity", f"{V_pipe:.3f} m/s")
    with result_col2:
        st.metric("Reynolds Number", f"{Re_pipe:.0f}")
    with result_col3:
        st.metric("Flow Type", flow_type)
    with result_col4:
        st.metric("Pressure Drop", f"{delta_P:.2f} Pa")
    
    if Re_pipe < 2300:
        st.info(f"**Laminar Flow**: Using Hagen-Poiseuille equation. ΔP = 128μLQ/(πD⁴)")
    else:
        st.warning(f"**Turbulent Flow**: Using Darcy-Weisbach with Blasius correlation. Higher pressure drop due to turbulent mixing.")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 20px; font-size: 0.9em;'>
    <p>🎓 Developed for Chemical Engineering Students</p>
    <p>University of Surrey | School of Chemistry and Chemical Engineering</p>
</div>
""", unsafe_allow_html=True)

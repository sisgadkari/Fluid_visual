import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Pump Head Demand Calculator", layout="wide")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>⚡ Pump Head Demand Calculator</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
Calculate pump requirements for two-reservoir systems using the equivalent length method.
Understand how elevation, friction, and fittings affect total head demand.
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# Create tabs for different aspects
tab1, tab2, tab3 = st.tabs(["🎯 Interactive Simulation", "📚 Understanding Pump Systems", "📋 Real-World Applications"])

def get_fittings_database():
    """Return the fittings database with equivalent lengths"""
    return {
        "90° Standard Elbow": {"n": 35, "icon": "🔄", "desc": "Common pipe elbow"},
        "90° Long Radius Elbow": {"n": 23, "icon": "🔄", "desc": "Smoother bend, less loss"},
        "45° Elbow": {"n": 16, "icon": "↗️", "desc": "Gentler direction change"},
        "T-junction (flow through)": {"n": 20, "icon": "➕", "desc": "Straight flow through tee"},
        "T-junction (branch flow)": {"n": 60, "icon": "➕", "desc": "90° turn through tee"},
        "Sharp Pipe Exit": {"n": 50, "icon": "➡️", "desc": "Sudden expansion to reservoir"},
        "Sharp Inlet": {"n": 25, "icon": "⬅️", "desc": "Square-edged entrance"},
        "Radius Inlet": {"n": 0, "icon": "⬅️", "desc": "Rounded entrance, minimal loss"},
        "Re-entrant Inlet": {"n": 50, "icon": "⬅️", "desc": "Pipe protruding into tank"},
        "Globe Valve (fully open)": {"n": 180, "icon": "🌐", "desc": "High control, high loss"},
        "Gate Valve (fully open)": {"n": 7, "icon": "🚪", "desc": "Low loss when open"},
        "Gate Valve (3/4 open)": {"n": 40, "icon": "🚪", "desc": "Partially closed"},
        "Gate Valve (1/2 open)": {"n": 200, "icon": "🚪", "desc": "Half closed"},
        "Gate Valve (1/4 open)": {"n": 800, "icon": "🚪", "desc": "Nearly closed, huge loss"},
        "Ball Valve (fully open)": {"n": 3, "icon": "⚽", "desc": "Very low loss"},
        "Check Valve (swing)": {"n": 50, "icon": "✓", "desc": "Prevents backflow"},
        "Butterfly Valve (fully open)": {"n": 45, "icon": "🦋", "desc": "Moderate loss"},
    }

def calculate_friction_factor(reynolds, relative_roughness):
    """Calculate friction factor using Churchill equation"""
    if reynolds < 2300:  # Laminar
        return 64 / reynolds
    else:  # Turbulent - Churchill equation
        A = (2.457 * np.log(1 / ((7/reynolds)**0.9 + 0.27 * relative_roughness)))**16
        B = (37530 / reynolds)**16
        f = 8 * ((8/reynolds)**12 + 1/(A + B)**(3/2))**(1/12)
        return f

def calculate_system(Q, L, D, epsilon, z1, z2, rho, nu, fittings):
    """Calculate complete system head demand"""
    # Flow characteristics
    A = np.pi * (D/2)**2
    V = Q / A if A > 0 else 0
    Re = (V * D) / nu if nu > 0 else 0
    
    # Flow regime
    if Re < 2300:
        regime = "Laminar"
    elif Re < 4000:
        regime = "Transitional"
    else:
        regime = "Turbulent"
    
    # Friction factor
    rel_rough = epsilon / D if D > 0 else 0
    f = calculate_friction_factor(Re, rel_rough)
    
    # Equivalent length from fittings
    Le_fittings = 0
    for fitting_data in fittings.values():
        Le_fittings += D * fitting_data['n'] * fitting_data['quantity']
    
    Le_total = L + Le_fittings
    
    # Head losses
    static_head = z2 - z1
    
    # Darcy-Weisbach equation for total friction loss
    if V > 0 and D > 0:
        h_friction_total = f * (4 * Le_total / D) * (V**2 / (2 * 9.81))
        h_friction_pipe = f * (4 * L / D) * (V**2 / (2 * 9.81))
        h_friction_fittings = h_friction_total - h_friction_pipe
    else:
        h_friction_total = 0
        h_friction_pipe = 0
        h_friction_fittings = 0
    
    # Total head demand
    H_demand = static_head + h_friction_total
    
    # Power calculations
    P_hydraulic = rho * 9.81 * Q * H_demand  # Watts
    P_80 = P_hydraulic / 0.80 / 1000  # kW
    P_70 = P_hydraulic / 0.70 / 1000  # kW
    P_60 = P_hydraulic / 0.60 / 1000  # kW
    
    return {
        'velocity': V,
        'reynolds': Re,
        'flow_regime': regime,
        'friction_factor': f,
        'static_head': static_head,
        'pipe_friction_loss': h_friction_pipe,
        'fittings_loss': h_friction_fittings,
        'total_dynamic_loss': h_friction_total,
        'total_head_demand': H_demand,
        'equivalent_length': Le_total,
        'power_hydraulic': P_hydraulic,
        'power_80': P_80,
        'power_70': P_70,
        'power_60': P_60
    }

with tab1:
    # --- Main Layout ---
    col1, col2 = st.columns([2, 3])

    # --- Column 1: Inputs and Results ---
    with col1:
        st.header("🔬 Parameters")
        
        # --- Interactive Scenarios ---
        SCENARIOS = {
            "Custom...": {
                "z2": 100, "L": 500, "D": 150, "Q": 50, "material": "Commercial steel (new)",
                "desc": "Manually adjust all parameters below."
            },
            "Building Water Supply": {
                "z2": 50, "L": 200, "D": 100, "Q": 30, "material": "Commercial steel (new)",
                "desc": "Pumping water to 50m high building, 200m pipe run. Typical commercial application."
            },
            "Irrigation System": {
                "z2": 20, "L": 1000, "D": 200, "Q": 100, "material": "Commercial steel (used)",
                "desc": "Long horizontal run to elevated fields. Large diameter, high flow rate."
            },
            "Fire Protection": {
                "z2": 80, "L": 300, "D": 150, "Q": 150, "material": "Commercial steel (new)",
                "desc": "High flow rate required, elevated storage tank. Critical safety system."
            },
            "Mining Dewatering": {
                "z2": 150, "L": 800, "D": 250, "Q": 200, "material": "Cast iron (used)",
                "desc": "Deep mine, long vertical lift. Heavy-duty pumping, large diameter."
            },
            "Domestic Well": {
                "z2": 30, "L": 100, "D": 50, "Q": 5, "material": "Smooth (drawn tubing)",
                "desc": "Small diameter, low flow. Residential water supply from well to house."
            }
        }
        
        scenario = st.selectbox("Select Application Scenario", list(SCENARIOS.keys()))
        selected = SCENARIOS[scenario]
        st.info(selected["desc"])
        
        st.subheader("Reservoir Elevations")
        c1, c2 = st.columns(2)
        with c1:
            z1 = 0.0  # Reference level
            st.metric("Reservoir 1 Elevation", f"{z1} m", help="Reference level (ground)")
        with c2:
            z2 = st.slider("Reservoir 2 Elevation (m)", 10, 200, selected["z2"], 5,
                          help="Height above reservoir 1")
        
        st.subheader("Pipe Specifications")
        c1, c2 = st.columns(2)
        with c1:
            L = st.slider("Pipe Length (m)", 10, 2000, selected["L"], 10,
                         help="Total length of pipeline")
        with c2:
            D_mm = st.slider("Pipe Diameter (mm)", 25, 500, selected["D"], 5,
                            help="Internal diameter")
            D = D_mm / 1000  # Convert to meters
        
        st.subheader("Pipe Material & Roughness")
        roughness_options = {
            "Smooth (drawn tubing)": 0.0015e-3,
            "Commercial steel (new)": 0.045e-3,
            "Commercial steel (used)": 0.15e-3,
            "Galvanized iron": 0.15e-3,
            "Cast iron (new)": 0.26e-3,
            "Cast iron (used)": 2.0e-3,
            "Concrete (smooth)": 0.3e-3,
            "Concrete (rough)": 3.0e-3,
            "PVC": 0.0015e-3
        }
        
        material = st.selectbox("Pipe Material", list(roughness_options.keys()),
                               index=list(roughness_options.keys()).index(selected["material"]))
        epsilon = roughness_options[material]
        st.caption(f"Surface roughness: ε = {epsilon*1000:.4f} mm")
        
        st.subheader("Operating Conditions")
        c1, c2 = st.columns(2)
        with c1:
            Q_m3h = st.number_input("Flow Rate (m³/h)", 1.0, 500.0, float(selected["Q"]), 1.0,
                                   help="Desired flow rate")
            Q = Q_m3h / 3600  # Convert to m³/s
        with c2:
            Q_Ls = Q * 1000
            st.metric("Flow Rate", f"{Q_Ls:.2f} L/s")
        
        st.subheader("Fluid Properties")
        c1, c2 = st.columns(2)
        with c1:
            rho = st.number_input("Density (kg/m³)", 800, 1200, 1000, 10)
        with c2:
            nu_cSt = st.number_input("Kinematic Viscosity (cSt)", 0.5, 10.0, 1.0, 0.1)
            nu = nu_cSt * 1e-6  # Convert to m²/s
        
        st.subheader("Fittings & Minor Losses")
        st.markdown("*Select fittings in the system:*")
        
        fittings_db = get_fittings_database()
        selected_fittings = {}
        
        # Organize fittings by category
        fitting_categories = {
            "Bends": ["90° Standard Elbow", "90° Long Radius Elbow", "45° Elbow"],
            "Junctions": ["T-junction (flow through)", "T-junction (branch flow)"],
            "Inlets/Exits": ["Sharp Inlet", "Radius Inlet", "Re-entrant Inlet", "Sharp Pipe Exit"],
            "Valves": ["Globe Valve (fully open)", "Gate Valve (fully open)", "Gate Valve (3/4 open)", 
                      "Gate Valve (1/2 open)", "Gate Valve (1/4 open)", "Ball Valve (fully open)", 
                      "Check Valve (swing)", "Butterfly Valve (fully open)"]
        }
        
        for category, fittings_list in fitting_categories.items():
            with st.expander(f"{category}"):
                for fitting_name in fittings_list:
                    if fitting_name in fittings_db:
                        fitting_data = fittings_db[fitting_name]
                        qty = st.number_input(
                            f"{fitting_data['icon']} {fitting_name}",
                            min_value=0, max_value=20, value=0, step=1,
                            key=f"qty_{fitting_name}",
                            help=f"{fitting_data['desc']} | Le/D = {fitting_data['n']}"
                        )
                        if qty > 0:
                            selected_fittings[fitting_name] = {
                                "quantity": qty,
                                "n": fitting_data["n"],
                                "icon": fitting_data["icon"]
                            }
        
        # Calculate results
        results = calculate_system(Q, L, D, epsilon, z1, z2, rho, nu, selected_fittings)
        
        st.markdown("---")
        st.header("📈 Results Summary")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("**TOTAL HEAD DEMAND**", f"{results['total_head_demand']:.2f} m",
                     help="Required pump head")
            st.metric("Static Head", f"{results['static_head']:.1f} m")
        with col_r2:
            st.metric("Power Required (η=80%)", f"{results['power_80']:.2f} kW")
            st.metric("Total Friction Loss", f"{results['total_dynamic_loss']:.2f} m")
        
        col_r3, col_r4 = st.columns(2)
        with col_r3:
            st.metric("Pipe Velocity", f"{results['velocity']:.2f} m/s")
            st.metric("Reynolds Number", f"{results['reynolds']:,.0f}")
        with col_r4:
            st.metric("Flow Regime", results['flow_regime'])
            st.metric("Friction Factor", f"{results['friction_factor']:.4f}")
        
        st.markdown("---")
        st.header("🧮 Step-by-Step Calculation")
        
        with st.expander("📖 See Detailed Breakdown", expanded=False):
            st.markdown("### Pump Head Demand Calculation")
            
            st.markdown("#### Step 1: Calculate Flow Parameters")
            st.write(f"**Given:**")
            st.write(f"• Flow rate: Q = {Q_m3h:.1f} m³/h = {Q:.6f} m³/s = {Q_Ls:.2f} L/s")
            st.write(f"• Pipe diameter: D = {D_mm} mm = {D:.3f} m")
            
            st.write(f"\n**Cross-sectional area:**")
            st.latex(r'A = \frac{\pi D^2}{4}')
            A = np.pi * (D/2)**2
            st.write(f"A = π × ({D:.3f}/2)² = {A:.6f} m²")
            
            st.write(f"\n**Flow velocity:**")
            st.latex(r'V = \frac{Q}{A}')
            st.write(f"V = {Q:.6f} / {A:.6f} = **{results['velocity']:.3f} m/s**")
            
            st.write(f"\n**Reynolds number:**")
            st.latex(r'Re = \frac{VD}{\nu}')
            st.write(f"Re = ({results['velocity']:.3f} × {D:.3f}) / {nu:.2e}")
            st.write(f"Re = **{results['reynolds']:,.0f}** → **{results['flow_regime']} flow**")
            
            st.markdown("#### Step 2: Determine Friction Factor")
            if results['reynolds'] < 2300:
                st.write("For **laminar flow** (Re < 2300):")
                st.latex(r'f = \frac{64}{Re}')
                st.write(f"f = 64 / {results['reynolds']:.0f} = **{results['friction_factor']:.5f}**")
            else:
                st.write("For **turbulent flow**, use Churchill equation:")
                rel_rough = epsilon / D
                st.latex(r'\frac{1}{\sqrt{f}} = -2\log_{10}\left(\frac{\varepsilon/D}{3.7} + \frac{2.51}{Re\sqrt{f}}\right)')
                st.write(f"• Relative roughness: ε/D = {epsilon*1000:.4f}mm / {D_mm}mm = {rel_rough:.6f}")
                st.write(f"• Reynolds number: Re = {results['reynolds']:,.0f}")
                st.write(f"• Calculated friction factor: f = **{results['friction_factor']:.5f}**")
            
            st.markdown("#### Step 3: Calculate Equivalent Length")
            st.write("**Pipe length:** L_pipe = {} m".format(L))
            
            if selected_fittings:
                st.write("\n**Fitting contributions:**")
                st.latex(r'L_e = L_{pipe} + D \sum (n \times quantity)')
                
                total_n = 0
                for name, data in selected_fittings.items():
                    contribution = data['n'] * data['quantity']
                    total_n += contribution
                    st.write(f"• {data['quantity']}× {name}: n={data['n']}, contribution = {contribution}")
                
                Le_fittings = D * total_n
                st.write(f"\n**Total from fittings:** {D:.3f} m × {total_n} = {Le_fittings:.2f} m")
                st.write(f"**Total equivalent length:** L_e = {L} + {Le_fittings:.2f} = **{results['equivalent_length']:.2f} m**")
            else:
                st.write("No fittings selected")
                st.write(f"**Total equivalent length:** L_e = **{results['equivalent_length']:.2f} m**")
            
            st.markdown("#### Step 4: Calculate Head Losses")
            
            st.write("**A. Static head (elevation difference):**")
            st.latex(r'H_{static} = z_2 - z_1')
            st.write(f"H_static = {z2} - {z1} = **{results['static_head']:.1f} m**")
            
            st.write("\n**B. Friction head loss (Darcy-Weisbach):**")
            st.latex(r'H_{friction} = f \frac{4L_e}{D} \frac{V^2}{2g}')
            st.write(f"H_friction = {results['friction_factor']:.5f} × (4×{results['equivalent_length']:.2f})/{D:.3f} × ({results['velocity']:.3f})²/(2×9.81)")
            st.write(f"H_friction = **{results['total_dynamic_loss']:.3f} m**")
            
            st.write("\n**Breakdown:**")
            st.write(f"• Pipe friction: {results['pipe_friction_loss']:.3f} m ({results['pipe_friction_loss']/results['total_dynamic_loss']*100:.1f}%)")
            st.write(f"• Fittings loss: {results['fittings_loss']:.3f} m ({results['fittings_loss']/results['total_dynamic_loss']*100:.1f}%)")
            
            st.markdown("#### Step 5: Total Head Demand")
            st.write("**Modified Bernoulli equation:**")
            st.latex(r'H_{demand} = \Delta z + H_{friction}')
            st.write("\n**Assumptions:**")
            st.write("• Both reservoirs open to atmosphere: p₁ = p₂ = p_atm")
            st.write("• Large reservoirs: V₁ ≈ V₂ ≈ 0")
            
            st.write(f"\n**Calculation:**")
            st.write(f"H_demand = {results['static_head']:.1f} + {results['total_dynamic_loss']:.3f}")
            st.write(f"H_demand = **{results['total_head_demand']:.3f} m**")
            
            st.markdown("#### Step 6: Power Requirements")
            st.write("**Hydraulic power:**")
            st.latex(r'P_{hydraulic} = \rho g Q H_{demand}')
            st.write(f"P_hyd = {rho} × 9.81 × {Q:.6f} × {results['total_head_demand']:.3f}")
            st.write(f"P_hyd = **{results['power_hydraulic']:.2f} W** = {results['power_hydraulic']/1000:.3f} kW")
            
            st.write("\n**Actual power (accounting for pump efficiency):**")
            st.latex(r'P_{actual} = \frac{P_{hydraulic}}{\eta}')
            st.write(f"• At η=80%: P = {results['power_hydraulic']/1000:.3f} / 0.80 = **{results['power_80']:.2f} kW**")
            st.write(f"• At η=70%: P = {results['power_hydraulic']/1000:.3f} / 0.70 = **{results['power_70']:.2f} kW**")
            st.write(f"• At η=60%: P = {results['power_hydraulic']/1000:.3f} / 0.60 = **{results['power_60']:.2f} kW**")
            
            st.markdown("### Physical Interpretation")
            
            total_head = results['total_head_demand']
            static_pct = (results['static_head'] / total_head) * 100
            friction_pct = (results['total_dynamic_loss'] / total_head) * 100
            
            if static_pct > 70:
                st.success(f"🏔️ **Static-dominated system** ({static_pct:.1f}%): Head requirement mainly due to elevation. Friction losses are minor.")
            elif friction_pct > 50:
                st.warning(f"🔧 **Friction-dominated system** ({friction_pct:.1f}%): Consider larger diameter to reduce losses.")
            else:
                st.info(f"⚖️ **Balanced system**: Static {static_pct:.1f}%, Friction {friction_pct:.1f}%")
            
            if results['velocity'] > 3:
                st.warning(f"⚠️ **High velocity** ({results['velocity']:.2f} m/s): Consider larger pipe to reduce friction and erosion.")
            elif results['velocity'] < 0.5:
                st.info(f"🐌 **Low velocity** ({results['velocity']:.2f} m/s): System may be oversized.")
            else:
                st.success(f"✅ **Good velocity** ({results['velocity']:.2f} m/s): Within recommended range (0.5-3 m/s).")

    # --- Column 2: Visualization ---
    with col2:
        st.header("🖼️ Visualization")
        
        # Create system diagram
        fig = go.Figure()
        
        # Scale factors for visualization
        pipe_height = z2
        pipe_width = 10
        
        # Draw Reservoir 1 (ground level)
        reservoir1_width = 3
        reservoir1_height = 2
        fig.add_shape(type="rect", x0=0, y0=z1, x1=reservoir1_width, y1=z1+reservoir1_height,
                     fillcolor="lightblue", line=dict(color="darkblue", width=2))
        fig.add_annotation(x=reservoir1_width/2, y=z1+reservoir1_height/2, text="<b>Reservoir 1</b>",
                          showarrow=False, font=dict(size=12, color="darkblue"))
        
        # Draw pipe from reservoir 1 to reservoir 2
        pipe_x = [reservoir1_width, reservoir1_width, pipe_width-reservoir1_width, pipe_width-reservoir1_width]
        pipe_y = [z1+reservoir1_height/2, z2+reservoir1_height/2, z2+reservoir1_height/2, z1+reservoir1_height/2]
        fig.add_trace(go.Scatter(x=pipe_x, y=pipe_y, fill="toself", fillcolor="gray",
                                line=dict(color="black", width=2), mode='lines', showlegend=False))
        
        # Add pump symbol
        pump_x = reservoir1_width + 1
        pump_y = z1 + reservoir1_height/2
        fig.add_shape(type="circle", x0=pump_x-0.3, y0=pump_y-0.3, x1=pump_x+0.3, y1=pump_y+0.3,
                     fillcolor="orange", line=dict(color="darkorange", width=2))
        fig.add_annotation(x=pump_x, y=pump_y, text="⚡<br>PUMP", showarrow=False,
                          font=dict(size=10, color="white"))
        
        # Draw Reservoir 2
        fig.add_shape(type="rect", x0=pipe_width-reservoir1_width, y0=z2, 
                     x1=pipe_width, y1=z2+reservoir1_height,
                     fillcolor="lightblue", line=dict(color="darkblue", width=2))
        fig.add_annotation(x=pipe_width-reservoir1_width/2, y=z2+reservoir1_height/2,
                          text="<b>Reservoir 2</b>", showarrow=False,
                          font=dict(size=12, color="darkblue"))
        
        # Elevation annotations
        fig.add_annotation(x=-0.5, y=z1, text=f"z₁ = {z1} m", showarrow=False,
                          font=dict(size=11, color="blue"))
        fig.add_annotation(x=pipe_width+0.5, y=z2, text=f"z₂ = {z2} m", showarrow=False,
                          font=dict(size=11, color="blue"))
        
        # Elevation difference arrow
        fig.add_shape(type="line", x0=pipe_width+1, y0=z1, x1=pipe_width+1, y1=z2,
                     line=dict(color="red", width=3, dash="dash"))
        fig.add_annotation(x=pipe_width+1.5, y=(z1+z2)/2, text=f"<b>Δz = {z2-z1} m</b>",
                          showarrow=False, font=dict(size=13, color="red"),
                          textangle=90, bgcolor="rgba(255,255,255,0.8)")
        
        # System specs
        specs_text = f"<b>Pipe:</b> L={L}m, D={D_mm}mm, ε={epsilon*1000:.3f}mm<br>"
        specs_text += f"<b>Flow:</b> Q={Q_m3h:.1f} m³/h, V={results['velocity']:.2f} m/s<br>"
        specs_text += f"<b>Head:</b> H={results['total_head_demand']:.2f} m"
        fig.add_annotation(x=pipe_width/2, y=z1-3, text=specs_text, showarrow=False,
                          font=dict(size=10), bgcolor="rgba(255,255,255,0.9)",
                          bordercolor="gray", borderwidth=1)
        
        fig.update_layout(
            title="<b>Two-Reservoir Pumping System</b>",
            xaxis=dict(range=[-1, pipe_width+2], showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(range=[z1-4, z2+3], title="<b>Elevation (m)</b>"),
            showlegend=False,
            height=500,
            plot_bgcolor='rgba(240,248,255,0.5)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Pie chart of head loss breakdown
        st.subheader("Head Loss Breakdown")
        
        labels = ['Static Head', 'Pipe Friction', 'Fittings Loss']
        values = [results['static_head'], results['pipe_friction_loss'], results['fittings_loss']]
        colors = ['lightblue', 'orange', 'red']
        
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4,
                                         marker_colors=colors)])
        fig_pie.update_layout(
            annotations=[dict(text='Head<br>Components', x=0.5, y=0.5, font_size=14, showarrow=False)],
            height=400
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Fittings table if any selected
        if selected_fittings:
            st.subheader("Selected Fittings")
            fittings_data = []
            for name, data in selected_fittings.items():
                fittings_data.append({
                    "Fitting": f"{data['icon']} {name}",
                    "Qty": data['quantity'],
                    "Le/D (n)": data['n'],
                    "Total n": data['n'] * data['quantity'],
                    "Le (m)": f"{D * data['n'] * data['quantity']:.2f}"
                })
            st.table(pd.DataFrame(fittings_data))

with tab2:
    st.header("📚 Understanding Pump Head Demand")
    
    col_edu1, col_edu2 = st.columns([1, 1])
    
    with col_edu1:
        st.markdown("""
        ### What is Pump Head?
        
        **Pump head** is the height to which a pump can raise a column of fluid. It represents the 
        **total energy per unit weight** that the pump must provide to move fluid through the system.
        
        Units: meters (m) of fluid column
        
        ### The Energy Equation (Modified Bernoulli)
        
        For a pumping system between two reservoirs:
        """)
        
        st.latex(r'H_{pump} = \Delta z + H_{friction}')
        
        st.markdown("""
        Where:
        - **Δz** = z₂ - z₁ (elevation difference)
        - **H_friction** = Total head loss due to friction
        
        ### Why These Components?
        
        **1. Static Head (Δz):**
        - Work against gravity
        - Independent of flow rate
        - Fixed by system geometry
        - **Cannot be reduced** without changing elevation
        
        **2. Dynamic Head (H_friction):**
        - Work against friction
        - Increases with flow rate (∝ V²)
        - Depends on pipe roughness and length
        - **Can be reduced** by:
          - Larger diameter pipe
          - Smoother pipe material
          - Fewer/better fittings
          - Shorter pipe length
        """)
    
    with col_edu2:
        st.markdown("""
        ### Friction Loss Calculation
        
        The **Darcy-Weisbach equation** calculates friction loss:
        """)
        
        st.latex(r'H_f = f \frac{L}{D} \frac{V^2}{2g}')
        
        st.markdown("""
        Where:
        - **f** = friction factor (depends on Re and ε/D)
        - **L** = pipe length (m)
        - **D** = pipe diameter (m)
        - **V** = flow velocity (m/s)
        - **g** = gravity (9.81 m/s²)
        
        ### The Equivalent Length Method
        
        **Minor losses** from fittings are converted to equivalent pipe length:
        """)
        
        st.latex(r'L_e = L_{pipe} + D \sum (n \times quantity)')
        
        st.markdown("""
        Where **n** is the **loss coefficient** (Le/D) for each fitting type.
        
        **Advantages:**
        - Simple: treat all losses as pipe friction
        - Single friction factor f for entire system
        - Easy to add/remove fittings
        
        ### Friction Factor Determination
        
        **Laminar flow** (Re < 2300):
        """)
        st.latex(r'f = \frac{64}{Re}')
        
        st.markdown("""
        **Turbulent flow** (Re > 4000):
        
        Use Moody diagram or Churchill equation:
        - Depends on **Reynolds number** (Re)
        - Depends on **relative roughness** (ε/D)
        - Iterative solution required
        
        ### Power Requirements
        
        **Hydraulic power:**
        """)
        st.latex(r'P_{hyd} = \rho g Q H')
        
        st.markdown("""
        **Actual power (with pump efficiency η):**
        """)
        st.latex(r'P_{actual} = \frac{P_{hyd}}{\eta}')
        
        st.markdown("""
        Typical pump efficiencies:
        - Small pumps: 50-70%
        - Medium pumps: 70-85%
        - Large pumps: 80-90%
        """)
    
    st.markdown("---")
    
    st.markdown("### Key Concepts")
    
    concept_col1, concept_col2, concept_col3 = st.columns(3)
    
    with concept_col1:
        st.markdown("""
        #### Reynolds Number
        
        Determines flow regime:
        """)
        st.latex(r'Re = \frac{VD}{\nu}')
        
        st.markdown("""
        - Re < 2300: Laminar
        - 2300 < Re < 4000: Transitional
        - Re > 4000: Turbulent
        
        Most pumping systems operate in **turbulent** regime.
        """)
    
    with concept_col2:
        st.markdown("""
        #### Pipe Sizing Trade-offs
        
        **Larger diameter:**
        - ✅ Lower friction loss
        - ✅ Lower velocity
        - ✅ Reduced pump power
        - ❌ Higher pipe cost
        - ❌ More space required
        
        **Optimal diameter** balances capital cost vs operating cost.
        """)
    
    with concept_col3:
        st.markdown("""
        #### System Curve
        
        Head demand vs flow rate:
        """)
        st.latex(r'H = \Delta z + K Q^2')
        
        st.markdown("""
        - Static head: constant
        - Friction: quadratic with Q
        - Intersection with **pump curve** determines operating point
        """)
    
    st.markdown("---")
    
    st.markdown("### Common Design Mistakes")
    
    mistake_col1, mistake_col2 = st.columns(2)
    
    with mistake_col1:
        st.error("""
        **❌ WRONG: "Pump only needs to overcome elevation"**
        
        Ignoring friction losses.
        
        **✅ CORRECT:** Pump must overcome BOTH:
        - Static head (elevation)
        - Dynamic head (friction)
        
        Friction can be 10-50% of total head!
        """)
        
        st.error("""
        **❌ WRONG: "All fittings have similar losses"**
        
        Treating all fittings equally.
        
        **✅ CORRECT:** Fitting losses vary hugely:
        - Ball valve: n = 3 (minimal)
        - 90° elbow: n = 35 (moderate)
        - Globe valve: n = 180 (large!)
        - Gate valve (1/4 open): n = 800 (huge!)
        
        Partially closed valves can dominate system losses!
        """)
    
    with mistake_col2:
        st.error("""
        **❌ WRONG: "Friction loss is proportional to length"**
        
        Linear thinking about losses.
        
        **✅ CORRECT:** Loss relationships:
        - H_f ∝ L (linear with length)
        - H_f ∝ 1/D (inverse with diameter)
        - H_f ∝ V² ∝ Q² (quadratic with flow!)
        
        Doubling flow rate quadruples friction loss!
        """)
        
        st.error("""
        **❌ WRONG: "Pump efficiency doesn't matter much"**
        
        Ignoring long-term operating costs.
        
        **✅ CORRECT:** Over pump lifetime:
        - Energy cost >> initial pump cost
        - 10% efficiency improvement can save thousands
        - Proper sizing crucial for efficiency
        """)

with tab3:
    st.header("📋 Real-World Applications")
    
    st.markdown("""
    Pump systems are ubiquitous in industry, agriculture, and municipal infrastructure.
    Understanding head demand is essential for proper pump selection and system design.
    """)
    
    app_col1, app_col2 = st.columns(2)
    
    with app_col1:
        st.markdown("""
        ### Water Supply Systems
        
        **1. Municipal Water Distribution**
        - **Typical head**: 40-100 m (4-10 bar pressure)
        - **Pipe size**: 100-600 mm mains
        - **Flow rates**: 50-500 m³/h
        - **Challenges**:
          - Variable demand throughout day
          - Long distribution networks
          - Aging infrastructure (increasing roughness)
          - Pressure management
        - **Design considerations**:
          - Multiple pumps for redundancy
          - Variable speed drives for efficiency
          - Pressure zones for tall buildings
        
        **2. Building Water Supply**
        - **Typical head**: 20-80 m (depending on building height)
        - **Pipe size**: 50-150 mm
        - **Rule of thumb**: 4 m head per floor + pressure + friction
        - **System types**:
          - Direct pumping (small buildings)
          - Roof tank + gravity (medium buildings)
          - Booster pumps on floors (tall buildings)
        - **Key issue**: Peak demand vs average demand
        
        **3. Irrigation Systems**
        - **Typical head**: 10-50 m
        - **Pipe size**: 75-250 mm
        - **Flow rates**: 20-200 m³/h
        - **Special considerations**:
          - Seasonal operation
          - Often long horizontal runs
          - Multiple outlets (sprinklers/drippers)
          - Elevation changes in fields
        - **Energy cost**: Major operating expense
        
        **4. Fire Protection**
        - **Typical head**: 60-100 m minimum
        - **Pipe size**: 100-200 mm
        - **Flow rates**: 100-500 m³/h (very high!)
        - **Critical requirements**:
          - Must work during power outage (diesel backup)
          - Regular testing mandatory
          - Oversized for safety margin
          - Jockey pump maintains pressure
        
        ### Industrial Processes
        
        **5. Chemical Plants**
        - **Applications**: Reactor feed, product transfer, cooling
        - **Challenges**:
          - Corrosive fluids (special materials)
          - High temperatures (thermal expansion)
          - Precise flow control needed
          - Safety critical (ATEX zones)
        - **Pump types**: Centrifugal, positive displacement
        
        **6. Oil & Gas**
        - **Pipeline transport**: Very high head (100-500 m)
        - **Well injection**: Extremely high pressure
        - **Offshore platforms**: Compact, reliable pumps needed
        - **Considerations**:
          - Viscosity variations
          - Multiphase flow (oil/water/gas)
          - Remote locations (maintenance difficulty)
        
        **7. Mining Dewatering**
        - **Typical head**: 50-300 m (deep mines)
        - **Harsh conditions**: Abrasive slurries, solids
        - **High reliability needed**: Flooding risk
        - **Multiple stages**: Sump pumps at different levels
        - **Large powers**: Can exceed 1000 kW
        """)
    
    with app_col2:
        st.markdown("""
        ### Specialized Applications
        
        **8. Wastewater Treatment**
        - **Raw sewage pumping**: Handles solids, rags
        - **Sludge transfer**: Very viscous, high head
        - **Aeration**: Large volume, low head
        - **Design challenges**:
          - Clogging prevention
          - Corrosive environment (H₂S)
          - Variable flow rates
          - Energy optimization (largest operating cost)
        
        **9. HVAC Systems**
        - **Chilled water**: 10-30 m head typical
        - **Hot water**: Similar, but thermal expansion issues
        - **Condenser water**: Cooling tower circuits
        - **Characteristics**:
          - Closed loop (no static head!)
          - Only friction losses
          - Variable speed for part-load efficiency
        
        **10. Hydraulic Systems**
        - **High pressure**: 100-300 bar (1000-3000 m head!)
        - **Small flow rates**: 1-50 L/min
        - **Applications**: Construction equipment, manufacturing
        - **Pumps**: Positive displacement (piston, gear)
        
        ### Agricultural Applications
        
        **11. Well Pumping**
        - **Submersible pumps** in well
        - **Typical depth**: 20-200 m
        - **Domestic**: 2-5 m³/h
        - **Agricultural**: 10-50 m³/h
        - **Key factors**:
          - Well yield (sustainable flow)
          - Water table fluctuation
          - Pump placement depth
          - Cable run losses
        
        **12. Center Pivot Irrigation**
        - **Large systems**: 50-150 ha coverage
        - **Flow rates**: 50-200 m³/h
        - **Low pressure**: Modern designs use <20 m
        - **Efficiency critical**: Energy cost major expense
        - **Design**: Minimize friction with large pipes
        
        ### Design Guidelines
        
        #### Pipe Velocity Recommendations
        
        | Application | Recommended Velocity |
        |------------|---------------------|
        | Suction lines | 0.5-1.5 m/s |
        | Water supply | 1.0-3.0 m/s |
        | Industrial process | 1.5-3.5 m/s |
        | Fire protection | 3.0-6.0 m/s |
        | Slurries | 2.0-4.0 m/s |
        
        #### Common Pipe Materials
        
        | Material | Roughness (mm) | Applications |
        |----------|---------------|-------------|
        | PVC | 0.0015 | Cold water, drainage |
        | PE (polyethylene) | 0.0015 | Irrigation, gas |
        | Steel (new) | 0.045 | General industrial |
        | Steel (used) | 0.15 | Aging systems |
        | Cast iron | 0.26-2.0 | Water mains |
        | Concrete | 0.3-3.0 | Large diameter |
        
        #### Pump Selection Criteria
        
        1. **Flow rate** (Q): Maximum required
        2. **Head** (H): Static + dynamic + safety margin
        3. **Efficiency**: High efficiency at design point
        4. **NPSH**: Net Positive Suction Head available
        5. **Materials**: Compatible with fluid
        6. **Duty cycle**: Continuous vs intermittent
        7. **Reliability**: Criticality of application
        8. **Cost**: Initial + operating (energy!)
        
        #### Energy Saving Strategies
        
        - **Proper sizing**: Don't oversize!
        - **Variable speed drives**: Match demand
        - **Parallel pumps**: Run optimal number
        - **Pipe sizing**: Reduce friction
        - **Reduce fittings**: Every elbow costs energy
        - **Regular maintenance**: Keep efficiency high
        - **System optimization**: Reduce head demand
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Case Study: Optimizing an Irrigation System
    
    **Initial Design:**
    - Static head: 20 m
    - Pipe: 100 mm diameter, 1000 m length, old steel (ε=0.15 mm)
    - Flow: 50 m³/h
    - Fittings: 20× 90° elbows, 5× gate valves
    
    **Calculated head**: 42 m, Power: 7.2 kW, Annual cost: $12,000
    
    **Optimized Design:**
    - Same static head: 20 m
    - Pipe: 125 mm diameter, same length, PVC (ε=0.0015 mm)
    - Flow: Same 50 m³/h
    - Fittings: 10× long radius elbows, 3× ball valves
    
    **New head**: 27 m, Power: 4.6 kW, Annual cost: $7,800
    
    **Savings**: 36% energy reduction, pays back pipe upgrade in 2-3 years!
    """)

st.markdown("---")
st.info("💡 **Tip**: Use the Interactive Simulation tab to experiment with different system configurations and see how each parameter affects total head demand!")

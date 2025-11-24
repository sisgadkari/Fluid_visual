import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Turbine Power Calculator", layout="wide")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>⚡ Hydroelectric Turbine Power Calculator</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
Calculate power generation from gravity-driven water turbines. Understand how head, flow rate, 
and system losses affect electricity production.
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# Create tabs for different aspects
tab1, tab2, tab3 = st.tabs(["🎯 Interactive Simulation", "📚 Understanding Turbines", "📋 Real-World Applications"])

def calculate_friction_factor(reynolds, relative_roughness):
    """Calculate friction factor using Churchill equation"""
    if reynolds < 2300:  # Laminar
        return 64 / reynolds
    else:  # Turbulent - Churchill equation
        A = (2.457 * np.log(1 / ((7/reynolds)**0.9 + 0.27 * relative_roughness)))**16
        B = (37530 / reynolds)**16
        f = 8 * ((8/reynolds)**12 + 1/(A + B)**(3/2))**(1/12)
        return f

def get_fittings_equivalent_length(inlet_type, elbow_type, num_elbows, valve_type, num_valves, exit_type, D):
    """Calculate equivalent length from fittings"""
    Le_total = 0
    
    # Inlet contributions
    inlet_n = {"Radius inlet": 0, "Sharp inlet": 25, "Re-entrant inlet": 50}
    Le_total += D * inlet_n.get(inlet_type, 0)
    
    # Elbow contributions
    elbow_n = {"90° Long Radius Elbow": 23, "90° Standard Elbow": 35, "45° Elbow": 16}
    Le_total += D * elbow_n.get(elbow_type, 35) * num_elbows
    
    # Valve contributions
    valve_n = {"Fully open": 7, "3/4 open": 40, "1/2 open": 200, "1/4 open": 800}
    Le_total += D * valve_n.get(valve_type, 0) * num_valves
    
    # Exit contributions
    exit_n = {"Smooth exit": 0, "Sharp pipe exit": 50}
    Le_total += D * exit_n.get(exit_type, 0)
    
    return Le_total

def calculate_turbine_system(Q, D, L, epsilon, H_static, eta_turbine, Le_fittings):
    """Calculate complete turbine system performance"""
    # Flow characteristics
    A = np.pi * (D/2)**2
    V = Q / A if A > 0 else 0
    nu = 1e-6  # Water kinematic viscosity at 20°C
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
    
    # Equivalent length
    Le_total = L + Le_fittings
    
    # Head losses using Darcy-Weisbach
    if V > 0 and D > 0:
        h_loss_total = f * (4 * Le_total / D) * (V**2 / (2 * 9.81))
        h_loss_pipe = f * (4 * L / D) * (V**2 / (2 * 9.81))
        h_loss_fittings = h_loss_total - h_loss_pipe
    else:
        h_loss_total = 0
        h_loss_pipe = 0
        h_loss_fittings = 0
    
    # Net turbine head
    H_turbine = H_static - h_loss_total
    
    # Power calculations
    rho = 1000  # kg/m³
    P_hydraulic = rho * 9.81 * Q * H_turbine / 1000  # kW
    P_shaft = P_hydraulic * eta_turbine  # kW
    E_annual = P_shaft * 8760 / 1000  # MWh/year
    
    return {
        'velocity': V,
        'reynolds': Re,
        'flow_regime': regime,
        'friction_factor': f,
        'static_head': H_static,
        'pipe_friction_loss': h_loss_pipe,
        'fittings_loss': h_loss_fittings,
        'total_head_loss': h_loss_total,
        'turbine_head': H_turbine,
        'equivalent_length': Le_total,
        'hydraulic_power': P_hydraulic,
        'shaft_power': P_shaft,
        'annual_energy': E_annual,
        'system_efficiency': (H_turbine / H_static * 100) if H_static > 0 else 0
    }

def recommend_turbine_type(head, flow):
    """Recommend turbine type based on head and flow"""
    specific_speed = (flow**0.5) / (head**0.75)  # Simplified Ns calculation
    
    if head > 300:
        return "Pelton Wheel (High head, low flow)"
    elif head > 100:
        if flow > 5:
            return "Francis Turbine (Medium head, medium flow)"
        else:
            return "Pelton Wheel or Francis Turbine"
    elif head > 30:
        return "Francis Turbine (Medium head, medium-high flow)"
    elif head > 10:
        return "Kaplan Turbine (Low head, high flow)"
    else:
        return "Kaplan or Propeller Turbine (Very low head, very high flow)"

with tab1:
    # --- Main Layout ---
    col1, col2 = st.columns([2, 3])

    # --- Column 1: Inputs and Results ---
    with col1:
        st.header("🔬 Parameters")
        
        # --- Interactive Scenarios ---
        SCENARIOS = {
            "Custom...": {
                "H": 110, "Q": 0.4, "D": 500, "L": 300, "material": "Commercial steel (new)",
                "eta": 95, "desc": "Manually adjust all parameters below."
            },
            "Small Hydro Plant": {
                "H": 150, "Q": 0.8, "D": 600, "L": 500, "material": "Commercial steel (new)",
                "eta": 90, "desc": "150m head, 800 L/s flow. Typical small hydroelectric facility."
            },
            "Micro Hydro System": {
                "H": 50, "Q": 0.15, "D": 250, "L": 200, "material": "PVC",
                "eta": 85, "desc": "Small off-grid installation. 50m head, 150 L/s flow."
            },
            "High Head Alpine": {
                "H": 400, "Q": 0.3, "D": 400, "L": 1000, "material": "Commercial steel (new)",
                "eta": 92, "desc": "Mountain hydropower. Very high head, moderate flow."
            },
            "Low Head Run-of-River": {
                "H": 20, "Q": 2.0, "D": 1000, "L": 150, "material": "Concrete (smooth)",
                "eta": 88, "desc": "River-based system. Low head, very high flow rate."
            },
            "Pumped Storage": {
                "H": 300, "Q": 1.5, "D": 800, "L": 800, "material": "Commercial steel (used)",
                "eta": 87, "desc": "Energy storage facility. High head, high flow, reversible."
            }
        }
        
        scenario = st.selectbox("Select Application Scenario", list(SCENARIOS.keys()))
        selected = SCENARIOS[scenario]
        st.info(selected["desc"])
        
        st.subheader("System Elevation")
        H_static = st.slider("Static Head (m)", 10, 500, selected["H"], 5,
                            help="Vertical height from reservoir surface to turbine discharge")
        
        st.subheader("Pipe Specifications (Penstock)")
        c1, c2 = st.columns(2)
        with c1:
            L = st.slider("Pipe Length (m)", 50, 2000, selected["L"], 50,
                         help="Total length of penstock")
        with c2:
            D_mm = st.slider("Pipe Diameter (mm)", 100, 1500, selected["D"], 50,
                            help="Internal diameter")
            D = D_mm / 1000  # Convert to meters
        
        st.subheader("Pipe Material & Roughness")
        roughness_options = {
            "Smooth steel (new)": 0.05e-3,
            "Commercial steel (new)": 0.045e-3,
            "Commercial steel (used)": 0.15e-3,
            "Galvanized iron": 0.15e-3,
            "Cast iron (new)": 0.26e-3,
            "Cast iron (used)": 2.0e-3,
            "Concrete (smooth)": 0.3e-3,
            "Concrete (rough)": 3.0e-3,
            "PVC": 0.0015e-3,
            "Riveted steel": 1.0e-3
        }
        
        material = st.selectbox("Pipe Material", list(roughness_options.keys()),
                               index=list(roughness_options.keys()).index(selected["material"]))
        epsilon = roughness_options[material]
        st.caption(f"Surface roughness: ε = {epsilon*1000:.4f} mm")
        
        st.subheader("Operating Conditions")
        c1, c2 = st.columns(2)
        with c1:
            Q = st.number_input("Flow Rate (m³/s)", 0.05, 5.0, selected["Q"], 0.05,
                               help="Water flow through turbine")
        with c2:
            Q_Ls = Q * 1000
            st.metric("Flow Rate", f"{Q_Ls:.1f} L/s")
        
        st.subheader("Turbine Performance")
        eta_turbine = st.slider("Turbine Efficiency (%)", 70, 98, selected["eta"], 1,
                               help="Overall turbine efficiency") / 100
        
        st.subheader("Fittings & Minor Losses")
        
        with st.expander("Inlet/Exit"):
            inlet_type = st.selectbox("Reservoir Inlet", ["Radius inlet", "Sharp inlet", "Re-entrant inlet"])
            exit_type = st.selectbox("Pipe Exit to Turbine", ["Smooth exit", "Sharp pipe exit"])
        
        with st.expander("Bends"):
            elbow_type = st.selectbox("Elbow Type", ["90° Long Radius Elbow", "90° Standard Elbow", "45° Elbow"])
            num_elbows = st.number_input("Number of Elbows", 0, 10, 1, 1)
        
        with st.expander("Valves"):
            valve_type = st.selectbox("Gate Valve Opening", ["Fully open", "3/4 open", "1/2 open", "None"])
            num_valves = 0 if valve_type == "None" else st.number_input("Number of Gate Valves", 0, 5, 1, 1)
        
        # Calculate equivalent length from fittings
        Le_fittings = get_fittings_equivalent_length(inlet_type, elbow_type, num_elbows, 
                                                     valve_type, num_valves, exit_type, D)
        
        # Calculate results
        results = calculate_turbine_system(Q, D, L, epsilon, H_static, eta_turbine, Le_fittings)
        
        st.markdown("---")
        st.header("📈 Results Summary")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("**SHAFT POWER OUTPUT**", f"{results['shaft_power']:.1f} kW",
                     help="Actual power output after turbine efficiency")
            st.metric("Net Turbine Head", f"{results['turbine_head']:.1f} m")
        with col_r2:
            st.metric("Annual Energy Production", f"{results['annual_energy']:.1f} MWh",
                     help="At 100% capacity factor")
            st.metric("Hydraulic Power", f"{results['hydraulic_power']:.1f} kW")
        
        col_r3, col_r4 = st.columns(2)
        with col_r3:
            st.metric("Water Velocity", f"{results['velocity']:.2f} m/s")
            st.metric("Reynolds Number", f"{results['reynolds']:,.0f}")
        with col_r4:
            st.metric("Flow Regime", results['flow_regime'])
            st.metric("System Efficiency", f"{results['system_efficiency']:.1f}%",
                     help="Net head / Gross head")
        
        st.markdown("---")
        st.header("🧮 Step-by-Step Calculation")
        
        with st.expander("📖 See Detailed Breakdown", expanded=False):
            st.markdown("### Turbine Power Calculation")
            
            st.markdown("#### Step 1: Calculate Flow Parameters")
            st.write(f"**Given:**")
            st.write(f"• Flow rate: Q = {Q:.3f} m³/s = {Q_Ls:.1f} L/s")
            st.write(f"• Pipe diameter: D = {D_mm} mm = {D:.3f} m")
            
            st.write(f"\n**Cross-sectional area:**")
            st.latex(r'A = \frac{\pi D^2}{4}')
            A = np.pi * (D/2)**2
            st.write(f"A = π × ({D:.3f}/2)² = {A:.6f} m²")
            
            st.write(f"\n**Flow velocity:**")
            st.latex(r'V = \frac{Q}{A}')
            st.write(f"V = {Q:.3f} / {A:.6f} = **{results['velocity']:.3f} m/s**")
            
            st.write(f"\n**Reynolds number:**")
            st.latex(r'Re = \frac{VD}{\nu}')
            nu = 1e-6
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
            st.write(f"**Fittings equivalent length:** L_fittings = {Le_fittings:.2f} m")
            st.latex(r'L_e = L_{pipe} + L_{fittings}')
            st.write(f"L_e = {L} + {Le_fittings:.2f} = **{results['equivalent_length']:.2f} m**")
            
            st.markdown("#### Step 4: Calculate Head Losses")
            
            st.write("**A. Gross static head:**")
            st.latex(r'H_{static} = z_{reservoir} - z_{turbine}')
            st.write(f"H_static = **{results['static_head']:.1f} m**")
            
            st.write("\n**B. Friction head loss (Darcy-Weisbach):**")
            st.latex(r'H_{loss} = f \frac{4L_e}{D} \frac{V^2}{2g}')
            st.write(f"H_loss = {results['friction_factor']:.5f} × (4×{results['equivalent_length']:.2f})/{D:.3f} × ({results['velocity']:.3f})²/(2×9.81)")
            st.write(f"H_loss = **{results['total_head_loss']:.3f} m**")
            
            st.write("\n**Breakdown:**")
            st.write(f"• Pipe friction: {results['pipe_friction_loss']:.3f} m ({results['pipe_friction_loss']/results['total_head_loss']*100:.1f}%)")
            st.write(f"• Fittings loss: {results['fittings_loss']:.3f} m ({results['fittings_loss']/results['total_head_loss']*100:.1f}%)")
            
            st.write("\n**C. Net turbine head:**")
            st.latex(r'H_{turbine} = H_{static} - H_{loss}')
            st.write(f"H_turbine = {results['static_head']:.1f} - {results['total_head_loss']:.3f}")
            st.write(f"H_turbine = **{results['turbine_head']:.3f} m**")
            
            st.markdown("#### Step 5: Calculate Power Output")
            st.write("**Hydraulic power (water power to turbine):**")
            st.latex(r'P_{hydraulic} = \rho g Q H_{turbine}')
            st.write(f"P_hyd = 1000 × 9.81 × {Q:.3f} × {results['turbine_head']:.3f}")
            st.write(f"P_hyd = **{results['hydraulic_power']:.2f} kW**")
            
            st.write("\n**Shaft power (actual electrical output):**")
            st.latex(r'P_{shaft} = P_{hydraulic} \times \eta_{turbine}')
            st.write(f"P_shaft = {results['hydraulic_power']:.2f} × {eta_turbine:.2f}")
            st.write(f"P_shaft = **{results['shaft_power']:.2f} kW**")
            
            st.write("\n**Annual energy production:**")
            st.latex(r'E_{annual} = P_{shaft} \times 8760 \text{ hours/year}')
            st.write(f"E_annual = {results['shaft_power']:.2f} × 8760 / 1000")
            st.write(f"E_annual = **{results['annual_energy']:.2f} MWh/year**")
            
            st.markdown("#### Step 6: System Assessment")
            st.write(f"**System efficiency:** {results['system_efficiency']:.1f}%")
            st.write(f"(Net head / Gross head = {results['turbine_head']:.1f} / {results['static_head']:.1f})")
            
            if results['system_efficiency'] > 90:
                st.success("✅ **Excellent system efficiency** - Very low losses")
            elif results['system_efficiency'] > 80:
                st.info("⚡ **Good system efficiency** - Acceptable losses")
            else:
                st.warning("⚠️ **Consider optimization** - High head losses reducing output")
            
            st.write(f"\n**Specific power:** {results['shaft_power']/Q:.0f} kW/(m³/s)")
            
            turbine_type = recommend_turbine_type(results['turbine_head'], Q)
            st.write(f"\n**Recommended turbine:** {turbine_type}")

    # --- Column 2: Visualization ---
    with col2:
        st.header("🖼️ Visualization")
        
        # Create system diagram
        fig = go.Figure()
        
        # Calculate reservoir dimensions that scale with head
        reservoir_width = 3
        reservoir_base_height = max(H_static * 0.08, 8)  # Scale with head, minimum 8m
        reservoir_base_height = min(reservoir_base_height, 25)  # Cap at 25m
        
        reservoir_base = H_static - 5
        reservoir_top = reservoir_base + reservoir_base_height
        water_level = reservoir_top * 0.95
        
        # Draw Reservoir
        # Tank structure
        fig.add_shape(type="rect", x0=0, y0=reservoir_base, x1=reservoir_width, y1=reservoir_top,
                     fillcolor="rgba(200,200,200,0.3)", line=dict(color="darkblue", width=3))
        
        # Water inside
        fig.add_shape(type="rect", x0=0.15, y0=reservoir_base+0.2, x1=reservoir_width-0.15, y1=water_level,
                     fillcolor="rgba(100,150,255,0.6)", line=dict(color="blue", width=2))
        
        # Reservoir label
        fig.add_annotation(x=reservoir_width/2, y=reservoir_top-reservoir_base_height*0.3,
                          text="<b>RESERVOIR</b><br>(Headwater)", showarrow=False,
                          font=dict(size=12, color="darkblue", family="Arial Black"),
                          bgcolor="rgba(255,255,255,0.8)", borderpad=4)
        
        # Penstock (pipe) - curved path
        penstock_start_x = reservoir_width
        penstock_start_y = water_level - 1
        penstock_end_x = 10
        penstock_end_y = 5
        
        # Create curved penstock
        t = np.linspace(0, 1, 100)
        penstock_x = penstock_start_x + (penstock_end_x - penstock_start_x) * t
        # Exponential curve for realistic profile
        penstock_y = penstock_start_y * (1 - t)**2 + penstock_end_y
        
        pipe_thickness = 0.2
        
        # Pipe outline
        fig.add_trace(go.Scatter(x=penstock_x, y=penstock_y + pipe_thickness,
                                mode='lines', line=dict(color='darkgray', width=4),
                                showlegend=False, hoverinfo='none'))
        fig.add_trace(go.Scatter(x=penstock_x, y=penstock_y - pipe_thickness,
                                mode='lines', line=dict(color='darkgray', width=4),
                                showlegend=False, hoverinfo='none'))
        
        # Water flow inside pipe
        flow_color = 'lightblue' if results['velocity'] < 4 else 'cyan' if results['velocity'] < 6 else 'orange'
        fig.add_trace(go.Scatter(x=penstock_x, y=penstock_y,
                                mode='lines', line=dict(color=flow_color, width=3),
                                showlegend=False, hoverinfo='none'))
        
        # Turbine house
        turbine_width = 2.5
        turbine_height = 4
        turbine_x = penstock_end_x - 0.5
        turbine_y = 2
        
        fig.add_shape(type="rect", x0=turbine_x, y0=turbine_y,
                     x1=turbine_x+turbine_width, y1=turbine_y+turbine_height,
                     fillcolor="rgba(169,169,169,0.8)", line=dict(color="black", width=3))
        
        # Turbine symbol (circle with blades)
        turbine_center_x = turbine_x + turbine_width/2
        turbine_center_y = turbine_y + turbine_height/2
        
        fig.add_shape(type="circle", x0=turbine_center_x-0.8, y0=turbine_center_y-0.8,
                     x1=turbine_center_x+0.8, y1=turbine_center_y+0.8,
                     fillcolor="rgba(255,215,0,0.9)", line=dict(color="orange", width=3))
        
        # Turbine blades
        for angle in [0, 60, 120, 180, 240, 300]:
            rad = np.radians(angle)
            blade_x = turbine_center_x + 0.6 * np.cos(rad)
            blade_y = turbine_center_y + 0.6 * np.sin(rad)
            fig.add_shape(type="line", x0=turbine_center_x, y0=turbine_center_y,
                         x1=blade_x, y1=blade_y, line=dict(color="darkred", width=3))
        
        # Generator symbol
        gen_x = turbine_center_x + 1.5
        gen_y = turbine_center_y
        fig.add_shape(type="circle", x0=gen_x-0.4, y0=gen_y-0.4,
                     x1=gen_x+0.4, y1=gen_y+0.4,
                     fillcolor="rgba(50,205,50,0.9)", line=dict(color="darkgreen", width=2))
        fig.add_annotation(x=gen_x, y=gen_y, text="<b>G</b>", showarrow=False,
                          font=dict(size=14, color="white", family="Arial Black"))
        
        # Turbine house label
        fig.add_annotation(x=turbine_center_x, y=turbine_y-0.5,
                          text="<b>TURBINE + GENERATOR</b>", showarrow=False,
                          font=dict(size=10, color="black"))
        
        # Discharge/Tailwater
        discharge_y = 0
        fig.add_shape(type="rect", x0=turbine_x, y0=discharge_y,
                     x1=turbine_x+turbine_width, y1=turbine_y,
                     fillcolor="rgba(100,150,255,0.3)", line=dict(color="blue", width=1))
        
        fig.add_annotation(x=turbine_center_x, y=discharge_y+0.5,
                          text="Tailwater", showarrow=False,
                          font=dict(size=9, color="blue"))
        
        # Head annotations
        arrow_x = 11
        
        # Gross head arrow
        fig.add_shape(type="line", x0=arrow_x, y0=water_level, x1=arrow_x, y1=discharge_y,
                     line=dict(color="red", width=3, dash="dash"))
        fig.add_annotation(x=arrow_x, y=water_level, ax=arrow_x, ay=water_level-reservoir_base_height*0.2,
                          arrowhead=2, arrowsize=1.5, arrowwidth=3, arrowcolor='red')
        fig.add_annotation(x=arrow_x, y=discharge_y, ax=arrow_x, ay=discharge_y+reservoir_base_height*0.2,
                          arrowhead=2, arrowsize=1.5, arrowwidth=3, arrowcolor='red')
        
        fig.add_annotation(x=arrow_x+0.8, y=water_level/2,
                          text=f"<b>Gross Head<br>H = {H_static} m</b>",
                          showarrow=False, font=dict(size=12, color="red", family="Arial Black"),
                          bgcolor="rgba(255,255,200,0.9)", bordercolor="red", borderwidth=2,
                          textangle=90, borderpad=6)
        
        # System specs
        specs_text = f"<b>📏 Penstock:</b> L = {L} m, D = {D_mm} mm<br>"
        specs_text += f"<b>💧 Flow:</b> Q = {Q:.2f} m³/s ({Q_Ls:.0f} L/s), V = {results['velocity']:.2f} m/s<br>"
        specs_text += f"<b>⚡ Power:</b> P<sub>shaft</sub> = {results['shaft_power']:.1f} kW, η = {eta_turbine*100:.0f}%"
        
        fig.add_annotation(x=5.5, y=reservoir_base-3, text=specs_text,
                          showarrow=False, font=dict(size=10),
                          bgcolor="rgba(255,255,255,0.95)", bordercolor="gray", borderwidth=2,
                          borderpad=8)
        
        # Update layout
        y_padding = reservoir_base_height * 0.4
        fig.update_layout(
            title={
                'text': "<b>⚡ Hydroelectric Turbine System</b>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': 'darkslategray', 'family': 'Arial Black'}
            },
            xaxis=dict(range=[-0.5, 12], showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(range=[discharge_y-2, reservoir_top+y_padding],
                      title="<b>Elevation (m)</b>",
                      title_font=dict(size=14, color="darkblue"),
                      showgrid=True, gridcolor='rgba(200,200,200,0.3)'),
            showlegend=False,
            height=600,
            plot_bgcolor='rgba(240,248,255,0.5)',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Energy breakdown pie chart
        st.subheader("Energy Distribution")
        
        labels = ['Shaft Power Output', 'Turbine Losses', 'Pipe Friction', 'Fittings Loss']
        values = [
            results['shaft_power'],
            results['hydraulic_power'] - results['shaft_power'],
            results['hydraulic_power'] * (results['pipe_friction_loss'] / H_static),
            results['hydraulic_power'] * (results['fittings_loss'] / H_static)
        ]
        colors = ['lightgreen', 'yellow', 'orange', 'red']
        
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4,
                                         marker_colors=colors)])
        fig_pie.update_layout(
            annotations=[dict(text='Power<br>Flow', x=0.5, y=0.5, font_size=14, showarrow=False)],
            height=400
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.header("📚 Understanding Hydroelectric Turbines")
    
    col_edu1, col_edu2 = st.columns([1, 1])
    
    with col_edu1:
        st.markdown("""
        ### What is a Hydraulic Turbine?
        
        A **hydraulic turbine** is a mechanical device that converts the energy of flowing water 
        into rotational mechanical energy, which drives a generator to produce electricity.
        
        ### The Energy Conversion Process
        
        **1. Potential Energy (stored in elevated water)**
        """)
        st.latex(r'E_{potential} = mgh = \rho g Q H t')
        
        st.markdown("""
        **2. Kinetic Energy (water flows through penstock)**
        - High-pressure water accelerates through pipe
        - Friction losses reduce available energy
        
        **3. Mechanical Energy (turbine rotation)**
        """)
        st.latex(r'P_{shaft} = \rho g Q H_{net} \eta_{turbine}')
        
        st.markdown("""
        **4. Electrical Energy (generator output)**
        """)
        st.latex(r'P_{electrical} = P_{shaft} \times \eta_{generator}')
        
        st.markdown("""
        ### Key Equations
        
        **Energy Equation (Modified Bernoulli):**
        """)
        st.latex(r'H_{gross} = H_{net} + H_{losses}')
        
        st.markdown("""
        Where:
        - **H_gross** = Gross static head (elevation difference)
        - **H_net** = Net head at turbine (after losses)
        - **H_losses** = Friction + minor losses
        
        **Turbine Power:**
        """)
        st.latex(r'P = \rho g Q H \eta')
        
        st.markdown("""
        Where:
        - **ρ** = Water density (1000 kg/m³)
        - **g** = Gravity (9.81 m/s²)
        - **Q** = Flow rate (m³/s)
        - **H** = Net head (m)
        - **η** = Turbine efficiency (0.85-0.95)
        """)
    
    with col_edu2:
        st.markdown("""
        ### Types of Hydraulic Turbines
        
        **1. Impulse Turbines**
        - **Pelton Wheel**: High head (>100m), low flow
          - Jet hits buckets on wheel periphery
          - Efficiency: 85-90%
          - Application: Mountain hydro plants
        
        - **Cross-Flow (Banki)**: Medium head, low flow
          - Water passes through blade twice
          - Simple design, robust
        
        **2. Reaction Turbines**
        - **Francis Turbine**: Medium head (30-300m)
          - Most common type worldwide
          - Efficiency: 90-95%
          - Wide operating range
        
        - **Kaplan Turbine**: Low head (<30m), high flow
          - Adjustable blades
          - Efficiency: 88-92%
          - Run-of-river applications
        
        - **Propeller Turbine**: Low head, high flow
          - Fixed blades (simpler than Kaplan)
          - Lower cost
        
        ### Turbine Selection Criteria
        
        | Head Range | Flow | Best Turbine |
        |-----------|------|--------------|
        | >300 m | Low | Pelton |
        | 100-300 m | Medium | Francis or Pelton |
        | 30-100 m | Medium-High | Francis |
        | 10-30 m | High | Kaplan |
        | <10 m | Very High | Kaplan/Propeller |
        
        ### Efficiency Factors
        
        **Turbine efficiency depends on:**
        - **Design point operation**: Peak efficiency at rated flow
        - **Part-load performance**: Efficiency drops at low flow
        - **Head variation**: Some designs more sensitive
        - **Cavitation**: Low pressure causes bubbles, damage
        - **Mechanical losses**: Bearings, seals
        - **Age/wear**: Erosion, corrosion reduce efficiency
        
        **Typical overall efficiencies:**
        - Pelton: 85-90%
        - Francis: 90-95%
        - Kaplan: 88-92%
        
        ### System Losses
        
        **Head losses reduce net power:**
        
        **1. Pipe friction** (major loss):
        """)
        st.latex(r'h_f = f \frac{L}{D} \frac{V^2}{2g}')
        
        st.markdown("""
        - Proportional to length
        - Inversely proportional to diameter
        - Quadratic with velocity
        
        **2. Minor losses** (fittings):
        - Bends, valves, inlet/outlet
        - Use equivalent length method
        - Can be 10-30% of total loss
        
        **Design strategy:** Minimize losses to maximize net head!
        - Large diameter penstock (expensive but efficient)
        - Smooth pipe material (low roughness)
        - Minimize bends and fittings
        - Gradual inlet and outlet
        """)
    
    st.markdown("---")
    
    st.markdown("### Hydroelectric Power Plant Components")
    
    comp_col1, comp_col2, comp_col3 = st.columns(3)
    
    with comp_col1:
        st.markdown("""
        #### Reservoir/Headpond
        - **Function**: Store water at elevation
        - **Types**:
          - Storage reservoir (dam)
          - Run-of-river (small pond)
          - Pumped storage (reversible)
        - **Design**: Adequate volume for demand
        
        #### Intake Structure
        - **Trash rack**: Filter debris
        - **Gate/valve**: Flow control
        - **Entrance**: Smooth, low-loss design
        """)
    
    with comp_col2:
        st.markdown("""
        #### Penstock
        - **Function**: Convey water under pressure
        - **Materials**:
          - Steel (high pressure)
          - Concrete (buried, low pressure)
          - HDPE/FRP (small systems)
        - **Considerations**:
          - Water hammer protection
          - Expansion joints
          - Support/anchoring
          - Surge tank (long penstocks)
        """)
    
    with comp_col3:
        st.markdown("""
        #### Powerhouse
        - **Turbine**: Energy converter
        - **Generator**: Electrical output
        - **Governor**: Flow/speed control
        - **Switchgear**: Protection, distribution
        
        #### Tailrace
        - **Function**: Discharge water
        - **Design**: Minimize backpressure
        - **Draft tube**: Recover kinetic energy
        """)
    
    st.markdown("---")
    
    st.markdown("### Common Design Mistakes")
    
    mistake_col1, mistake_col2 = st.columns(2)
    
    with mistake_col1:
        st.error("""
        **❌ WRONG: "More head always means more power"**
        
        Ignoring flow rate equally important.
        
        **✅ CORRECT:** Power = f(Q, H)
        - Doubling head doubles power (at same Q)
        - Doubling flow doubles power (at same H)
        - Both matter equally!
        - P ∝ Q × H
        """)
        
        st.error("""
        **❌ WRONG: "Small penstock saves money"**
        
        Undersizing pipe to reduce cost.
        
        **✅ CORRECT:** Friction loss ∝ 1/D⁵ (approx)
        - Small diameter = huge losses
        - Lost head = lost power = lost revenue
        - Optimal diameter balances cost vs efficiency
        - NPV analysis over 30-50 year lifetime
        - Larger pipe often pays back quickly
        """)
    
    with mistake_col2:
        st.error("""
        **❌ WRONG: "Turbine efficiency is constant"**
        
        Assuming peak efficiency at all conditions.
        
        **✅ CORRECT:** Efficiency varies with:
        - Flow rate (drops at part load)
        - Head (if different from design)
        - Age/wear (maintenance critical)
        - Cavitation (proper NPSH needed)
        
        Modern turbines: adjustable blades/guide vanes
        """)
        
        st.error("""
        **❌ WRONG: "Ignore minor losses"**
        
        Only considering pipe friction.
        
        **✅ CORRECT:** Fittings can be significant:
        - Sharp inlet: Le/D = 25
        - Each 90° elbow: Le/D = 35
        - Globe valve: Le/D = 180 (!!)
        
        For short penstocks, fittings dominate!
        Always use equivalent length method.
        """)

with tab3:
    st.header("📋 Real-World Applications")
    
    st.markdown("""
    Hydroelectric power is the world's largest source of renewable electricity, providing about 
    16% of global electricity generation. From massive dams to tiny micro-hydro systems, turbines 
    convert the energy of flowing water into clean, reliable power.
    """)
    
    app_col1, app_col2 = st.columns(2)
    
    with app_col1:
        st.markdown("""
        ### Large-Scale Hydroelectric Dams
        
        **1. Major Power Plants**
        - **Typical capacity**: 1000-20,000 MW
        - **Head**: 50-250 m
        - **Flow**: 100-1000 m³/s
        - **Turbine type**: Francis (multiple units)
        - **Examples**:
          - Three Gorges Dam (China): 22,500 MW
          - Itaipu Dam (Brazil/Paraguay): 14,000 MW
          - Hoover Dam (USA): 2,080 MW
        - **Characteristics**:
          - Large reservoir for storage
          - Flood control benefit
          - Navigation locks
          - Long-term investment (50-100 years)
        
        **2. Pumped Storage**
        - **Function**: Energy storage
        - **Operation**: 
          - Pump water uphill (off-peak)
          - Generate power (peak demand)
        - **Typical efficiency**: 70-85% round-trip
        - **Head**: 200-500 m
        - **Reversible turbines**: Francis design
        - **Benefits**:
          - Grid stability
          - Load balancing
          - Renewable integration
        - **Examples**:
          - Bath County (USA): 3,003 MW
          - Dinorwig (UK): 1,728 MW
        
        **3. Run-of-River**
        - **No large reservoir**: Minimal storage
        - **Typical capacity**: 10-500 MW
        - **Head**: 10-50 m (usually low)
        - **Flow**: River's natural flow
        - **Environmental**: Less ecological impact
        - **Limitation**: Output varies with river flow
        - **Turbine**: Kaplan (adjustable for flow variation)
        
        ### Small & Micro Hydropower
        
        **4. Small Hydro (1-10 MW)**
        - **Applications**: 
          - Small communities
          - Industrial facilities
          - Grid-connected or standalone
        - **Head**: 20-100 m
        - **Flow**: 1-20 m³/s
        - **Turbine**: Francis or Pelton
        - **Economics**: 
          - Lower capital cost than large dams
          - Faster project development
          - Feed-in tariffs in many countries
        
        **5. Mini Hydro (100 kW - 1 MW)**
        - **Applications**:
          - Villages, farms
          - Remote mining operations
          - Tourist facilities
        - **Head**: 10-100 m
        - **Flow**: 0.2-5 m³/s
        - **Turbine**: Crossflow, Francis, Pelton
        - **Advantages**:
          - Modular equipment
          - Local manufacturing possible
          - Lower environmental impact
        
        **6. Micro Hydro (<100 kW)**
        - **Applications**:
          - Single household or farm
          - Remote communities (off-grid)
          - Telecommunications repeater
        - **Head**: 5-50 m
        - **Flow**: 0.01-0.5 m³/s
        - **Turbine**: Crossflow, Pelton, Turgo
        - **Power**: 1-100 kW
        - **Benefits**:
          - Very low cost per kW
          - Minimal environmental impact
          - Community ownership
          - No fuel costs
        - **Challenges**:
          - Seasonal flow variation
          - Debris management
          - Wildlife protection
        """)
    
    with app_col2:
        st.markdown("""
        ### Specialized Applications
        
        **7. High-Head Alpine Systems**
        - **Location**: Mountain regions
        - **Head**: 300-1800 m (!)
        - **Flow**: 0.5-10 m³/s
        - **Turbine**: Multi-jet Pelton
        - **Power**: 10-500 MW
        - **Characteristics**:
          - Very long penstocks (2-5 km)
          - Extreme water hammer forces
          - Surge tanks required
          - Cable car access for maintenance
        - **Examples**:
          - Swiss Alps installations
          - Austrian hydropower
          - Himalayan projects
        
        **8. Low-Head River Systems**
        - **Head**: 2-10 m
        - **Flow**: 10-200 m³/s (very high!)
        - **Turbine**: Kaplan, Propeller
        - **Power**: 5-50 MW
        - **Applications**:
          - Existing dam retrofit
          - Canal drops
          - River barrages
        - **Fish passage**: Critical design consideration
        
        **9. Tidal Power**
        - **Function**: Harness tidal range
        - **Head**: 3-15 m (twice daily)
        - **Flow**: Bidirectional
        - **Turbine**: Specialized bulb turbines
        - **Examples**:
          - La Rance (France): 240 MW
          - Sihwa Lake (Korea): 254 MW
        - **Advantage**: Predictable (lunar cycle)
        - **Challenge**: Salt water corrosion
        
        **10. Industrial Process Water**
        - **Source**: Waste pressure in processes
        - **Applications**:
          - Water treatment plants
          - Irrigation canals
          - Industrial cooling water
          - Mine dewatering
        - **Power**: 10-500 kW
        - **Benefit**: "Free" energy from existing flow
        - **Turbine**: Custom for available head/flow
        
        ### Economic Considerations
        
        #### Capital Costs (approximate)
        
        | System Size | Capital Cost | $/kW |
        |------------|--------------|------|
        | Large hydro | $1-3M per MW | $1,000-3,000 |
        | Small hydro | $2-5M per MW | $2,000-5,000 |
        | Mini hydro | $3-8M per MW | $3,000-8,000 |
        | Micro hydro | $5-15k per kW | $5,000-15,000 |
        
        Higher $/kW for smaller systems, but absolute cost lower.
        
        #### Operating Costs
        - **Very low**: 1-2% of capital per year
        - **No fuel cost**: Water is free
        - **Long lifetime**: 50-100 years
        - **Main costs**:
          - Routine maintenance
          - Occasional refurbishment
          - Insurance
          - Grid connection fees (if applicable)
        
        #### Revenue
        - **Capacity factor**: 40-90% (vs solar 15-25%)
        - **Electricity price**: $0.05-0.20/kWh
        - **Feed-in tariffs**: Higher rates for renewable
        - **Payback period**: 5-20 years typical
        - **Lifetime revenue**: 30-50 years continuous
        
        ### Environmental Considerations
        
        **Positive Impacts:**
        - Zero greenhouse gas emissions
        - Renewable (water cycle)
        - Flood control
        - Irrigation supply
        - Recreation (reservoir)
        
        **Negative Impacts:**
        - River ecology disruption
        - Fish migration barriers
        - Sediment trapping
        - Land inundation (dams)
        - Methane from reservoirs (tropical)
        
        **Mitigation Measures:**
        - Fish ladders/passages
        - Environmental flow releases
        - Sediment flushing
        - Run-of-river design
        - Small vs large projects
        
        ### Future Trends
        
        **1. Modernization:**
        - Digital controls
        - Predictive maintenance
        - Remote monitoring
        
        **2. Efficiency improvements:**
        - Advanced turbine designs
        - Variable speed generators
        - Coating materials (abrasion/corrosion)
        
        **3. Grid integration:**
        - Frequency regulation
        - Renewable firming
        - Energy storage (pumped)
        
        **4. Sustainability:**
        - Environmental flow requirements
        - Fish-friendly turbines
        - Sediment management
        - Small/distributed systems
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Case Study: Small Hydro Plant Design
    
    **Location:** Mountain stream in Alps
    
    **Initial Assessment:**
    - Available head: 120 m
    - Average flow: 0.6 m³/s (minimum 0.3 m³/s)
    - Distance: 400 m from intake to powerhouse
    
    **Design Choices:**
    
    **Option 1: Small diameter (400 mm)**
    - Lower pipe cost: $120,000
    - High friction loss: 18 m
    - Net head: 102 m
    - Power output: 480 kW
    - Annual energy: 3,400 MWh
    - Revenue @ $0.10/kWh: $340,000/year
    
    **Option 2: Large diameter (600 mm)**
    - Higher pipe cost: $180,000
    - Low friction loss: 5 m
    - Net head: 115 m
    - Power output: 540 kW
    - Annual energy: 3,830 MWh
    - Revenue @ $0.10/kWh: $383,000/year
    
    **Analysis:**
    - Extra pipe cost: $60,000
    - Extra revenue: $43,000/year
    - **Payback: 1.4 years!**
    - Over 40-year lifetime: Extra profit = $1,720,000
    
    **Decision:** Large diameter penstock - dramatically better economics!
    
    **Key lesson:** Don't undersize the penstock!
    """)

st.markdown("---")
st.info("💡 **Tip**: Use the Interactive Simulation tab to experiment with different system configurations and see how head, flow rate, and losses affect power output!")

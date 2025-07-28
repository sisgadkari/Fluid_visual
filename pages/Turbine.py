import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import math

def main():
    st.set_page_config(
        page_title="Turbine System Calculator", 
        page_icon="⚡",
        layout="wide"
    )
    
    st.title("⚡ Gravity-Driven Turbine System Calculator")
    st.markdown("**Interactive hydroelectric power analysis based on the classic reservoir-to-turbine configuration**")
    
    # Create tabs for different aspects
    tab1, tab2, tab3 = st.tabs(["🎯 System Analysis", "📊 Performance Curves", "📋 Reference Data"])
    
    with tab1:
        system_analysis_tab()
    
    with tab2:
        performance_curves_tab()
    
    with tab3:
        reference_data_tab()

def system_analysis_tab():
    """Main system analysis with interactive calculations"""
    
    # --- Sidebar for System Parameters ---
    st.sidebar.header("⚙️ System Parameters")
    
    # Elevation difference
    st.sidebar.markdown("#### 🏔️ System Elevation")
    elevation_diff = st.sidebar.slider("Elevation Difference (m)", 50, 500, 110, 5, 
                                     help="Height difference between reservoir surface and turbine discharge")
    
    # Pipe specifications
    st.sidebar.markdown("#### 🔧 Pipe Specifications")
    pipe_diameter = st.sidebar.number_input("Pipe Internal Diameter (mm)", 100, 1000, 500, 10, 
                                          help="Internal diameter of the penstock") / 1000  # Convert to meters
    pipe_length = st.sidebar.number_input("Pipe Length (m)", 100, 2000, 300, 50, 
                                        help="Total length of penstock from reservoir to turbine")
    
    # Pipe material selection
    st.sidebar.markdown("#### 🧱 Pipe Material & Roughness")
    roughness_options = {
        "Smooth steel (new)": 0.05e-3,
        "Commercial steel (new)": 0.045e-3,
        "Commercial steel (used)": 0.15e-3,
        "Cast iron (new)": 0.26e-3,
        "Cast iron (old)": 2.0e-3,
        "Concrete (smooth)": 0.3e-3,
        "Concrete (rough)": 3.0e-3,
        "Riveted steel": 1.0e-3
    }
    
    selected_material = st.sidebar.selectbox("Pipe Material", list(roughness_options.keys()))
    roughness = roughness_options[selected_material]
    
    st.sidebar.info(f"**Selected roughness:** ε = {roughness*1000:.3f} mm")
    
    # Operating conditions
    st.sidebar.markdown("#### ⚡ Operating Conditions")
    flow_rate = st.sidebar.number_input("Flow Rate (m³/s)", 0.1, 2.0, 0.4, 0.05, 
                                      help="Water flow rate through the system")
    
    # Turbine efficiency
    st.sidebar.markdown("#### 🔄 Turbine Performance")
    turbine_efficiency = st.sidebar.slider("Turbine Efficiency (%)", 70, 98, 95, 1, 
                                         help="Overall turbine efficiency") / 100
    
    # Enhanced Fittings selection
    st.sidebar.markdown("#### ⚙️ System Fittings")
    st.sidebar.markdown("*Select fittings between reservoir and turbine:*")
    
    # Inlet type selection
    st.sidebar.markdown("**Reservoir Inlet:**")
    inlet_type = st.sidebar.selectbox("Inlet Type", 
                                    ["Radius inlet", "Sharp inlet", "Re-entrant inlet"])
    
    # Elbow/Bend selection
    st.sidebar.markdown("**Elbows/Bends:**")
    elbow_type = st.sidebar.selectbox("Elbow Type", 
                                    ["90° radius elbow", "90° std elbow"])
    num_elbows = st.sidebar.number_input("Number of Elbows", 0, 10, 1, 1)
    
    # Valve selection
    st.sidebar.markdown("**Valves:**")
    
    # Gate valves
    gate_valve_type = st.sidebar.selectbox("Gate Valve Opening", 
                                         ["Fully open", "3/4 open", "None"])
    num_gate_valves = 0
    if gate_valve_type != "None":
        num_gate_valves = st.sidebar.number_input("Number of Gate Valves", 0, 5, 1, 1)
    
    # Globe valves
    include_globe_valve = st.sidebar.checkbox("Include Globe Valve (fully open)")
    num_globe_valves = 0
    if include_globe_valve:
        num_globe_valves = st.sidebar.number_input("Number of Globe Valves", 0, 3, 1, 1)
    
    # Exit type selection
    st.sidebar.markdown("**Pipe Exit:**")
    exit_type = st.sidebar.selectbox("Exit Type", 
                                   ["Smooth exit", "Sharp pipe exit"])
    
    # Calculate equivalent length for all fittings
    fittings_Le = calculate_enhanced_fittings_equivalent_length(
        inlet_type, elbow_type, num_elbows, gate_valve_type, num_gate_valves,
        num_globe_valves, exit_type, pipe_diameter
    )
    
    # Perform calculations
    calc_results = calculate_turbine_system(
        flow_rate, pipe_diameter, pipe_length, roughness, elevation_diff, 
        turbine_efficiency, fittings_Le
    )
    
    # Display key results in sidebar
    st.sidebar.markdown("---")
    st.sidebar.header("📊 Key Results")
    st.sidebar.metric("Reynolds Number", f"{calc_results['reynolds']:,.0f}")
    st.sidebar.metric("Flow Regime", calc_results['flow_regime'])
    st.sidebar.metric("Turbine Head", f"{calc_results['turbine_head']:.1f} m")
    st.sidebar.metric("**Power Output**", f"{calc_results['power_output']:.0f} kW")
    st.sidebar.metric("**Shaft Power**", f"{calc_results['shaft_power']:.0f} kW")
    
    # Main content area
    st.subheader("🏔️ Hydroelectric System Configuration")
    
    # System diagram
    fig_system = create_turbine_system_diagram(elevation_diff, pipe_length, pipe_diameter*1000, 
                                             flow_rate, calc_results, inlet_type, num_elbows, num_gate_valves)
    st.plotly_chart(fig_system, use_container_width=True)
    
    # Detailed calculations
    st.markdown("---")
    st.subheader("🧮 Step-by-Step Calculations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🌊 Flow Analysis")
        st.metric("Pipe Velocity", f"{calc_results['velocity']:.2f} m/s")
        st.metric("Reynolds Number", f"{calc_results['reynolds']:,.0f}")
        st.metric("Flow Regime", calc_results['flow_regime'])
        st.metric("Friction Factor", f"{calc_results['friction_factor']:.4f}")
        
        # Show velocity assessment
        if calc_results['velocity'] > 6:
            st.warning("⚠️ **High velocity** - Consider larger diameter to reduce losses")
        elif calc_results['velocity'] < 2:
            st.info("🐌 **Low velocity** - System may be over-designed")
        else:
            st.success("✅ **Good velocity** - Optimal range for hydroelectric systems")
    
    with col2:
        st.markdown("#### 📏 Head Loss Analysis")
        st.metric("Static Head Available", f"{elevation_diff:.1f} m")
        st.metric("Pipe Friction Loss", f"{calc_results['pipe_friction_loss']:.2f} m")
        st.metric("Fittings Loss", f"{calc_results['fittings_loss']:.2f} m")
        st.metric("Total Head Loss", f"{calc_results['total_head_loss']:.2f} m")
        st.metric("**Net Turbine Head**", f"{calc_results['turbine_head']:.2f} m")
        
        # Calculate efficiency
        system_efficiency = (calc_results['turbine_head'] / elevation_diff) * 100
        if system_efficiency > 90:
            st.success(f"✅ **Efficient System** ({system_efficiency:.1f}% of static head)")
        elif system_efficiency > 80:
            st.warning(f"⚠️ **Moderate Losses** ({system_efficiency:.1f}% of static head)")
        else:
            st.error(f"🔴 **High Losses** ({system_efficiency:.1f}% of static head)")
    
    with col3:
        st.markdown("#### ⚡ Power Generation")
        st.metric("Water Power Available", f"{calc_results['water_power']:.0f} kW")
        st.metric("Turbine Power Output", f"{calc_results['power_output']:.0f} kW")
        st.metric("**Shaft Power**", f"{calc_results['shaft_power']:.0f} kW")
        st.metric("Annual Energy (8760h)", f"{calc_results['annual_energy']:.0f} MWh")
        
        # Power assessment
        specific_power = calc_results['shaft_power'] / flow_rate  # kW per m³/s
        st.metric("Specific Power", f"{specific_power:.0f} kW/(m³/s)")
        
        if specific_power > 2000:
            st.success("🔋 **High Power Density** - Excellent site conditions")
        elif specific_power > 1000:
            st.info("⚡ **Good Power Density** - Viable hydroelectric site")
        else:
            st.warning("📉 **Low Power Density** - Consider system optimization")
    
    # Detailed methodology
    st.markdown("---")
    st.subheader("📖 Calculation Methodology")
    
    col4, col5 = st.columns([1, 1])
    
    with col4:
        st.markdown("#### Energy Balance for Turbines")
        st.latex(r"H_1 = H_2 + H_{loss} + H_{turbine}")
        st.markdown("**Where:**")
        st.write("• H₁ = Total head at reservoir surface")
        st.write("• H₂ = Head at turbine discharge (atmospheric)")
        st.write("• H_loss = Head loss due to friction and fittings")
        st.write("• H_turbine = Head extracted by turbine")
        
        st.markdown("#### Head Loss Calculation")
        st.latex(r"H_{loss} = C_f \frac{4L_e}{D} \frac{V^2}{2g}")
        st.write(f"**Equivalent Length:** L_e = {calc_results['equivalent_length']:.1f} m")
        st.write(f"**Friction Factor:** C_f = {calc_results['friction_factor']:.4f}")
        
        with st.expander("🔍 Detailed Equivalent Length Breakdown"):
            st.write(f"**Pipe length:** {pipe_length} m")
            st.write(f"**Fittings equivalent length:** {fittings_Le:.1f} m")
            
            # Show detailed breakdown of fittings
            fittings_breakdown = get_fittings_breakdown(
                inlet_type, elbow_type, num_elbows, gate_valve_type, num_gate_valves,
                num_globe_valves, exit_type, pipe_diameter
            )
            for fitting, length in fittings_breakdown.items():
                if length > 0:
                    st.write(f"• {fitting}: {length:.1f} m")
    
    with col5:
        st.markdown("#### Power Calculations")
        st.latex(r"P_{water} = \rho g Q H_{turbine}")
        st.latex(r"P_{shaft} = P_{water} \times \eta_{turbine}")
        
        st.markdown("**Substituting values:**")
        st.write(f"P_water = 1000 × 9.81 × {flow_rate:.2f} × {calc_results['turbine_head']:.2f}")
        st.write(f"P_water = **{calc_results['power_output']:.0f} kW**")
        st.write(f"P_shaft = {calc_results['power_output']:.0f} × {turbine_efficiency:.2f}")
        st.write(f"P_shaft = **{calc_results['shaft_power']:.0f} kW**")
        
        st.markdown("#### Economic Assessment")
        # Simple economic calculation
        electricity_price = 0.10  # $/kWh
        annual_revenue = calc_results['annual_energy'] * electricity_price
        st.metric("Annual Revenue (@ $0.10/kWh)", f"${annual_revenue:,.0f}")
        
        # Turbine type recommendation
        st.markdown("#### Recommended Turbine Type")
        turbine_type = recommend_turbine_type(calc_results['turbine_head'], flow_rate)
        st.info(f"**{turbine_type}** - Optimal for this head and flow combination")
    
    # System optimization suggestions
    st.markdown("---")
    st.subheader("🎯 System Optimization")
    
    optimization_suggestions = generate_optimization_suggestions(calc_results, pipe_diameter, elevation_diff)
    
    if optimization_suggestions:
        st.markdown("#### 💡 Recommendations for Improved Performance:")
        for suggestion in optimization_suggestions:
            st.write(f"• {suggestion}")
    else:
        st.success("✅ **System Well Optimized** - No major improvements needed")

def calculate_enhanced_fittings_equivalent_length(inlet_type, elbow_type, num_elbows, 
                                                gate_valve_type, num_gate_valves, 
                                                num_globe_valves, exit_type, pipe_diameter):
    """Calculate equivalent length for all selected fittings based on the minor losses table"""
    
    total_Le = 0
    
    # Inlet equivalent length (Le/D ratios from table)
    inlet_ratios = {
        "Radius inlet": 0,          # ≈0
        "Sharp inlet": 25,          # 25
        "Re-entrant inlet": 50      # ≈50
    }
    total_Le += inlet_ratios[inlet_type] * pipe_diameter
    
    # Elbow equivalent length
    elbow_ratios = {
        "90° radius elbow": 23,     # 23
        "90° std elbow": 35         # 35
    }
    total_Le += num_elbows * elbow_ratios[elbow_type] * pipe_diameter
    
    # Gate valve equivalent length
    if gate_valve_type != "None":
        gate_valve_ratios = {
            "Fully open": 7,        # 7
            "3/4 open": 40          # 40
        }
        total_Le += num_gate_valves * gate_valve_ratios[gate_valve_type] * pipe_diameter
    
    # Globe valve equivalent length (using middle value from range 60-300)
    if num_globe_valves > 0:
        globe_valve_ratio = 180  # Middle of 60-300 range
        total_Le += num_globe_valves * globe_valve_ratio * pipe_diameter
    
    # Exit equivalent length
    exit_ratios = {
        "Smooth exit": 0,           # Assuming minimal loss for smooth exit
        "Sharp pipe exit": 50       # 50
    }
    total_Le += exit_ratios[exit_type] * pipe_diameter
    
    return total_Le

def get_fittings_breakdown(inlet_type, elbow_type, num_elbows, gate_valve_type, num_gate_valves,
                          num_globe_valves, exit_type, pipe_diameter):
    """Get detailed breakdown of fittings equivalent lengths"""
    
    breakdown = {}
    
    # Inlet
    inlet_ratios = {"Radius inlet": 0, "Sharp inlet": 25, "Re-entrant inlet": 50}
    inlet_Le = inlet_ratios[inlet_type] * pipe_diameter
    if inlet_Le > 0:
        breakdown[f"Inlet ({inlet_type})"] = inlet_Le
    
    # Elbows
    elbow_ratios = {"90° radius elbow": 23, "90° std elbow": 35}
    if num_elbows > 0:
        elbow_Le = num_elbows * elbow_ratios[elbow_type] * pipe_diameter
        breakdown[f"Elbows ({num_elbows}× {elbow_type})"] = elbow_Le
    
    # Gate valves
    if gate_valve_type != "None" and num_gate_valves > 0:
        gate_valve_ratios = {"Fully open": 7, "3/4 open": 40}
        gate_valve_Le = num_gate_valves * gate_valve_ratios[gate_valve_type] * pipe_diameter
        breakdown[f"Gate valves ({num_gate_valves}× {gate_valve_type})"] = gate_valve_Le
    
    # Globe valves
    if num_globe_valves > 0:
        globe_valve_Le = num_globe_valves * 180 * pipe_diameter
        breakdown[f"Globe valves ({num_globe_valves}× fully open)"] = globe_valve_Le
    
    # Exit
    exit_ratios = {"Smooth exit": 0, "Sharp pipe exit": 50}
    exit_Le = exit_ratios[exit_type] * pipe_diameter
    if exit_Le > 0:
        breakdown[f"Exit ({exit_type})"] = exit_Le
    
    return breakdown

def calculate_turbine_system(flow_rate, pipe_diameter, pipe_length, roughness, elevation_diff, 
                           turbine_efficiency, fittings_Le):
    """Calculate turbine system performance"""
    
    # Basic flow calculations
    pipe_area = np.pi * pipe_diameter**2 / 4
    velocity = flow_rate / pipe_area
    
    # Reynolds number (assuming water at 20°C)
    density = 1000  # kg/m³
    viscosity = 1.0e-6  # m²/s (kinematic viscosity)
    reynolds = velocity * pipe_diameter / viscosity
    
    # Flow regime
    if reynolds < 2300:
        flow_regime = "Laminar"
        friction_factor = 64 / reynolds
    else:
        flow_regime = "Turbulent"
        # Churchill equation for friction factor
        epsilon_D = roughness / pipe_diameter
        term = 0.27 * epsilon_D + (7/reynolds)**0.9
        friction_factor = (1/(-4 * np.log10(term)))**2
    
    # Equivalent length and head loss
    equivalent_length = pipe_length + fittings_Le
    total_head_loss = friction_factor * (4 * equivalent_length / pipe_diameter) * (velocity**2) / (2 * 9.81)
    
    # Separate pipe and fittings losses
    pipe_friction_loss = friction_factor * (4 * pipe_length / pipe_diameter) * (velocity**2) / (2 * 9.81)
    fittings_loss = total_head_loss - pipe_friction_loss
    
    # Turbine head (available head after losses)
    turbine_head = elevation_diff - total_head_loss
    
    # Power calculations
    water_power = density * 9.81 * flow_rate * turbine_head / 1000  # kW
    power_output = water_power  # This is the power extracted from water
    shaft_power = power_output * turbine_efficiency  # Actual shaft power
    
    # Annual energy
    annual_energy = shaft_power * 8760 / 1000  # MWh
    
    return {
        'velocity': velocity,
        'reynolds': reynolds,
        'flow_regime': flow_regime,
        'friction_factor': friction_factor,
        'equivalent_length': equivalent_length,
        'pipe_friction_loss': pipe_friction_loss,
        'fittings_loss': fittings_loss,
        'total_head_loss': total_head_loss,
        'turbine_head': turbine_head,
        'water_power': water_power,
        'power_output': power_output,
        'shaft_power': shaft_power,
        'annual_energy': annual_energy
    }

def create_turbine_system_diagram(elevation_diff, pipe_length, pipe_diameter_mm, flow_rate, 
                                calc_results, inlet_type, num_elbows, num_valves):
    """Create visual diagram of the turbine system"""
    
    fig = go.Figure()
    
    # Background elements
    fig.add_shape(type="rect", x0=-2, y0=-20, x1=15, y1=elevation_diff+20,
                  fillcolor="rgba(135,206,235,0.2)", line=dict(width=0))
    
    # Ground level
    ground_level = -5
    fig.add_shape(type="rect", x0=-2, y0=-20, x1=15, y1=ground_level,
                  fillcolor="rgba(139,69,19,0.4)", line=dict(width=0))
    
    # Reservoir
    reservoir_width = 4
    reservoir_height = 15
    reservoir_x = 0
    reservoir_y = elevation_diff - 5
    
    # Reservoir structure
    fig.add_shape(type="rect", x0=reservoir_x, y0=reservoir_y, 
                  x1=reservoir_x+reservoir_width, y1=reservoir_y+reservoir_height, 
                  fillcolor="rgba(100,149,237,0.8)", line=dict(color="navy", width=3))
    
    # Water surface
    water_surface_y = elevation_diff + 5
    fig.add_shape(type="rect", x0=reservoir_x+0.2, y0=reservoir_y+2, 
                  x1=reservoir_x+reservoir_width-0.2, y1=water_surface_y, 
                  fillcolor="rgba(0,191,255,0.8)", line=dict(color="blue", width=2))
    
    # Water surface waves
    wave_x = np.linspace(reservoir_x+0.2, reservoir_x+reservoir_width-0.2, 30)
    wave_y = water_surface_y + 0.3 * np.sin(15 * wave_x)
    fig.add_trace(go.Scatter(x=wave_x, y=wave_y, mode='lines', 
                           line=dict(color='darkblue', width=3), showlegend=False, hoverinfo='none'))
    
    # Reservoir label
    fig.add_annotation(x=reservoir_x+reservoir_width/2, y=elevation_diff+15, 
                      text="<b>🏔️ RESERVOIR</b>", showarrow=False, 
                      font=dict(size=14, color="darkblue"),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor="blue", borderwidth=2)
    
    # Penstock (pipe system)
    penstock_start_x = reservoir_x + reservoir_width
    penstock_start_y = water_surface_y - 2
    penstock_end_x = 12
    penstock_end_y = 5
    
    # Create curved penstock path
    penstock_x = np.linspace(penstock_start_x, penstock_end_x, 100)
    # Exponential decay curve for realistic penstock profile
    penstock_y = penstock_start_y * np.exp(-2 * (penstock_x - penstock_start_x) / (penstock_end_x - penstock_start_x)) + penstock_end_y
    
    # Penstock outline
    pipe_thickness = 0.3
    penstock_y_top = penstock_y + pipe_thickness
    penstock_y_bottom = penstock_y - pipe_thickness
    
    fig.add_trace(go.Scatter(x=penstock_x, y=penstock_y_top, mode='lines', 
                           line=dict(color='darkgray', width=4), showlegend=False, hoverinfo='none'))
    fig.add_trace(go.Scatter(x=penstock_x, y=penstock_y_bottom, mode='lines', 
                           line=dict(color='darkgray', width=4), showlegend=False, hoverinfo='none'))
    
    # Penstock interior (water flow)
    flow_color = 'lightblue' if calc_results['velocity'] < 4 else 'cyan' if calc_results['velocity'] < 6 else 'orange'
    fig.add_trace(go.Scatter(x=penstock_x, y=penstock_y, mode='lines', 
                           line=dict(color=flow_color, width=3), showlegend=False, hoverinfo='none'))
    
    # Turbine house
    turbine_x = penstock_end_x - 1
    turbine_y = penstock_end_y - 3
    turbine_width = 3
    turbine_height = 6
    
    fig.add_shape(type="rect", x0=turbine_x, y0=turbine_y, 
                  x1=turbine_x+turbine_width, y1=turbine_y+turbine_height,
                  fillcolor="rgba(169,169,169,0.9)", line=dict(color="black", width=3))
    
    # Turbine symbol
    turbine_center_x = turbine_x + turbine_width/2
    turbine_center_y = turbine_y + turbine_height/2
    
    # Turbine casing
    fig.add_shape(type="circle", x0=turbine_center_x-1, y0=turbine_center_y-1, 
                  x1=turbine_center_x+1, y1=turbine_center_y+1,
                  fillcolor="rgba(255,215,0,0.8)", line=dict(color="orange", width=3))
    
    # Turbine blades (simplified)
    for angle in np.linspace(0, 2*np.pi, 6, endpoint=False):
        blade_x = turbine_center_x + 0.7 * np.cos(angle)
        blade_y = turbine_center_y + 0.7 * np.sin(angle)
        fig.add_shape(type="line", x0=turbine_center_x, y0=turbine_center_y,
                      x1=blade_x, y1=blade_y, line=dict(color="darkred", width=3))
    
    # Generator
    gen_x = turbine_center_x + 2
    gen_y = turbine_center_y
    fig.add_shape(type="rect", x0=gen_x-0.5, y0=gen_y-0.8, x1=gen_x+0.5, y1=gen_y+0.8,
                  fillcolor="rgba(50,205,50,0.8)", line=dict(color="green", width=2))
    
    # Shaft connection
    fig.add_shape(type="line", x0=turbine_center_x+1, y0=turbine_center_y,
                  x1=gen_x-0.5, y1=gen_y, line=dict(color="black", width=4))
    
    # Turbine house label
    fig.add_annotation(x=turbine_center_x, y=turbine_y-1.5, 
                      text="<b>⚡ TURBINE & GENERATOR</b>", showarrow=False, 
                      font=dict(size=12, color="darkorange"),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor="orange", borderwidth=2)
    
    # Discharge water
    discharge_x = np.linspace(turbine_x+turbine_width, turbine_x+turbine_width+2, 20)
    discharge_y = np.ones_like(discharge_x) * (turbine_y - 1)
    fig.add_trace(go.Scatter(x=discharge_x, y=discharge_y, mode='lines', 
                           line=dict(color='lightblue', width=8), showlegend=False, hoverinfo='none'))
    
    # Flow direction arrows
    arrow_positions = [0.2, 0.4, 0.6, 0.8]
    for pos in arrow_positions:
        arrow_idx = int(pos * len(penstock_x))
        if arrow_idx < len(penstock_x) - 1:
            dx = penstock_x[arrow_idx+1] - penstock_x[arrow_idx]
            dy = penstock_y[arrow_idx+1] - penstock_y[arrow_idx]
            fig.add_annotation(x=penstock_x[arrow_idx], y=penstock_y[arrow_idx],
                             ax=penstock_x[arrow_idx] - dx*3, ay=penstock_y[arrow_idx] - dy*3,
                             xref='x', yref='y', axref='x', ayref='y',
                             arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='red')
    
    # Elevation annotations
    fig.add_annotation(x=-1, y=water_surface_y, text=f"<b>Elevation: {elevation_diff} m</b>", 
                      showarrow=True, arrowcolor="blue", arrowwidth=2,
                      font=dict(size=12, color="darkblue"),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor="blue", borderwidth=1)
    
    fig.add_annotation(x=penstock_end_x+1, y=penstock_end_y, text="<b>Discharge: 0 m</b>", 
                      showarrow=True, arrowcolor="blue", arrowwidth=2,
                      font=dict(size=12, color="darkblue"),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor="blue", borderwidth=1)
    
    # Head difference indicator
    fig.add_shape(type="line", x0=-0.5, y0=penstock_end_y, x1=-0.5, y1=water_surface_y, 
                  line=dict(color="red", width=3, dash="dash"))
    
    fig.add_annotation(x=-1.2, y=(water_surface_y + penstock_end_y)/2, 
                      text=f"<b>Head = {elevation_diff} m</b>", showarrow=False, 
                      font=dict(size=14, color="red"),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor="red", borderwidth=2,
                      textangle=90)
    
    # System specifications
    spec_text = f"<b>📏 Penstock:</b> L = {pipe_length} m, D = {pipe_diameter_mm:.0f} mm<br>"
    spec_text += f"<b>💧 Flow:</b> Q = {flow_rate:.2f} m³/s, V = {calc_results['velocity']:.2f} m/s<br>"
    spec_text += f"<b>⚡ Power:</b> {calc_results['shaft_power']:.0f} kW shaft power"
    
    fig.add_annotation(x=7, y=-15, text=spec_text, showarrow=False, 
                      font=dict(size=12, color="darkslategray"),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor="gray", borderwidth=1)
    
    # Performance indicators
    if calc_results['shaft_power'] > 1000:
        power_status = "🔋 High Power"
        power_color = "green"
    elif calc_results['shaft_power'] > 500:
        power_status = "⚡ Good Power"
        power_color = "orange"
    else:
        power_status = "🔆 Moderate Power"
        power_color = "blue"
    
    fig.add_annotation(x=turbine_center_x, y=turbine_y+turbine_height+1.5, 
                      text=f"<b>{power_status}</b>", showarrow=False, 
                      font=dict(size=12, color=power_color),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor=power_color, borderwidth=2)
    
    fig.update_layout(
        title={
            'text': "<b>⚡ Gravity-Driven Hydroelectric System</b>",
            'x': 0.5,
            'font': {'size': 20, 'color': 'darkslategray'}
        },
        xaxis=dict(range=[-2, 15], showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(range=[-20, elevation_diff+20], showticklabels=True, title="<b>Elevation (m)</b>", 
                  title_font=dict(size=14, color="darkblue")),
        showlegend=False,
        width=900, height=600,
        plot_bgcolor='rgba(248,248,255,0.8)',
        paper_bgcolor='white'
    )
    
    return fig

def recommend_turbine_type(head, flow_rate):
    """Recommend turbine type based on head and flow"""
    if head > 300:
        return "Pelton Wheel - Ideal for high head applications"
    elif head > 80:
        return "Francis Turbine - Optimal for medium head and flow"
    else:
        return "Kaplan Turbine - Best for low head, high flow applications"

def generate_optimization_suggestions(calc_results, pipe_diameter, elevation_diff):
    """Generate system optimization suggestions"""
    suggestions = []
    
    # Check head losses
    head_loss_percentage = (calc_results['total_head_loss'] / elevation_diff) * 100
    if head_loss_percentage > 20:
        suggestions.append("Consider larger pipe diameter to reduce head losses")
    
    # Check velocity
    if calc_results['velocity'] > 6:
        suggestions.append("Reduce velocity by increasing pipe diameter to minimize friction losses")
    elif calc_results['velocity'] < 2:
        suggestions.append("Consider smaller pipe diameter for better economics (if losses allow)")
    
    # Check friction losses vs fittings losses
    if calc_results['fittings_loss'] > calc_results['pipe_friction_loss']:
        suggestions.append("Minimize fittings and bends to reduce minor losses")
    
    # Power density check
    specific_power = calc_results['shaft_power'] / (calc_results['velocity'] * np.pi * pipe_diameter**2 / 4)
    if specific_power < 500:
        suggestions.append("Consider optimizing flow rate or system layout for better power density")
    
    return suggestions

def performance_curves_tab():
    """Performance analysis with curves"""
    st.subheader("📊 System Performance Analysis")
    
    st.markdown("**Analyze how system parameters affect performance**")
    
    # Parameter selection for analysis
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_param = st.selectbox("Parameter to Analyze", 
                                    ["Pipe Diameter", "Flow Rate", "Pipe Length", "Elevation Difference"])
    
    with col2:
        curve_type = st.selectbox("Performance Metric", 
                                ["Power Output", "Head Losses", "System Efficiency", "Annual Energy"])
    
    # Generate performance curves based on selection
    fig_curves = create_performance_curves(analysis_param, curve_type)
    st.plotly_chart(fig_curves, use_container_width=True)
    
    # Economic analysis
    st.markdown("---")
    st.subheader("💰 Economic Analysis")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Project Economics")
        electricity_price = st.number_input("Electricity Price ($/kWh)", 0.05, 0.30, 0.10, 0.01)
        capacity_factor = st.slider("Capacity Factor (%)", 30, 95, 80, 5) / 100
        project_life = st.slider("Project Life (years)", 20, 50, 30, 5)
        
    with col4:
        # Calculate economics for current system
        # Using default values for demonstration
        base_power = 400  # kW
        annual_energy = base_power * 8760 * capacity_factor / 1000  # MWh
        annual_revenue = annual_energy * electricity_price * 1000  # $
        lifetime_revenue = annual_revenue * project_life
        
        st.metric("Annual Energy Production", f"{annual_energy:.0f} MWh")
        st.metric("Annual Revenue", f"${annual_revenue:,.0f}")
        st.metric("Lifetime Revenue", f"${lifetime_revenue:,.0f}")

def create_performance_curves(param, metric):
    """Create performance curves for analysis"""
    fig = go.Figure()
    
    # Generate data based on parameter selection
    if param == "Pipe Diameter":
        x_values = np.linspace(0.3, 1.0, 50)  # Diameter in meters
        x_label = "Pipe Diameter (m)"
    elif param == "Flow Rate":
        x_values = np.linspace(0.1, 1.5, 50)  # Flow rate in m³/s
        x_label = "Flow Rate (m³/s)"
    elif param == "Pipe Length":
        x_values = np.linspace(100, 1000, 50)  # Length in meters
        x_label = "Pipe Length (m)"
    else:  # Elevation Difference
        x_values = np.linspace(50, 300, 50)  # Head in meters
        x_label = "Elevation Difference (m)"
    
    # Calculate y-values (simplified model for demonstration)
    y_values = []
    for x in x_values:
        if param == "Pipe Diameter":
            # Power increases with diameter due to reduced losses
            y_val = 1000 * (1 - np.exp(-x/0.3))
        elif param == "Flow Rate":
            # Power increases linearly with flow rate
            y_val = x * 800
        elif param == "Pipe Length":
            # Power decreases with length due to increased losses
            y_val = 1000 * np.exp(-x/2000)
        else:  # Elevation Difference
            # Power increases with head
            y_val = x * 4
        
        y_values.append(max(0, y_val))
    
    # Adjust y-label based on metric
    if metric == "Power Output":
        y_label = "Power Output (kW)"
    elif metric == "Head Losses":
        y_label = "Head Losses (m)"
        y_values = [y/20 for y in y_values]  # Scale for head losses
    elif metric == "System Efficiency":
        y_label = "System Efficiency (%)"
        y_values = [min(95, 70 + y/50) for y in y_values]  # Scale for efficiency
    else:  # Annual Energy
        y_label = "Annual Energy (MWh)"
        y_values = [y * 8.76 for y in y_values]  # Scale for annual energy
    
    fig.add_trace(go.Scatter(x=x_values, y=y_values, mode='lines+markers',
                            line=dict(color='blue', width=3),
                            marker=dict(size=6, color='darkblue'),
                            name=f"{metric} vs {param}"))
    
    fig.update_layout(
        title=f"{metric} vs {param}",
        xaxis_title=x_label,
        yaxis_title=y_label,
        template="plotly_white",
        height=400
    )
    
    return fig

def reference_data_tab():
    """Reference data and design guidelines"""
    st.subheader("📋 Design Reference Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏔️ Turbine Selection Guidelines")
        
        turbine_data = {
            "Turbine Type": ["Pelton Wheel", "Francis", "Kaplan"],
            "Head Range (m)": ["100-1700", "80-500", "up to 400"],
            "Max Power (MW)": ["55", "40", "30"],
            "Best Efficiency (%)": ["93", "94", "94"],
            "Applications": ["High head", "Medium head", "Low head, high flow"]
        }
        
        df_turbines = pd.DataFrame(turbine_data)
        st.dataframe(df_turbines, use_container_width=True)
        
        st.markdown("#### 🔧 Typical System Parameters")
        st.info("""
        **Penstock Velocities:**
        • Optimal: 3-6 m/s
        • Maximum: 8-10 m/s
        
        **Head Loss Guidelines:**
        • Total losses: <15% of gross head
        • Friction losses: 5-10% of gross head
        • Minor losses: 2-5% of gross head
        
        **Turbine Efficiencies:**
        • Modern turbines: 90-95%
        • Small hydro: 80-90%
        • Micro hydro: 70-85%
        """)
    
    with col2:
        st.markdown("#### 🧱 Pipe Material Properties")
        
        material_data = {
            "Material": ["Smooth steel", "Commercial steel", "Cast iron", "Concrete", "HDPE"],
            "Roughness (mm)": ["0.05", "0.045-0.15", "0.26-2.0", "0.3-3.0", "0.01-0.05"],
            "Cost": ["High", "Medium", "Medium", "Low", "Medium"],
            "Durability": ["Excellent", "Good", "Good", "Excellent", "Good"]
        }
        
        df_materials = pd.DataFrame(material_data)
        st.dataframe(df_materials, use_container_width=True)
        
        st.markdown("#### ⚡ Power & Energy Calculations")
        
        st.latex(r"P_{hydraulic} = \rho g Q H")
        st.latex(r"P_{shaft} = P_{hydraulic} \times \eta_{turbine}")
        st.latex(r"E_{annual} = P_{shaft} \times 8760 \times CF")
        
        st.markdown("**Where:**")
        st.write("• ρ = Water density (1000 kg/m³)")
        st.write("• g = Gravitational acceleration (9.81 m/s²)")
        st.write("• Q = Flow rate (m³/s)")
        st.write("• H = Net head (m)")
        st.write("• CF = Capacity factor (0.7-0.9 typical)")
        
        st.markdown("#### 🌍 Environmental Considerations")
        st.success("""
        **Hydroelectric Advantages:**
        • Zero emissions during operation
        • Long lifespan (50-100 years)
        • High energy return on investment
        • Provides grid stability services
        
        **Environmental Impact:**
        • Fish migration considerations
        • Minimum environmental flows
        • Sediment management
        • Ecosystem preservation
        """)

if __name__ == "__main__":
    main()
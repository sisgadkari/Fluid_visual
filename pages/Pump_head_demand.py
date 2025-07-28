import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import math

def main():
    st.set_page_config(page_title="Two-Reservoir System Calculator", layout="wide")
    
    st.title("🏔️ Two-Reservoir System Head Demand Calculator")
    st.markdown("**Calculate pump head requirements using the equivalent length method for fitting losses**")
    
    # Create tabs for different aspects
    tab1, tab2 = st.tabs(["🎯 System Analysis", "📋 Fittings Reference"])
    
    with tab1:
        system_analysis_tab()
    
    with tab2:
        fittings_reference_tab()

def get_fittings_database():
    """Return the fittings database from the reference table"""
    return {
        "90° Standard Elbow": {"n": 35, "icon": "🔄"},
        "90° Radius Elbow": {"n": 23, "icon": "🔄"},
        "Sharp Pipe Exit": {"n": 50, "icon": "➡️"},
        "Sharp Inlet": {"n": 25, "icon": "⬅️"},
        "Radius Inlet": {"n": 0, "icon": "⬅️"},
        "Re-entrant Inlet": {"n": 50, "icon": "⬅️"},
        "Globe Valve (Fully Open)": {"n": 180, "icon": "🌐"},
        "Gate Valve (Fully Open)": {"n": 7, "icon": "🚪"},
        "Gate Valve (3/4 Open)": {"n": 40, "icon": "🚪"},
        "Gate Valve (1/4 Open)": {"n": 800, "icon": "🚪"},
    }

def system_analysis_tab():
    """Main system analysis with step-by-step calculations"""
    
    # --- Sidebar for System Parameters ---
    st.sidebar.header("⚙️ System Parameters")
    
    # Reservoir elevations
    st.sidebar.markdown("#### 🏔️ Reservoir Elevations")
    z1 = st.sidebar.number_input("Reservoir 1 Elevation (m)", value=0.0, disabled=True, help="Reference level")
    z2 = st.sidebar.slider("Reservoir 2 Elevation (m)", 50, 200, 100, 5, help="Height above reservoir 1")
    
    # Pipe specifications
    st.sidebar.markdown("#### 🔧 Pipe Specifications")
    pipe_length = st.sidebar.number_input("Pipe Length (m)", 10, 2000, 500, 10, help="Total length of connecting pipe")
    pipe_diameter = st.sidebar.number_input("Pipe Internal Diameter (mm)", 25, 500, 150, 5, help="Internal diameter") / 1000  # Convert to meters
    
    # Pipe roughness selection
    st.sidebar.markdown("#### 🧱 Pipe Material & Roughness")
    roughness_options = {
        "Smooth (drawn tubing)": 0.0015e-3,
        "Commercial steel (new)": 0.045e-3,
        "Commercial steel (used)": 0.15e-3,
        "Galvanized iron": 0.15e-3,
        "Cast iron (new)": 0.26e-3,
        "Cast iron (old)": 2.0e-3,
        "Concrete (smooth)": 0.3e-3,
        "Concrete (rough)": 3.0e-3
    }
    
    selected_material = st.sidebar.selectbox("Pipe Material", list(roughness_options.keys()))
    roughness = roughness_options[selected_material]
    
    st.sidebar.info(f"**Selected roughness:** ε = {roughness*1000:.3f} mm")
    
    # Flow rate
    st.sidebar.markdown("#### ⚡ Operating Conditions")
    flow_rate = st.sidebar.number_input("Flow Rate (m³/h)", 1.0, 500.0, 50.0, 1.0, help="Desired flow rate from reservoir 1 to 2")
    flow_rate_m3s = flow_rate / 3600  # Convert to m³/s
    
    # Fluid properties
    st.sidebar.markdown("#### 💧 Fluid Properties")
    fluid_density = st.sidebar.number_input("Density (kg/m³)", 800, 1200, 1000, 10)
    fluid_viscosity = st.sidebar.number_input("Kinematic Viscosity (cSt)", 0.5, 10.0, 1.0, 0.1) * 1e-6  # Convert to m²/s
    
    # Fittings selection
    st.sidebar.markdown("#### ⚙️ Fittings & Minor Losses")
    st.sidebar.markdown("*Select fittings present in the system:*")
    
    fittings_db = get_fittings_database()
    selected_fittings = {}
    
    # Create fitting selection interface
    for fitting_name, fitting_data in fittings_db.items():
        quantity = st.sidebar.number_input(
            f"{fitting_data['icon']} {fitting_name}",
            min_value=0, max_value=10, value=0, step=1,
            key=f"qty_{fitting_name}",
            help=f"n = Le/D = {fitting_data['n']}"
        )
        
        if quantity > 0:
            selected_fittings[fitting_name] = {
                "quantity": quantity,
                "n": fitting_data["n"],
                "icon": fitting_data["icon"]
            }
    
    # System diagram - now using full width
    st.subheader("📐 System Configuration & Analysis")
    fig_system = create_system_diagram(z1, z2, pipe_length, pipe_diameter*1000, flow_rate, selected_fittings)
    st.plotly_chart(fig_system, use_container_width=True)
    
    # Perform calculations
    calc_results = calculate_system_head_demand_equivalent_length(
        flow_rate_m3s, pipe_length, pipe_diameter, roughness, z1, z2, 
        fluid_density, fluid_viscosity, selected_fittings
    )
    
    # Move calculations below the visual
    st.markdown("---")
    st.subheader("🧮 Step-by-Step Calculations")
    
    # Display calculations in organized sections
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.markdown("#### 🌊 Flow Characteristics")
        st.metric("Pipe Velocity", f"{calc_results['velocity']:.2f} m/s")
        st.metric("Reynolds Number", f"{calc_results['reynolds']:,.0f}")
        st.metric("Flow Regime", calc_results['flow_regime'])
        st.metric("Friction Factor", f"{calc_results['friction_factor']:.4f}")
        
        # Show friction factor calculation method
        with st.expander("📖 Friction Factor Calculation"):
            if calc_results['reynolds'] < 2300:
                st.latex(r"f = \frac{64}{Re}")
                st.write(f"f = 64/{calc_results['reynolds']:.0f} = {calc_results['friction_factor']:.4f}")
            else:
                st.markdown("**Churchill equation for turbulent flow:**")
                st.latex(r"\frac{1}{\sqrt{C_f}} = -4 \log_{10}\left[0.27\frac{\varepsilon}{D} + \left(\frac{7}{Re}\right)^{0.9}\right]")
                st.write(f"Using ε/D = {roughness/pipe_diameter:.6f} and Re = {calc_results['reynolds']:.0f}")
                st.write(f"Calculated friction factor: f = {calc_results['friction_factor']:.4f}")
    
    with col4:
        st.markdown("#### 📏 Head Loss Components")
        st.metric("Static Head", f"{calc_results['static_head']:.1f} m")
        st.metric("Pipe Friction Loss", f"{calc_results['pipe_friction_loss']:.2f} m")
        st.metric("Fittings Loss", f"{calc_results['fittings_loss']:.2f} m")
        st.metric("**Total Dynamic Loss**", f"{calc_results['total_dynamic_loss']:.2f} m")
        
        # Show equivalent length method
        with st.expander("📖 Equivalent Length Method"):
            st.markdown("**Total Equivalent Length:**")
            st.latex(r"L_e = L_{pipe} + D \sum (n \times quantity)")
            
            st.write(f"**Pipe length:** {pipe_length} m")
            if selected_fittings:
                st.write("**Fitting contributions:**")
                total_n = 0
                for name, data in selected_fittings.items():
                    contribution = data['n'] * data['quantity']
                    total_n += contribution
                    st.write(f"• {data['quantity']}× {name}: {data['n']} × {data['quantity']} = {contribution}")
                st.write(f"**Total Σ(n):** {total_n}")
                st.write(f"**Equivalent length from fittings:** {pipe_diameter:.3f} × {total_n} = {pipe_diameter * total_n:.1f} m")
            
            st.write(f"**Total Le:** {calc_results['equivalent_length']:.1f} m")
            
            st.markdown("**Head Loss Calculation:**")
            st.latex(r"h_L = C_f \frac{4L_e}{D} \frac{V^2}{2g}")
            st.write(f"h_L = {calc_results['friction_factor']:.4f} × (4×{calc_results['equivalent_length']:.1f})/{pipe_diameter:.3f} × {calc_results['velocity']:.2f}²/(2×9.81)")
            st.write(f"h_L = **{calc_results['total_dynamic_loss']:.2f} m**")
    
    with col5:
        st.markdown("#### 🎯 **Final Results**")
        st.metric("**TOTAL HEAD DEMAND**", f"{calc_results['total_head_demand']:.2f} m", 
                 help="Required pump head to achieve desired flow rate")
        st.metric("Required Pressure", f"{calc_results['required_pressure']:.0f} Pa")
        st.metric("Power Required (η=80%)", f"{calc_results['power_80_eff']:.2f} kW")
        st.metric("Power Required (η=70%)", f"{calc_results['power_70_eff']:.2f} kW")
        
        # Show Bernoulli equation application
        with st.expander("📖 Bernoulli Equation Application"):
            st.markdown("**Modified Bernoulli Equation:**")
            st.latex(r"H_{demand} = \frac{p_2-p_1}{\rho g} + \frac{V_2^2-V_1^2}{2g} + (z_2-z_1) + H_{loss}")
            
            st.markdown("**Assumptions:**")
            st.write("• Both reservoirs open to atmosphere: p₁ = p₂")
            st.write("• Large reservoirs: V₁ ≈ V₂ ≈ 0")
            
            st.markdown("**Simplified equation:**")
            st.latex(r"H_{demand} = (z_2-z_1) + H_{total\_loss}")
            
            st.write(f"H_demand = {calc_results['static_head']:.1f} + {calc_results['total_dynamic_loss']:.2f}")
            st.write(f"H_demand = **{calc_results['total_head_demand']:.2f} m**")
    
    # Fittings breakdown if any selected
    if selected_fittings:
        st.markdown("---")
        st.subheader("🔧 Selected Fittings Analysis")
        
        col6, col7 = st.columns([1, 1])
        
        with col6:
            # Create fittings breakdown table
            fittings_data = []
            for name, data in selected_fittings.items():
                individual_loss = calc_results['friction_factor'] * 4 * (pipe_diameter * data['n']) / pipe_diameter * (calc_results['velocity']**2) / (2 * 9.81) * data['quantity']
                fittings_data.append({
                    "Fitting": f"{data['icon']} {name}",
                    "Quantity": data['quantity'],
                    "n (Le/D)": data['n'],
                    "Total n": data['n'] * data['quantity'],
                    "Le (m)": pipe_diameter * data['n'] * data['quantity'],
                    "Head Loss (m)": individual_loss
                })
            
            df_fittings = pd.DataFrame(fittings_data)
            st.dataframe(df_fittings, use_container_width=True)
        
        with col7:
            # Create pie chart of fitting contributions
            fig_fittings = create_fittings_breakdown_chart(selected_fittings, calc_results)
            st.plotly_chart(fig_fittings, use_container_width=True)
    
    # Analysis insights
    st.markdown("---")
    st.subheader("💡 Analysis Insights")
    
    # Create pie chart of head loss components
    fig_breakdown = create_head_loss_breakdown(calc_results)
    
    col8, col9 = st.columns([1, 1])
    
    with col8:
        st.plotly_chart(fig_breakdown, use_container_width=True)
    
    with col9:
        st.markdown("#### 🔍 System Characteristics")
        
        # Calculate percentages
        total_head = calc_results['total_head_demand']
        static_pct = (calc_results['static_head'] / total_head) * 100
        pipe_friction_pct = (calc_results['pipe_friction_loss'] / total_head) * 100
        fittings_pct = (calc_results['fittings_loss'] / total_head) * 100
        
        st.markdown(f"**Static Head:** {static_pct:.1f}% of total")
        st.markdown(f"**Pipe Friction:** {pipe_friction_pct:.1f}% of total")
        st.markdown(f"**Fittings Losses:** {fittings_pct:.1f}% of total")
        
        if static_pct > 70:
            st.info("🏔️ **Static-dominated system** - Head requirement mainly due to elevation difference")
        elif pipe_friction_pct > 50:
            st.warning("🔧 **Friction-dominated system** - Consider larger pipe diameter to reduce losses")
        elif fittings_pct > 30:
            st.warning("⚙️ **Fitting-dominated system** - Consider reducing number of fittings or using low-loss alternatives")
        else:
            st.success("⚖️ **Balanced system** - Reasonable distribution of head losses")
        
        # Velocity check
        if calc_results['velocity'] > 3:
            st.warning(f"⚠️ **High velocity** ({calc_results['velocity']:.1f} m/s) - Consider larger pipe diameter")
        elif calc_results['velocity'] < 0.5:
            st.info(f"🐌 **Low velocity** ({calc_results['velocity']:.1f} m/s) - System may be oversized")
        else:
            st.success(f"✅ **Good velocity** ({calc_results['velocity']:.1f} m/s) - Within recommended range")
    
    # Summary equation box
    st.markdown("---")
    st.subheader("📋 Summary")
    
    # Create a summary box with the key equation and result
    summary_col1, summary_col2 = st.columns([1, 1])
    
    with summary_col1:
        st.markdown("### **System Equation (Equivalent Length)**")
        st.latex(r"H_{demand} = \Delta z + C_f \frac{4L_e}{D} \frac{V^2}{2g}")
        st.latex(r"L_e = L_{pipe} + D \sum (n \times quantity)")
        
        st.markdown("**Substituting values:**")
        st.write(f"• Δz = {calc_results['static_head']:.1f} m")
        st.write(f"• Le = {calc_results['equivalent_length']:.1f} m")
        st.write(f"• V = {calc_results['velocity']:.2f} m/s")
        st.write(f"• Cf = {calc_results['friction_factor']:.4f}")
    
    with summary_col2:
        st.markdown("### **Final Answer**")
        
        # Large result box
        st.markdown(f"""
        <div style="
            background-color: #e1f5fe; 
            border: 2px solid #01579b; 
            border-radius: 10px; 
            padding: 20px; 
            text-align: center;
            margin: 20px 0px;
        ">
            <h2 style="color: #01579b; margin: 0;">H<sub>demand</sub> = {calc_results['total_head_demand']:.2f} m</h2>
            <p style="margin: 5px 0; font-size: 16px;">Required pump head for Q = {flow_rate:.1f} m³/h</p>
        </div>
        """, unsafe_allow_html=True)

def fittings_reference_tab():
    """Reference tab showing the fittings database"""
    
    st.subheader("📋 Fittings Reference Table")
    st.markdown("Reference data for pipe fittings using equivalent length method (n = Le/D values)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create reference table
        fittings_db = get_fittings_database()
        
        ref_data = []
        for fitting_name, data in fittings_db.items():
            ref_data.append({
                "Fitting": f"{data['icon']} {fitting_name}",
                "n = Le/D": data['n'],
                "Category": get_fitting_category(fitting_name)
            })
        
        df_ref = pd.DataFrame(ref_data)
        st.dataframe(df_ref, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📐 Equivalent Length Method")
        
        st.markdown("**Converting fittings to equivalent pipe length:**")
        st.latex(r"L_e = L_{pipe} + D \sum (n \times quantity)")
        st.latex(r"h_L = C_f \frac{4L_e}{D} \frac{V^2}{2g}")
        
        st.markdown("**Where:**")
        st.write("• Le = total equivalent length")
        st.write("• Lpipe = actual pipe length") 
        st.write("• n = Le/D ratio for each fitting (from table above)")
        st.write("• Cf = Darcy friction factor")
        
        st.markdown("**Advantages:**")
        st.write("• Converts all fittings to equivalent pipe length")
        st.write("• Simpler calculation for multiple fittings")
        st.write("• Single formula for all losses")
        st.write("• Widely used in engineering practice")
    
    with col2:
        st.markdown("### 💡 Usage Tips")
        
        st.info("""
        **High Loss Fittings (avoid if possible):**
        • Globe valves (n=180)
        • Gate valve 1/4 open (n=800)
        • Sharp exit (n=50)
        
        **Low Loss Fittings (prefer these):**
        • Gate valve fully open (n=7)
        • Radius elbow (n=23)
        • Radius inlet (n=0)
        
        **Note:** n = Le/D is the equivalent length ratio
        """)
        
        st.markdown("### 🔍 Fitting Categories")
        
        categories = {
            "Valves": ["Gate Valve", "Globe Valve"],
            "Bends": ["90° Standard Elbow", "90° Radius Elbow"],
            "Inlets": ["Sharp Inlet", "Radius Inlet", "Re-entrant Inlet"],
            "Exits": ["Sharp Pipe Exit"]
        }
        
        for category, fittings in categories.items():
            with st.expander(f"{category}"):
                for fitting in fittings:
                    matching_fittings = [k for k in fittings_db.keys() if any(f in k for f in [fitting])]
                    for match in matching_fittings:
                        data = fittings_db[match]
                        st.write(f"• {data['icon']} {match}: n={data['n']}")

# Helper functions

def calculate_system_head_demand_equivalent_length(flow_rate_m3s, pipe_length, pipe_diameter, roughness, z1, z2, density, viscosity, selected_fittings):
    """Calculate system head demand using equivalent length method"""
    
    # Basic calculations
    pipe_area = np.pi * pipe_diameter**2 / 4
    velocity = flow_rate_m3s / pipe_area if pipe_area > 0 else 0
    
    # Reynolds number
    reynolds = velocity * pipe_diameter / viscosity if viscosity > 0 else 1e6
    
    # Flow regime and friction factor
    if reynolds < 2300:
        flow_regime = "Laminar"
        friction_factor = 64 / reynolds if reynolds > 0 else 0.02
    else:
        flow_regime = "Turbulent"
        # Churchill equation for friction factor
        epsilon_D = roughness / pipe_diameter if pipe_diameter > 0 else 0
        if reynolds > 0:
            term = 0.27 * epsilon_D + (7/reynolds)**0.9
            friction_factor = (1/(-4 * np.log10(term)))**2
        else:
            friction_factor = 0.02
    
    # Head loss components
    static_head = z2 - z1
    
    # Calculate total equivalent length using Method 2
    # Le = Lpipe + D × Σ(n × quantity)
    total_n_value = 0
    if selected_fittings:
        for fitting_name, fitting_data in selected_fittings.items():
            total_n_value += fitting_data['n'] * fitting_data['quantity']
    
    equivalent_length = pipe_length + pipe_diameter * total_n_value
    
    # Total head loss using equivalent length
    # h_L = Cf × (4Le/D) × (V²/2g)
    total_dynamic_loss = friction_factor * (4 * equivalent_length / pipe_diameter) * (velocity**2) / (2 * 9.81) if pipe_diameter > 0 else 0
    
    # Separate pipe friction and fittings losses for display
    pipe_friction_loss = friction_factor * (4 * pipe_length / pipe_diameter) * (velocity**2) / (2 * 9.81) if pipe_diameter > 0 else 0
    fittings_loss = total_dynamic_loss - pipe_friction_loss
    
    # Total head demand
    total_head_demand = static_head + total_dynamic_loss
    
    # Power calculations
    required_pressure = total_head_demand * density * 9.81
    power_80_eff = flow_rate_m3s * required_pressure / (0.80 * 1000)  # kW
    power_70_eff = flow_rate_m3s * required_pressure / (0.70 * 1000)  # kW
    
    return {
        'velocity': velocity,
        'reynolds': reynolds,
        'flow_regime': flow_regime,
        'friction_factor': friction_factor,
        'static_head': static_head,
        'pipe_friction_loss': pipe_friction_loss,
        'fittings_loss': fittings_loss,
        'total_dynamic_loss': total_dynamic_loss,
        'total_head_demand': total_head_demand,
        'required_pressure': required_pressure,
        'power_80_eff': power_80_eff,
        'power_70_eff': power_70_eff,
        'equivalent_length': equivalent_length,
        'total_n_value': total_n_value
    }

def create_system_diagram(z1, z2, pipe_length, pipe_diameter_mm, flow_rate, selected_fittings):
    """Create an enhanced visual diagram of the two-reservoir system with selected fittings"""
    
    fig = go.Figure()
    
    # Add background gradient/sky
    fig.add_shape(type="rect", x0=-2, y0=z1-5, x1=13, y1=z2+10,
                  fillcolor="rgba(135,206,235,0.3)", line=dict(width=0))
    
    # Add ground/terrain
    ground_level = z1 - 1
    fig.add_shape(type="rect", x0=-2, y0=z1-5, x1=13, y1=ground_level,
                  fillcolor="rgba(139,69,19,0.6)", line=dict(width=0))
    
    # Reservoir 1 (lower) - more realistic with water
    reservoir1_width = 3.5
    reservoir1_height = 3
    
    # Reservoir 1 structure (concrete walls)
    fig.add_shape(type="rect", x0=-0.2, y0=z1-0.5, x1=reservoir1_width, y1=z1+reservoir1_height, 
                  fillcolor="rgba(169,169,169,0.8)", line=dict(color="gray", width=3))
    
    # Water in reservoir 1
    water_level_1 = z1 + reservoir1_height * 0.8
    fig.add_shape(type="rect", x0=0, y0=z1, x1=reservoir1_width-0.2, y1=water_level_1, 
                  fillcolor="rgba(0,191,255,0.7)", line=dict(color="blue", width=1))
    
    # Water surface animation effect (small waves)
    wave_x = np.linspace(0, reservoir1_width-0.2, 20)
    wave_y = water_level_1 + 0.05 * np.sin(10 * wave_x)
    fig.add_trace(go.Scatter(x=wave_x, y=wave_y, mode='lines', 
                           line=dict(color='navy', width=2), showlegend=False))
    
    # Reservoir 1 label with better styling
    fig.add_annotation(x=reservoir1_width/2, y=z1+reservoir1_height+0.5, 
                      text="<b>Reservoir 1</b><br>(Lower)", showarrow=False, 
                      font=dict(size=14, color="darkblue"),
                      bgcolor="rgba(255,255,255,0.8)", bordercolor="blue", borderwidth=1)
    
    # Reservoir 2 (upper) - more realistic with water
    reservoir2_width = 3.5
    reservoir2_height = 3
    
    # Reservoir 2 structure
    fig.add_shape(type="rect", x0=6.8, y0=z2-0.5, x1=6.8+reservoir2_width, y1=z2+reservoir2_height, 
                  fillcolor="rgba(169,169,169,0.8)", line=dict(color="gray", width=3))
    
    # Water in reservoir 2
    water_level_2 = z2 + reservoir2_height * 0.6  # Lower water level
    fig.add_shape(type="rect", x0=7, y0=z2, x1=6.8+reservoir2_width-0.2, y1=water_level_2, 
                  fillcolor="rgba(0,191,255,0.7)", line=dict(color="blue", width=1))
    
    # Water surface in reservoir 2
    wave_x2 = np.linspace(7, 6.8+reservoir2_width-0.2, 20)
    wave_y2 = water_level_2 + 0.05 * np.sin(10 * wave_x2)
    fig.add_trace(go.Scatter(x=wave_x2, y=wave_y2, mode='lines', 
                           line=dict(color='navy', width=2), showlegend=False))
    
    # Reservoir 2 label
    fig.add_annotation(x=6.8+reservoir2_width/2, y=z2+reservoir2_height+0.5, 
                      text="<b>Reservoir 2</b><br>(Upper)", showarrow=False, 
                      font=dict(size=14, color="darkblue"),
                      bgcolor="rgba(255,255,255,0.8)", bordercolor="blue", borderwidth=1)
    
    # Enhanced connecting pipe with gradient effect
    pipe_y_start = water_level_1
    pipe_y_end = water_level_2
    
    # Main pipe with gradient
    pipe_points_x = [3.2, 3.5, 4, 5, 6, 6.5, 6.8]
    pipe_points_y = [pipe_y_start, pipe_y_start + 5, pipe_y_start + 15, 
                     (pipe_y_start + pipe_y_end)/2, pipe_y_end - 15, pipe_y_end - 5, pipe_y_end]
    
    # Pipe outline (darker)
    fig.add_trace(go.Scatter(x=pipe_points_x, y=[y + 0.2 for y in pipe_points_y], 
                           mode='lines', line=dict(color='darkgray', width=8), showlegend=False))
    fig.add_trace(go.Scatter(x=pipe_points_x, y=[y - 0.2 for y in pipe_points_y], 
                           mode='lines', line=dict(color='darkgray', width=8), showlegend=False))
    
    # Pipe interior (lighter)
    fig.add_trace(go.Scatter(x=pipe_points_x, y=pipe_points_y, mode='lines', 
                           line=dict(color='lightblue', width=6), showlegend=False))
    
    # Enhanced pump symbol
    pump_x = 5
    pump_y = (pipe_y_start + pipe_y_end) / 2
    
    # Pump housing (main body)
    fig.add_shape(type="rect", x0=pump_x-0.7, y0=pump_y-0.5, x1=pump_x+0.7, y1=pump_y+0.5,
                  fillcolor="rgba(255,165,0,0.9)", line=dict(color="darkorange", width=3))
    
    # Pump impeller (inner circle)
    fig.add_shape(type="circle", x0=pump_x-0.3, y0=pump_y-0.3, x1=pump_x+0.3, y1=pump_y+0.3,
                  fillcolor="rgba(255,215,0,0.8)", line=dict(color="gold", width=2))
    
    # Pump motor
    fig.add_shape(type="rect", x0=pump_x-0.4, y0=pump_y+0.5, x1=pump_x+0.4, y1=pump_y+1,
                  fillcolor="rgba(128,128,128,0.8)", line=dict(color="black", width=2))
    
    # Pump label with better styling
    fig.add_annotation(x=pump_x, y=pump_y-1.2, text="<b>🔄 PUMP</b>", showarrow=False, 
                      font=dict(size=14, color="darkorange"),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor="orange", borderwidth=2)
    
    # Enhanced fittings with better visual design
    if selected_fittings:
        fitting_positions = np.linspace(3.8, 6.2, len(selected_fittings))
        
        i = 0
        for fitting_name, fitting_data in selected_fittings.items():
            if i < len(fitting_positions):
                x_pos = fitting_positions[i]
                y_pos = np.interp(x_pos, pipe_points_x, pipe_points_y)
                
                # Enhanced fitting symbols with better colors and shapes
                if "Valve" in fitting_name:
                    # Valve symbol - diamond shape
                    fig.add_shape(type="rect", x0=x_pos-0.2, y0=y_pos-0.2, x1=x_pos+0.2, y1=y_pos+0.2,
                                 fillcolor="rgba(220,20,60,0.8)", line=dict(color="darkred", width=2))
                    # Valve stem
                    fig.add_shape(type="line", x0=x_pos, y0=y_pos+0.2, x1=x_pos, y1=y_pos+0.5,
                                 line=dict(color="darkred", width=3))
                    
                elif "Elbow" in fitting_name:
                    # Elbow symbol - curved
                    fig.add_shape(type="circle", x0=x_pos-0.15, y0=y_pos-0.15, x1=x_pos+0.15, y1=y_pos+0.15,
                                 fillcolor="rgba(34,139,34,0.8)", line=dict(color="darkgreen", width=2))
                    
                elif "Inlet" in fitting_name:
                    # Inlet symbol - funnel shape
                    fig.add_shape(type="rect", x0=x_pos-0.25, y0=y_pos-0.1, x1=x_pos+0.1, y1=y_pos+0.1,
                                 fillcolor="rgba(30,144,255,0.8)", line=dict(color="blue", width=2))
                    
                elif "Exit" in fitting_name:
                    # Exit symbol - expanding
                    fig.add_shape(type="rect", x0=x_pos-0.1, y0=y_pos-0.1, x1=x_pos+0.25, y1=y_pos+0.1,
                                 fillcolor="rgba(138,43,226,0.8)", line=dict(color="purple", width=2))
                
                # Enhanced fitting labels
                label = f"{fitting_data['icon']}"
                if fitting_data['quantity'] > 1:
                    label += f" ×{fitting_data['quantity']}"
                
                fig.add_annotation(x=x_pos, y=y_pos+0.7, text=f"<b>{label}</b>", 
                                 showarrow=False, font=dict(size=10, color="black"),
                                 bgcolor="rgba(255,255,255,0.8)", bordercolor="gray", borderwidth=1)
                i += 1
    
    # Enhanced elevation annotations with better styling
    fig.add_annotation(x=-0.5, y=water_level_1, text=f"<b>z₁ = {z1} m</b>", 
                      showarrow=True, arrowcolor="darkblue", arrowwidth=2,
                      font=dict(size=12, color="darkblue"),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor="blue", borderwidth=1)
    
    fig.add_annotation(x=11, y=water_level_2, text=f"<b>z₂ = {z2} m</b>", 
                      showarrow=True, arrowcolor="darkblue", arrowwidth=2,
                      font=dict(size=12, color="darkblue"),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor="blue", borderwidth=1)
    
    # Enhanced elevation difference indicator
    fig.add_shape(type="line", x0=11.5, y0=water_level_1, x1=11.5, y1=water_level_2, 
                  line=dict(color="red", width=3, dash="dash"))
    
    # Elevation difference arrows
    fig.add_annotation(x=11.5, y=water_level_1, ax=11.5, ay=water_level_1+10,
                      xref='x', yref='y', axref='x', ayref='y',
                      arrowhead=2, arrowsize=1, arrowwidth=3, arrowcolor='red')
    fig.add_annotation(x=11.5, y=water_level_2, ax=11.5, ay=water_level_2-10,
                      xref='x', yref='y', axref='x', ayref='y',
                      arrowhead=2, arrowsize=1, arrowwidth=3, arrowcolor='red')
    
    fig.add_annotation(x=12.2, y=(water_level_1+water_level_2)/2, 
                      text=f"<b>Δz = {z2-z1} m</b>", showarrow=False, 
                      font=dict(size=14, color="red"),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor="red", borderwidth=2,
                      textangle=90)
    
    # Enhanced system specifications
    spec_text = f"<b>📏 Pipe:</b> L = {pipe_length} m, D = {pipe_diameter_mm:.0f} mm"
    if selected_fittings:
        total_fittings = sum(data['quantity'] for data in selected_fittings.values())
        spec_text += f"<br><b>⚙️ Fittings:</b> {total_fittings} components"
    
    fig.add_annotation(x=5, y=z1-4, text=spec_text, showarrow=False, 
                      font=dict(size=12, color="darkslategray"),
                      bgcolor="rgba(255,255,255,0.9)", bordercolor="gray", borderwidth=1)
    
    # Add title with better styling
    fig.update_layout(
        title={
            'text': "<b>🏔️ Two-Reservoir Pumping System</b>",
            'x': 0.5,
            'font': {'size': 20, 'color': 'darkslategray'}
        },
        xaxis=dict(range=[-2, 13], showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(range=[z1-5, z2+8], showticklabels=True, title="<b>Elevation (m)</b>", 
                  title_font=dict(size=14, color="darkblue")),
        showlegend=False,
        width=900, height=500,
        plot_bgcolor='rgba(248,248,255,0.8)',
        paper_bgcolor='white'
    )
    
    return fig

def create_head_loss_breakdown(calc_results):
    """Create pie chart showing breakdown of head losses"""
    
    labels = ['Static Head', 'Pipe Friction', 'Fittings']
    values = [
        calc_results['static_head'],
        calc_results['pipe_friction_loss'],
        calc_results['fittings_loss']
    ]
    colors = ['lightblue', 'orange', 'red']
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3,
                                marker_colors=colors)])
    
    fig.update_layout(
        title="Head Loss Breakdown",
        annotations=[dict(text='Head<br>Components', x=0.5, y=0.5, font_size=12, showarrow=False)]
    )
    
    return fig

def create_fittings_breakdown_chart(selected_fittings, calc_results):
    """Create chart showing contribution of each fitting type"""
    
    fitting_contributions = []
    labels = []
    
    for name, data in selected_fittings.items():
        # Calculate individual contribution to equivalent length
        contribution = data['n'] * data['quantity']
        fitting_contributions.append(contribution)
        label = f"{data['icon']} {name}"
        if data['quantity'] > 1:
            label += f" (×{data['quantity']})"
        labels.append(label)
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=fitting_contributions, hole=0.3)])
    
    fig.update_layout(
        title="Fitting Contributions to Equivalent Length",
        annotations=[dict(text='Σ(n×qty)', x=0.5, y=0.5, font_size=12, showarrow=False)]
    )
    
    return fig

def get_fitting_category(fitting_name):
    """Get category for fitting organization"""
    if "Valve" in fitting_name:
        return "Valves"
    elif "Elbow" in fitting_name:
        return "Bends"
    elif "Inlet" in fitting_name:
        return "Inlets"
    elif "Exit" in fitting_name:
        return "Exits"
    else:
        return "Other"

if __name__ == "__main__":
    main()
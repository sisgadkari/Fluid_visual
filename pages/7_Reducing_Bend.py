import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Pipe Bend Momentum Analysis", layout="wide")

# --- Sidebar for Inputs and Calculations ---
with st.sidebar:
    st.header("🔧 System Parameters")
    
    # Fluid Properties
    st.subheader("Fluid Properties")
    fluid_type = st.selectbox("Select Fluid", ["Water", "Air", "Oil", "Custom"])
    
    if fluid_type == "Water":
        rho = 1000.0  # kg/m³
    elif fluid_type == "Air":
        rho = 1.2  # kg/m³
    elif fluid_type == "Oil":
        rho = 850.0  # kg/m³
    else:
        rho = st.number_input("Fluid Density ρ (kg/m³)", value=1000.0, min_value=0.1, step=10.0)
    
    st.caption(f"ρ = {rho:.1f} kg/m³")
    
    # Pipe Geometry
    st.subheader("Pipe Geometry")
    D1_cm = st.number_input("Inlet Diameter D₁ (cm)", value=20.0, min_value=5.0, max_value=100.0, step=1.0)
    D1 = D1_cm / 100  # Convert to meters
    D2_cm = st.number_input("Outlet Diameter D₂ (cm)", value=10.0, min_value=5.0, max_value=D1_cm, step=1.0)
    D2 = D2_cm / 100  # Convert to meters
    
    theta_deg = st.slider("Bend Angle θ (degrees)", 30, 90, 45, step=5,
                         help="Angle between inlet and outlet directions (limited to 30-90° for visual clarity)")
    theta = np.radians(theta_deg)
    
    # Flow Conditions
    st.subheader("Flow Conditions")
    
    flow_unit = st.radio("Flow Rate Units", ["L/s", "m³/h", "kg/s"], horizontal=True)
    
    if flow_unit == "L/s":
        Q_input = st.number_input("Flow Rate Q (L/s)", value=10.0, min_value=0.1, step=0.5)
        Q = Q_input / 1000
    elif flow_unit == "m³/h":
        Q_input = st.number_input("Flow Rate Q (m³/h)", value=36.0, min_value=0.1, step=1.0)
        Q = Q_input / 3600
    else:  # kg/s
        m_dot = st.number_input("Mass Flow Rate ṁ (kg/s)", value=10.0, min_value=0.1, step=0.5)
        Q = m_dot / rho if rho > 0 else 0
    
    if flow_unit != "kg/s":
        m_dot = rho * Q

    # --- Pressure Unit Selection and Conversion ---
    pressure_unit = st.radio("Inlet Pressure Unit", ["kPa", "atm"], horizontal=True)
    if pressure_unit == "kPa":
        p1_gauge_val = st.number_input("Inlet Gauge Pressure p₁ (kPa)", value=200.0, min_value=0.0, step=10.0)
        p1_gauge = p1_gauge_val * 1000  # Pa
        p1_gauge_kPa = p1_gauge_val
    else:  # atm
        p1_gauge_val = st.number_input("Inlet Gauge Pressure p₁ (atm)", value=2.0, min_value=0.0, step=0.1, format="%.2f")
        p1_gauge = p1_gauge_val * 101325  # 1 atm = 101325 Pa
        p1_gauge_kPa = p1_gauge / 1000

# --- Calculations ---
A1 = np.pi * (D1/2)**2
A2 = np.pi * (D2/2)**2
U1 = Q / A1 if A1 > 0 else 0
U2 = Q / A2 if A2 > 0 else 0
p2_gauge = p1_gauge + 0.5 * rho * (U1**2 - U2**2)
p2_gauge_kPa = p2_gauge / 1000
Fx_fluid = m_dot * (U2 * np.cos(theta) - U1) + p1_gauge * A1 - p2_gauge * A2 * np.cos(theta)
Fy_fluid = m_dot * U2 * np.sin(theta) - p2_gauge * A2 * np.sin(theta)
Rx = -Fx_fluid
Ry = -Fy_fluid
R = np.sqrt(Rx**2 + Ry**2)
phi = np.degrees(np.arctan2(Ry, Rx)) if Rx != 0 else (90 if Ry > 0 else -90)

# --- Main Page Content ---
st.markdown("<h1 style='text-align: center;'>Interactive Pipe Bend Momentum Analysis</h1>", unsafe_allow_html=True)
st.markdown("""<p style='text-align: center; font-size: 18px;'>Explore how fluid momentum changes create forces on pipe bends. Adjust the parameters in the sidebar to see how flow rate, pipe dimensions, and bend angle affect the forces on the pipe.</p>""", unsafe_allow_html=True)
st.markdown("---")

st.header("🎨 Visualization")
    
# Pipe Bend Visualization
fig_pipe = go.Figure()

inlet_length, outlet_length, bend_radius = 0.8, 0.8, 0.8
inlet_x, inlet_y_top, inlet_y_bot = [-inlet_length, 0], [D1/2, D1/2], [-D1/2, -D1/2]

n_bend = 50
bend_angles = np.linspace(0, theta, n_bend)
D_bend = np.linspace(D1, D2, n_bend)
x_centerline = bend_radius * np.sin(bend_angles)
y_centerline = bend_radius * (1 - np.cos(bend_angles))

x_bend_top, y_bend_top, x_bend_bot, y_bend_bot = [], [], [], []

for i in range(n_bend):
    normal_angle = bend_angles[i] + np.pi/2 if i > 0 else np.pi/2
    x_bend_top.append(x_centerline[i] + D_bend[i]/2 * np.cos(normal_angle))
    y_bend_top.append(y_centerline[i] + D_bend[i]/2 * np.sin(normal_angle))
    x_bend_bot.append(x_centerline[i] - D_bend[i]/2 * np.cos(normal_angle))
    y_bend_bot.append(y_centerline[i] - D_bend[i]/2 * np.sin(normal_angle))

outlet_start_x, outlet_start_y = x_centerline[-1], y_centerline[-1]
outlet_end_x = outlet_start_x + outlet_length * np.cos(theta)
outlet_end_y = outlet_start_y + outlet_length * np.sin(theta)

outlet_normal = theta + np.pi/2
outlet_x_top = [outlet_start_x + D2/2 * np.cos(outlet_normal), outlet_end_x + D2/2 * np.cos(outlet_normal)]
outlet_y_top = [outlet_start_y + D2/2 * np.sin(outlet_normal), outlet_end_y + D2/2 * np.sin(outlet_normal)]
outlet_x_bot = [outlet_start_x - D2/2 * np.cos(outlet_normal), outlet_end_x - D2/2 * np.cos(outlet_normal)]
outlet_y_bot = [outlet_start_y - D2/2 * np.sin(outlet_normal), outlet_end_y - D2/2 * np.sin(outlet_normal)]

x_top, y_top = inlet_x + x_bend_top + outlet_x_top, inlet_y_top + y_bend_top + outlet_y_top
fig_pipe.add_trace(go.Scatter(x=x_top, y=y_top, mode='lines', line=dict(color='black', width=3), showlegend=False, hoverinfo='none'))

x_bot, y_bot = inlet_x + x_bend_bot + outlet_x_bot, inlet_y_bot + y_bend_bot + outlet_y_bot
fig_pipe.add_trace(go.Scatter(x=x_bot, y=y_bot, mode='lines', line=dict(color='black', width=3), showlegend=False, hoverinfo='none'))

x_fill, y_fill = x_top + outlet_x_bot[::-1] + x_bend_bot[::-1] + inlet_x[::-1], y_top + outlet_y_bot[::-1] + y_bend_bot[::-1] + inlet_y_bot[::-1]
fluid_color = 'rgba(59, 130, 246, 0.5)' if fluid_type == "Water" else 'rgba(200, 200, 200, 0.5)'
fig_pipe.add_trace(go.Scatter(x=x_fill, y=y_fill, fill="toself", fillcolor=fluid_color, mode='none', showlegend=False, hoverinfo='none'))

fig_pipe.add_annotation(x=-inlet_length*0.7, y=0, ax=-inlet_length*0.7 - 0.2, ay=0, showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor='darkblue')
arrow_x, arrow_y = outlet_start_x + outlet_length*0.5 * np.cos(theta), outlet_start_y + outlet_length*0.5 * np.sin(theta)
fig_pipe.add_annotation(x=arrow_x, y=arrow_y, ax=arrow_x - 0.2*np.cos(theta), ay=arrow_y - 0.2*np.sin(theta), showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor='darkblue')

fig_pipe.add_annotation(x=-inlet_length/2, y=D1/2+0.15, text=f"D₁={D1_cm:.0f}cm<br>U₁={U1:.2f}m/s<br>p₁={p1_gauge_kPa:.0f}kPa", showarrow=False, font=dict(size=16), bgcolor="white", borderwidth=1)
outlet_label_x, outlet_label_y = outlet_start_x + outlet_length*0.5*np.cos(theta), outlet_start_y + outlet_length*0.5*np.sin(theta) + D2/2 + 0.15
fig_pipe.add_annotation(x=outlet_label_x, y=outlet_label_y, text=f"D₂={D2_cm:.0f}cm<br>U₂={U2:.2f}m/s<br>p₂={p2_gauge_kPa:.0f}kPa", showarrow=False, font=dict(size=16), bgcolor="white", borderwidth=1)

# Angle annotation moved outside the pipe
angle_arc_radius = bend_radius + D1/2 + 0.2
fig_pipe.add_annotation(x=angle_arc_radius*np.sin(theta/2), y=angle_arc_radius*(1-np.cos(theta/2)) - 0.1, text=f"θ={theta_deg}°", showarrow=False, font=dict(size=14, color='red'))

# --- Show resultant force vector at fixed position above the bend ---
# Choose fixed position above bend
force_x_pos = (bend_radius + D1/2) * np.sin(theta/2)
force_y_pos = (bend_radius + D1/2) * (1 - np.cos(theta/2)) + 1.0  # 1.0 above
force_length = 0.5  # fixed visual length

phi_rad = np.radians(phi)
force_arrow_x = force_x_pos + force_length * np.cos(phi_rad)
force_arrow_y = force_y_pos + force_length * np.sin(phi_rad)

fig_pipe.add_annotation(
    x=force_arrow_x, y=force_arrow_y,
    ax=force_x_pos, ay=force_y_pos,
    showarrow=True, arrowhead=3, arrowsize=2, arrowwidth=5, arrowcolor="red"
)
fig_pipe.add_annotation(
    x=force_arrow_x, y=force_arrow_y + 0.15,
    text=f"<b>R = {R/1000:.2f} kN<br>φ = {phi:.1f}°</b>",
    font=dict(color="red", size=24),
    showarrow=False
)

# Determine plot range dynamically to fit the pipe bend
all_x = x_top + x_bot
all_y = y_top + y_bot
x_min, x_max = min(all_x), max(all_x)
y_min, y_max = min(all_y), max(all_y)

# Add padding
padding_x = (x_max - x_min) * 0.2
padding_y = (y_max - y_min) * 0.2
x_range = [x_min - padding_x, x_max + padding_x]
y_range = [y_min - padding_y, y_max + padding_y + 1.2]  # Add more for vector

fig_pipe.update_layout(
    xaxis=dict(range=x_range, visible=False, scaleanchor="y", scaleratio=1), 
    yaxis=dict(range=y_range, visible=False), 
    plot_bgcolor='white', 
    height=700, 
    showlegend=False, 
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig_pipe, use_container_width=True)

st.markdown("---")
st.header("📊 Calculations & Results")

# Display calculated values
col_c1, col_c2 = st.columns(2)
with col_c1:
    st.metric("Inlet Velocity U₁", f"{U1:.2f} m/s")
    st.metric("Inlet Area A₁", f"{A1*10000:.1f} cm²")
    st.metric("Mass Flow Rate ṁ", f"{m_dot:.2f} kg/s")
with col_c2:
    st.metric("Outlet Velocity U₂", f"{U2:.2f} m/s")
    st.metric("Outlet Area A₂", f"{A2*10000:.1f} cm²")
    st.metric("Outlet Pressure p₂", f"{p2_gauge_kPa:.1f} kPa")

# Momentum Forces
st.subheader("Force Analysis")
st.metric("Force on Pipe (X-component) Rₓ", f"{Rx:.1f} N")
st.metric("Force on Pipe (Y-component) Rᵧ", f"{Ry:.1f} N")
st.metric("Total Force on Pipe |R|", f"{R:.1f} N", delta=f"at {phi:.1f}°")

# Educational content
with st.expander("📚 Understanding Momentum Forces in Pipe Bends"):
    st.markdown("""
    ### The Physics Behind Pipe Bend Forces
    When fluid flows through a pipe bend, it must change direction. According to Newton's second law, 
    this change in momentum requires a force. The pipe must exert this force on the fluid, and by 
    Newton's third law, the fluid exerts an equal and opposite force on the pipe.
    """)

# Problem-solving guide
with st.expander("🎯 Step-by-Step Solution Guide"):
    st.markdown(f"""
    ### Given Data:
    - Inlet diameter: D₁ = {D1_cm} cm = {D1:.3f} m
    - Outlet diameter: D₂ = {D2_cm} cm = {D2:.3f} m
    - Bend angle: θ = {theta_deg}° = {theta:.3f} rad
    - Flow rate: Q = {Q*1000:.2f} L/s = {Q:.4f} m³/s
    - Fluid density: ρ = {rho} kg/m³
    - Inlet pressure: p₁ = {p1_gauge_kPa} kPa (gauge)
        
    ### Step 1: Calculate Areas
    - A₁ = π(D₁/2)² = π({D1/2:.3f})² = {A1:.6f} m²
    - A₂ = π(D₂/2)² = π({D2/2:.3f})² = {A2:.6f} m²
        
    ### Step 2: Find Velocities (Continuity Equation)
    - U₁ = Q/A₁ = {Q:.4f}/{A1:.6f} = {U1:.2f} m/s
    - U₂ = Q/A₂ = {Q:.4f}/{A2:.6f} = {U2:.2f} m/s
        
    ### Step 3: Find Outlet Pressure (Bernoulli Equation)
    - p₂ = p₁ + ½ρ(U₁² - U₂²)
    - p₂ = {p1_gauge_kPa} + ½({rho})({U1:.2f}² - {U2:.2f}²)
    - p₂ = {p2_gauge_kPa:.1f} kPa
        
    ### Step 4: Apply Momentum Equation for Force on Fluid (F)
    - Fₓ = ṁ(U₂cosθ - U₁) + p₁A₁ - p₂A₂cosθ = {Fx_fluid:.1f} N
    - Fᵧ = ṁU₂sinθ - p₂A₂sinθ = {Fy_fluid:.1f} N
        
    ### Step 5: Find Reaction Force on Pipe (R)
    - Rₓ = -Fₓ = {Rx:.1f} N
    - Rᵧ = -Fᵧ = {Ry:.1f} N
    - |R| = √(Rₓ² + Rᵧ²) = {R:.1f} N
    - φ = tan⁻¹(Rᵧ/Rₓ) = {phi:.1f}°
    """)

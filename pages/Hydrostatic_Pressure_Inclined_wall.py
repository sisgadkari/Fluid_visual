import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(page_title="Hydrostatic Force on Inclined Wall", layout="wide")

# --- Custom CSS for a more professional look ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        font-size: 2.8em;
        font-weight: bold;
        color: #1c3977;
    }
    h2 {
        border-bottom: 2px solid #d0d0d0;
        padding-bottom: 8px;
        color: #1c3977;
    }
    h3 {
        color: #333333;
    }
    .stMetric {
        background-color: #F8F9FA;
        border: 1px solid #E0E0E0;
        border-left: 5px solid #D7263D;
        border-radius: 0.5rem;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>Hydrostatic Force on an Inclined Wall</h1>", unsafe_allow_html=True)
st.markdown(
    "<h4 style='text-align: center; font-weight: normal;'>Explore how inclination angle affects hydrostatic pressure distribution and total force on a submerged inclined surface.</h4>",
    unsafe_allow_html=True
)
st.markdown("---")

# --- Main Layout ---
col1, col2 = st.columns([2, 3])

# --- Column 1: Inputs and Results ---
with col1:
    st.header("🧮 Parameters")
    
    st.subheader("Wall Geometry")
    c1, c2 = st.columns(2)
    with c1:
        L = st.slider("Wall length, L (m)", 0.1, 10.0, 5.0, step=0.05,
                      help="Length of inclined wall along the slope")
    with c2:
        w = st.slider("Wall width, w (m)", 0.1, 10.0, 3.0, step=0.05,
                      help="Width of wall (into the page)")
    
    theta_deg = st.slider("Inclination angle, θ (degrees)", 0, 90, 45, step=1,
                          help="Angle from horizontal (0° = horizontal, 90° = vertical)")
    theta_rad = np.deg2rad(theta_deg)
    
    st.subheader("Fluid Properties")
    c1, c2 = st.columns(2)
    with c1:
        rho = st.number_input("Fluid density, ρ (kg/m³)", value=1000.0, step=10.0, format="%.1f")
    with c2:
        g = st.number_input("Gravity, g (m/s²)", value=9.81, format="%.2f")
    
    st.subheader("📊 Visualization Options")
    show_pressure_arrows = st.checkbox("Show Pressure Distribution", value=True,
                                     help="Toggle to visualize pressure acting perpendicular to inclined wall")
    
    if show_pressure_arrows:
        c1, c2 = st.columns(2)
        with c1:
            n_arrows = st.slider("Number of arrows", 5, 20, 10, step=1)
        with c2:
            arrow_style = st.radio("Arrow style", 
                                 ["Perpendicular arrows", "Triangular arrows", "Force vectors"])
    
    # --- Calculations ---
    # Vertical depth
    h = L * np.sin(theta_rad)
    
    # Normal force (perpendicular to inclined surface)
    F_N = 0.5 * rho * g * w * L**2 * np.sin(theta_rad)
    F_N_kN = F_N / 1000
    
    st.markdown("---")
    st.header("📈 Results")
    
    # Main force result
    st.metric(label="Normal Force on Wall (F_N)", value=f"{F_N_kN:,.2f} kN",
              help="Force acting perpendicular to inclined surface")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<b>Key Formulas:</b>", unsafe_allow_html=True)
    st.latex(r"F_N = \frac{1}{2}\,\rho\,g\,w\,L^2\,\sin\theta")

# --- Column 2: Visualization ---
with col2:
    st.header("📊 Inclined Wall Pressure Diagram")
    
    if not show_pressure_arrows:
        st.info("👆 Enable 'Show Pressure Distribution' to visualize pressure acting on the inclined wall")

    fig = go.Figure()
    
    # --- Geometry Setup ---
    x0, y0 = 0, 0
    x1, y1 = L * np.cos(theta_rad), L * np.sin(theta_rad)
    
    plot_width = max(L * 1.5, 8)
    plot_height = max(h * 1.5, 6)
    
    # 1. Draw water region (left side of wall only)
    water_points_x = [-plot_width/3]
    water_points_y = [0]
    n_wall_points = 50
    for i in range(n_wall_points + 1):
        frac = i / n_wall_points
        if frac * L * np.sin(theta_rad) <= h:
            water_points_x.append(frac * L * np.cos(theta_rad))
            water_points_y.append(frac * L * np.sin(theta_rad))
    water_points_x.extend([x1, -plot_width/3])
    water_points_y.extend([h, h])
    fig.add_trace(go.Scatter(
        x=water_points_x, y=water_points_y,
        fill="toself",
        fillcolor="rgba(0, 119, 182, 0.3)",
        line=dict(width=0),
        showlegend=False,
        hoverinfo='none'
    ))
    
    # 2. Draw pressure gradient on wall (always on)
    gradient_steps = 50
    for i in range(gradient_steps):
        s_start = i * L / gradient_steps
        s_end = (i + 1) * L / gradient_steps
        xs_start = s_start * np.cos(theta_rad)
        ys_start = s_start * np.sin(theta_rad)
        xs_end = s_end * np.cos(theta_rad)
        ys_end = s_end * np.sin(theta_rad)
        offset = 0.1
        perp_x = -np.sin(theta_rad) * offset
        perp_y = np.cos(theta_rad) * offset
        avg_depth = (ys_start + ys_end) / 2
        opacity = 0.02 + 0.15 * (avg_depth / h) if h > 0 else 0.02
        grad_x = [xs_start, xs_end, xs_end + perp_x, xs_start + perp_x]
        grad_y = [ys_start, ys_end, ys_end + perp_y, ys_start + perp_y]
        fig.add_trace(go.Scatter(
            x=grad_x, y=grad_y,
            fill="toself",
            fillcolor=f"rgba(255, 0, 0, {opacity})",
            line=dict(width=0),
            showlegend=False,
            hoverinfo='none'
        ))
    
    # 3. Draw the inclined wall
    fig.add_trace(go.Scatter(
        x=[x0, x1], y=[y0, y1],
        mode='lines',
        line=dict(color="black", width=8),
        name='Inclined Wall',
        showlegend=False
    ))
    
    # Add the horizontal base of the vessel
    fig.add_trace(go.Scatter(
        x=[-plot_width/3, x0], y=[y0, y0],
        mode='lines',
        line=dict(color="black", width=8),
        showlegend=False,
        hoverinfo='none'
    ))

    mid_x = (x0 + x1) / 2
    mid_y = (y0 + y1) / 2
    wall_angle = np.degrees(np.arctan2(y1 - y0, x1 - x0))
    fig.add_annotation(
        x=mid_x, y=mid_y,
        text="<b>WALL</b>",
        showarrow=False,
        font=dict(size=14, color="white"),
        textangle=-wall_angle,
        bgcolor="black",
        borderpad=4
    )
    
    # 4. Draw pressure arrows if enabled (depth = h - y_wall)
    if show_pressure_arrows:
        max_pressure = rho * g * h
        arrow_max_length = min(2.5, plot_width * 0.3)
        if arrow_style == "Perpendicular arrows":
            for i in range(n_arrows):
                frac = (i + 0.5) / n_arrows
                s = frac * L
                x_wall = s * np.cos(theta_rad)
                y_wall = s * np.sin(theta_rad)
                depth = h - y_wall
                pressure = rho * g * depth
                arrow_length = arrow_max_length * (pressure / max_pressure) if max_pressure > 0 else 0
                arrow_dx = -np.sin(theta_rad) * arrow_length
                arrow_dy = np.cos(theta_rad) * arrow_length
                fig.add_shape(
                    type="line",
                    x0=x_wall + arrow_dx, y0=y_wall + arrow_dy,
                    x1=x_wall - 0.02 * np.sin(theta_rad), y1=y_wall + 0.02 * np.cos(theta_rad),
                    line=dict(color="red", width=4)
                )
                head_size = 0.15
                head_perp_x = np.cos(theta_rad) * head_size/2
                head_perp_y = np.sin(theta_rad) * head_size/2
                head_along_x = -np.sin(theta_rad) * head_size
                head_along_y = np.cos(theta_rad) * head_size
                fig.add_trace(go.Scatter(
                    x=[x_wall + head_along_x - head_perp_x,
                       x_wall,
                       x_wall + head_along_x + head_perp_x],
                    y=[y_wall + head_along_y - head_perp_y,
                       y_wall,
                       y_wall + head_along_y + head_perp_y],
                    fill="toself",
                    fillcolor="red",
                    line=dict(color="red", width=0),
                    mode='lines',
                    showlegend=False,
                    hoverinfo='text',
                    text=f"Pressure: {pressure/1000:.1f} kPa<br>Depth: {depth:.1f} m"
                ))
        elif arrow_style == "Triangular arrows":
            for i in range(n_arrows):
                frac = (i + 0.5) / n_arrows
                s = frac * L
                x_wall = s * np.cos(theta_rad)
                y_wall = s * np.sin(theta_rad)
                depth = h - y_wall
                pressure = rho * g * depth
                arrow_length = arrow_max_length * (pressure / max_pressure) if max_pressure > 0 else 0
                arrow_dx = -np.sin(theta_rad) * arrow_length
                arrow_dy = np.cos(theta_rad) * arrow_length
                tri_width = 0.2
                width_x = np.cos(theta_rad) * tri_width/2
                width_y = np.sin(theta_rad) * tri_width/2
                fig.add_trace(go.Scatter(
                    x=[x_wall + arrow_dx - width_x,
                       x_wall,
                       x_wall + arrow_dx + width_x],
                    y=[y_wall + arrow_dy - width_y,
                       y_wall,
                       y_wall + arrow_dy + width_y],
                    fill="toself",
                    fillcolor="red",
                    line=dict(color="darkred", width=1),
                    mode='lines',
                    showlegend=False,
                    hoverinfo='text',
                    text=f"Pressure: {pressure/1000:.1f} kPa<br>Depth: {depth:.1f} m"
                ))
        else:  # Force vectors
            for i in range(n_arrows):
                frac = (i + 0.5) / n_arrows
                s = frac * L
                x_wall = s * np.cos(theta_rad)
                y_wall = s * np.sin(theta_rad)
                depth = h - y_wall
                pressure = rho * g * depth
                arrow_length = arrow_max_length * (pressure / max_pressure) if max_pressure > 0 else 0
                arrow_dx = -np.sin(theta_rad) * arrow_length
                arrow_dy = np.cos(theta_rad) * arrow_length
                fig.add_trace(go.Scatter(
                    x=[x_wall + arrow_dx],
                    y=[y_wall + arrow_dy],
                    mode='markers',
                    marker=dict(size=8, color='red'),
                    showlegend=False,
                    hoverinfo='text',
                    text=f"Pressure: {pressure/1000:.1f} kPa<br>Depth: {depth:.1f} m"
                ))
                fig.add_shape(
                    type="line",
                    x0=x_wall + arrow_dx, y0=y_wall + arrow_dy,
                    x1=x_wall - 0.02 * np.sin(theta_rad), y1=y_wall + 0.02 * np.cos(theta_rad),
                    line=dict(color="red", width=3)
                )
    
    # 5. Fluid surface line (only on fluid side)
    fig.add_shape(
        type="line",
        x0=-plot_width/3, y0=h,
        x1=x1, y1=h,
        line=dict(color="#0077B6", width=3, dash="dash")
    )
    fig.add_annotation(
        x=-plot_width/6, y=h,
        text="Fluid Surface",
        showarrow=False,
        font=dict(color="#0077B6", size=14),
        xanchor="center",
        yshift=15
    )
    
    # 6. Angle indicator
    arc_radius = min(1.0, L * 0.2)
    arc_angles = np.linspace(0, theta_rad, 30)
    arc_x = arc_radius * np.cos(arc_angles)
    arc_y = arc_radius * np.sin(arc_angles)
    fig.add_trace(go.Scatter(
        x=arc_x, y=arc_y,
        mode='lines',
        line=dict(color="gray", width=2, dash="dot"),
        showlegend=False,
        hoverinfo='none'
    ))
    fig.add_annotation(
        x=arc_radius * np.cos(theta_rad/2) * 1.3,
        y=arc_radius * np.sin(theta_rad/2) * 1.3,
        text=f"θ = {theta_deg}°",
        showarrow=False,
        font=dict(size=14, color="gray")
    )
    
    # 7. Depth markers (on fluid side)
    depth_markers = 5
    for i in range(1, depth_markers + 1):
        depth_mark = i * h / depth_markers
        fig.add_annotation(
            x=-plot_width/3 - 0.5, y=depth_mark,
            text=f"{depth_mark:.1f} m",
            showarrow=False,
            font=dict(size=10, color="gray"),
            xanchor="right"
        )
    
    # Update layout
    fig.update_xaxes(
        range=[-plot_width/2, plot_width/2],
        scaleanchor="y",
        scaleratio=1,
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)',
        zeroline=True,
        title="Horizontal Distance (m)"
    )
    fig.update_yaxes(
        range=[-0.5, plot_height],
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)',
        zeroline=True,
        title="Vertical Distance (m)"
    )
    fig.update_layout(
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=10, b=10),
        height=600,
        showlegend=False,
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Dynamic caption
    if show_pressure_arrows:
        st.caption(
            f"Red arrows show hydrostatic pressure acting perpendicular to the inclined wall. "
            f"Pressure increases linearly with depth, reaching {rho * g * h / 1000:.1f} kPa at the bottom. "
            f"Total normal force: {F_N_kN:.2f} kN."
        )
    else:
        st.caption(
            f"The inclined wall (θ = {theta_deg}°) experiences hydrostatic pressure from the water. "
            f"Maximum depth: {h:.2f} m. Total normal force: {F_N_kN:.2f} kN acting on the wall. "
            "Enable 'Show Pressure Distribution' to visualize the pressure variation."
        )

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(page_title="Hydrostatic Force on Wall", layout="wide")

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
st.markdown("<h1 style='text-align: center;'>Hydrostatic Force on a Straight Side Wall</h1>", unsafe_allow_html=True)
st.markdown(
    "<h4 style='text-align: center; font-weight: normal;'>Interactively explore the pressure distribution and total force on a submerged wall.</h4>",
    unsafe_allow_html=True
)
st.markdown("---")

# --- Main Layout ---
col1, col2 = st.columns([2, 3])

# --- Column 1: Inputs and Results ---
with col1:
    st.header("🧮 Parameters")
    
    st.subheader("Wall and Fluid Properties")
    c1, c2 = st.columns(2)
    with c1:
        D = st.slider("Height of fluid, D (m)", 0.1, 10.0, 5.0, step=0.05)
    with c2:
        w = st.slider("Width of wall, w (m)", 0.1, 10.0, 3.0, step=0.05)

    c1, c2 = st.columns(2)
    with c1:
        rho = st.number_input("Fluid density, ρ (kg/m³)", value=1000.0, step=10.0, format="%.1f")
    with c2:
        g = st.number_input("Gravity, g (m/s²)", value=9.81, format="%.2f")
    
    st.subheader("📊 Visualization Options")
    # Main toggle for pressure arrows
    show_pressure_arrows = st.checkbox("Show Pressure Distribution", value=False,
                                     help="Toggle to visualize how pressure acts on the wall")
    
    # Show additional options only when pressure arrows are enabled
    if show_pressure_arrows:
        c1, c2 = st.columns(2)
        with c1:
            n_arrows = st.slider("Number of pressure arrows", 5, 20, 10, step=1)
        with c2:
            arrow_style = st.radio("Arrow style", 
                                 ["Lines with heads", "Triangular arrows", "Force vectors"])
    
    # Always show gradient option
    show_gradient = st.checkbox("Show pressure gradient on wall", value=True,
                               help="Shows color gradient indicating pressure intensity")

    # --- Calculations ---
    F = 0.5 * rho * g * w * D**2  # Force in Newtons (N)
    F_kN = F / 1000
    
    # Calculate center of pressure
    y_cp = (2/3) * D  # Center of pressure from water surface
    
    # Calculate moment about base
    M = F * (D - y_cp)  # Moment in N⋅m
    M_kNm = M / 1000

    st.markdown("---")
    st.header("📈 Results")
    
    # Display metrics in a more organized way
    st.metric(label="Total Hydrostatic Force (F)", value=f"{F_kN:,.2f} kN",
              help="Total force acting on the wall")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric(label="Center of Pressure", value=f"{y_cp:.2f} m",
                  help="Distance from water surface")
    with col_m2:
        st.metric(label="Moment at Base", value=f"{M_kNm:.2f} kN⋅m",
                  help="Overturning moment")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<b>Key Formulas:</b>", unsafe_allow_html=True)
    st.latex(r"F = \frac{1}{2}\,\rho\,g\,w\,D^2")
    st.latex(r"\bar{y} = \frac{2}{3}\,D")

# --- Column 2: Visualization ---
with col2:
    st.header("📊 Hydrostatic Pressure & Force Diagram")
    
    # Add instructional message when arrows are hidden
    if not show_pressure_arrows:
        st.info("👆 Enable 'Show Pressure Distribution' to visualize how pressure acts on the wall")

    fig = go.Figure()
    
    # --- Visualization Constants ---
    wall_x = 0
    fluid_x_end = 10
    vessel_depth = 10.0

    y_surface = vessel_depth - D
    y_bottom = vessel_depth

    # 1. Draw the Wall/Vessel Outline
    fig.add_shape(
        type="rect", x0=wall_x-0.5, y0=0, x1=wall_x, y1=vessel_depth,
        fillcolor="rgba(128, 128, 128, 0.3)",
        line=dict(color="black", width=2),
        layer="below"
    )
    
    # Add wall label
    fig.add_annotation(
        x=wall_x-0.25, y=vessel_depth/2, 
        text="<b>WALL</b>", 
        textangle=-90,
        showarrow=False, 
        font=dict(size=12, color="black"),
        xanchor="center"
    )
    
    # 2. Draw the Fluid
    fig.add_shape(
        type="rect", x0=wall_x, y0=y_surface, x1=fluid_x_end, y1=y_bottom,
        fillcolor="rgba(0, 119, 182, 0.3)",
        line_width=0,
        layer="below"
    )
    
    # 3. Draw pressure gradient if enabled
    if show_gradient:
        gradient_steps = 50
        for i in range(gradient_steps):
            y_top = y_surface + (i * D / gradient_steps)
            y_bot = y_surface + ((i + 1) * D / gradient_steps)
            opacity = 0.02 + 0.1 * (i / gradient_steps)
            
            # Gradient on wall surface
            fig.add_shape(
                type="rect", 
                x0=wall_x - 0.1, y0=y_top, 
                x1=wall_x, y1=y_bot,
                fillcolor=f"rgba(255, 0, 0, {opacity})",
                line_width=0,
                layer="above"
            )

    # Calculate max pressure for labels
    max_pressure = rho * g * D
    arrow_max_length = 4
    
    # 4. Draw Pressure Arrows if enabled
    if show_pressure_arrows:
        
        if arrow_style == "Lines with heads":
            # Draw arrows as lines with triangular heads at the wall
            for i in range(n_arrows):
                frac = (i + 0.5) / n_arrows
                y_arrow = y_surface + frac * D
                depth_from_surface = frac * D
                pressure = rho * g * depth_from_surface
                arrow_length = arrow_max_length * (pressure / max_pressure)
                
                # Draw arrow shaft
                fig.add_shape(
                    type="line",
                    x0=wall_x + arrow_length, y0=y_arrow,
                    x1=wall_x + 0.05, y1=y_arrow,
                    line=dict(color="red", width=4)
                )
                
                # Draw arrow head
                head_size = 0.2
                fig.add_trace(go.Scatter(
                    x=[wall_x + head_size + 0.05, wall_x + 0.02, wall_x + head_size + 0.05],
                    y=[y_arrow - head_size/2, y_arrow, y_arrow + head_size/2],
                    fill="toself",
                    fillcolor="red",
                    line=dict(color="red", width=0),
                    mode='lines',
                    showlegend=False,
                    hoverinfo='text',
                    text=f"Pressure: {pressure/1000:.1f} kPa<br>Depth: {depth_from_surface:.1f} m"
                ))
        
        elif arrow_style == "Triangular arrows":
            # Draw arrows as solid triangles
            for i in range(n_arrows):
                frac = (i + 0.5) / n_arrows
                y_arrow = y_surface + frac * D
                depth_from_surface = frac * D
                pressure = rho * g * depth_from_surface
                arrow_length = arrow_max_length * (pressure / max_pressure)
                
                triangle_height = 0.15
                fig.add_trace(go.Scatter(
                    x=[wall_x + arrow_length, wall_x + 0.02, wall_x + arrow_length],
                    y=[y_arrow - triangle_height, y_arrow, y_arrow + triangle_height],
                    fill="toself",
                    fillcolor="red",
                    line=dict(color="darkred", width=1),
                    mode='lines',
                    showlegend=False,
                    hoverinfo='text',
                    text=f"Pressure: {pressure/1000:.1f} kPa<br>Depth: {depth_from_surface:.1f} m"
                ))
        
        else:  # Force vectors
            # Draw as force vectors with dots
            for i in range(n_arrows):
                frac = (i + 0.5) / n_arrows
                y_arrow = y_surface + frac * D
                depth_from_surface = frac * D
                pressure = rho * g * depth_from_surface
                arrow_length = arrow_max_length * (pressure / max_pressure)
                
                # Draw base point
                fig.add_trace(go.Scatter(
                    x=[wall_x + arrow_length], 
                    y=[y_arrow],
                    mode='markers',
                    marker=dict(size=8, color='red'),
                    showlegend=False,
                    hoverinfo='text',
                    text=f"Pressure: {pressure/1000:.1f} kPa<br>Depth: {depth_from_surface:.1f} m"
                ))
                
                # Draw arrow shaft
                fig.add_shape(
                    type="line",
                    x0=wall_x + arrow_length, y0=y_arrow,
                    x1=wall_x + 0.05, y1=y_arrow,
                    line=dict(color="red", width=3)
                )
                # Add arrowhead
                fig.add_shape(
                    type="path",
                    path=f"M {wall_x + 0.25} {y_arrow - 0.1} L {wall_x + 0.02} {y_arrow} L {wall_x + 0.25} {y_arrow + 0.1} Z",
                    fillcolor="red",
                    line=dict(color="red", width=0)
                )

    # 5. Water surface line
    fig.add_shape(
        type="line", 
        x0=wall_x, y0=y_surface, 
        x1=fluid_x_end, y1=y_surface, 
        line=dict(color="#0077B6", width=3, dash="dash")
    )
    fig.add_annotation(
        x=fluid_x_end-0.5, y=y_surface, 
        text="Water Surface", 
        showarrow=False, 
        font=dict(color="#0077B6", size=14), 
        xanchor="right", 
        yshift=-15
    )
    
    # 6. Add depth markers
    depth_markers = 5
    for i in range(depth_markers + 1):
        depth_frac = i / depth_markers
        y_mark = y_surface + depth_frac * D
        actual_depth = depth_frac * D
        
        fig.add_annotation(
            x=fluid_x_end + 0.5, y=y_mark,
            text=f"{actual_depth:.1f} m",
            showarrow=False,
            font=dict(size=10, color="gray"),
            xanchor="left"
        )
    
    # 7. Add labels based on arrow visibility
    if show_pressure_arrows:
        fig.add_annotation(
            x=wall_x + arrow_max_length/2, y=y_surface - 0.8,
            text="<b>Hydrostatic Pressure Distribution</b>",
            showarrow=False,
            font=dict(size=14),
            xanchor="center"
        )
        
        # Add pressure scale
        fig.add_annotation(
            x=wall_x + arrow_max_length + 0.5, y=(y_surface + y_bottom)/2,
            text=f"← Max: {max_pressure/1000:.1f} kPa",
            showarrow=False,
            font=dict(size=12, color="red"),
            xanchor="left"
        )
    
    # Always show center of pressure marker
    y_cp_plot = y_surface + y_cp
    fig.add_shape(
        type="line",
        x0=wall_x - 0.3, y0=y_cp_plot,
        x1=wall_x + 0.3, y1=y_cp_plot,
        line=dict(color="green", width=3, dash="dot")
    )
    fig.add_annotation(
        x=wall_x - 0.35, y=y_cp_plot,
        text="C.P.",
        showarrow=False,
        font=dict(size=12, color="green"),
        xanchor="right"
    )
    
    # Show maximum pressure location
    fig.add_shape(
        type="rect",
        x0=wall_x - 0.5, y0=y_bottom - 0.02,
        x1=wall_x + 2, y1=y_bottom + 0.02,
        fillcolor="yellow",
        opacity=0.3,
        line=dict(color="orange", width=1)
    )
    fig.add_annotation(
        x=wall_x + 0.75, y=y_bottom,
        text=f"p_max = {max_pressure/1000:.1f} kPa",
        showarrow=False,
        font=dict(size=10, color="darkorange"),
        xanchor="center"
    )

    # --- Layout and Axes Configuration ---
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-2, fluid_x_end + 2]),
        yaxis=dict(
            title="Vertical Position (m)",
            range=[vessel_depth + 1, -0.5],
            showgrid=True, 
            gridcolor='rgba(0,0,0,0.1)',
            zeroline=False,
            dtick=1
        ),
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=20, b=10),
        height=600,
        showlegend=False,
        hovermode='closest'
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Dynamic caption based on visualization state
    if show_pressure_arrows:
        st.caption(
            "The red arrows represent hydrostatic pressure acting perpendicular to the wall. "
            "Arrow length increases linearly with depth. The green dashed line shows the center of pressure "
            f"located at {y_cp:.2f} m from the surface (2/3 of the fluid depth)."
        )
    else:
        st.caption(
            "The fluid exerts hydrostatic pressure on the submerged wall. "
            f"Total force: {F_kN:.2f} kN acting at the center of pressure (green line). "
            "Enable 'Show Pressure Distribution' to visualize the pressure variation."
        )
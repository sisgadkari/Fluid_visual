import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    "<h4 style='text-align: center; font-weight: normal;'>Interactively explore the pressure distribution and total force on a submerged wall with 3D visualization.</h4>",
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
    
    # View mode selection
    view_mode = st.radio("View Mode", 
                        ["2D Side View", "3D Isometric View", "Split View (2D + 3D)"],
                        help="Choose how to visualize the wall and pressure distribution")
    
    # Main toggle for pressure arrows
    show_pressure_arrows = st.checkbox("Show Pressure Distribution", value=True,
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
    
    # 3D specific options
    if "3D" in view_mode:
        show_3d_grid = st.checkbox("Show 3D grid lines", value=True,
                                  help="Display grid to enhance 3D depth perception")
        show_width_dimension = st.checkbox("Show width dimension", value=True,
                                          help="Display width measurement arrows")

    # --- Calculations ---
    F = 0.5 * rho * g * w * D**2  # Force in Newtons (N)
    F_kN = F / 1000
    
    # Calculate center of pressure
    y_cp = (2/3) * D  # Center of pressure from water surface
    
    # Calculate moment about base
    M = F * (D - y_cp)  # Moment in N⋅m
    M_kNm = M / 1000
    
    # Pressure at bottom
    P_bottom = rho * g * D  # Pressure at bottom (Pa)
    P_bottom_kPa = P_bottom / 1000

    st.markdown("---")
    st.header("📈 Results")
    
    # Display metrics in a more organized way
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.metric(label="Total Hydrostatic Force (F)", value=f"{F_kN:,.2f} kN",
                  help="Total force acting on the wall")
        st.metric(label="Pressure at Bottom", value=f"{P_bottom_kPa:.2f} kPa",
                  help="Maximum pressure at the bottom of the wall")
    with col_r2:
        st.metric(label="Center of Pressure", value=f"{y_cp:.2f} m",
                  help=f"Distance from water surface = (2/3) × {D:.2f} m")
        st.metric(label="Moment about Base", value=f"{M_kNm:.2f} kN⋅m",
                  help="Moment of force about the base of the wall")
    
    st.markdown("---")
    st.header("🧮 Step-by-Step Calculation")
    
    with st.expander("📖 See Detailed Breakdown", expanded=False):
        st.markdown("### Hydrostatic Force Calculation")
        
        st.markdown("#### Step 1: Understand Pressure Distribution")
        st.write("Pressure in a static fluid increases linearly with depth:")
        st.latex(r'P(y) = \rho g y')
        st.write(f"Where y is the depth below the water surface.")
        st.write(f"At the bottom (y = {D} m): P = {rho} × {g} × {D} = **{P_bottom:.0f} Pa** = **{P_bottom_kPa:.2f} kPa**")
        
        st.markdown("#### Step 2: Calculate Hydrostatic Force")
        st.write("For a rectangular wall, the force is the average pressure times the area:")
        st.latex(r'F = P_{avg} \times A = \frac{1}{2}P_{bottom} \times (D \times w)')
        st.latex(r'F = \frac{1}{2}\rho g D \times (D \times w) = \frac{1}{2}\rho g w D^2')
        st.write(f"F = 0.5 × {rho} × {g} × {w} × {D}²")
        st.write(f"F = 0.5 × {rho} × {g} × {w} × {D**2:.2f}")
        st.write(f"F = **{F:.0f} N** = **{F_kN:.2f} kN**")
        
        st.markdown("#### Step 3: Locate Center of Pressure")
        st.write("The center of pressure is where the resultant force acts.")
        st.write("For a rectangular wall with fluid on one side:")
        st.latex(r'y_{cp} = \frac{2}{3}D')
        st.write(f"y_cp = (2/3) × {D} = **{y_cp:.2f} m** from the water surface")
        st.write(f"Or **{D - y_cp:.2f} m** from the bottom of the wall")
        
        st.markdown("#### Step 4: Calculate Moment about Base")
        st.write("The moment about the base of the wall:")
        st.latex(r'M = F \times (D - y_{cp})')
        st.write(f"M = {F_kN:.2f} kN × {D - y_cp:.2f} m")
        st.write(f"M = **{M_kNm:.2f} kN⋅m**")
        
        st.markdown("#### Physical Interpretation")
        if F_kN < 10:
            st.info(f"💡 Relatively small force: {F_kN:.2f} kN. Suitable for small tanks or shallow water.")
        elif F_kN < 100:
            st.success(f"✅ Moderate force: {F_kN:.2f} kN. Typical for swimming pools or small retention walls.")
        elif F_kN < 1000:
            st.warning(f"⚠️ Large force: {F_kN:.2f} kN. Significant structural design required (dams, large tanks).")
        else:
            st.error(f"❗ Very large force: {F_kN:.2f} kN. Major civil engineering structure (large dam or retaining wall).")
    
    st.markdown("---")
    st.header("🔍 Analysis Insights")
    
    with st.expander("💡 Parameter Effects", expanded=False):
        st.markdown("**How parameters affect the hydrostatic force:**")
        
        st.markdown("#### 1. Fluid Depth (D)")
        st.write(f"• Current value: {D} m")
        st.write(f"• Effect: F ∝ D² (quadratic relationship)")
        
        # Show effect of depth changes
        depths = [D * 0.5, D, D * 1.5, D * 2]
        forces = [0.5 * rho * g * w * d**2 / 1000 for d in depths]
        
        st.write("**Force at different depths:**")
        for d, f in zip(depths, forces):
            ratio = (d / D)
            st.write(f"• D = {d:.2f} m → F = {f:.2f} kN (×{ratio:.2f} depth = ×{ratio**2:.2f} force)")
        
        st.warning("⚠️ **Critical insight**: Doubling the depth quadruples the force! This is why dam design is so challenging.")
        
        st.markdown("#### 2. Wall Width (w)")
        st.write(f"• Current value: {w} m")
        st.write(f"• Effect: F ∝ w (linear relationship)")
        
        widths = [w * 0.5, w, w * 2]
        forces_w = [0.5 * rho * g * width * D**2 / 1000 for width in widths]
        
        st.write("**Force at different widths:**")
        for width, f in zip(widths, forces_w):
            ratio = width / w
            st.write(f"• w = {width:.2f} m → F = {f:.2f} kN (×{ratio:.2f} width = ×{ratio:.2f} force)")
        
        st.markdown("#### 3. Fluid Density (ρ)")
        st.write(f"• Current value: {rho} kg/m³")
        st.write(f"• Effect: F ∝ ρ (linear relationship)")
        
        st.write("**Common fluids:**")
        fluids = {
            "Fresh water": 1000,
            "Seawater": 1025,
            "Gasoline": 750,
            "Mercury": 13600,
            "Current fluid": rho
        }
        for fluid_name, density in fluids.items():
            force_fluid = 0.5 * density * g * w * D**2 / 1000
            st.write(f"• {fluid_name} (ρ = {density} kg/m³): F = {force_fluid:.2f} kN")
        
        st.markdown("#### 4. Pressure Distribution Shape")
        st.write("• Triangular distribution: P = 0 at surface, maximum at bottom")
        st.write("• Average pressure = P_max / 2")
        st.write("• Resultant force acts at 2/3 depth from surface")
        st.write("• This is **independent** of fluid depth or density!")
        
    with st.expander("⚙️ Design Considerations", expanded=False):
        st.markdown("**Engineering Applications:**")
        
        st.markdown("#### Dam and Retaining Wall Design")
        st.write("**Key considerations:**")
        st.write("• Foundation must resist both force and overturning moment")
        st.write("• Factor of safety typically 1.5-3.0 for static loads")
        st.write("• Must account for: wave action, seismic loads, ice pressure")
        
        # Calculate required foundation resistance
        safety_factor = 2.0
        required_resistance = F_kN * safety_factor
        st.write(f"\n**For current wall:**")
        st.write(f"• Design force (SF=2.0): {required_resistance:.2f} kN")
        st.write(f"• Overturning moment: {M_kNm:.2f} kN⋅m")
        
        st.markdown("#### Tank and Vessel Design")
        st.write("**Material selection based on force:**")
        if F_kN < 50:
            st.info("💡 Light duty: Plastic, fiberglass, or thin steel adequate")
        elif F_kN < 500:
            st.success("✅ Medium duty: Reinforced concrete or structural steel")
        else:
            st.warning("⚠️ Heavy duty: Thick reinforced concrete with steel reinforcement")
        
        st.markdown("#### Pressure at Different Heights")
        st.write("**Pressure distribution table:**")
        
        pressure_table = []
        for i in range(6):
            depth_frac = i / 5
            depth = depth_frac * D
            pressure = rho * g * depth
            pressure_table.append({
                "Depth from surface (m)": f"{depth:.2f}",
                "Pressure (kPa)": f"{pressure/1000:.2f}",
                "% of max": f"{depth_frac*100:.0f}%"
            })
        
        import pandas as pd
        st.table(pd.DataFrame(pressure_table))

# --- Column 2: Visualization ---
with col2:
    st.header("📊 Hydrostatic Pressure & Force Visualization")
    
    # Add instructional message when arrows are hidden
    if not show_pressure_arrows:
        st.info("👆 Enable 'Show Pressure Distribution' to visualize how pressure acts on the wall")
    
    # --- Visualization Constants ---
    wall_x = 0
    fluid_x_end = 10
    vessel_depth = 10.0
    
    y_surface = vessel_depth - D
    y_bottom = vessel_depth
    
    # Calculate max pressure for labels
    max_pressure = rho * g * D
    arrow_max_length = 4
    
    # Create visualization based on selected view mode
    if view_mode == "Split View (2D + 3D)":
        # Create side-by-side subplots
        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.5, 0.5],
            subplot_titles=("2D Side View", "3D Isometric View"),
            specs=[[{"type": "xy"}, {"type": "scene"}]]
        )
        
        # --- 2D VIEW (Left subplot) ---
        # 1. Draw the Wall
        fig.add_shape(
            type="rect", x0=wall_x-0.5, y0=0, x1=wall_x, y1=vessel_depth,
            fillcolor="rgba(128, 128, 128, 0.3)",
            line=dict(color="black", width=2),
            layer="below",
            row=1, col=1
        )
        
        fig.add_annotation(
            x=wall_x-0.25, y=vessel_depth/2, 
            text="<b>WALL</b>", 
            textangle=-90,
            showarrow=False, 
            font=dict(size=12, color="black"),
            xanchor="center",
            row=1, col=1
        )
        
        # 2. Draw the Fluid
        fig.add_shape(
            type="rect", x0=wall_x, y0=y_surface, x1=fluid_x_end, y1=y_bottom,
            fillcolor="rgba(0, 119, 182, 0.3)",
            line_width=0,
            layer="below",
            row=1, col=1
        )
        
        # 3. Draw pressure gradient if enabled
        if show_gradient:
            gradient_steps = 50
            for i in range(gradient_steps):
                y_top = y_surface + (i * D / gradient_steps)
                y_bot = y_surface + ((i + 1) * D / gradient_steps)
                opacity = 0.02 + 0.1 * (i / gradient_steps)
                
                fig.add_shape(
                    type="rect", 
                    x0=wall_x - 0.1, y0=y_top, 
                    x1=wall_x, y1=y_bot,
                    fillcolor=f"rgba(255, 0, 0, {opacity})",
                    line_width=0,
                    layer="above",
                    row=1, col=1
                )
        
        # 4. Draw Pressure Arrows if enabled (2D)
        if show_pressure_arrows:
            for i in range(n_arrows):
                frac = (i + 0.5) / n_arrows
                y_arrow = y_surface + frac * D
                depth_from_surface = frac * D
                pressure = rho * g * depth_from_surface
                arrow_length = arrow_max_length * (pressure / max_pressure)
                
                if arrow_style == "Lines with heads":
                    # Arrow shaft
                    fig.add_shape(
                        type="line",
                        x0=wall_x + arrow_length, y0=y_arrow,
                        x1=wall_x + 0.05, y1=y_arrow,
                        line=dict(color="red", width=4),
                        row=1, col=1
                    )
                    
                    # Arrow head
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
                    ), row=1, col=1)
        
        # 5. Water surface line
        fig.add_shape(
            type="line", 
            x0=wall_x, y0=y_surface, 
            x1=fluid_x_end, y1=y_surface, 
            line=dict(color="#0077B6", width=3, dash="dash"),
            row=1, col=1
        )
        
        # 6. Center of pressure marker
        y_cp_plot = y_surface + y_cp
        fig.add_shape(
            type="line",
            x0=wall_x - 0.3, y0=y_cp_plot,
            x1=wall_x + 0.3, y1=y_cp_plot,
            line=dict(color="green", width=3, dash="dot"),
            row=1, col=1
        )
        fig.add_annotation(
            x=wall_x - 0.35, y=y_cp_plot,
            text="C.P.",
            showarrow=False,
            font=dict(size=12, color="green"),
            xanchor="right",
            row=1, col=1
        )
        
        # --- 3D VIEW (Right subplot) ---
        # Create 3D wall with depth
        wall_depth = w  # Use actual width for Z dimension
        
        # Define wall corners (using isometric-like positioning)
        # Wall front face (at z=0)
        wall_x_3d = [0, 0, 0, 0, 0]
        wall_y_3d = [0, D, D, 0, 0]
        wall_z_3d = [0, 0, wall_depth, wall_depth, 0]
        
        # Draw wall as multiple surfaces for 3D effect
        # Front face
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0, 0],
            y=[0, D, D, 0],
            z=[0, 0, 0, 0],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='gray',
            opacity=0.5,
            showlegend=False,
            hoverinfo='skip'
        ), row=1, col=2)
        
        # Back face
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0, 0],
            y=[0, D, D, 0],
            z=[wall_depth, wall_depth, wall_depth, wall_depth],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='darkgray',
            opacity=0.5,
            showlegend=False,
            hoverinfo='skip'
        ), row=1, col=2)
        
        # Bottom face
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0, 0],
            y=[0, 0, 0, 0],
            z=[0, wall_depth, wall_depth, 0],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='dimgray',
            opacity=0.7,
            showlegend=False,
            hoverinfo='skip'
        ), row=1, col=2)
        
        # Top face
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0, 0],
            y=[D, D, D, D],
            z=[0, wall_depth, wall_depth, 0],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='lightgray',
            opacity=0.5,
            showlegend=False,
            hoverinfo='skip'
        ), row=1, col=2)
        
        # Water volume
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0, 0, 5, 5, 5, 5],
            y=[0, D, D, 0, 0, D, D, 0],
            z=[0, 0, wall_depth, wall_depth, 0, 0, wall_depth, wall_depth],
            i=[0, 2, 4, 6, 0, 1, 2, 3],
            j=[1, 3, 5, 7, 4, 5, 6, 7],
            k=[2, 6, 6, 5, 5, 6, 7, 7],
            color='rgba(0, 119, 182, 0.3)',
            opacity=0.3,
            showlegend=False,
            hoverinfo='skip'
        ), row=1, col=2)
        
        # Draw pressure arrows in 3D
        if show_pressure_arrows:
            n_arrows_3d = max(5, n_arrows // 2)  # Fewer arrows in 3D
            n_width_arrows = 5  # Arrows across width
            
            for i in range(n_arrows_3d):
                for j in range(n_width_arrows):
                    frac_height = (i + 0.5) / n_arrows_3d
                    frac_width = (j + 0.5) / n_width_arrows
                    
                    y_pos = frac_height * D
                    z_pos = frac_width * wall_depth
                    depth_from_surface = frac_height * D
                    pressure = rho * g * depth_from_surface
                    arrow_length_3d = 2 * (pressure / max_pressure)
                    
                    # Draw arrow
                    fig.add_trace(go.Scatter3d(
                        x=[arrow_length_3d, 0],
                        y=[y_pos, y_pos],
                        z=[z_pos, z_pos],
                        mode='lines',
                        line=dict(color='red', width=4),
                        showlegend=False,
                        hoverinfo='text',
                        text=f"Pressure: {pressure/1000:.1f} kPa"
                    ), row=1, col=2)
                    
                    # Arrow head (cone)
                    fig.add_trace(go.Cone(
                        x=[0.1],
                        y=[y_pos],
                        z=[z_pos],
                        u=[-1],
                        v=[0],
                        w=[0],
                        sizemode="absolute",
                        sizeref=0.3,
                        colorscale=[[0, 'red'], [1, 'red']],
                        showscale=False,
                        showlegend=False,
                        hoverinfo='skip'
                    ), row=1, col=2)
        
        # Show width dimension if enabled
        if show_width_dimension:
            # Width dimension arrows
            fig.add_trace(go.Scatter3d(
                x=[-0.5, -0.5],
                y=[-0.5, -0.5],
                z=[0, wall_depth],
                mode='lines+text',
                line=dict(color='black', width=3),
                text=['', f'w = {w} m'],
                textposition='middle right',
                showlegend=False,
                hoverinfo='skip'
            ), row=1, col=2)
        
        # Show 3D grid if enabled
        if show_3d_grid:
            # Grid lines on wall
            for i in range(6):
                frac = i / 5
                # Horizontal lines
                fig.add_trace(go.Scatter3d(
                    x=[0, 0],
                    y=[frac * D, frac * D],
                    z=[0, wall_depth],
                    mode='lines',
                    line=dict(color='rgba(0,0,0,0.2)', width=1),
                    showlegend=False,
                    hoverinfo='skip'
                ), row=1, col=2)
                
                # Vertical lines
                fig.add_trace(go.Scatter3d(
                    x=[0, 0],
                    y=[0, D],
                    z=[frac * wall_depth, frac * wall_depth],
                    mode='lines',
                    line=dict(color='rgba(0,0,0,0.2)', width=1),
                    showlegend=False,
                    hoverinfo='skip'
                ), row=1, col=2)
        
        # Update 2D layout
        fig.update_xaxes(showgrid=False, zeroline=False, visible=False, range=[-2, fluid_x_end + 2], row=1, col=1)
        fig.update_yaxes(
            title="Height (m)",
            range=[vessel_depth + 1, -0.5],
            showgrid=True, 
            gridcolor='rgba(0,0,0,0.1)',
            zeroline=False,
            dtick=1,
            row=1, col=1
        )
        
        # Update 3D layout
        fig.update_scenes(
            xaxis=dict(title="", showgrid=False, showticklabels=False, range=[-1, 6]),
            yaxis=dict(title="Height (m)", showgrid=True, range=[0, D*1.2]),
            zaxis=dict(title="Width (m)", showgrid=True, range=[0, wall_depth*1.2]),
            camera=dict(
                eye=dict(x=1.5, y=-1.5, z=1.2),
                center=dict(x=0, y=0, z=0)
            ),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1.5, z=0.8),
            row=1, col=2
        )
        
        fig.update_layout(
            plot_bgcolor="white",
            margin=dict(l=10, r=10, t=40, b=10),
            height=700,
            showlegend=False,
            hovermode='closest'
        )
        
    elif view_mode == "3D Isometric View":
        # Pure 3D view
        fig = go.Figure()
        
        wall_depth = w
        
        # Wall surfaces
        # Front face
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0, 0],
            y=[0, D, D, 0],
            z=[0, 0, 0, 0],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='gray',
            opacity=0.5,
            showlegend=False,
            name='Wall Front',
            hoverinfo='name'
        ))
        
        # Back face
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0, 0],
            y=[0, D, D, 0],
            z=[wall_depth, wall_depth, wall_depth, wall_depth],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='darkgray',
            opacity=0.5,
            showlegend=False,
            name='Wall Back',
            hoverinfo='name'
        ))
        
        # Bottom, top, and side faces
        # Bottom
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0, 0],
            y=[0, 0, 0, 0],
            z=[0, wall_depth, wall_depth, 0],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='dimgray',
            opacity=0.7,
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Top
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0, 0],
            y=[D, D, D, D],
            z=[0, wall_depth, wall_depth, 0],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='lightgray',
            opacity=0.5,
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Water volume (transparent)
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0, 0, 5, 5, 5, 5],
            y=[0, D, D, 0, 0, D, D, 0],
            z=[0, 0, wall_depth, wall_depth, 0, 0, wall_depth, wall_depth],
            i=[0, 2, 4, 6, 0, 1, 2, 3],
            j=[1, 3, 5, 7, 4, 5, 6, 7],
            k=[2, 6, 6, 5, 5, 6, 7, 7],
            color='lightblue',
            opacity=0.3,
            showlegend=False,
            name='Water',
            hoverinfo='name'
        ))
        
        # Pressure arrows in 3D
        if show_pressure_arrows:
            n_arrows_3d = max(8, n_arrows // 2)
            n_width_arrows = 7
            
            for i in range(n_arrows_3d):
                for j in range(n_width_arrows):
                    frac_height = (i + 0.5) / n_arrows_3d
                    frac_width = (j + 0.5) / n_width_arrows
                    
                    y_pos = frac_height * D
                    z_pos = frac_width * wall_depth
                    depth_from_surface = frac_height * D
                    pressure = rho * g * depth_from_surface
                    arrow_length_3d = 2.5 * (pressure / max_pressure)
                    
                    # Arrow line
                    fig.add_trace(go.Scatter3d(
                        x=[arrow_length_3d, 0.05],
                        y=[y_pos, y_pos],
                        z=[z_pos, z_pos],
                        mode='lines',
                        line=dict(color='red', width=5),
                        showlegend=False,
                        hoverinfo='text',
                        text=f"Depth: {depth_from_surface:.1f} m<br>Pressure: {pressure/1000:.1f} kPa"
                    ))
                    
                    # Arrow head
                    fig.add_trace(go.Cone(
                        x=[0.15],
                        y=[y_pos],
                        z=[z_pos],
                        u=[-1],
                        v=[0],
                        w=[0],
                        sizemode="absolute",
                        sizeref=0.4,
                        colorscale=[[0, 'red'], [1, 'red']],
                        showscale=False,
                        showlegend=False,
                        hoverinfo='skip'
                    ))
        
        # Center of pressure marker (3D line across width)
        y_cp_3d = (2/3) * D
        fig.add_trace(go.Scatter3d(
            x=[0, 0],
            y=[y_cp_3d, y_cp_3d],
            z=[0, wall_depth],
            mode='lines',
            line=dict(color='green', width=8, dash='dot'),
            name='Center of Pressure',
            hoverinfo='name'
        ))
        
        # Dimension arrows
        if show_width_dimension:
            # Width dimension
            fig.add_trace(go.Scatter3d(
                x=[-0.8, -0.8],
                y=[-0.5, -0.5],
                z=[0, wall_depth],
                mode='lines+text',
                line=dict(color='black', width=4),
                text=['', f'Width = {w} m'],
                textposition='middle right',
                textfont=dict(size=14, color='black'),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Height dimension
            fig.add_trace(go.Scatter3d(
                x=[-0.8, -0.8],
                y=[0, D],
                z=[-0.5, -0.5],
                mode='lines+text',
                line=dict(color='black', width=4),
                text=['', f'Depth = {D} m'],
                textposition='top center',
                textfont=dict(size=14, color='black'),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Grid lines
        if show_3d_grid:
            for i in range(11):
                frac = i / 10
                # Horizontal lines
                fig.add_trace(go.Scatter3d(
                    x=[0, 0],
                    y=[frac * D, frac * D],
                    z=[0, wall_depth],
                    mode='lines',
                    line=dict(color='rgba(0,0,0,0.15)', width=1),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # Vertical lines
                fig.add_trace(go.Scatter3d(
                    x=[0, 0],
                    y=[0, D],
                    z=[frac * wall_depth, frac * wall_depth],
                    mode='lines',
                    line=dict(color='rgba(0,0,0,0.15)', width=1),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # Annotations
        fig.add_trace(go.Scatter3d(
            x=[0],
            y=[D + 0.5],
            z=[wall_depth / 2],
            mode='text',
            text=[f'Total Force: {F_kN:.2f} kN'],
            textfont=dict(size=16, color='darkred'),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            scene=dict(
                xaxis=dict(title="", showgrid=False, showticklabels=False, range=[-1.5, 6]),
                yaxis=dict(title="Height (m)", showgrid=True, range=[-0.5, D*1.3]),
                zaxis=dict(title="Width (m)", showgrid=True, range=[-0.5, wall_depth*1.3]),
                camera=dict(
                    eye=dict(x=1.8, y=-1.8, z=1.3),
                    center=dict(x=0, y=0, z=0)
                ),
                aspectmode='manual',
                aspectratio=dict(x=1.2, y=1.5, z=1)
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            height=800,
            showlegend=False,
            hovermode='closest'
        )
        
    else:  # 2D Side View
        fig = go.Figure()
        
        # Standard 2D view (same as original)
        # 1. Draw the Wall
        fig.add_shape(
            type="rect", x0=wall_x-0.5, y0=0, x1=wall_x, y1=vessel_depth,
            fillcolor="rgba(128, 128, 128, 0.3)",
            line=dict(color="black", width=2),
            layer="below"
        )
        
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
        
        # 3. Draw pressure gradient
        if show_gradient:
            gradient_steps = 50
            for i in range(gradient_steps):
                y_top = y_surface + (i * D / gradient_steps)
                y_bot = y_surface + ((i + 1) * D / gradient_steps)
                opacity = 0.02 + 0.1 * (i / gradient_steps)
                
                fig.add_shape(
                    type="rect", 
                    x0=wall_x - 0.1, y0=y_top, 
                    x1=wall_x, y1=y_bot,
                    fillcolor=f"rgba(255, 0, 0, {opacity})",
                    line_width=0,
                    layer="above"
                )
        
        # 4. Draw Pressure Arrows
        if show_pressure_arrows:
            
            if arrow_style == "Lines with heads":
                for i in range(n_arrows):
                    frac = (i + 0.5) / n_arrows
                    y_arrow = y_surface + frac * D
                    depth_from_surface = frac * D
                    pressure = rho * g * depth_from_surface
                    arrow_length = arrow_max_length * (pressure / max_pressure)
                    
                    fig.add_shape(
                        type="line",
                        x0=wall_x + arrow_length, y0=y_arrow,
                        x1=wall_x + 0.05, y1=y_arrow,
                        line=dict(color="red", width=4)
                    )
                    
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
                for i in range(n_arrows):
                    frac = (i + 0.5) / n_arrows
                    y_arrow = y_surface + frac * D
                    depth_from_surface = frac * D
                    pressure = rho * g * depth_from_surface
                    arrow_length = arrow_max_length * (pressure / max_pressure)
                    
                    fig.add_trace(go.Scatter(
                        x=[wall_x + arrow_length], 
                        y=[y_arrow],
                        mode='markers',
                        marker=dict(size=8, color='red'),
                        showlegend=False,
                        hoverinfo='text',
                        text=f"Pressure: {pressure/1000:.1f} kPa<br>Depth: {depth_from_surface:.1f} m"
                    ))
                    
                    fig.add_shape(
                        type="line",
                        x0=wall_x + arrow_length, y0=y_arrow,
                        x1=wall_x + 0.05, y1=y_arrow,
                        line=dict(color="red", width=3)
                    )
                    
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
        
        # 7. Center of pressure marker
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
        
        # 8. Maximum pressure indicator
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
            height=700,
            showlegend=False,
            hovermode='closest'
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Dynamic caption
    if view_mode == "3D Isometric View":
        st.caption(
            f"3D visualization showing the wall with width of {w} m. "
            f"Red arrows represent pressure distribution acting perpendicular to the wall surface. "
            f"Green line shows center of pressure at {y_cp:.2f} m from water surface."
        )
    elif view_mode == "Split View (2D + 3D)":
        st.caption(
            "Left: 2D side view showing pressure distribution. "
            "Right: 3D isometric view showing the wall's width and depth. "
            f"Total force: {F_kN:.2f} kN acting at center of pressure (green line)."
        )
    else:
        st.caption(
            f"The fluid exerts hydrostatic pressure on the submerged wall. "
            f"Total force: {F_kN:.2f} kN acting at the center of pressure (green line) "
            f"located at {y_cp:.2f} m from the surface."
        )

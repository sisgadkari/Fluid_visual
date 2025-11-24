import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Page Configuration ---
st.set_page_config(page_title="Laminar and Turbulent Flow", layout="wide")

# --- Title and Introduction ---
st.markdown("<h1 style='text-align: center;'>🌊 Laminar and Turbulent Flow in Pipes</h1>", unsafe_allow_html=True)
st.markdown(
    """
<p style='text-align: center; font-size: 18px;'>
Explore the fundamental difference between smooth laminar flow and chaotic turbulent flow.
Visualise velocity profiles, particle paths, and understand the critical Reynolds number.
</p>
""",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- Tabs ---
tab1, tab2 = st.tabs(["🎯 Interactive Simulation", "📚 Understanding Flow Regimes"])


# ========== SHARED HELPERS ==========

@st.cache_data
def generate_particle_paths(n_particles, pipe_length, turbulence_intensity, turbulent_start_position):
    """
    Generate simple 2D particle paths with random perturbations to mimic turbulence.
    'pipe_length' and 'pipe_radius' are used only for visualisation (non-dimensional).
    """
    pipe_radius = 1.0
    paths = {}
    initial_y = np.linspace(-pipe_radius * 0.9, pipe_radius * 0.9, n_particles)

    for i in range(n_particles):
        path = [(0.0, float(initial_y[i]))]
        for x_step in range(1, pipe_length + 1):
            x_prev, y_prev = path[-1]
            if x_step > turbulent_start_position:
                # Add random perturbation to mimic turbulent mixing
                perturbation = np.random.normal(0.0, turbulence_intensity)
            else:
                perturbation = 0.0

            y_new = np.clip(y_prev + perturbation, -pipe_radius, pipe_radius)
            path.append((float(x_step), float(y_new)))
        paths[i] = np.array(path)

    return paths


@st.cache_data
def compute_velocity_profile(Re, V_avg):
    """
    Compute a normalised velocity profile v(r)/V_avg for:
    - Laminar (parabolic)
    - Transitional (blend)
    - Turbulent (flat core + thin wall layer)
    Returns r_points (normalised radius) and v_profile (actual velocity).
    """
    r_points = np.linspace(-1.0, 1.0, 200)  # r/R, -1 at bottom wall, 0 centre, +1 at top
    r_abs = np.abs(r_points)

    # Laminar (Poiseuille) – parabolic
    v_lam_norm = 2.0 * (1.0 - r_points**2)  # avg of this is 1

    # Turbulent: explicitly "flat core + thin wall layer"
    y_from_wall = 1.0 - r_abs  # 0 at wall, 1 at centre
    v_turb_norm = np.zeros_like(r_points)

    # Core region (most of the pipe cross-section)
    core_mask = y_from_wall > 0.2  # |r| < 0.8
    v_turb_norm[core_mask] = 1.10  # about 10% above V_avg in the core

    # Near-wall region (thin layer)
    wall_mask = ~core_mask
    y_wall = y_from_wall[wall_mask] / 0.2  # 0 at wall → 1 at core edge
    n_wall = 7.0
    v_turb_norm[wall_mask] = 1.10 * (y_wall ** (1.0 / n_wall))

    # Renormalise turbulent profile so its average is 1
    if np.any(v_turb_norm > 0):
        avg_turb = np.trapz(v_turb_norm, r_points) / np.trapz(np.ones_like(r_points), r_points)
        if avg_turb > 0:
            v_turb_norm /= avg_turb

    # Decide regime and blend
    if Re < 2300:
        v_norm = v_lam_norm
        profile_name = "Laminar (Parabolic)"
        profile_color = "green"
    elif Re > 4000:
        v_norm = v_turb_norm
        profile_name = "Turbulent (Flat Core)"
        profile_color = "red"
    else:
        # Transitional: blend laminar and turbulent
        trans_factor = (Re - 2300.0) / (4000.0 - 2300.0)
        v_norm = v_lam_norm * (1.0 - trans_factor) + v_turb_norm * trans_factor
        profile_name = "Transitional"
        profile_color = "orange"

    v_profile = v_norm * V_avg
    return r_points, v_profile, profile_name, profile_color


# ========== TAB 1: INTERACTIVE SIMULATION ==========

with tab1:
    col1, col2 = st.columns([2, 3])

    # --- Left: Inputs & Summary ---
    with col1:
        st.header("🔬 Parameters")

        # Scenarios
        SCENARIOS = {
            "Custom...": {"fluid": "Water", "D": 0.10, "V": 0.50, "desc": "Adjust all parameters manually."},
            "Water in Garden Hose": {
                "fluid": "Water",
                "D": 0.016,
                "V": 2.0,
                "desc": "16 mm hose, 2 m/s. Typical outdoor tap – turbulent.",
            },
            "Blood in Artery": {
                "fluid": "Blood",
                "D": 0.004,
                "V": 0.3,
                "desc": "4 mm artery, 0.3 m/s. Laminar flow in large arteries.",
            },
            "Oil in Pipeline": {
                "fluid": "Oil",
                "D": 0.50,
                "V": 1.5,
                "desc": "50 cm pipeline, 1.5 m/s. High Re despite viscosity.",
            },
            "Air in Duct": {
                "fluid": "Air",
                "D": 0.30,
                "V": 5.0,
                "desc": "30 cm ventilation duct, 5 m/s. Highly turbulent.",
            },
            "Honey in Tube": {
                "fluid": "Honey",
                "D": 0.005,
                "V": 0.05,
                "desc": "5 mm tube with honey. Extremely laminar (Re ≪ 1).",
            },
        }

        scenario = st.selectbox("Select flow scenario", list(SCENARIOS.keys()))
        sel = SCENARIOS[scenario]
        st.info(sel["desc"])

        fluid_type = st.selectbox(
            "Fluid",
            ["Water", "Oil", "Blood", "Air", "Honey", "Custom"],
            index=["Water", "Oil", "Blood", "Air", "Honey", "Custom"].index(sel["fluid"])
            if sel["fluid"] in ["Water", "Oil", "Blood", "Air", "Honey"]
            else 0,
        )

        # Fluid properties
        if fluid_type == "Water":
            rho_default, mu_default = 1000.0, 0.001
        elif fluid_type == "Oil":
            rho_default, mu_default = 900.0, 0.05
        elif fluid_type == "Blood":
            rho_default, mu_default = 1060.0, 0.003
        elif fluid_type == "Air":
            rho_default, mu_default = 1.2, 1.8e-5
        elif fluid_type == "Honey":
            rho_default, mu_default = 1400.0, 10.0
        else:
            rho_default, mu_default = 1000.0, 0.001

        c_prop1, c_prop2 = st.columns(2)
        with c_prop1:
            if fluid_type == "Custom":
                rho = st.number_input("Density ρ (kg/m³)", value=1000.0, min_value=0.1, step=10.0)
            else:
                rho = rho_default
                st.metric("Density ρ", f"{rho:.1f} kg/m³")

        with c_prop2:
            if fluid_type == "Custom":
                mu = st.number_input("Viscosity μ (Pa·s)", value=0.001, min_value=0.00001, step=0.0001, format="%.5f")
            else:
                mu = mu_default
                st.metric("Viscosity μ", f"{mu:.5f} Pa·s" if mu >= 0.001 else f"{mu:.2e} Pa·s")

        # Pipe & flow
        st.subheader("Pipe and flow conditions")
        c_dim1, c_dim2 = st.columns(2)
        with c_dim1:
            D = (
                st.slider(
                    "Pipe diameter D (cm)",
                    0.1,
                    100.0,
                    sel["D"] * 100,
                    step=0.1,
                    help="Internal pipe diameter",
                )
                / 100.0
            )
        with c_dim2:
            V = st.slider(
                "Average velocity V (m/s)",
                0.01,
                10.0,
                sel["V"],
                step=0.01,
                help="Mean flow velocity",
            )

        # Options
        st.subheader("Visualisation options")
        show_velocity_profile = st.checkbox("Show velocity profile", value=True)
        show_particle_paths = st.checkbox("Show particle streamlines", value=True)

        if show_particle_paths:
            n_particles = st.slider("Number of streamlines", 5, 31, 15, step=2)
            view_mode = st.radio(
                "Display mode",
                ["Static (full paths)", "Animated (developing)"],
                help="Static shows full trajectories; Animated shows development along the pipe.",
            )

        # Basic calculations
        Re = rho * V * D / mu if mu > 0 else 0.0
        if Re < 2300:
            regime = "Laminar"
            regime_icon = "🟢"
            turbulence_intensity = 0.0
            turbulent_start_position = 200  # effectively no turbulence
        elif Re <= 4000:
            regime = "Transitional"
            regime_icon = "🟡"
            trans_factor = (Re - 2300.0) / (4000.0 - 2300.0)
            turbulence_intensity = 0.1 + trans_factor * 0.4
            turbulent_start_position = int(200 * (1.0 - trans_factor * 0.7))
        else:
            regime = "Turbulent"
            regime_icon = "🔴"
            turbulence_intensity = 0.8 + (Re - 4000.0) / 20000.0
            turbulent_start_position = 20

        Q = np.pi * D**2 * V / 4.0
        Q_L_s = Q * 1000.0

        st.markdown("---")
        st.header("📊 Flow summary")
        st.metric("Reynolds number (Re)", f"{Re:,.0f}")
        st.metric("Flow regime", f"{regime_icon} {regime}")
        st.metric("Volumetric flow rate", f"{Q_L_s:.2f} L/s")

    # --- Right: Visualisation ---
    with col2:
        st.header("🖼️ Visualisation")

        fig = make_subplots(
            rows=2,
            cols=1,
            row_heights=[0.45, 0.55],
            vertical_spacing=0.12,
            subplot_titles=("Velocity profile across pipe", "Particle streamlines"),
        )

        # --- Velocity profile ---
        if show_velocity_profile:
            r_points, v_profile, profile_name, profile_color = compute_velocity_profile(Re, V)
            V_max_eff = float(np.max(v_profile))

            if profile_color == "green":
                fillcolor = "rgba(0, 255, 0, 0.3)"
            elif profile_color == "orange":
                fillcolor = "rgba(255, 165, 0, 0.3)"
            else:
                fillcolor = "rgba(255, 0, 0, 0.3)"

            fig.add_trace(
                go.Scatter(
                    x=v_profile,
                    y=r_points,
                    mode="lines",
                    fill="tozerox",
                    fillcolor=fillcolor,
                    line=dict(color=profile_color, width=3),
                    name=profile_name,
                    hovertemplate="Velocity: %{x:.3f} m/s<br>r/R: %{y:.2f}<extra></extra>",
                ),
                row=1,
                col=1,
            )

            # Vertical lines for V_avg and V_max
            fig.add_vline(
                x=V,
                line_dash="dash",
                line_color="gray",
                row=1,
                col=1,
                annotation_text=f"Avg V = {V:.2f} m/s",
                annotation_position="top",
            )
            fig.add_vline(
                x=V_max_eff,
                line_dash="dot",
                line_color="darkred",
                row=1,
                col=1,
                annotation_text=f"Max V ≈ {V_max_eff:.2f} m/s",
                annotation_position="bottom right",
            )

            # Annotation explaining shape
            if Re < 2300:
                fig.add_annotation(
                    x=V * 0.5,
                    y=0.0,
                    text="Parabolic profile<br>V_max = 2×V_avg",
                    showarrow=False,
                    font=dict(size=10, color="green"),
                    bgcolor="rgba(255,255,255,0.8)",
                    row=1,
                    col=1,
                )
            elif Re > 4000:
                fig.add_annotation(
                    x=V * 0.8,
                    y=0.0,
                    text="Flat core<br>Thin near-wall region",
                    showarrow=False,
                    font=dict(size=10, color="red"),
                    bgcolor="rgba(255,255,255,0.8)",
                    row=1,
                    col=1,
                )

            fig.update_xaxes(title_text="Velocity (m/s)", row=1, col=1, gridcolor="lightgray")
            fig.update_yaxes(
                title_text="Radial position (r/R)",
                row=1,
                col=1,
                gridcolor="lightgray",
                range=[-1.2, 1.2],
            )

        # --- Particle paths ---
        if show_particle_paths:
            PIPE_LENGTH = 120
            paths = generate_particle_paths(
                n_particles,
                pipe_length=PIPE_LENGTH,
                turbulence_intensity=turbulence_intensity,
                turbulent_start_position=turbulent_start_position,
            )

            if view_mode == "Static (full paths)":
                for i, path in paths.items():
                    x_vals, y_vals = path[:, 0], path[:, 1]
                    fig.add_trace(
                        go.Scatter(
                            x=x_vals,
                            y=y_vals,
                            mode="lines",
                            line=dict(width=1.5, color="rgba(0,0,150,0.5)"),
                            showlegend=False,
                        ),
                        row=2,
                        col=1,
                    )
            else:
                # Animated: frames along x
                frames = []
                for step in range(PIPE_LENGTH):
                    frame_data = []
                    for i, path in paths.items():
                        segment = path[: step + 1, :]
                        frame_data.append(
                            go.Scatter(
                                x=segment[:, 0],
                                y=segment[:, 1],
                                mode="lines",
                                line=dict(width=1.5, color="rgba(0,0,150,0.5)"),
                                showlegend=False,
                            )
                        )
                    frames.append(go.Frame(data=frame_data, name=str(step)))

                fig.frames = frames

                # Initial frame
                init_data = []
                for i, path in paths.items():
                    segment = path[:1, :]
                    init_data.append(
                        go.Scatter(
                            x=segment[:, 0],
                            y=segment[:, 1],
                            mode="lines",
                            line=dict(width=1.5, color="rgba(0,0,150,0.5)"),
                            showlegend=False,
                        )
                    )
                for tr in init_data:
                    fig.add_trace(tr, row=2, col=1)

                fig.update_layout(
                    updatemenus=[
                        dict(
                            type="buttons",
                            showactive=True,
                            x=0.05,
                            y=1.15,
                            direction="left",
                            buttons=[
                                dict(
                                    label="▶️ Play",
                                    method="animate",
                                    args=[
                                        None,
                                        {
                                            "frame": {"duration": 30, "redraw": True},
                                            "fromcurrent": True,
                                            "transition": {"duration": 0},
                                        },
                                    ],
                                ),
                                dict(
                                    label="⏸️ Pause",
                                    method="animate",
                                    args=[[None], {"frame": {"duration": 0, "redraw": False}}],
                                ),
                            ],
                        )
                    ]
                )

            fig.update_xaxes(
                title_text="Axial distance (arbitrary units)",
                row=2,
                col=1,
                range=[0, PIPE_LENGTH],
                showgrid=False,
            )
            fig.update_yaxes(
                title_text="Radial position",
                row=2,
                col=1,
                range=[-1.3, 1.3],
                showgrid=False,
            )

        fig.update_layout(
            height=800,
            showlegend=False,
            plot_bgcolor="white",
            margin=dict(l=60, r=40, t=80, b=40),
        )

        st.plotly_chart(fig, use_container_width=True)

        caption = f"**{regime} flow** (Re = {Re:,.0f}). "
        if Re < 2300:
            caption += "Smooth parabolic profile with parallel streamlines and no turbulent mixing."
        elif Re <= 4000:
            caption += "Transitional regime: profile and streamlines show a mix of laminar and turbulent features."
        else:
            caption += "Flatter core velocity profile with a thin wall layer and strong mixing in the streamlines."
        st.caption(caption)


# ========== TAB 2: CONCEPTUAL EXPLANATION ==========

with tab2:
    st.header("📚 Understanding Flow Regimes")

    cA, cB = st.columns(2)

    with cA:
        st.subheader("Reynolds number and flow regime")
        st.latex(r"Re = \dfrac{\rho V D}{\mu} = \dfrac{\text{Inertial forces}}{\text{Viscous forces}}")
        st.markdown(
            """
**Where:**

- ρ = density (kg/m³)  
- V = average velocity (m/s)  
- D = pipe diameter (m)  
- μ = dynamic viscosity (Pa·s)

**Interpretation:**

- Low Re → viscous forces dominate → smooth, ordered (laminar)  
- High Re → inertial forces dominate → chaotic, mixing (turbulent)

Typical thresholds for fully developed flow in circular pipes:

- Re < 2,300 → Laminar  
- 2,300 < Re < 4,000 → Transitional  
- Re > 4,000 → Turbulent
"""
        )

        st.subheader("Laminar flow characteristics")
        st.markdown(
            """
- Parabolic velocity profile (Poiseuille flow)  
- V_max = 2 × V_avg at centreline  
- No mixing between layers, smooth streamlines  
- Pressure drop ∝ V (friction factor f = 64/Re)  
- Lower energy loss, easy to model analytically
"""
        )

    with cB:
        st.subheader("Turbulent flow characteristics")
        st.markdown(
            """
- Flatter velocity profile with a nearly uniform core  
- Very steep velocity gradient in a thin layer near the wall  
- Chaotic, three-dimensional motion with eddies  
- Strong mixing and large velocity fluctuations  
- Pressure drop ∝ V² (friction factor from empirical correlations)  
- Much higher energy loss, but excellent mixing and heat transfer

In most industrial pipe systems (water networks, HVAC, process lines) the flow is
deliberately or unavoidably turbulent.
"""
        )

        st.subheader("Why does the turbulent profile look flatter?")
        st.markdown(
            """
Turbulent mixing moves momentum very effectively from the fast-moving core
towards the slower fluid near the wall. This:

- **Boosts the near-wall velocity** compared to laminar flow  
- **Reduces the centreline peak**, so V_max ≈ 1.2 × V_avg  
- Leaves only a **thin region near the wall** with a very steep velocity gradient

The result is a **plug-like core** with a thin viscous sublayer close to the wall.
That’s what the velocity plot in the simulation is trying to show.
"""
        )

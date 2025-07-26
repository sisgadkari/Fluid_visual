import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="Advanced Flow Simulator",
    page_icon="💨",
    layout="wide"
)

# --- Initialize Session State ---
if 'dye_mode' not in st.session_state:
    st.session_state.dye_mode = False

# --- App Title and Description ---
st.title("💨 Advanced Fluid Flow Simulator")
st.markdown("""
This app provides a comprehensive visualization of internal pipe flow. Adjust physical parameters and inject dye to explore fluid dynamics concepts.
- **Particle Paths:** Shows fluid particle trajectories. Use the '▶️ Play' button on the chart to animate.
- **Velocity Profile:** Shows the fluid velocity distribution across the pipe's cross-section.
- **Dye Injection:** Highlights a single stream to visualize dispersion in laminar vs. turbulent flow.
""")

# --- Sidebar for Physical Controls ---
st.sidebar.header("⚙️ Physical Parameters")

# Sliders for physical properties
density = st.sidebar.slider(
    "💧 Fluid Density (ρ) [kg/m³]", 800, 1200, 1000,
    help="Density of the fluid. Water is approximately 1000 kg/m³."
)
viscosity = st.sidebar.slider(
    "🍯 Dynamic Viscosity (μ) [Pa·s]", 0.0001, 0.01, 0.001, format="%.4f",
    help="A measure of a fluid's resistance to flow. Water is ~0.001 Pa·s."
)
diameter = st.sidebar.slider(
    "↔️ Pipe Diameter (D) [m]", 0.01, 0.5, 0.1,
    help="The diameter of the pipe."
)
velocity = st.sidebar.slider(
    "⏩ Average Velocity (V) [m/s]", 0.01, 5.0, 0.5,
    help="The average speed of the fluid through the pipe."
)

# --- Calculation of Reynolds Number and Flow Regime ---
if viscosity > 0 and density > 0 and velocity > 0 and diameter > 0:
    re_number = (density * velocity * diameter) / viscosity
else:
    re_number = 0

# Determine flow regime
if re_number < 2300:
    flow_regime = "Laminar"
    turbulence_intensity = 0
    turbulent_start_position = 101 # No turbulence in laminar
elif 2300 <= re_number <= 4000:
    flow_regime = "Transitional"
    trans_factor = (re_number - 2300) / (4000 - 2300)
    turbulence_intensity = 0.1 + trans_factor * 0.4
    turbulent_start_position = 100 * (1 - trans_factor * 0.7)
else:
    flow_regime = "Turbulent"
    # Increased base intensity for more visible turbulence
    turbulence_intensity = 0.8 + (re_number - 4000) / 20000 
    turbulent_start_position = 10

# Display calculated Re and regime in the sidebar
st.sidebar.markdown("---")
st.sidebar.header("📊 Calculated Results")
st.sidebar.metric("Reynolds Number ($Re$)", f"{re_number:,.0f}")
st.sidebar.metric("Flow Regime", flow_regime)


# --- Simulation & Plotting Parameters ---
NUM_PARTICLES = 31 # Use an odd number to have a perfect center particle
PIPE_LENGTH = 100
PIPE_RADIUS = 10 # Using a fixed radius for visualization purposes

# --- Pre-calculate Particle Paths with Eddy Simulation ---
@st.cache_data
def get_particle_paths(num_particles, pipe_length, pipe_radius, turb_intensity, turb_start_pos):
    paths = {}
    initial_y = np.linspace(-pipe_radius * 0.9, pipe_radius * 0.9, num_particles)
    
    for i in range(num_particles):
        path = [(0, initial_y[i])]
        for x_step in range(1, pipe_length):
            _, last_y = path[-1]
            perturbation = 0
            if x_step > turb_start_pos:
                # Simplified turbulence model using only random perturbations
                perturbation = np.random.normal(0, turb_intensity)

            new_y = np.clip(last_y + perturbation, -pipe_radius, pipe_radius)
            path.append((x_step, new_y))
        paths[i] = np.array(path)
    return paths

particle_paths = get_particle_paths(NUM_PARTICLES, PIPE_LENGTH, PIPE_RADIUS, turbulence_intensity, turbulent_start_position)

# --- Function to Calculate Velocity Profile ---
@st.cache_data
def get_velocity_profile(re, avg_vel, pipe_rad):
    y_points = np.linspace(-pipe_rad, pipe_rad, 100)
    v_max_laminar = 2 * avg_vel
    laminar_profile = v_max_laminar * (1 - (y_points / pipe_rad)**2)
    n = 7
    v_max_turbulent = avg_vel * (n + 1) * (2 * n + 1) / (2 * n**2)
    turbulent_profile = v_max_turbulent * (1 - np.abs(y_points / pipe_rad))**(1/n)
    if re < 2300: return y_points, laminar_profile
    if re > 4000: return y_points, turbulent_profile
    trans_factor = (re - 2300) / (4000 - 2300)
    return y_points, laminar_profile * (1 - trans_factor) + turbulent_profile * trans_factor

y_coords, vel_profile = get_velocity_profile(re_number, velocity, PIPE_RADIUS)


# --- UI Layout ---
col1, col2 = st.columns((3, 1.5))

with col1:
    st.subheader("Particle Paths")
    # Button to toggle dye mode
    if st.button('💉 Inject Dye Stream' if not st.session_state.dye_mode else '🌈 Show All Streams'):
        st.session_state.dye_mode = not st.session_state.dye_mode
    plot_placeholder = st.empty()

with col2:
    st.subheader("Velocity Profile")
    profile_placeholder = st.empty()

# --- Plot Drawing Functions ---
def draw_animated_particle_plot(is_dye_mode):
    layout = go.Layout(
        xaxis=dict(range=[0, PIPE_LENGTH], autorange=False, showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-PIPE_RADIUS*1.2, PIPE_RADIUS*1.2], autorange=False, showgrid=False, zeroline=False, showticklabels=False),
        xaxis_title="Flow Direction", yaxis_title="Pipe Cross-section",
        plot_bgcolor='#0E1117', paper_bgcolor='#0E1117', font_color='white',
        showlegend=False, height=400, margin=dict(l=10, r=10, t=40, b=10),
        updatemenus=[dict(type="buttons", direction="right", x=0.1, y=1.1, showactive=True,
            buttons=[
                dict(label="▶️ Play", method="animate", args=[None, {"frame": {"duration": 30, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}]),
                dict(label="⏸️ Pause", method="animate", args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}])
            ])]
    )

    colors = [f'hsl({int(h)}, 80%, 60%)' for h in np.linspace(0, 360, NUM_PARTICLES, endpoint=False)]
    base_traces = []
    dye_particle_index = NUM_PARTICLES // 2

    for i in range(NUM_PARTICLES):
        path = particle_paths[i]
        line_props = {'width': 2}
        if is_dye_mode:
            if i == dye_particle_index:
                line_props['color'] = 'magenta'
                line_props['width'] = 4
            else:
                line_props['color'] = 'rgba(200, 200, 200, 0.2)' # Faded background lines
        else:
            line_props['color'] = colors[i]
        
        base_traces.append(go.Scatter(x=path[:, 0], y=path[:, 1], mode='lines', line=line_props, hoverinfo='none'))

    fig = go.Figure(data=base_traces, layout=layout)
    
    frames = []
    for step in range(PIPE_LENGTH):
        frame_data = []
        for i in range(NUM_PARTICLES):
            path = particle_paths[i]
            frame_data.append(go.Scatter(x=path[:step+1, 0], y=path[:step+1, 1]))
        frames.append(go.Frame(data=frame_data, name=str(step), traces=list(range(NUM_PARTICLES))))
    
    fig.frames = frames
    return fig

def draw_velocity_profile_plot():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=vel_profile, y=y_coords, mode='lines', fill='tozerox', line=dict(color='#1f77b4', width=3)))
    fig.update_layout(
        xaxis_title="Velocity (m/s)", yaxis_title="",
        plot_bgcolor='#0E1117', paper_bgcolor='#0E1117', font_color='white',
        xaxis=dict(range=[0, max(vel_profile) * 1.1 if max(vel_profile) > 0 else 1], showgrid=True, gridcolor='rgba(255,255,255,0.2)'),
        yaxis=dict(range=[-PIPE_RADIUS, PIPE_RADIUS], showticklabels=False, showgrid=False, zeroline=False),
        height=400, margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig

# --- Logic for Displaying Plots ---
profile_placeholder.plotly_chart(draw_velocity_profile_plot(), use_container_width=True)
plot_placeholder.plotly_chart(draw_animated_particle_plot(st.session_state.dye_mode), use_container_width=True)

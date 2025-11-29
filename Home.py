import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="Fluid Mechanics Interactive Learning Hub",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Enhanced Styling with Animations ---
st.markdown("""
<style>
    /* Animated water wave background */
    @keyframes wave {
        0% { transform: translateX(0) translateY(0); }
        50% { transform: translateX(-25px) translateY(5px); }
        100% { transform: translateX(0) translateY(0); }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    
    @keyframes droplet {
        0% { transform: translateY(-20px); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateY(20px); opacity: 0; }
    }
    
    @keyframes flow {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .main-header {
        font-size: 3.5em;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(120deg, #1e3a8a, #3b82f6, #06b6d4, #3b82f6, #1e3a8a);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        padding: 20px 0;
        margin-bottom: 10px;
        animation: shimmer 3s linear infinite;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.3em;
        color: #64748b;
        margin-bottom: 30px;
        font-weight: 300;
    }
    
    /* Animated wave container */
    .wave-container {
        position: relative;
        width: 100%;
        height: 120px;
        overflow: hidden;
        background: linear-gradient(180deg, #e0f2fe 0%, #bae6fd 50%, #7dd3fc 100%);
        border-radius: 15px;
        margin: 20px 0;
    }
    
    .wave {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 200%;
        height: 100px;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%230ea5e9' fill-opacity='0.6' d='M0,192L48,197.3C96,203,192,213,288,229.3C384,245,480,267,576,250.7C672,235,768,181,864,181.3C960,181,1056,235,1152,234.7C1248,235,1344,181,1392,154.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E") repeat-x;
        background-size: 50% 100px;
        animation: wave 8s linear infinite;
    }
    
    .wave2 {
        bottom: 10px;
        opacity: 0.5;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%230284c7' fill-opacity='0.6' d='M0,64L48,80C96,96,192,128,288,128C384,128,480,96,576,90.7C672,85,768,107,864,122.7C960,139,1056,149,1152,138.7C1248,128,1344,96,1392,80L1440,64L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E") repeat-x;
        background-size: 50% 100px;
        animation: wave 6s linear infinite reverse;
    }
    
    /* Floating droplets */
    .droplet {
        position: absolute;
        font-size: 1.5em;
        animation: droplet 3s ease-in-out infinite;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 15px 0;
        color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(102, 126, 234, 0.4);
    }
    
    .feature-card h3 {
        color: white;
        font-size: 1.5em;
        margin-bottom: 10px;
    }
    
    .module-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
    }
    
    .module-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
        transition: left 0.5s ease;
    }
    
    .module-card:hover::before {
        left: 100%;
    }
    
    .module-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 8px 16px rgba(59, 130, 246, 0.2);
        transform: translateY(-2px);
    }
    
    .module-number {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        text-align: center;
        line-height: 35px;
        font-weight: bold;
        margin-right: 10px;
    }
    
    .stat-box {
        text-align: center;
        padding: 25px;
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        border-radius: 15px;
        color: white;
        margin: 10px;
        animation: float 4s ease-in-out infinite;
        box-shadow: 0 10px 30px rgba(6, 182, 212, 0.3);
    }
    
    .stat-box:nth-child(2) {
        animation-delay: 0.5s;
    }
    
    .stat-box:nth-child(3) {
        animation-delay: 1s;
    }
    
    .stat-number {
        font-size: 2.8em;
        font-weight: bold;
        display: block;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .stat-label {
        font-size: 1em;
        opacity: 0.95;
        margin-top: 5px;
    }
    
    /* Animated pipe with flowing water */
    .pipe-container {
        position: relative;
        width: 100%;
        height: 60px;
        background: linear-gradient(180deg, #475569 0%, #334155 50%, #475569 100%);
        border-radius: 30px;
        margin: 30px 0;
        overflow: hidden;
        box-shadow: inset 0 5px 15px rgba(0,0,0,0.3);
    }
    
    .pipe-water {
        position: absolute;
        top: 10px;
        left: 0;
        width: 200%;
        height: 40px;
        background: linear-gradient(90deg, #0ea5e9, #06b6d4, #22d3ee, #06b6d4, #0ea5e9);
        background-size: 50% 100%;
        border-radius: 20px;
        animation: flow 2s linear infinite;
    }
    
    .pipe-label {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-weight: bold;
        font-size: 1.1em;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        z-index: 10;
    }
    
    /* Bubble animation */
    @keyframes bubble {
        0% { transform: translateY(100%) scale(0); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateY(-100%) scale(1); opacity: 0; }
    }
    
    .bubble {
        position: absolute;
        background: rgba(255,255,255,0.6);
        border-radius: 50%;
        animation: bubble 4s ease-in-out infinite;
    }
    
    /* How to use cards */
    .how-to-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        border: 2px solid #bae6fd;
        transition: all 0.3s ease;
    }
    
    .how-to-card:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 25px rgba(14, 165, 233, 0.2);
    }
    
    .how-to-number {
        font-size: 3em;
        margin-bottom: 10px;
    }
    
    .cta-section {
        text-align: center;
        padding: 50px 30px;
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 20px;
        margin: 30px 0;
        border: 2px solid #667eea30;
        position: relative;
        overflow: hidden;
    }
    
    .cta-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102,126,234,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# --- Hero Section with Animation ---
st.markdown("<h1 class='main-header'>💧 Fluid Mechanics Interactive Learning Hub</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Transform Complex Concepts into Visual Understanding • Learn by Doing • Master Fluid Mechanics</p>", unsafe_allow_html=True)

# --- Animated Wave Banner ---
st.markdown("""
<div class='wave-container'>
    <div class='wave'></div>
    <div class='wave wave2'></div>
    <span class='droplet' style='left: 10%; top: 20%; animation-delay: 0s;'>💧</span>
    <span class='droplet' style='left: 30%; top: 10%; animation-delay: 0.5s;'>💧</span>
    <span class='droplet' style='left: 50%; top: 25%; animation-delay: 1s;'>💧</span>
    <span class='droplet' style='left: 70%; top: 15%; animation-delay: 1.5s;'>💧</span>
    <span class='droplet' style='left: 90%; top: 20%; animation-delay: 2s;'>💧</span>
</div>
""", unsafe_allow_html=True)

# --- Create animated stats ---
col_viz1, col_viz2, col_viz3 = st.columns(3)

with col_viz1:
    st.markdown("""
    <div class='stat-box'>
        <span class='stat-number'>10</span>
        <span class='stat-label'>Interactive Modules</span>
    </div>
    """, unsafe_allow_html=True)

with col_viz2:
    st.markdown("""
    <div class='stat-box' style='animation-delay: 0.5s;'>
        <span class='stat-number'>∞</span>
        <span class='stat-label'>Parameter Combinations</span>
    </div>
    """, unsafe_allow_html=True)

with col_viz3:
    st.markdown("""
    <div class='stat-box' style='animation-delay: 1s;'>
        <span class='stat-number'>100%</span>
        <span class='stat-label'>Visual Learning</span>
    </div>
    """, unsafe_allow_html=True)

# --- Animated Pipe Flow ---
st.markdown("""
<div class='pipe-container'>
    <div class='pipe-water'></div>
    <span class='pipe-label'>⟶ Explore the Flow of Knowledge ⟶</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Interactive Fluid Animation using Plotly ---
st.markdown("## 🌊 See Fluid Mechanics in Action")

# Create an animated plotly figure showing fluid concepts
fig = go.Figure()

# Create wave animation data
x = np.linspace(0, 4*np.pi, 100)
frames = []
for i in range(30):
    phase = i * 0.2
    y1 = np.sin(x + phase) * 0.5 + 1
    y2 = np.sin(x + phase + np.pi/4) * 0.3 + 0.5
    frames.append(go.Frame(data=[
        go.Scatter(x=x, y=y1, fill='tozeroy', fillcolor='rgba(14, 165, 233, 0.6)',
                  line=dict(color='#0284c7', width=3), name='Surface Wave'),
        go.Scatter(x=x, y=y2, fill='tozeroy', fillcolor='rgba(6, 182, 212, 0.4)',
                  line=dict(color='#06b6d4', width=2), name='Pressure Wave')
    ]))

# Initial frame
fig.add_trace(go.Scatter(x=x, y=np.sin(x)*0.5+1, fill='tozeroy', 
                         fillcolor='rgba(14, 165, 233, 0.6)',
                         line=dict(color='#0284c7', width=3), name='Surface Wave'))
fig.add_trace(go.Scatter(x=x, y=np.sin(x+np.pi/4)*0.3+0.5, fill='tozeroy',
                         fillcolor='rgba(6, 182, 212, 0.4)',
                         line=dict(color='#06b6d4', width=2), name='Pressure Wave'))

fig.frames = frames

fig.update_layout(
    title=dict(text="<b>Dynamic Wave Visualization</b>", x=0.5, font=dict(size=18)),
    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, title=""),
    yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, 2], title=""),
    plot_bgcolor='rgba(240,249,255,0.5)',
    paper_bgcolor='rgba(0,0,0,0)',
    height=250,
    margin=dict(l=20, r=20, t=50, b=20),
    showlegend=False,
    updatemenus=[dict(
        type="buttons",
        showactive=False,
        y=1.15,
        x=0.5,
        xanchor="center",
        buttons=[
            dict(label="▶ Play Wave Animation",
                 method="animate",
                 args=[None, {"frame": {"duration": 100, "redraw": True},
                             "fromcurrent": True,
                             "transition": {"duration": 50}}])
        ]
    )]
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- How to Use Section with animated cards ---
st.markdown("## 📖 How to Use this App")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='how-to-card'>
        <div class='how-to-number'>1️⃣</div>
        <h3>Choose Your Topic</h3>
        <p>Use the sidebar to navigate to any module that interests you. Start with basics or jump to advanced topics!</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='how-to-card'>
        <div class='how-to-number'>2️⃣</div>
        <h3>Adjust & Experiment</h3>
        <p>Play with sliders and input fields. Watch real-time updates as you change parameters. No wrong answers here!</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='how-to-card'>
        <div class='how-to-number'>3️⃣</div>
        <h3>Learn & Apply</h3>
        <p>Study the formulas, read the theory, and understand the calculations. Apply what you learn to solve real problems!</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- What Makes This Special Section ---
st.markdown("## 🚀 What Makes This Learning Experience Special")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class='feature-card'>
        <h3>🎮 Interactive Learning</h3>
        <p>No more passive reading! Adjust parameters in real-time and watch fluid behavior change instantly. See the immediate impact of your decisions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h3>📊 Visual Understanding</h3>
        <p>Complex equations come to life through beautiful animations and diagrams. Understand the 'why' behind every formula.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-card'>
        <h3>🧪 Experiment Freely</h3>
        <p>No lab equipment needed! Test extreme conditions, compare scenarios side-by-side, and learn from every experiment.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h3>📚 Step-by-Step Solutions</h3>
        <p>Each module includes detailed calculations and theory. Learn not just what happens, but how to solve problems yourself.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- Module Overview Section ---
st.markdown("## 🗺️ Explore Our Modules")
st.markdown("Each module is designed to make you an expert in a specific fluid mechanics concept. Click on any topic in the sidebar to begin!")

# Module descriptions with emojis and engaging text
modules = [
    {
        "number": "1",
        "icon": "💧",
        "title": "Capillary Rise",
        "description": "Watch liquid defy gravity! Explore how surface tension pulls fluids up narrow tubes. Experiment with water, mercury, and ethanol.",
        "key_concept": "Surface Tension & Contact Angles"
    },
    {
        "number": "2",
        "icon": "📏",
        "title": "Open Manometer",
        "description": "Master pressure measurement with U-tube manometers. See how fluid heights reveal pressure differences in real-time.",
        "key_concept": "Pressure Measurement & Fluid Statics"
    },
    {
        "number": "3",
        "icon": "🔒",
        "title": "Closed Manometer",
        "description": "Unlock the secrets of closed-system pressure measurements. Perfect for understanding vacuum and absolute pressure.",
        "key_concept": "Absolute vs Gauge Pressure"
    },
    {
        "number": "4",
        "icon": "✈️",
        "title": "Pitot-Static Tube",
        "description": "Discover how aircraft measure airspeed! Learn the principles behind one of aviation's most important instruments.",
        "key_concept": "Dynamic Pressure & Flow Velocity"
    },
    {
        "number": "5",
        "icon": "🏗️",
        "title": "Hydrostatic Force - Straight Wall",
        "description": "Calculate massive forces on dams and tanks! Visualize pressure distribution and find the center of pressure on vertical walls.",
        "key_concept": "Hydrostatic Force & Pressure Distribution"
    },
    {
        "number": "6",
        "icon": "📐",
        "title": "Hydrostatic Force - Inclined Wall",
        "description": "See how tilting a surface changes everything! Master force calculations on inclined gates and surfaces.",
        "key_concept": "Forces on Inclined Surfaces"
    },
    {
        "number": "7",
        "icon": "🔄",
        "title": "Reducing Pipe Bend",
        "description": "Witness momentum in action! Calculate forces on pipe bends and understand why pipelines need support structures.",
        "key_concept": "Momentum Equation & Reaction Forces"
    },
    {
        "number": "8",
        "icon": "🌊",
        "title": "Laminar vs Turbulent Flow",
        "description": "Inject virtual dye and watch flow patterns emerge! Cross the Reynolds number threshold and see chaos unfold.",
        "key_concept": "Reynolds Number & Flow Regimes"
    },
    {
        "number": "9",
        "icon": "⚡",
        "title": "Pump Head & Power",
        "description": "Design pumping systems like a pro! Calculate required pump power for any piping configuration.",
        "key_concept": "Bernoulli Equation & Energy Analysis"
    },
    {
        "number": "10",
        "icon": "⚙️",
        "title": "Turbine Power",
        "description": "Extract energy from flowing fluids! Explore how turbines convert fluid power into mechanical work.",
        "key_concept": "Energy Extraction & Efficiency"
    }
]

# Display modules in two columns
col1, col2 = st.columns(2)

for i, module in enumerate(modules):
    with col1 if i % 2 == 0 else col2:
        st.markdown(f"""
        <div class='module-card'>
            <h3><span class='module-number'>{module['number']}</span> {module['icon']} {module['title']}</h3>
            <p style='color: #475569; margin: 10px 0;'>{module['description']}</p>
            <p style='color: #3b82f6; font-weight: 600; font-size: 0.9em; margin-top: 10px;'>
                🎯 Key Concept: {module['key_concept']}
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- Call to Action with animation ---
st.markdown("""
<div class='cta-section'>
    <h2 style='color: #1e293b; margin-bottom: 15px; position: relative; z-index: 1;'>🚀 Ready to Master Fluid Mechanics?</h2>
    <p style='font-size: 1.1em; color: #475569; margin-bottom: 25px; position: relative; z-index: 1;'>
        Choose your first module from the sidebar and start your interactive learning journey today!
    </p>
    <p style='font-size: 1.5em; position: relative; z-index: 1;'>👈 <strong>Start exploring now!</strong></p>
</div>
""", unsafe_allow_html=True)

# --- Footer with Educational Tips ---
st.markdown("---")
st.markdown("## 💡 Pro Tips for Maximum Learning")

tip_col1, tip_col2 = st.columns(2)

with tip_col1:
    st.markdown("""
    - 🎯 **Start with extremes**: Test minimum and maximum values to understand boundaries
    - 📝 **Take notes**: Document interesting parameter combinations you discover
    - 🔄 **Compare scenarios**: Use preset options to see real-world applications
    """)

with tip_col2:
    st.markdown("""
    - 🧪 **Challenge yourself**: Try to predict outcomes before adjusting parameters
    - 📊 **Study the graphs**: Pay attention to how curves and distributions change
    - 🤔 **Ask "what if?"**: The best learning comes from curiosity-driven exploration
    """)

st.markdown("---")

# --- Credits Footer ---
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 20px; font-size: 0.9em;'>
    <p>🎓 Developed for Chemical Engineering Students</p>
    <p>University of Surrey | School of Chemistry and Chemical Engineering</p>
    <p style='margin-top: 10px;'>👨‍💻 Developer: <strong>Dr Siddharth Gadkari</strong></p>
    <p style='margin-top: 5px;'>🏆 Funded by the <strong>Fluor Global University Sponsorship Program (GUSP) Award</strong> and <strong>Faculty of Engineering and Physical Sciences Teaching Innovation Fund</strong></p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Developer Credit ---
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; padding: 10px; font-size: 0.85em; color: #64748b;'>
    <p style='margin: 5px 0;'>💻 <strong>App developed by</strong></p>
    <p style='margin: 5px 0; font-weight: 600; color: #1e293b;'>Dr. Siddharth Gadkari</p>
    <p style='margin: 5px 0; font-size: 0.8em;'>University of Surrey</p>
</div>
""", unsafe_allow_html=True)

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

# --- Custom CSS for Enhanced Styling ---
st.markdown("""
<style>
    /* Animated droplet keyframes */
    @keyframes droplet {
        0% { transform: translateY(-20px); opacity: 0; }
        20% { opacity: 1; }
        100% { transform: translateY(100px); opacity: 0; }
    }
    
    @keyframes wave {
        0% { transform: translateX(0) translateY(0); }
        50% { transform: translateX(-25px) translateY(5px); }
        100% { transform: translateX(0) translateY(0); }
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
        animation: droplet 4s ease-in-out infinite;
    }

    .main-header {
        font-size: 3.5em;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(120deg, #1e3a8a, #3b82f6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        padding: 20px 0;
        margin-bottom: 10px;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.3em;
        color: #64748b;
        margin-bottom: 30px;
        font-weight: 300;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 15px 0;
        color: white;
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
        padding: 20px;
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        border-radius: 10px;
        color: white;
        margin: 10px;
    }
    
    .stat-number {
        font-size: 2.5em;
        font-weight: bold;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 25px;
        text-align: center;
        font-size: 1.2em;
        font-weight: bold;
        margin: 20px auto;
        display: block;
        width: fit-content;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .concept-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #86efac;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .concept-card:hover {
        border-color: #22c55e;
        box-shadow: 0 8px 16px rgba(34, 197, 94, 0.2);
        transform: translateY(-2px);
    }
    
    .concept-number {
        display: inline-block;
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        text-align: center;
        line-height: 35px;
        font-weight: bold;
        margin-right: 10px;
    }
    
    .section-header {
        background: linear-gradient(135deg, #f0fdf4 0%, #bbf7d0 100%);
        border-left: 5px solid #22c55e;
        padding: 15px 20px;
        border-radius: 0 10px 10px 0;
        margin: 30px 0 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("📚 Navigation")

# Interactive Modules Section
st.sidebar.markdown("### 🔬 Interactive Modules")
st.sidebar.page_link("pages/1_💧_Capillary_Rise.py", label="💧 Capillary Rise")
st.sidebar.page_link("pages/2_📏_Open_Manometer.py", label="📏 Open Manometer")
st.sidebar.page_link("pages/3_🔒_Closed_Manometer.py", label="🔒 Closed Manometer")
st.sidebar.page_link("pages/4_✈️_Pitot-Static_Tube.py", label="✈️ Pitot-Static Tube")
st.sidebar.page_link("pages/5_🏗️_Hydrostatic_Pressure_Straight_Wall.py", label="🏗️ Hydrostatic Force - Straight Wall")
st.sidebar.page_link("pages/6_📐_Hydrostatic_Pressure_Inclined_Wall.py", label="📐 Hydrostatic Force - Inclined Wall")
st.sidebar.page_link("pages/7_🔄_Reducing_Pipe_Bend.py", label="🔄 Reducing Pipe Bend")
st.sidebar.page_link("pages/8_🌊_Laminar_and_Turbulent_Flow.py", label="🌊 Laminar & Turbulent Flow")
st.sidebar.page_link("pages/9_⚡_Pump_Head_Demand.py", label="⚡ Pump Head & Power")
st.sidebar.page_link("pages/10_⚙️_Turbine_Power.py", label="⚙️ Turbine Power")

# Fundamental Concepts Section
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Fundamental Concepts")
st.sidebar.page_link("pages/Fundamental_Concepts/1_🍯_Viscosity.py", label="🍯 Viscosity")

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; padding: 10px; font-size: 0.85em; color: #64748b;'>
    <p style='margin: 5px 0;'>💻 <strong>App developed by</strong></p>
    <p style='margin: 5px 0; font-weight: 600; color: #1e293b;'>Dr. Siddharth Gadkari</p>
    <p style='margin: 5px 0; font-size: 0.8em;'>University of Surrey</p>
</div>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("<h1 class='main-header'>💧 Fluid Mechanics Interactive Learning Hub</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Transform Complex Concepts into Visual Understanding • Learn by Doing • Master Fluid Mechanics</p>", unsafe_allow_html=True)

# --- Animated Wave Banner with Droplets ---
st.markdown("""
<div class='wave-container'>
    <div class='wave'></div>
    <div class='wave wave2'></div>
    <span class='droplet' style='left: 10%; top: 10%; animation-delay: 0s;'>💧</span>
    <span class='droplet' style='left: 25%; top: 5%; animation-delay: 0.7s;'>💧</span>
    <span class='droplet' style='left: 40%; top: 15%; animation-delay: 1.4s;'>💧</span>
    <span class='droplet' style='left: 55%; top: 8%; animation-delay: 2.1s;'>💧</span>
    <span class='droplet' style='left: 70%; top: 12%; animation-delay: 2.8s;'>💧</span>
    <span class='droplet' style='left: 85%; top: 6%; animation-delay: 3.5s;'>💧</span>
</div>
""", unsafe_allow_html=True)

# --- Create a simple animated visualization ---
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
    <div class='stat-box'>
        <span class='stat-number'>∞</span>
        <span class='stat-label'>Parameter Combinations</span>
    </div>
    """, unsafe_allow_html=True)

with col_viz3:
    st.markdown("""
    <div class='stat-box'>
        <span class='stat-number'>100%</span>
        <span class='stat-label'>Visual Learning</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- How to Use Section ---
st.markdown("## 📖 How to Use this App")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 1️⃣ Choose Your Topic
    Use the sidebar to navigate to any module that interests you. Start with basics or jump to advanced topics!
    """)

with col2:
    st.markdown("""
    ### 2️⃣ Adjust & Experiment
    Play with sliders and input fields. Watch real-time updates as you change parameters. No wrong answers here!
    """)

with col3:
    st.markdown("""
    ### 3️⃣ Learn & Apply
    Study the formulas, read the theory, and understand the calculations. Apply what you learn to solve real problems!
    """)

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

# --- Fundamental Concepts Section ---
st.markdown("""
<div class='section-header'>
    <h2 style='margin: 0; color: #166534;'>📖 Fundamental Concepts</h2>
    <p style='margin: 5px 0 0 0; color: #15803d; font-size: 0.95em;'>Master the building blocks of fluid mechanics</p>
</div>
""", unsafe_allow_html=True)

st.markdown("Before diving into complex applications, understand these essential concepts that form the foundation of fluid mechanics.")

# Fundamental concepts list
concepts = [
    {
        "number": "1",
        "icon": "🍯",
        "title": "Viscosity",
        "description": "Understand how fluids resist flow and deformation. Explore the difference between honey and water, learn about Newtonian vs Non-Newtonian fluids, and see the falling ball viscometer in action.",
        "key_concept": "Newton's Law of Viscosity & Fluid Resistance"
    },
    {
        "number": "2",
        "icon": "💧",
        "title": "Surface Tension",
        "description": "Coming soon! Discover why water forms droplets, how insects walk on water, and the molecular forces at fluid interfaces.",
        "key_concept": "Cohesive Forces & Capillary Effects",
        "coming_soon": True
    },
]

# Display concepts in two columns
col1, col2 = st.columns(2)

for i, concept in enumerate(concepts):
    with col1 if i % 2 == 0 else col2:
        opacity_style = "opacity: 0.6;" if concept.get('coming_soon') else ""
        badge = "<span style='background: #fbbf24; color: #78350f; padding: 2px 8px; border-radius: 10px; font-size: 0.7em; margin-left: 10px;'>COMING SOON</span>" if concept.get('coming_soon') else ""
        
        st.markdown(f"""
        <div class='concept-card' style='{opacity_style}'>
            <h3><span class='concept-number'>{concept['number']}</span> {concept['icon']} {concept['title']}{badge}</h3>
            <p style='color: #475569; margin: 10px 0;'>{concept['description']}</p>
            <p style='color: #22c55e; font-weight: 600; font-size: 0.9em; margin-top: 10px;'>
                📚 Key Concept: {concept['key_concept']}
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- Call to Action ---
st.markdown("""
<div style='text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%); border-radius: 15px; margin: 20px 0;'>
    <h2 style='color: #1e293b; margin-bottom: 15px;'>Ready to Master Fluid Mechanics?</h2>
    <p style='font-size: 1.1em; color: #475569; margin-bottom: 25px;'>
        Choose your first module from the sidebar and start your interactive learning journey today!
    </p>
    <p style='font-size: 1.3em;'>👈 <strong>Start exploring now!</strong></p>
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

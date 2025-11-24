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
</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("<h1 class='main-header'>💧 Fluid Mechanics Interactive Learning Hub</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Transform Complex Concepts into Visual Understanding • Learn by Doing • Master Fluid Mechanics</p>", unsafe_allow_html=True)

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

# --- What Makes This Special Section ---
st.markdown("## 🌟 Why This App is Different")

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

# --- How to Use Section ---
st.markdown("## 🚀 Getting Started")

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

# --- Sidebar Developer Credit ---
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; padding: 10px; font-size: 0.85em; color: #64748b;'>
    <p style='margin: 5px 0;'>💻 <strong>App developed by</strong></p>
    <p style='margin: 5px 0; font-weight: 600; color: #1e293b;'>Dr. Siddharth Gadkari</p>
    <p style='margin: 5px 0; font-size: 0.8em;'>University of Surrey</p>
</div>
""", unsafe_allow_html=True)

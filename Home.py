import streamlit as st

st.set_page_config(page_title="Fluid Mechanics Interactive Learning Hub", layout="wide")

st.markdown("<h1 style='text-align: center;'>Fluid Mechanics Interactive Learning Hub</h1>", unsafe_allow_html=True)
st.markdown(
    "<h4 style='text-align: center; font-weight: normal;'>Welcome! Select a topic from the sidebar to start learning and exploring key concepts interactively.</h4>",
    unsafe_allow_html=True
)

st.markdown("""
---
**What can you do here?**
- Visualize surface tension and capillary rise.
- Experiment with open and closed manometers.
- Explore hydrostatic forces on straight and inclined walls.
- Change parameters and see results update in real time!

---

**To begin:**  
- Use the sidebar to navigate to each topic.
- Each page provides interactive widgets, diagrams, and formulas.
""")

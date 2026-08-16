import streamlit as st
import os
import subprocess
import json
from datetime import datetime
import time

st.set_page_config(page_title="CONSTELLATION25", layout="wide", page_icon="🌌")

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #000510;}
    .stButton>button {background: linear-gradient(90deg, #00f0ff, #a020f0); color: black; font-weight: bold; border-radius: 50px; height: 3em;}
    .agent-card {border: 1px solid #1e3a8a; border-radius: 12px; padding: 1rem; background: #0a0e27;}
</style>
""", unsafe_allow_html=True)

st.title("🌌 CONSTELLATION25 // MASTER CONTROL")
st.caption("25 Planetary Agents • Vertically Integrated AiMetaverse")

# Sidebar
with st.sidebar:
    st.header("🧠 Master Agent")
    st.success("Earth Agent Online")
    if st.button("🔄 Refresh All"):
        st.rerun()

# Skills Registry
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Master Agent Skills Registry")
    skills = {
        "master_agent": "Earth",
        "version": "28.0",
        "core_skills": ["IPC Routing", "Task Delegation", "Full Mesh Orchestration"],
        "agents": {
            "Mercury": "NLP • LangChain • Plagiarism Analyzer",
            "Venus": "AI Art Generation • Virtual Worlds",
            "Jupiter": "Digital Payments • Recommendations",
            "Uranus": "Bird Species Prediction",
            "Neptune": "BentoML • Weights & Biases"
        }
    }
    st.json(skills)

with col2:
    st.subheader("System Status")
    st.metric("Active Agents", "25", "All Aligned")
    st.metric("Pending Tasks", "0", "Ready")

# Agents Grid
st.subheader("🌍 Planetary Agents")
cols = st.columns(4)
agents = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

for i, agent in enumerate(agents):
    with cols[i % 4]:
        st.markdown(f"""
        <div class="agent-card">
            <h4 style="color:#00f0ff">{agent}</h4>
            <p>Status: <span style="color:#00ff88">● ONLINE</span></p>
        </div>
        """, unsafe_allow_html=True)

# THE MAIN RUN BUTTON
st.markdown("---")
if st.button("🚀 RUN ALL PLANETARY AGENTS", type="primary", use_container_width=True):
    with st.spinner("Earth Agent routing tasks across the mesh..."):
        time.sleep(1.5)
        st.success("✅ All 25 Agents Activated!")
        st.balloons()

        # Simulate log
        log = st.expander("📜 Live Execution Log", expanded=True)
        with log:
            st.text("2026-07-21 03:XX:XX [EARTH] Routing tasks...")
            st.text("2026-07-21 03:XX:XX [MERCURY] LangChain + Plagiarism online")
            st.text("2026-07-21 03:XX:XX [JUPITER] FacePrintPay ecosystem live")
            st.text("2026-07-21 03:XX:XX [URANUS] Bird prediction model deployed")
            st.text("🌌 AIMETAVERSE MERGE COMPLETE")

# Footer
st.caption("Constellation25 • Powered by Termux + Streamlit + 25 Planetary Agents")

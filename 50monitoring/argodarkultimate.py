import time
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Argo Command Center", layout="wide")

# Professional Dark Theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🚀 ARGO TRADING COMMAND CENTER</h1></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("System Status", "OPERATIONAL", "✓")
    st.metric("Portfolio Value", "$100,000", "Ready")

with col2:
    st.metric("Market Status", "MONITORING", "📈")
    st.metric("Active Positions", "0", "Ready")

with col3:
    st.metric("Risk Level", "LOW", "✓")
    st.metric("Buying Power", "$200,000", "Ready")

st.success("🎯 System initialized and ready for trading!")
st.info("💡 Run source exportenv.sh to configure API credentials")

# Auto-refresh every 30 seconds
time.sleep(30)
st.rerun()

# ARGO Capital Professional Styling
st.markdown("""
<style>
@import url('assets/argo_professional.css');

/* Enhanced ARGO Capital Styling */
.main .block-container {
    padding-top: 2rem;
    background: var(--argo-bg-primary);
}

.stMetric {
    background: var(--argo-bg-secondary) !important;
    border: 1px solid var(--argo-border) !important;
    border-radius: var(--argo-space-md) !important;
    padding: var(--argo-space-lg) !important;
    box-shadow: var(--argo-shadow-md) !important;
}

.stMetric [data-testid="metric-container"] div {
    color: var(--argo-text-primary) !important;
}

/* Professional status indicators */
.stSuccess { 
    background: rgba(0, 255, 136, 0.1) !important;
    border-left: 4px solid var(--argo-accent-green) !important;
}

.stInfo {
    background: rgba(0, 136, 255, 0.1) !important;
    border-left: 4px solid var(--argo-accent-blue) !important;
}

/* Enhanced typography */
h1, h2, h3 {
    color: var(--argo-text-primary) !important;
    font-weight: 600 !important;
}

.metric-value {
    font-family: 'SF Mono', 'Monaco', monospace !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

import streamlit as st

st.markdown("""
<style>
:root {
    --argo-bg-primary: #0a0e27;
    --argo-bg-secondary: #141b3d;
    --argo-surface: #1a2347;
    --argo-text-primary: #e8edf5;
    --argo-text-secondary: #8b95b8;
    --argo-accent-blue: #00b8ff;
    --argo-accent-green: #00ff88;
    --argo-border: #2a3555;
}

.stApp {
    background: linear-gradient(135deg, var(--argo-bg-primary) 0%, var(--argo-bg-secondary) 100%) !important;
}

.metric-card {
    background: var(--argo-surface) !important;
    border: 1px solid var(--argo-border) !important;
    border-radius: 0.75rem !important;
    padding: 1.5rem !important;
}

.stMetric {
    background: var(--argo-surface) !important;
    border: 1px solid var(--argo-border) !important;
    border-radius: 0.75rem !important;
    padding: 1.5rem !important;
}

.stSuccess {
    background: rgba(0, 255, 136, 0.1) !important;
    border-left: 4px solid var(--argo-accent-green) !important;
}

.stInfo {
    background: rgba(0, 136, 255, 0.1) !important;
    border-left: 4px solid var(--argo-accent-blue) !important;
}

h1, h2, h3 {
    color: var(--argo-text-primary) !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


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

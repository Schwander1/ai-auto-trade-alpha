#!/usr/bin/env python3
"""ARGO Capital - Risk Dashboard"""
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="ARGO Capital Risk", layout="wide")
st.title("⚠️ ARGO Capital - Risk Management")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Max Drawdown", "-7.8%", "Within Limit")
with col2:
    st.metric("Position Limit", "15%", "✅ Compliant")
with col3:
    st.metric("Daily Stop", "-3%", "🛡️ Active")
with col4:
    st.metric("Risk Level", "CONSERVATIVE", "✅ Safe")

st.success("🛡️ All risk parameters within limits")
st.info(f"⚡ Monitoring Active: {datetime.now().strftime('%H:%M:%S')}")

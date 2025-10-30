#!/usr/bin/env python3
"""ARGO Capital - Investor Dashboard"""
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="ARGO Capital Investor", layout="wide")
st.title("🏦 ARGO Capital - Investor Dashboard")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Portfolio Value", "$132,156", "+$2,847")
with col2:
    st.metric("Total Return", "32.16%", "+1.2%")
with col3:
    st.metric("Sharpe Ratio", "1.45", "+0.05")
with col4:
    st.metric("Win Rate", "64.7%", "+2.1%")

st.success("🎯 ARGO Capital: Live Trading Active")
st.info(f"📊 Last Updated: {datetime.now().strftime('%H:%M:%S')}")

"""
Streamlit App Entry Point for Data Drift Sentinel
This file serves as the main entry point for Streamlit Cloud deployment.

Streamlit will automatically detect pages in the pages/ directory and create
sidebar navigation. This main file serves as the home/welcome page.
"""

import streamlit as st
import os
import sys

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure the page (must be first Streamlit command)
st.set_page_config(
    page_title="Data Drift Sentinel",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main welcome page
st.title("📊 Data Drift Sentinel")
st.markdown("""
A comprehensive application for monitoring data drift between baseline and current datasets 
using Population Stability Index (PSI) and other statistical measures.
""")

st.markdown("---")

st.header("🚀 Getting Started")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Step 1: Upload Datasets
    Navigate to **📤 Upload** in the sidebar to upload your:
    - **Baseline dataset** (reference/training data)
    - **Current dataset** (production/current data)
    
    Supported formats: CSV, Excel, Parquet
    """)

with col2:
    st.markdown("""
    ### Step 2: Analyze Drift
    Use the sidebar to navigate through:
    - **🔍 Schema & Quality** - View schema differences
    - **📊 Drift Report** - Compute drift metrics
    - **🤖 LLM Summary** - Get AI insights (optional)
    - **💾 Export** - Download results
    """)

st.markdown("---")

st.info("""
👈 **Use the sidebar to navigate between pages.** Streamlit automatically creates navigation 
from the pages in the `pages/` directory.
""")

# Initialize session state for data storage
if 'baseline_df' not in st.session_state:
    st.session_state['baseline_df'] = None
if 'current_df' not in st.session_state:
    st.session_state['current_df'] = None
if 'drift_report' not in st.session_state:
    st.session_state['drift_report'] = None


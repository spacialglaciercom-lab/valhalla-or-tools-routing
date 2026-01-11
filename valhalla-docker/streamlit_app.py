"""
Streamlit Web Interface for Valhalla + OR-tools Routing System
"""

import streamlit as st
import requests
import json
import time
from typing import List, Dict, Optional
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Routing System - VRP & Trash Routes",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API endpoints
VALHALLA_URL = "http://localhost:8002"
OR_TOOLS_URL = "http://localhost:5000"
TRASH_API_URL = "http://localhost:8003"

# Initialize session state
if 'vrp_result' not in st.session_state:
    st.session_state.vrp_result = None
if 'trash_route_job_id' not in st.session_state:
    st.session_state.trash_route_job_id = None


def check_service_health(url: str, service_name: str) -> bool:
    """Check if a service is healthy"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_service_status() -> Dict[str, bool]:
    """Get status of all services"""
    return {
        "Valhalla": check_service_health(VALHALLA_URL, "Valhalla"),
        "OR-tools API": check_service_health(OR_TOOLS_URL, "OR-tools"),
        "Trash Route API": check_service_health(TRASH_API_URL, "Trash Route API")
    }


# Sidebar navigation
st.sidebar.title("🗺️ Routing System")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "VRP Solver", "Trash Route Generator"]
)

# Service status in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Service Status")
status = get_service_status()
for service, is_healthy in status.items():
    status_icon = "🟢" if is_healthy else "🔴"
    st.sidebar.markdown(f"{status_icon} {service}")

if not all(status.values()):
    st.sidebar.warning("⚠️ Some services are offline. Start Docker services first.")


# Dashboard Page
if page == "Dashboard":
    st.title("🗺️ Routing System Dashboard")
    st.markdown("Welcome to the Valhalla + OR-tools Routing System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Valhalla Routing")
        if status["Valhalla"]:
            st.success("🟢 Online")
            try:
                valhalla_info = requests.get(f"{VALHALLA_URL}/status", timeout=5).json()
                st.json(valhalla_info)
            except:
                st.info("Status endpoint available")
        else:
            st.error("🔴 Offline")
            st.info("Start with: `docker compose up -d valhalla`")
    
    with col2:
        st.subheader("OR-tools VRP Solver")
        if status["OR-tools API"]:
            st.success("🟢 Online")
            try:
                or_tools_info = requests.get(f"{OR_TOOLS_URL}/", timeout=5).json()
                st.json(or_tools_info)
            except:
                st.info("API endpoint available")
        else:
            st.error("🔴 Offline")
            st.info("Start with: `docker compose up -d or-tools-solver`")
    
    with col3:
        st.subheader("Trash Route API")
        if status["Trash Route API"]:
            st.success("🟢 Online")
            try:
                trash_info = requests.get(f"{TRASH_API_URL}/", timeout=5).json()
                st.json(trash_info)
            except:
                st.info("API endpoint available")
        else:
            st.error("🔴 Offline")
            st.info("Start with: `docker compose up -d trash-route-api`")
    
    st.markdown("---")
    st.subheader("Quick Start")
    st.markdown("""
    1. **Start Services**: Run `docker compose up -d` in the valhalla-docker directory
    2. **VRP Solver**: Use the VRP Solver page to optimize routes for multiple locations
    3. **Trash Routes**: Use the Trash Route Generator to create routes from OSM files
    """)
    
    st.markdown("---")
    st.subheader("Documentation")
    st.markdown("""
    - [Quick Start Guide](QUICK_START.md)
    - [Architecture Documentation](ARCHITECTURE.md)
    - [API Documentation](README.md)
    """)


# VRP Solver Page
elif page == "VRP Solver":
    st.title("🚗 VRP Solver")
    st.markdown("Solve Vehicle Routing Problems with multiple locations")
    st.markdown("---")
    
    if not status["OR-tools API"]:
        st.error("❌ OR-tools API is offline. Please start the service first.")
        st.info("Run: `docker compose up -d or-tools-solver`")
        st.stop()
    
    # Input section
    st.subheader("Input Locations")
    
    # Option 1: Manual input
    input_method = st.radio(
        "Input Method",
        ["Manual Entry", "JSON Upload"],
        horizontal=True
    )
    
    locations = []
    
    if input_method == "Manual Entry":
        num_locations = st.number_input("Number of Locations", min_value=2, max_value=50, value=3)
        
        for i in range(num_locations):
            with st.expander(f"Location {i+1}", expanded=(i == 0)):
                col1, col2, col3 = st.columns([2, 3, 3])
                with col1:
                    loc_id = st.number_input(f"ID", value=i+1, min_value=1, key=f"id_{i}")
                with col2:
                    lat = st.number_input(f"Latitude", value=45.2462012 + i*0.001, format="%.7f", key=f"lat_{i}")
                with col3:
                    lon = st.number_input(f"Longitude", value=-74.2427412 + i*0.001, format="%.7f", key=f"lon_{i}")
                name = st.text_input(f"Name (optional)", value=f"Loc {loc_id}", key=f"name_{i}")
                
                locations.append({
                    "id": int(loc_id),
                    "latitude": float(lat),
                    "longitude": float(lon),
                    "name": name
                })
    
    else:  # JSON Upload
        json_file = st.file_uploader("Upload JSON file", type=['json'])
        if json_file:
            try:
                json_data = json.load(json_file)
                if "locations" in json_data:
                    locations = json_data["locations"]
                    st.success(f"Loaded {len(locations)} locations")
                    st.json(locations)
                else:
                    st.error("JSON file must contain 'locations' array")
            except Exception as e:
                st.error(f"Error reading JSON file: {e}")
    
    # Solver parameters
    st.markdown("---")
    st.subheader("Solver Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        num_vehicles = st.number_input("Number of Vehicles", min_value=1, max_value=10, value=1)
    
    with col2:
        depot_id = st.number_input(
            "Depot ID (starting location)",
            min_value=1,
            max_value=len(locations) if locations else 1,
            value=1
        ) if locations else 1
    
    # Solve button
    st.markdown("---")
    solve_button = st.button("🚀 Solve VRP", type="primary", use_container_width=True)
    
    if solve_button and locations:
        if len(locations) < 2:
            st.error("At least 2 locations are required")
        else:
            with st.spinner("Solving VRP problem..."):
                try:
                    payload = {
                        "locations": locations,
                        "num_vehicles": int(num_vehicles),
                        "depot_id": int(depot_id)
                    }
                    
                    response = requests.post(
                        f"{OR_TOOLS_URL}/api/v1/solve",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.vrp_result = result
                        st.success("✅ Solution found!")
                    else:
                        st.error(f"Error: {response.status_code}")
                        st.code(response.text)
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")
                    st.info("Make sure OR-tools service is running")
    
    # Display results
    if st.session_state.vrp_result:
        result = st.session_state.vrp_result
        st.markdown("---")
        st.subheader("Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Distance", f"{result.get('total_distance_m', 0):,} m")
        with col2:
            st.metric("Number of Routes", result.get('num_routes', 0))
        with col3:
            st.metric("Vehicles Used", result.get('num_vehicles_used', 0))
        
        # Routes table
        if result.get('routes'):
            st.markdown("### Routes")
            for route in result['routes']:
                with st.expander(f"Vehicle {route['vehicle']} - {route['distance_m']:,} m - {len(route['stops'])} stops"):
                    route_df = pd.DataFrame(route['stops'])
                    st.dataframe(route_df[['id', 'name', 'latitude', 'longitude']], use_container_width=True)
            
            # Download results
            st.markdown("---")
            st.subheader("Download Results")
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="📥 Download Results (JSON)",
                data=json_str,
                file_name=f"vrp_solution_{int(time.time())}.json",
                mime="application/json"
            )


# Trash Route Generator Page
elif page == "Trash Route Generator":
    st.title("🗑️ Trash Route Generator")
    st.markdown("Generate optimized trash collection routes from OSM files")
    st.markdown("---")
    
    if not status["Trash Route API"]:
        st.error("❌ Trash Route API is offline. Please start the service first.")
        st.info("Run: `docker compose up -d trash-route-api`")
        st.stop()
    
    # File upload
    st.subheader("Upload OSM File")
    uploaded_file = st.file_uploader(
        "Choose OSM file",
        type=['osm', 'pbf', 'xml'],
        help="Upload OpenStreetMap file in XML or PBF format"
    )
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        st.info(f"Size: {uploaded_file.size / 1024:.2f} KB")
    
    # Generate button
    if uploaded_file:
        st.markdown("---")
        generate_button = st.button("🚀 Generate Route", type="primary", use_container_width=True)
        
        if generate_button:
            with st.spinner("Uploading file and generating route..."):
                try:
                    # Upload file
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    upload_response = requests.post(
                        f"{TRASH_API_URL}/upload",
                        files=files,
                        timeout=60
                    )
                    
                    if upload_response.status_code == 200:
                        upload_result = upload_response.json()
                        job_id = upload_result.get('job_id')
                        st.session_state.trash_route_job_id = job_id
                        st.success(f"✅ File uploaded! Job ID: {job_id}")
                        
                        # Start generation
                        generate_response = requests.post(
                            f"{TRASH_API_URL}/generate",
                            json={"job_id": job_id},
                            timeout=5
                        )
                        
                        if generate_response.status_code == 200:
                            st.info("⏳ Route generation started. Check status below.")
                        else:
                            st.error(f"Error starting generation: {generate_response.status_code}")
                    else:
                        st.error(f"Upload error: {upload_response.status_code}")
                        st.code(upload_response.text)
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")
    
    # Status check
    if st.session_state.trash_route_job_id:
        st.markdown("---")
        st.subheader("Generation Status")
        
        job_id = st.session_state.trash_route_job_id
        
        if st.button("🔄 Check Status"):
            try:
                status_response = requests.get(
                    f"{TRASH_API_URL}/status/{job_id}",
                    timeout=5
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status_state = status_data.get('status', 'unknown')
                    
                    if status_state == 'completed':
                        st.success("✅ Route generation completed!")
                        
                        # Download results
                        st.markdown("### Download Results")
                        
                        download_response = requests.get(
                            f"{TRASH_API_URL}/download/{job_id}",
                            timeout=30
                        )
                        
                        if download_response.status_code == 200:
                            download_data = download_response.json()
                            
                            # Download GPX
                            if 'gpx_file' in download_data:
                                st.download_button(
                                    label="📥 Download GPX File",
                                    data=download_data['gpx_file'],
                                    file_name=f"trash_route_{job_id}.gpx",
                                    mime="application/gpx+xml"
                                )
                            
                            # Download Report
                            if 'report_file' in download_data:
                                st.download_button(
                                    label="📥 Download Report",
                                    data=download_data['report_file'],
                                    file_name=f"trash_route_report_{job_id}.md",
                                    mime="text/markdown"
                                )
                            
                            st.json(download_data)
                    elif status_state == 'processing':
                        st.info("⏳ Route generation in progress...")
                        st.progress(0.5)
                    elif status_state == 'error':
                        st.error("❌ Route generation failed")
                        if 'error' in status_data:
                            st.code(status_data['error'])
                    else:
                        st.info(f"Status: {status_state}")
                        st.json(status_data)
                else:
                    st.error(f"Status check error: {status_response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")

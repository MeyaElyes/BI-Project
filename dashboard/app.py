"""
Energy Data Analytics Dashboard
Visualizes CO2 emissions, electricity production, energy consumption, and oil production data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Energy Data Analytics Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE_URL = "http://localhost:8000/api"

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to fetch data from API
@st.cache_data(ttl=300)
def fetch_data(endpoint):
    """Fetch data from Django REST API"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Handle paginated response
            if isinstance(data, dict) and 'results' in data:
                return pd.DataFrame(data['results'])
            return pd.DataFrame(data)
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return pd.DataFrame()

# Main title
st.markdown('<h1 class="main-header">⚡ Energy Data Analytics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Select Analysis",
    ["🌍 Overview", "💨 CO2 Emissions", "⚡ Electricity Production", 
     "🔋 Energy Consumption", "🛢️ Oil Production"]
)

st.sidebar.markdown("---")
st.sidebar.info("Data source: Django REST API\nPowered by Apache Airflow ETL Pipeline")

# ====================
# OVERVIEW PAGE
# ====================
if page == "🌍 Overview":
    st.header("Global Energy Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch all datasets
    co2_df = fetch_data("co2-emissions")
    elec_df = fetch_data("electricity-production")
    energy_df = fetch_data("energy-prod-cons")
    oil_df = fetch_data("oil-production")
    
    # Display key metrics
    with col1:
        if not co2_df.empty:
            total_records = len(co2_df)
            st.metric("CO2 Records", f"{total_records:,}")
    
    with col2:
        if not elec_df.empty:
            total_records = len(elec_df)
            st.metric("Electricity Records", f"{total_records:,}")
    
    with col3:
        if not energy_df.empty:
            total_records = len(energy_df)
            st.metric("Energy Records", f"{total_records:,}")
    
    with col4:
        if not oil_df.empty:
            total_records = len(oil_df)
            st.metric("Oil Records", f"{total_records:,}")
    
    st.markdown("---")
    
    # Show sample data from each dataset
    tab1, tab2, tab3, tab4 = st.tabs(["CO2 Emissions", "Electricity", "Energy", "Oil"])
    
    with tab1:
        if not co2_df.empty:
            st.dataframe(co2_df.head(10), use_container_width=True)
    
    with tab2:
        if not elec_df.empty:
            st.dataframe(elec_df.head(10), use_container_width=True)
    
    with tab3:
        if not energy_df.empty:
            st.dataframe(energy_df.head(10), use_container_width=True)
    
    with tab4:
        if not oil_df.empty:
            st.dataframe(oil_df.head(10), use_container_width=True)

# ====================
# CO2 EMISSIONS PAGE
# ====================
elif page == "💨 CO2 Emissions":
    st.header("CO2 Emissions Analysis")
    
    df = fetch_data("co2-emissions")
    
    if not df.empty:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            countries = ['All'] + sorted(df['entity'].unique().tolist())
            selected_country = st.selectbox("Select Country", countries)
        
        with col2:
            if 'year' in df.columns:
                years = sorted(df['year'].unique())
                year_range = st.slider("Year Range", 
                                      int(min(years)), 
                                      int(max(years)), 
                                      (int(min(years)), int(max(years))))
        
        # Filter data
        filtered_df = df.copy()
        if selected_country != 'All':
            filtered_df = filtered_df[filtered_df['entity'] == selected_country]
        if 'year' in df.columns:
            filtered_df = filtered_df[(filtered_df['year'] >= year_range[0]) & 
                                     (filtered_df['year'] <= year_range[1])]
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Time series
            if not filtered_df.empty and 'annual_co2_emissions' in filtered_df.columns:
                fig = px.line(filtered_df, 
                             x='year', 
                             y='annual_co2_emissions',
                             color='entity' if selected_country == 'All' else None,
                             title=f"CO2 Emissions Over Time")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top emitters
            if 'annual_co2_emissions' in filtered_df.columns:
                top_emitters = filtered_df.groupby('entity')['annual_co2_emissions'].sum().nlargest(10)
                fig = px.bar(x=top_emitters.values, 
                           y=top_emitters.index,
                           orientation='h',
                           title="Top 10 CO2 Emitters",
                           labels={'x': 'Total Emissions', 'y': 'Country'})
                st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("Detailed Data")
        st.dataframe(filtered_df, use_container_width=True)

# ====================
# ELECTRICITY PRODUCTION PAGE
# ====================
elif page == "⚡ Electricity Production":
    st.header("Electricity Production by Source")
    
    df = fetch_data("electricity-production")
    
    if not df.empty:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            countries = ['All'] + sorted(df['entity'].unique().tolist())
            selected_country = st.selectbox("Select Country", countries)
        
        with col2:
            if 'year' in df.columns:
                years = sorted(df['year'].unique())
                selected_year = st.selectbox("Select Year", sorted(years, reverse=True))
        
        # Filter data
        filtered_df = df.copy()
        if selected_country != 'All':
            filtered_df = filtered_df[filtered_df['entity'] == selected_country]
        
        # Energy source columns
        energy_cols = [col for col in df.columns if 'electricity_from' in col]
        
        if energy_cols:
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Stacked area chart over time
                if selected_country != 'All' and 'year' in df.columns:
                    country_data = df[df['entity'] == selected_country].sort_values('year')
                    fig = go.Figure()
                    
                    for col in energy_cols:
                        clean_name = col.replace('electricity_from_', '').replace('_', ' ').title()
                        fig.add_trace(go.Scatter(
                            x=country_data['year'],
                            y=country_data[col],
                            mode='lines',
                            stackgroup='one',
                            name=clean_name
                        ))
                    
                    fig.update_layout(title=f"Electricity Production Mix - {selected_country}",
                                    xaxis_title="Year",
                                    yaxis_title="TWh")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Pie chart for selected year
                if 'year' in df.columns:
                    year_data = filtered_df[filtered_df['year'] == selected_year]
                    if not year_data.empty:
                        energy_sum = {col.replace('electricity_from_', '').replace('_', ' ').title(): 
                                    year_data[col].sum() for col in energy_cols}
                        energy_sum = {k: v for k, v in energy_sum.items() if v > 0}
                        
                        if energy_sum:
                            fig = px.pie(values=list(energy_sum.values()),
                                       names=list(energy_sum.keys()),
                                       title=f"Energy Mix in {selected_year}")
                            st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("Detailed Data")
        st.dataframe(filtered_df, use_container_width=True)

# ====================
# ENERGY CONSUMPTION PAGE
# ====================
elif page == "🔋 Energy Consumption":
    st.header("Energy Production vs Consumption")
    
    df = fetch_data("energy-prod-cons")
    
    if not df.empty:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            countries = ['All'] + sorted(df['entity'].unique().tolist())
            selected_country = st.selectbox("Select Country", countries)
        
        with col2:
            if 'year' in df.columns:
                years = sorted(df['year'].unique())
                year_range = st.slider("Year Range", 
                                      int(min(years)), 
                                      int(max(years)), 
                                      (int(min(years)), int(max(years))))
        
        # Filter data
        filtered_df = df.copy()
        if selected_country != 'All':
            filtered_df = filtered_df[filtered_df['entity'] == selected_country]
        if 'year' in df.columns:
            filtered_df = filtered_df[(filtered_df['year'] >= year_range[0]) & 
                                     (filtered_df['year'] <= year_range[1])]
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Time series comparison
            if 'consumption_based_energy' in filtered_df.columns and 'production_based_energy' in filtered_df.columns:
                fig = go.Figure()
                
                if selected_country != 'All':
                    fig.add_trace(go.Scatter(x=filtered_df['year'], 
                                           y=filtered_df['consumption_based_energy'],
                                           mode='lines+markers',
                                           name='Consumption'))
                    fig.add_trace(go.Scatter(x=filtered_df['year'], 
                                           y=filtered_df['production_based_energy'],
                                           mode='lines+markers',
                                           name='Production'))
                else:
                    yearly = filtered_df.groupby('year').agg({
                        'consumption_based_energy': 'sum',
                        'production_based_energy': 'sum'
                    }).reset_index()
                    
                    fig.add_trace(go.Scatter(x=yearly['year'], 
                                           y=yearly['consumption_based_energy'],
                                           mode='lines+markers',
                                           name='Consumption'))
                    fig.add_trace(go.Scatter(x=yearly['year'], 
                                           y=yearly['production_based_energy'],
                                           mode='lines+markers',
                                           name='Production'))
                
                fig.update_layout(title="Energy Production vs Consumption",
                                xaxis_title="Year",
                                yaxis_title="Energy")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Energy balance
            if 'consumption_based_energy' in filtered_df.columns and 'production_based_energy' in filtered_df.columns:
                filtered_df['balance'] = filtered_df['production_based_energy'] - filtered_df['consumption_based_energy']
                
                fig = px.bar(filtered_df,
                           x='year',
                           y='balance',
                           color='balance',
                           color_continuous_scale=['red', 'yellow', 'green'],
                           title="Energy Balance (Production - Consumption)")
                st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("Detailed Data")
        st.dataframe(filtered_df, use_container_width=True)

# ====================
# OIL PRODUCTION PAGE
# ====================
elif page == "🛢️ Oil Production":
    st.header("Oil Production Analysis")
    
    df = fetch_data("oil-production")
    
    if not df.empty:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            countries = ['All'] + sorted(df['entity'].unique().tolist())
            selected_country = st.selectbox("Select Country", countries)
        
        with col2:
            if 'year' in df.columns:
                years = sorted(df['year'].unique())
                year_range = st.slider("Year Range", 
                                      int(min(years)), 
                                      int(max(years)), 
                                      (int(min(years)), int(max(years))))
        
        # Filter data
        filtered_df = df.copy()
        if selected_country != 'All':
            filtered_df = filtered_df[filtered_df['entity'] == selected_country]
        if 'year' in df.columns:
            filtered_df = filtered_df[(filtered_df['year'] >= year_range[0]) & 
                                     (filtered_df['year'] <= year_range[1])]
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Time series
            if 'oil_production_twh' in filtered_df.columns:
                fig = px.line(filtered_df,
                            x='year',
                            y='oil_production_twh',
                            color='entity' if selected_country == 'All' else None,
                            title="Oil Production Over Time")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top producers
            if 'oil_production_twh' in filtered_df.columns:
                top_producers = filtered_df.groupby('entity')['oil_production_twh'].sum().nlargest(10)
                fig = px.bar(x=top_producers.values,
                           y=top_producers.index,
                           orientation='h',
                           title="Top 10 Oil Producers",
                           labels={'x': 'Total Production (TWh)', 'y': 'Country'})
                st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("Detailed Data")
        st.dataframe(filtered_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: gray;'>"
    f"Dashboard last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    f"</div>",
    unsafe_allow_html=True
)

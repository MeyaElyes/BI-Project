"""
Italy Energy Analytics Dashboard
Comprehensive analysis of Italy energy data across all sectors
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# Page Configuration
st.set_page_config(
    page_title="Italy Energy Analytics",
    page_icon="🇮🇹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api"
TARGET_COUNTRY = "Italy"

# Professional Color Palette
COLORS = {
    'red': '#FF6B6B',
    'yellow': '#FFE66D',
    'green': '#4ECDC4',
    'blue': '#45B7D1',
    'purple': '#A8DADC',
    'orange': '#F77F00',
    'teal': '#06FFA5',
    'pink': '#FF006E'
}

# Custom CSS - Dark Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    
    .main-header {
        font-size: 4rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF6B6B 0%, #FFE66D 25%, #4ECDC4 50%, #45B7D1 75%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
    }
    
    .country-badge {
        text-align: center;
        font-size: 1.5rem;
        color: #FFE66D;
        margin-bottom: 2rem;
    }
    
    h2 {
        color: #4ECDC4 !important;
        border-bottom: 3px solid #FF6B6B;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    [data-testid="stMetricValue"] {
        color: #4ECDC4;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    [data-testid="stMetricLabel"] {
        color: #95E1D3;
        font-size: 1.2rem;
    }
    
    [data-testid="stMetricDelta"] {
        color: #FFE66D;
    }
    
    hr {
        border: 2px solid #FF6B6B;
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Data Fetching Function
@st.cache_data(ttl=300)
def fetch_data(endpoint):
    """Fetch data from Django REST API"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}/?limit=50000", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                return pd.DataFrame(data['results'])
            return pd.DataFrame(data)
        else:
            st.error(f"API Error: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return pd.DataFrame()

# Main Title
st.markdown('<h1 class="main-header">🇮🇹 ITALY ENERGY ANALYTICS</h1>', unsafe_allow_html=True)
st.markdown('<p class="country-badge">Comprehensive Energy Data Analysis</p>', unsafe_allow_html=True)

# Fetch all datasets for Italy
with st.spinner("🔄 Loading Italy energy data..."):
    co2_df = fetch_data("co2-emissions")
    elec_df = fetch_data("electricity-production")
    energy_df = fetch_data("energy-prod-cons")
    oil_df = fetch_data("oil-production")

# Filter for Italy only
co2_df = co2_df[co2_df['entity'] == TARGET_COUNTRY] if not co2_df.empty else co2_df
elec_df = elec_df[elec_df['entity'] == TARGET_COUNTRY] if not elec_df.empty else elec_df
energy_df = energy_df[energy_df['entity'] == TARGET_COUNTRY] if not energy_df.empty else energy_df
oil_df = oil_df[oil_df['entity'] == TARGET_COUNTRY] if not oil_df.empty else oil_df

# Filter for years >= 1995
if not co2_df.empty and 'year' in co2_df.columns:
    co2_df = co2_df[co2_df['year'] >= 1995]
if not elec_df.empty and 'year' in elec_df.columns:
    elec_df = elec_df[elec_df['year'] >= 1995]
if not energy_df.empty and 'year' in energy_df.columns:
    energy_df = energy_df[energy_df['year'] >= 1995]
if not oil_df.empty and 'year' in oil_df.columns:
    oil_df = oil_df[oil_df['year'] >= 1995]

# ============= KEY METRICS =============
st.markdown("## 📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if not co2_df.empty and 'annual_co2_emissions' in co2_df.columns:
        total_co2 = co2_df['annual_co2_emissions'].sum() / 1e9
        latest_co2 = co2_df.iloc[-1]['annual_co2_emissions'] / 1e9 if len(co2_df) > 0 else 0
        st.metric("🌍 Total CO2", f"{total_co2:.2f}B tons", 
                 delta=f"Latest: {latest_co2:.2f}B")

with col2:
    if not elec_df.empty:
        energy_cols = [col for col in elec_df.columns if 'electricity_from' in col]
        if energy_cols:
            total_elec = sum(elec_df[col].sum() for col in energy_cols) / 1e3
            st.metric("⚡ Electricity", f"{total_elec:.2f}K TWh",
                     delta=f"{len(energy_cols)} sources")

with col3:
    if not energy_df.empty and 'consumption_based_energy' in energy_df.columns:
        total_consumption = energy_df['consumption_based_energy'].sum()
        avg_consumption = energy_df['consumption_based_energy'].mean()
        st.metric("🔋 Consumption", f"{total_consumption:.2f} units",
                 delta=f"Avg: {avg_consumption:.1f}")

with col4:
    if not oil_df.empty and 'oil_production_twh' in oil_df.columns:
        total_oil = oil_df['oil_production_twh'].sum()
        latest_oil = oil_df.iloc[-1]['oil_production_twh'] if len(oil_df) > 0 else 0
        st.metric("🛢️ Oil Production", f"{total_oil:.2f} TWh",
                 delta=f"Latest: {latest_oil:.1f}")

st.markdown("---")

# ============= CO2 EMISSIONS ANALYSIS =============
st.markdown("## 💨 CO2 Emissions Analysis")

if not co2_df.empty and 'annual_co2_emissions' in co2_df.columns and 'year' in co2_df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # CO2 Trend Line
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=co2_df['year'],
            y=co2_df['annual_co2_emissions'] / 1e9,
            mode='lines+markers',
            name='CO2 Emissions',
            line=dict(color=COLORS['red'], width=4),
            marker=dict(size=8, color=COLORS['orange']),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.2)'
        ))
        fig.update_layout(
            title='Italy CO2 Emissions Over Time',
            xaxis=dict(title='Year', showgrid=True, gridcolor='#2d3142'),
            yaxis=dict(title='CO2 Emissions (Billion tons)', showgrid=True, gridcolor='#2d3142'),
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29',
            font=dict(color='#FFFFFF', size=12),
            hovermode='x'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cumulative CO2
        co2_df_sorted = co2_df.sort_values('year')
        co2_df_sorted['cumulative'] = co2_df_sorted['annual_co2_emissions'].cumsum() / 1e9
        
        fig = px.area(co2_df_sorted, x='year', y='cumulative',
                     title='Cumulative CO2 Emissions',
                     labels={'year': 'Year', 'cumulative': 'Cumulative CO2 (Billion tons)'},
                     color_discrete_sequence=[COLORS['pink']])
        fig.update_layout(
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29',
            font=dict(color='#FFFFFF', size=12),
            xaxis=dict(showgrid=True, gridcolor='#2d3142'),
            yaxis=dict(showgrid=True, gridcolor='#2d3142')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Year-over-Year Change
    if len(co2_df) > 1:
        co2_df_sorted = co2_df.sort_values('year')
        co2_df_sorted['yoy_change'] = co2_df_sorted['annual_co2_emissions'].pct_change() * 100
        
        fig = go.Figure()
        colors = [COLORS['green'] if x > 0 else COLORS['red'] for x in co2_df_sorted['yoy_change']]
        fig.add_trace(go.Bar(
            x=co2_df_sorted['year'],
            y=co2_df_sorted['yoy_change'],
            marker_color=colors,
            name='YoY Change'
        ))
        fig.add_hline(y=0, line_dash="dash", line_color=COLORS['yellow'])
        fig.update_layout(
            title='Year-over-Year CO2 Change (%)',
            xaxis=dict(title='Year', showgrid=False),
            yaxis=dict(title='% Change', showgrid=True, gridcolor='#2d3142'),
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29',
            font=dict(color='#FFFFFF', size=12),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============= ELECTRICITY PRODUCTION =============
st.markdown("## ⚡ Electricity Production by Source")

if not elec_df.empty:
    energy_cols = [col for col in elec_df.columns if 'electricity_from' in col]
    
    if energy_cols and 'year' in elec_df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar Chart by Source
            elec_df_sorted = elec_df.sort_values('year')
            
            colors_map = {
                'coal': COLORS['orange'],
                'gas': COLORS['blue'],
                'oil': COLORS['red'],
                'nuclear': COLORS['purple'],
                'hydro': COLORS['teal'],
                'wind': COLORS['green'],
                'solar': COLORS['yellow'],
                'bioenergy': COLORS['pink']
            }
            
            # Aggregate by source
            source_totals = {}
            for col in energy_cols:
                clean_name = col.replace('electricity_from_', '').replace('_', ' ').title()
                source_totals[clean_name] = elec_df_sorted[col].sum()
            
            # Sort by value
            sorted_sources = sorted(source_totals.items(), key=lambda x: x[1], reverse=True)
            sources = [s[0] for s in sorted_sources]
            values = [s[1] for s in sorted_sources]
            
            # Assign colors
            bar_colors = []
            for source in sources:
                source_key = source.lower().split()[0]
                bar_colors.append(colors_map.get(source_key, COLORS['blue']))
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sources,
                y=values,
                marker_color=bar_colors,
                text=[f'{v:.1f}' for v in values],
                textposition='outside',
                hovertemplate='%{x}<br>%{y:.2f} TWh<extra></extra>'
            ))
            
            fig.update_layout(
                title='Italy Energy Production by Source',
                xaxis=dict(title='Energy Source', showgrid=False, tickangle=-45),
                yaxis=dict(title='Total Production (TWh)', showgrid=True, gridcolor='#2d3142'),
                plot_bgcolor='#1a1d29',
                paper_bgcolor='#1a1d29',
                font=dict(color='#FFFFFF', size=12),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Grouped Bar Chart - Latest vs Historical Average
            # Get latest year and calculate historical average
            latest_year = elec_df_sorted['year'].max()
            latest_data = elec_df_sorted[elec_df_sorted['year'] == latest_year].iloc[0]
            
            source_comparison = []
            for col in energy_cols:
                clean_name = col.replace('electricity_from_', '').replace('_', ' ').title()
                latest_val = latest_data[col]
                avg_val = elec_df_sorted[col].mean()
                if latest_val > 0 or avg_val > 0:
                    source_comparison.append({
                        'source': clean_name,
                        'latest': latest_val,
                        'average': avg_val
                    })
            
            # Sort by latest value
            source_comparison.sort(key=lambda x: x['latest'], reverse=True)
            sources = [s['source'] for s in source_comparison]
            latest_vals = [s['latest'] for s in source_comparison]
            avg_vals = [s['average'] for s in source_comparison]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name=f'{latest_year}',
                x=sources,
                y=latest_vals,
                marker_color=COLORS['green'],
                text=[f'{v:.1f}' for v in latest_vals],
                textposition='outside'
            ))
            fig.add_trace(go.Bar(
                name='Historical Avg',
                x=sources,
                y=avg_vals,
                marker_color=COLORS['blue'],
                text=[f'{v:.1f}' for v in avg_vals],
                textposition='outside'
            ))
            
            fig.update_layout(
                title=f'Energy Sources: Latest ({latest_year}) vs Average',
                xaxis=dict(title='Energy Source', showgrid=False, tickangle=-45),
                yaxis=dict(title='Production (TWh)', showgrid=True, gridcolor='#2d3142'),
                plot_bgcolor='#1a1d29',
                paper_bgcolor='#1a1d29',
                font=dict(color='#FFFFFF', size=12),
                barmode='group',
                legend=dict(bgcolor='#0e1117', bordercolor='#4ECDC4', borderwidth=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Pie Chart - Latest Year Distribution
        latest_year = elec_df['year'].max()
        latest_data = elec_df[elec_df['year'] == latest_year].iloc[0]
        
        energy_sum = {}
        for col in energy_cols:
            clean_name = col.replace('electricity_from_', '').replace('_', ' ').title()
            value = latest_data[col]
            if value > 0:
                energy_sum[clean_name] = value
        
        if energy_sum:
            fig = px.pie(
                values=list(energy_sum.values()),
                names=list(energy_sum.keys()),
                title=f'Italy Energy Mix Distribution ({latest_year})',
                color_discrete_sequence=[COLORS['red'], COLORS['orange'], COLORS['yellow'], 
                                        COLORS['green'], COLORS['blue'], COLORS['purple'], 
                                        COLORS['teal'], COLORS['pink']]
            )
            fig.update_layout(
                plot_bgcolor='#1a1d29',
                paper_bgcolor='#1a1d29',
                font=dict(color='#FFFFFF', size=12)
            )
            fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============= ENERGY PRODUCTION VS CONSUMPTION =============
st.markdown("## 🔋 Energy Production vs Consumption")

if not energy_df.empty and 'consumption_based_energy' in energy_df.columns and 'production_based_energy' in energy_df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Dual Line Chart with Fill
        energy_df_sorted = energy_df.sort_values('year')
        
        fig = go.Figure()
        
        # Production with fill
        fig.add_trace(go.Scatter(
            x=energy_df_sorted['year'],
            y=energy_df_sorted['production_based_energy'],
            mode='lines+markers',
            name='Production',
            line=dict(color=COLORS['green'], width=4),
            marker=dict(size=10, symbol='circle'),
            fill='tozeroy',
            fillcolor='rgba(78, 205, 196, 0.2)',
            hovertemplate='Production: %{y:.2f}<extra></extra>'
        ))
        
        # Consumption with fill
        fig.add_trace(go.Scatter(
            x=energy_df_sorted['year'],
            y=energy_df_sorted['consumption_based_energy'],
            mode='lines+markers',
            name='Consumption',
            line=dict(color=COLORS['red'], width=4, dash='dash'),
            marker=dict(size=10, symbol='diamond'),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.2)',
            hovertemplate='Consumption: %{y:.2f}<extra></extra>'
        ))
        
        # Add annotations for latest values
        latest = energy_df_sorted.iloc[-1]
        fig.add_annotation(
            x=latest['year'],
            y=latest['production_based_energy'],
            text=f"Production<br>{latest['production_based_energy']:.1f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor=COLORS['green'],
            bgcolor=COLORS['green'],
            font=dict(color='#FFFFFF', size=10)
        )
        fig.add_annotation(
            x=latest['year'],
            y=latest['consumption_based_energy'],
            text=f"Consumption<br>{latest['consumption_based_energy']:.1f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor=COLORS['red'],
            bgcolor=COLORS['red'],
            font=dict(color='#FFFFFF', size=10)
        )
        
        fig.update_layout(
            title='Italy Energy: Production vs Consumption (Clear View)',
            xaxis=dict(title='Year', showgrid=True, gridcolor='#2d3142'),
            yaxis=dict(title='Energy (units)', showgrid=True, gridcolor='#2d3142'),
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29',
            font=dict(color='#FFFFFF', size=12),
            hovermode='x unified',
            legend=dict(bgcolor='#0e1117', bordercolor='#4ECDC4', borderwidth=1, x=0.02, y=0.98)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Energy Balance
        energy_df_sorted['balance'] = energy_df_sorted['production_based_energy'] - energy_df_sorted['consumption_based_energy']
        
        colors = [COLORS['green'] if x >= 0 else COLORS['red'] for x in energy_df_sorted['balance']]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=energy_df_sorted['year'],
            y=energy_df_sorted['balance'],
            marker_color=colors,
            name='Energy Balance'
        ))
        fig.add_hline(y=0, line_dash="dash", line_color=COLORS['yellow'], 
                     annotation_text="Break-even", annotation_position="right")
        
        fig.update_layout(
            title='Italy Energy Balance (Production - Consumption)',
            xaxis=dict(title='Year', showgrid=False),
            yaxis=dict(title='Energy Balance', showgrid=True, gridcolor='#2d3142'),
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29',
            font=dict(color='#FFFFFF', size=12),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Balance Percentage
    energy_df_sorted['balance_pct'] = (energy_df_sorted['balance'] / energy_df_sorted['consumption_based_energy'].replace(0, 1)) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=energy_df_sorted['year'],
        y=energy_df_sorted['balance_pct'],
        mode='lines+markers',
        name='Balance %',
        line=dict(color=COLORS['blue'], width=4),
        marker=dict(size=10, color=COLORS['teal']),
        fill='tozeroy',
        fillcolor='rgba(69, 183, 209, 0.2)'
    ))
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS['red'])
    
    fig.update_layout(
        title='Italy Energy Self-Sufficiency (%)',
        xaxis=dict(title='Year', showgrid=True, gridcolor='#2d3142'),
        yaxis=dict(title='Balance Percentage (%)', showgrid=True, gridcolor='#2d3142'),
        plot_bgcolor='#1a1d29',
        paper_bgcolor='#1a1d29',
        font=dict(color='#FFFFFF', size=12)
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============= OIL PRODUCTION =============
st.markdown("## 🛢️ Oil Production Analysis")

if not oil_df.empty and 'oil_production_twh' in oil_df.columns and 'year' in oil_df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Oil Production Trend
        oil_df_sorted = oil_df.sort_values('year')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=oil_df_sorted['year'],
            y=oil_df_sorted['oil_production_twh'],
            mode='lines+markers',
            name='Oil Production',
            line=dict(color=COLORS['orange'], width=4),
            marker=dict(size=8, color=COLORS['yellow']),
            fill='tozeroy',
            fillcolor='rgba(247, 127, 0, 0.2)'
        ))
        
        fig.update_layout(
            title='Italy Oil Production Over Time',
            xaxis=dict(title='Year', showgrid=True, gridcolor='#2d3142'),
            yaxis=dict(title='Oil Production (TWh)', showgrid=True, gridcolor='#2d3142'),
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29',
            font=dict(color='#FFFFFF', size=12)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Moving Average
        oil_df_sorted['ma_5yr'] = oil_df_sorted['oil_production_twh'].rolling(window=5, min_periods=1).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=oil_df_sorted['year'],
            y=oil_df_sorted['oil_production_twh'],
            mode='markers',
            name='Actual',
            marker=dict(size=8, color=COLORS['red'])
        ))
        fig.add_trace(go.Scatter(
            x=oil_df_sorted['year'],
            y=oil_df_sorted['ma_5yr'],
            mode='lines',
            name='5-Year Moving Avg',
            line=dict(color=COLORS['green'], width=4)
        ))
        
        fig.update_layout(
            title='Oil Production with 5-Year Moving Average',
            xaxis=dict(title='Year', showgrid=True, gridcolor='#2d3142'),
            yaxis=dict(title='Oil Production (TWh)', showgrid=True, gridcolor='#2d3142'),
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29',
            font=dict(color='#FFFFFF', size=12),
            legend=dict(bgcolor='#0e1117', bordercolor='#4ECDC4', borderwidth=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Year-over-Year Growth
    if len(oil_df_sorted) > 1:
        oil_df_sorted['yoy_change'] = oil_df_sorted['oil_production_twh'].pct_change() * 100
        
        colors = [COLORS['green'] if x >= 0 else COLORS['red'] for x in oil_df_sorted['yoy_change'].fillna(0)]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=oil_df_sorted['year'],
            y=oil_df_sorted['yoy_change'],
            marker_color=colors,
            name='YoY Growth'
        ))
        fig.add_hline(y=0, line_dash="dash", line_color=COLORS['yellow'])
        
        fig.update_layout(
            title='Oil Production Year-over-Year Growth (%)',
            xaxis=dict(title='Year', showgrid=False),
            yaxis=dict(title='Growth Rate (%)', showgrid=True, gridcolor='#2d3142'),
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29',
            font=dict(color='#FFFFFF', size=12),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

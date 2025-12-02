# Energy Data Dashboard

Interactive dashboard built with Streamlit for visualizing energy data.

## Features

- 🌍 **Overview**: Global energy statistics at a glance
- 💨 **CO2 Emissions**: Track emissions by country over time
- ⚡ **Electricity Production**: Analyze electricity generation by source (coal, gas, nuclear, solar, wind, hydro, etc.)
- 🔋 **Energy Consumption**: Compare energy production vs consumption
- 🛢️ **Oil Production**: Monitor oil production trends

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure the Django API is running at http://localhost:8000

3. Run the dashboard:
```bash
streamlit run app.py
```

The dashboard will open in your browser at http://localhost:8501

## Data Source

All data is fetched from the Django REST API endpoints:
- `/api/co2-emissions/`
- `/api/electricity-production/`
- `/api/energy-prod-cons/`
- `/api/oil-production/`

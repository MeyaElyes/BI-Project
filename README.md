# Energy Data ETL Pipeline

Automated pipeline for processing energy and environmental datasets using **Airflow**, **PostgreSQL**, and **Django REST API**.

---

## 📦 What's Included

- **Airflow ETL Pipeline** - Processes 4 energy datasets (CO2, electricity, oil, energy production/consumption)
- **PostgreSQL Database** - Stores cleaned data
- **Django REST API** - Provides HTTP endpoints to access data
- **pgAdmin** - Web UI for database management

---

## 🚀 Quick Start

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Access Applications
- **Airflow**: http://localhost:8090 (username: `airflow`, password: `airflow`)
- **Django API**: http://localhost:8000/api/
- **pgAdmin**: http://localhost:5050 (email: `admin@admin.com`, password: `admin`)

### 3. Run the ETL Pipeline
In Airflow UI:
1. Go to http://localhost:8090
2. Login with `airflow` / `airflow`
3. Find `energy_data_etl_pipeline` DAG
4. Click the ▶️ play button to trigger it
5. Wait ~1-2 minutes for completion

### 4. View Data
Once the pipeline completes:
- **Via API**: http://localhost:8000/api/co2-emissions/
- **Via pgAdmin**: Connect to PostgreSQL and view tables in `public` schema

---

## 📊 Data Sources

| Dataset | Records | Description |
|---------|---------|-------------|
| CO2 Emissions | 29,384 | Annual CO2 emissions by country |
| Electricity Production | 6,917 | Electricity generation by source |
| Energy Prod/Cons | 1,113 | Energy production vs consumption |
| Oil Production | 750 | Oil production by country |

---

## 🗂️ Project Structure

```
├── backend/              # Django REST API
│   ├── api/             # API app (models, views, serializers)
│   ├── config/          # Django settings
│   └── requirements.txt
├── dags/                # Airflow DAGs
│   ├── data/           # CSV source files
│   └── energy_etl_dag.py
├── config/              # Airflow configuration
├── docker-compose.yaml  # Docker services setup
└── README.md
```

---

## 🔧 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/co2-emissions/` | CO2 emissions data |
| `/api/electricity-production/` | Electricity production data |
| `/api/energy-prod-cons/` | Energy production/consumption |
| `/api/oil-production/` | Oil production data |

**Query Parameters:**
- `entity` - Filter by country name
- `code` - Filter by country code  
- `year`, `year_min`, `year_max` - Filter by year
- `page` - Pagination (100 per page)

**Example:**
```bash
curl "http://localhost:8000/api/co2-emissions/?entity=France&year=2020"
```

---

## 🛠️ Development Setup (Django)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🔄 How It Works

1. **Airflow** reads CSV files from `dags/data/`
2. **Cleans & transforms** the data (removes duplicates, standardizes columns, validates years)
3. **Loads** cleaned data into PostgreSQL tables
4. **Django API** serves the data via REST endpoints
5. **pgAdmin** provides database management interface

---

## 🐛 Troubleshooting

**Pipeline not running?**
```bash
# Restart Airflow scheduler
docker restart bi_final-main-airflow-scheduler-1
```

**No tables in database?**
- Trigger the DAG manually in Airflow UI
- Check logs in Airflow for errors

**Django API errors?**
- Ensure the Airflow pipeline has completed successfully
- Tables must exist in PostgreSQL before API works

---

## 📝 Notes

- Pipeline runs daily by default (configured in DAG)
- Data is stored in PostgreSQL container (persists via Docker volume)
- Django uses read-only database access

## ✅ Prerequisites

- **Docker Desktop** (with Docker Compose)
- **Git** (to clone the repository)
- At least **4GB RAM** available for Docker containers
- **Ports available:** 8080 (Airflow), 5432 (PostgreSQL), 5050 (pgAdmin)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd airflow
```

### 2. Start All Services
```bash
docker-compose up -d
```

This will start:
- Airflow Webserver (port 8080)
- Airflow Scheduler
- Airflow Worker (CeleryExecutor)
- PostgreSQL Database (port 5432)
- Redis (message broker)
- pgAdmin (port 5050)

### 3. Wait for Services to Initialize
```bash
# Check if all containers are healthy (wait ~30-60 seconds)
docker ps
```

All containers should show status as "Up" or "healthy".

### 4. Create Airflow Connection to PostgreSQL

**Option A: Using Docker Exec (Recommended)**
```bash
docker exec airflow-airflow-scheduler-1 airflow connections add 'postgres_energy_data' \
  --conn-type 'postgres' \
  --conn-host 'postgres' \
  --conn-schema 'airflow' \
  --conn-login 'airflow' \
  --conn-password 'airflow' \
  --conn-port 5432
```

**Option B: Using Airflow UI**
1. Go to http://localhost:8080
2. Login: `airflow` / `airflow`
3. Navigate to Admin → Connections
4. Click + (Add Connection)
5. Fill in:
   - Connection Id: `postgres_energy_data`
   - Connection Type: `Postgres`
   - Host: `postgres`
   - Schema: `airflow`
   - Login: `airflow`
   - Password: `airflow`
   - Port: `5432`

### 5. Trigger the DAG

**Option A: Using CLI**
```bash
docker exec airflow-airflow-scheduler-1 airflow dags trigger energy_data_etl_pipeline
```

**Option B: Using Airflow UI**
1. Go to http://localhost:8080
2. Find `energy_data_etl_pipeline` in the DAGs list
3. Click the ▶️ (Play) button on the right

### 6. Verify Data in pgAdmin

1. Open http://localhost:5050
2. Login with:
   - Email: `admin@admin.com`
   - Password: `admin`

3. Add PostgreSQL Server:
   - Right-click **Servers** → Register → Server
   - **General Tab:**
     - Name: `Airflow PostgreSQL`
   - **Connection Tab:**
     - Host: `postgres` ⚠️ (NOT localhost!)
     - Port: `5432`
     - Maintenance database: `airflow`
     - Username: `airflow`
     - Password: `airflow`
     - ✅ Save password

4. View Tables:
   - Navigate: Servers → Airflow PostgreSQL → Databases → airflow → Schemas → public → Tables
   - You should see:
     - `cleaned_co2_emissions`
     - `cleaned_electricity_production`
     - `cleaned_energy_prod_cons`
     - `cleaned_oil_production`

5. Query Data:
   - Right-click any table → View/Edit Data → First 100 Rows

## 📊 Data Sources

All CSV files are located in `dags/data/`:

| File | Records | Description |
|------|---------|-------------|
| `annual-co2-emissions-per-country.csv` | ~29K | Annual CO2 emissions by country |
| `electricity-prod-source-stacked.csv` | ~7K | Electricity production by source |
| `production-vs-consumption-energy.csv` | ~1K | Energy production vs consumption |
| `oil-production-by-country.csv` | ~750 | Oil production by country |

Each dataset includes a `.metadata.json` file with schema information.

## 🔐 Accessing the System

### Airflow Web UI
- **URL:** http://localhost:8080
- **Username:** `airflow`
- **Password:** `airflow`

### pgAdmin (Database Management)
- **URL:** http://localhost:5050
- **Email:** `admin@admin.com`
- **Password:** `admin`

### PostgreSQL Database (Direct)
- **Host:** `localhost` (external) or `postgres` (inside Docker)
- **Port:** `5432`
- **Database:** `airflow`
- **Username:** `airflow`
- **Password:** `airflow`

**Connect via psql:**
```bash
docker exec -it airflow-postgres-1 psql -U airflow -d airflow
```

**Example queries:**
```sql
-- Count records in each table
SELECT 'cleaned_co2_emissions' as table_name, COUNT(*) FROM cleaned_co2_emissions
UNION ALL
SELECT 'cleaned_electricity_production', COUNT(*) FROM cleaned_electricity_production
UNION ALL
SELECT 'cleaned_energy_prod_cons', COUNT(*) FROM cleaned_energy_prod_cons
UNION ALL
SELECT 'cleaned_oil_production', COUNT(*) FROM cleaned_oil_production;

-- View latest CO2 emissions
SELECT entity, code, year, annual_co2_emissions 
FROM cleaned_co2_emissions 
WHERE entity_type = 'country' AND year >= 2020 
ORDER BY year DESC, annual_co2_emissions DESC 
LIMIT 10;
```

## 🛠️ Troubleshooting

### DAG Not Showing Up
```bash
# Restart scheduler to reload DAGs
docker restart airflow-airflow-scheduler-1

# Check DAG list
docker exec airflow-airflow-scheduler-1 airflow dags list | grep energy
```

### DAG Failing
```bash
# View task logs in Airflow UI
# Or check via CLI:
docker exec airflow-airflow-scheduler-1 airflow tasks test energy_data_etl_pipeline load_data 2025-11-19
```

### No Tables in PostgreSQL
1. Verify DAG ran successfully (green status in UI)
2. Check connection exists:
   ```bash
   docker exec airflow-airflow-scheduler-1 airflow connections list | grep postgres
   ```
3. Check if data files exist:
   ```bash
   docker exec airflow-airflow-worker-1 ls -l /opt/airflow/dags/data/
   ```

### pgAdmin Can't Connect to PostgreSQL
- ⚠️ **Use hostname `postgres` NOT `localhost`**
- pgAdmin runs inside Docker, so it must use Docker's internal network
- Verify postgres container is running: `docker ps | grep postgres`

### Port Already in Use
If ports are occupied, modify `docker-compose.yaml`:
```yaml
# Change these ports to available ones
ports:
  - "8081:8080"  # Airflow (change 8080 → 8081)
  - "5433:5432"  # PostgreSQL (change 5432 → 5433)
  - "5051:80"    # pgAdmin (change 5050 → 5051)
```

### Reset Everything
```bash
# Stop and remove all containers + volumes
docker-compose down -v

# Start fresh
docker-compose up -d

# Re-create the Airflow connection (see Quick Start step 4)
```

## 📁 Project Structure

```
airflow/
├── dags/
│   ├── energy_etl_dag.py          # Main ETL DAG definition
│   └── data/                       # CSV and metadata files
│       ├── annual-co2-emissions-per-country.csv
│       ├── electricity-prod-source-stacked.csv
│       ├── production-vs-consumption-energy.csv
│       └── oil-production-by-country.csv
├── docker-compose.yaml             # Docker services configuration
├── config/
│   └── airflow.cfg                 # Airflow configuration
├── logs/                           # Airflow execution logs
├── plugins/                        # Custom Airflow plugins
└── README.md                       # This file
```

## 🔄 DAG Schedule

The ETL pipeline runs **daily at midnight** by default.

To change the schedule, edit `dags/energy_etl_dag.py`:
```python
dag = DAG(
    'energy_data_etl_pipeline',
    schedule='@daily',  # Options: '@hourly', '@weekly', '@monthly', None
    ...
)
```

After changing, restart the scheduler:
```bash
docker restart airflow-airflow-scheduler-1
```

## 📈 Monitoring

### Check DAG Status
```bash
# List recent runs
docker exec airflow-airflow-scheduler-1 airflow dags list-runs energy_data_etl_pipeline

# View task instance details
docker exec airflow-airflow-scheduler-1 airflow tasks list energy_data_etl_pipeline
```

### View Logs
- **Web UI:** Click on a task → View Log
- **CLI:** `docker logs airflow-airflow-worker-1`

## 🛑 Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove data volumes (⚠️ deletes database)
docker-compose down -v
```

## 📝 Notes

- First run may take 2-3 minutes to process all datasets
- Data is cleaned automatically (duplicates removed, years validated, columns standardized)
- PostgreSQL data persists in Docker volume `airflow_postgres-db-volume`
- All metadata columns added: `data_source`, `data_quality_flag`, `last_updated`, `entity_type`

## 🆘 Support

For issues or questions:
1. Check logs: `docker logs <container-name>`
2. View Airflow task logs in Web UI
3. Verify all containers are healthy: `docker ps`

---

**Built with Apache Airflow 3.x, PostgreSQL 16, and pgAdmin 4**
#   B I _ f i n a l 
 
 #   B I _ f i n a l 
 
 #   B I _ f i n a l 
 
 

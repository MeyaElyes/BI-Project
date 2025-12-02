# Django Backend - Energy Data BI

Simple Django REST API providing read-only access to energy data from PostgreSQL.

## Quick Start

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows | source venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**API:** http://localhost:8000/api/

## Configuration

Edit `.env` to connect to PostgreSQL (defaults work with Airflow setup):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=airflow
DB_USER=airflow
DB_PASSWORD=airflow
```

## API Endpoints

| Endpoint                       | Description                   | Records |
| ------------------------------ | ----------------------------- | ------- |
| `/api/co2-emissions/`          | CO2 emissions by country      | ~29K    |
| `/api/electricity-production/` | Electricity by source         | ~7K     |
| `/api/energy-prod-cons/`       | Energy production/consumption | ~1K     |
| `/api/oil-production/`         | Oil production                | ~750    |

### Query Parameters

- `entity` - Filter by country name
- `code` - Filter by country code
- `year`, `year_min`, `year_max` - Filter by year
- `entity_type` - `country` or `aggregate`
- `page` - Pagination (100 per page)

### Examples

```bash
# List data
curl http://localhost:8000/api/co2-emissions/

# Filter
curl "http://localhost:8000/api/co2-emissions/?entity=France&year=2020"

# Statistics
curl http://localhost:8000/api/co2-emissions/summary/
```

## Frontend Integration

**JavaScript:**

```javascript
const response = await fetch(
  "http://localhost:8000/api/co2-emissions/?entity=France"
);
const data = await response.json();
```

**Python:**

```python
import requests
r = requests.get('http://localhost:8000/api/co2-emissions/', params={'entity': 'France'})
```

## Admin Panel

```bash
python manage.py createsuperuser  # Create admin user
```

Visit: http://localhost:8000/admin

## Notes

- Read-only API (GET requests only)
- Models use `managed=False` (Django doesn't control schema)
- Data populated by Airflow ETL pipeline
- All endpoints support pagination, filtering, and search

## Troubleshooting

**Database connection error?** Ensure PostgreSQL is running: `docker ps | grep postgres`

**No data?** Run Airflow ETL first to populate tables

---

**Stack:** Django 5.0, DRF 3.14, PostgreSQL

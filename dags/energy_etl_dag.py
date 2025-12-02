"""
Airflow DAG for ETL Pipeline - Energy & Environmental Data
Cleans data and loads to PostgreSQL database
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import numpy as np
import json
from pathlib import Path

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 11, 19),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Initialize DAG
dag = DAG(
    'energy_data_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for energy and environmental datasets',
    schedule='@daily',  # Run daily, change as needed: '@hourly', '@weekly', '@monthly', None
    catchup=False,
    tags=['etl', 'energy', 'postgres'],
)

# Data directory - update this path to where your CSV files are located
DATA_DIR = Path('/opt/airflow/dags/data')  # Update this path


def load_data_and_metadata(**context):
    """Load all CSV files and their corresponding JSON metadata"""
    
    datasets = {
        'co2_emissions': {
            'csv': 'annual-co2-emissions-per-country.csv',
            'metadata': 'annual-co2-emissions-per-country.metadata.json'
        },
        'electricity_production': {
            'csv': 'electricity-prod-source-stacked.csv',
            'metadata': 'electricity-prod-source-stacked.metadata.json'
        },
        'oil_production': {
            'csv': 'oil-production-by-country.csv',
            'metadata': 'oil-production-by-country.metadata.json'
        },
        'energy_prod_cons': {
            'csv': 'production-vs-consumption-energy.csv',
            'metadata': 'production-vs-consumption-energy.metadata.json'
        }
    }
    
    loaded_data = {}
    
    for key, files in datasets.items():
        try:
            csv_path = DATA_DIR / files['csv']
            df = pd.read_csv(csv_path)
            print(f"✓ Loaded {key}: {len(df)} rows, {len(df.columns)} columns")
            
            metadata = None
            if files['metadata']:
                metadata_path = DATA_DIR / files['metadata']
                if metadata_path.exists():
                    with open(metadata_path, 'r', encoding='utf-8-sig') as f:
                        metadata = json.load(f)
                    print(f"✓ Metadata loaded for {key}")
            
            loaded_data[key] = {
                'data': df,
                'metadata': metadata,
                'filename': files['csv']
            }
            
        except Exception as e:
            print(f"✗ Error loading {key}: {e}")
            raise
    
    # Push to XCom for next task
    context['ti'].xcom_push(key='loaded_data_keys', value=list(loaded_data.keys()))
    
    # Save to temporary files for passing between tasks
    for key, dataset in loaded_data.items():
        dataset['data'].to_parquet(f'/tmp/{key}.parquet', index=False)
    
    return f"Loaded {len(loaded_data)} datasets"


def clean_and_transform_data(**context):
    """Clean and transform all datasets"""
    
    # Retrieve dataset keys from previous task
    dataset_keys = context['ti'].xcom_pull(key='loaded_data_keys', task_ids='load_data')
    
    cleaned_datasets = []
    
    for key in dataset_keys:
        print(f"\n{'='*60}")
        print(f"Cleaning: {key}")
        print(f"{'='*60}")
        
        # Load from temporary parquet
        df = pd.read_parquet(f'/tmp/{key}.parquet')
        original_rows = len(df)
        
        # Standardize column names
        df.columns = [
            col.lower()
            .replace('₂', '2')
            .replace('(', '').replace(')', '')
            .replace(' - ', '_')
            .replace(' ', '_')
            .replace('-', '_')
            .replace('__', '_')
            .strip('_')
            for col in df.columns
        ]
        
        # Handle missing codes
        if 'code' in df.columns:
            df['code'] = df['code'].replace('', np.nan)
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Validate years if present
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
            df = df[(df['year'] >= 1750) & (df['year'] <= 2025)]
        
        # Add metadata columns
        df['data_source'] = key
        df['data_quality_flag'] = 'clean'
        df['last_updated'] = datetime.now().date()
        
        # Add entity type classification
        if 'entity' in df.columns:
            aggregates = ['World', 'Africa', 'Asia', 'Europe', 'OECD', 'EU', 'ASEAN']
            df['entity_type'] = df['entity'].apply(
                lambda x: 'aggregate' if any(agg in str(x) for agg in aggregates) else 'country'
            )
        
        # Save cleaned data to temp
        df.to_parquet(f'/tmp/{key}_cleaned.parquet', index=False)
        
        cleaned_datasets.append({
            'dataset': key,
            'original_rows': original_rows,
            'cleaned_rows': len(df),
            'removed_rows': original_rows - len(df)
        })
        
        print(f"✓ Cleaned {key}: {len(df)} rows (removed {original_rows - len(df)})")
    
    # Push summary to XCom
    context['ti'].xcom_push(key='cleaning_summary', value=cleaned_datasets)
    context['ti'].xcom_push(key='cleaned_dataset_keys', value=dataset_keys)
    
    return f"Cleaned {len(cleaned_datasets)} datasets"


def load_to_postgres(**context):
    """Load cleaned data into PostgreSQL database"""
    
    # Get PostgreSQL connection
    # First try custom connection, then default, then direct connection
    from sqlalchemy import create_engine
    
    try:
        # Try to use Airflow connection
        postgres_hook = PostgresHook(postgres_conn_id='postgres_energy_data')
        engine = postgres_hook.get_sqlalchemy_engine()
        print("✓ Using Airflow connection: postgres_energy_data")
    except:
        try:
            # Fallback to default postgres connection
            postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
            engine = postgres_hook.get_sqlalchemy_engine()
            print("✓ Using Airflow connection: postgres_default")
        except:
            # Direct connection as last resort
            engine = create_engine('postgresql+psycopg2://airflow:airflow@postgres:5432/airflow')
            print("✓ Using direct connection to postgres:5432/airflow")
    
    # Retrieve cleaned dataset keys
    dataset_keys = context['ti'].xcom_pull(key='cleaned_dataset_keys', task_ids='clean_transform')
    
    load_summary = []
    
    for key in dataset_keys:
        table_name = f"cleaned_{key}"
        
        print(f"\nLoading: {key} -> {table_name}")
        
        try:
            # Load cleaned data from temp
            df = pd.read_parquet(f'/tmp/{key}_cleaned.parquet')
            
            # Add auto-incrementing id column for Django
            df.insert(0, 'id', range(1, len(df) + 1))
            
            print(f"  Rows: {len(df):,}")
            print(f"  Columns: {len(df.columns)}")
            
            # Load to PostgreSQL
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=1000
            )
            
            # Verify load
            result = pd.read_sql(f"SELECT COUNT(*) as count FROM {table_name}", engine)
            loaded_rows = result['count'][0]
            
            print(f"  ✓ Loaded {loaded_rows:,} rows to table '{table_name}'")
            
            load_summary.append({
                'dataset': key,
                'table_name': table_name,
                'rows_loaded': loaded_rows,
                'status': 'success'
            })
            
        except Exception as e:
            print(f"  ✗ Error loading {key}: {e}")
            load_summary.append({
                'dataset': key,
                'table_name': table_name,
                'error': str(e),
                'status': 'failed'
            })
            raise
    
    # Push summary to XCom
    context['ti'].xcom_push(key='load_summary', value=load_summary)
    
    engine.dispose()
    
    return f"Loaded {len(load_summary)} datasets to PostgreSQL"


def generate_report(**context):
    """Generate summary report of ETL execution"""
    
    cleaning_summary = context['ti'].xcom_pull(key='cleaning_summary', task_ids='clean_transform')
    load_summary = context['ti'].xcom_pull(key='load_summary', task_ids='load_postgres')
    
    report = {
        'execution_date': context['execution_date'].isoformat(),
        'dag_id': context['dag'].dag_id,
        'run_id': context['run_id'],
        'cleaning_summary': cleaning_summary,
        'load_summary': load_summary,
        'total_datasets': len(cleaning_summary),
        'successful_loads': len([s for s in load_summary if s['status'] == 'success']),
        'failed_loads': len([s for s in load_summary if s['status'] == 'failed'])
    }
    
    print("\n" + "="*80)
    print("ETL PIPELINE EXECUTION REPORT")
    print("="*80)
    print(f"\nExecution Date: {report['execution_date']}")
    print(f"Run ID: {report['run_id']}")
    print(f"\nDatasets Processed: {report['total_datasets']}")
    print(f"Successful Loads: {report['successful_loads']}")
    print(f"Failed Loads: {report['failed_loads']}")
    
    print("\n" + "-"*80)
    print("DATASET DETAILS")
    print("-"*80)
    
    for i, summary in enumerate(cleaning_summary, 1):
        load_info = next((l for l in load_summary if l['dataset'] == summary['dataset']), None)
        status = load_info['status'] if load_info else 'unknown'
        
        print(f"\n{i}. {summary['dataset'].upper()}")
        print(f"   Original Rows: {summary['original_rows']:,}")
        print(f"   Cleaned Rows:  {summary['cleaned_rows']:,}")
        print(f"   Removed Rows:  {summary['removed_rows']:,}")
        print(f"   Load Status:   {'✓' if status == 'success' else '✗'} {status.upper()}")
    
    print("\n" + "="*80)
    
    # Save report to XCom
    context['ti'].xcom_push(key='final_report', value=report)
    
    return "Report generated successfully"


# Define tasks
task_load = PythonOperator(
    task_id='load_data',
    python_callable=load_data_and_metadata,
    dag=dag,
)

task_clean = PythonOperator(
    task_id='clean_transform',
    python_callable=clean_and_transform_data,
    dag=dag,
)

task_load_db = PythonOperator(
    task_id='load_postgres',
    python_callable=load_to_postgres,
    dag=dag,
)

task_report = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report,
    dag=dag,
)

# Define task dependencies
task_load >> task_clean >> task_load_db >> task_report

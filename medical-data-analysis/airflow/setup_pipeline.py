#!/usr/bin/env python3
"""
Airflow Pipeline Setup Script

This script configures and initializes the medical data ingestion pipeline 
for use with Apache Airflow, setting up the required directories and components.
"""

import os
import sys
import argparse
import logging
import json
from pathlib import Path
import shutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directory_structure(base_dir: str) -> None:
    """
    Create the directory structure needed for the pipeline.
    
    Args:
        base_dir: Base directory for the pipeline
    """
    # Create main directories
    directories = [
        'dags',
        'input/pdf_documents',
        'input/text_documents',
        'input/html_documents',
        'input/csv_data',
        'processed_data/file_registry',
        'processed_data/reports',
        'processed_data/errors',
        'logs',
        'vectordb',
        'config'
    ]
    
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")

def create_airflow_config(base_dir: str) -> None:
    """
    Create Airflow configuration file.
    
    Args:
        base_dir: Base directory for the pipeline
    """
    config_dir = os.path.join(base_dir, 'config')
    config_path = os.path.join(config_dir, 'airflow.cfg')
    
    # Very basic airflow configuration
    config_content = f"""
[core]
dags_folder = {os.path.join(base_dir, 'dags')}
base_log_folder = {os.path.join(base_dir, 'logs')}
executor = LocalExecutor
sql_alchemy_conn = sqlite:///{os.path.join(base_dir, 'airflow.db')}
load_examples = False

[scheduler]
job_heartbeat_sec = 5
scheduler_heartbeat_sec = 5
run_duration = -1
min_file_process_interval = 0
dag_dir_list_interval = 30

[webserver]
web_server_host = 0.0.0.0
web_server_port = 8080
web_server_ssl_cert =
web_server_ssl_key =
access_logfile = -
error_logfile = -
expose_config = True
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    logger.info(f"Created Airflow config at: {config_path}")

def create_pipeline_config(base_dir: str) -> None:
    """
    Create pipeline configuration file.
    
    Args:
        base_dir: Base directory for the pipeline
    """
    config_dir = os.path.join(base_dir, 'config')
    config_path = os.path.join(config_dir, 'pipeline_config.json')
    
    config = {
        "pipeline": {
            "input_directories": {
                "pdf": os.path.join(base_dir, "input/pdf_documents"),
                "text": os.path.join(base_dir, "input/text_documents"),
                "html": os.path.join(base_dir, "input/html_documents"),
                "csv": os.path.join(base_dir, "input/csv_data")
            },
            "output_directory": os.path.join(base_dir, "processed_data"),
            "error_directory": os.path.join(base_dir, "processed_data/errors"),
            "report_directory": os.path.join(base_dir, "processed_data/reports"),
            "registry_directory": os.path.join(base_dir, "processed_data/file_registry"),
            "vectordb_directory": os.path.join(base_dir, "vectordb")
        },
        "extraction": {
            "pdf": {
                "use_ocr": True,
                "ocr_threshold": 0.8,
                "preserve_formatting": True
            },
            "text": {
                "encoding": "utf-8",
                "preserve_line_breaks": True
            },
            "html": {
                "extract_tables": True,
                "preserve_structure": True
            }
        },
        "processing": {
            "date_format": "%Y-%m-%d",
            "languages": ["en"],
            "max_content_length": 1000000
        },
        "ai": {
            "use_models": True,
            "entity_extraction": {
                "model": "medical_entity_extraction",
                "threshold": 0.7
            },
            "vectordb": {
                "embedding_model": "pritamdeka/S-PubMedBert-MS-MARCO",
                "use_gpu": False,
                "similarity_threshold": 0.6
            }
        },
        "database": {
            "enabled": True,
            "connection_string": "sqlite:///medical_data.db",
            "batch_size": 100
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Created pipeline config at: {config_path}")

def create_test_data(base_dir: str) -> None:
    """
    Create sample test data files.
    
    Args:
        base_dir: Base directory for the pipeline
    """
    # Sample PDF content (just a placeholder text file since we can't create actual PDFs here)
    pdf_dir = os.path.join(base_dir, "input/pdf_documents")
    with open(os.path.join(pdf_dir, "sample_medical_report.txt"), "w") as f:
        f.write("""
MEDICAL REPORT
Patient: John Doe
Date: 2023-09-15

DIAGNOSIS:
- Hypermobility Ehlers-Danlos Syndrome (hEDS)
- Postural Orthostatic Tachycardia Syndrome (POTS)

SYMPTOMS:
- Joint hypermobility with pain
- Chronic fatigue
- Dizziness upon standing
- Skin hyperextensibility

MEDICATION:
- Midodrine 5mg TID
- Propranolol 10mg BID

RECOMMENDATIONS:
- Physical therapy 2x weekly
- Increased fluid and salt intake
- Follow-up in 3 months
        """)
    
    # Sample text document
    text_dir = os.path.join(base_dir, "input/text_documents")
    with open(os.path.join(text_dir, "symptom_diary.txt"), "w") as f:
        f.write("""
SYMPTOM DIARY
2023-10-01: Experienced increased joint pain in fingers and wrists. Pain level 7/10.
2023-10-02: Fatigue very bad today, could barely get out of bed. Dizziness when standing.
2023-10-03: Slight improvement in pain (5/10), but noticed skin bruising easily.
2023-10-04: Digestive issues today, possibly related to new medication.
2023-10-05: Joint pain back to baseline (4/10). Fatigue improved slightly.
        """)
    
    # Sample HTML document
    html_dir = os.path.join(base_dir, "input/html_documents")
    with open(os.path.join(html_dir, "lab_results.html"), "w") as f:
        f.write("""
<html>
<head><title>Laboratory Test Results</title></head>
<body>
    <h1>Laboratory Test Results</h1>
    <p>Patient: John Doe</p>
    <p>Date: 2023-09-10</p>
    
    <table border="1">
        <tr>
            <th>Test</th>
            <th>Result</th>
            <th>Reference Range</th>
        </tr>
        <tr>
            <td>WBC Count</td>
            <td>6.5 x 10^9/L</td>
            <td>4.5-11.0 x 10^9/L</td>
        </tr>
        <tr>
            <td>Hemoglobin</td>
            <td>13.2 g/dL</td>
            <td>13.5-17.5 g/dL</td>
        </tr>
        <tr>
            <td>Ferritin</td>
            <td>15 ng/mL</td>
            <td>30-400 ng/mL</td>
        </tr>
    </table>
    
    <h2>Notes</h2>
    <p>Patient shows mild anemia and low ferritin levels. Recommend iron supplementation.</p>
</body>
</html>
        """)
    
    # Sample CSV data
    csv_dir = os.path.join(base_dir, "input/csv_data")
    with open(os.path.join(csv_dir, "vitals_tracking.csv"), "w") as f:
        f.write("""date,heart_rate_resting,heart_rate_standing,blood_pressure_systolic,blood_pressure_diastolic,temperature,pain_level
2023-09-01,65,110,118,75,98.6,3
2023-09-02,68,115,120,78,98.4,4
2023-09-03,70,125,115,72,98.7,6
2023-09-04,64,105,122,80,98.5,4
2023-09-05,67,118,121,76,98.8,3
        """)
    
    logger.info("Created sample test data files")

def setup_airflow_environment(base_dir: str) -> None:
    """
    Set up Airflow environment variables.
    
    Args:
        base_dir: Base directory for the pipeline
    """
    airflow_home = os.path.abspath(base_dir)
    
    # Write a shell script to set up the environment
    setup_script_path = os.path.join(base_dir, "setup_airflow_env.sh")
    with open(setup_script_path, "w") as f:
        f.write(f"""#!/bin/bash
export AIRFLOW_HOME="{airflow_home}"
export AIRFLOW__CORE__DAGS_FOLDER="{os.path.join(airflow_home, 'dags')}"
export AIRFLOW__CORE__BASE_LOG_FOLDER="{os.path.join(airflow_home, 'logs')}"
export AIRFLOW__CORE__SQL_ALCHEMY_CONN="sqlite:///{os.path.join(airflow_home, 'airflow.db')}"

# Initialize the database
airflow db init

# Create admin user
airflow users create \\
    --username admin \\
    --firstname Admin \\
    --lastname User \\
    --role Admin \\
    --email admin@example.com \\
    --password admin

echo "Airflow environment set up. Run the following to activate:"
echo "source {setup_script_path}"
""")
    
    # Make the script executable
    os.chmod(setup_script_path, 0o755)
    
    logger.info(f"Created Airflow environment setup script at: {setup_script_path}")

def copy_dag_file(base_dir: str) -> None:
    """
    Copy the DAG file to the dags directory.
    
    Args:
        base_dir: Base directory for the pipeline
    """
    source_dag_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   "..", "dags", "medical_data_ingestion_dag.py")
    dest_dag_path = os.path.join(base_dir, "dags", "medical_data_ingestion_dag.py")
    
    try:
        if os.path.exists(source_dag_path):
            shutil.copy2(source_dag_path, dest_dag_path)
            logger.info(f"Copied DAG file to: {dest_dag_path}")
        else:
            logger.warning(f"DAG file not found at: {source_dag_path}")
    except Exception as e:
        logger.error(f"Error copying DAG file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Set up the medical data ingestion pipeline for Airflow")
    parser.add_argument("--dir", default=".", help="Base directory for the pipeline")
    parser.add_argument("--create-test-data", action="store_true", help="Create sample test data files")
    
    args = parser.parse_args()
    
    base_dir = os.path.abspath(args.dir)
    logger.info(f"Setting up pipeline in directory: {base_dir}")
    
    # Create directory structure
    create_directory_structure(base_dir)
    
    # Create configuration files
    create_airflow_config(base_dir)
    create_pipeline_config(base_dir)
    
    # Set up Airflow environment
    setup_airflow_environment(base_dir)
    
    # Copy DAG file
    copy_dag_file(base_dir)
    
    # Create test data if requested
    if args.create_test_data:
        create_test_data(base_dir)
    
    logger.info(f"""
==============================================
Medical Data Ingestion Pipeline Setup Complete
==============================================

Pipeline has been set up in: {base_dir}

To start using the pipeline:
1. Activate the Airflow environment:
   source {os.path.join(base_dir, 'setup_airflow_env.sh')}

2. Start the Airflow webserver:
   airflow webserver --port 8080

3. Start the Airflow scheduler:
   airflow scheduler

4. Access the Airflow UI at: http://localhost:8080
   Username: admin
   Password: admin

5. Place medical documents in the appropriate input directories:
   - PDF documents: {os.path.join(base_dir, 'input/pdf_documents')}
   - Text documents: {os.path.join(base_dir, 'input/text_documents')}
   - HTML documents: {os.path.join(base_dir, 'input/html_documents')}
   - CSV data: {os.path.join(base_dir, 'input/csv_data')}

6. The pipeline will process these documents according to the schedule 
   defined in the DAG (default: daily).
""")

if __name__ == "__main__":
    main() 
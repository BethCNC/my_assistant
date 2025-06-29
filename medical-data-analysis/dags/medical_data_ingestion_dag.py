"""
Medical Data Ingestion DAG

This DAG orchestrates the end-to-end pipeline for processing medical data:
1. Monitoring for new files in input directories
2. Extracting content from various file formats
3. Processing and normalizing medical data
4. Applying AI analysis for entity extraction
5. Loading results into the database
6. Quality monitoring and error handling
"""

from datetime import datetime, timedelta
import os
from pathlib import Path
import json

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from airflow.sensors.filesystem import FileSensor

# Import the medical data pipeline
from src.pipeline.ingestion_pipeline import MedicalDataIngestionPipeline


# Default arguments for tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'queue': 'medical_pipeline',
    'pool': 'medical_data_pool',
    'priority_weight': 10,
    'start_date': datetime(2023, 1, 1),
    'execution_timeout': timedelta(hours=2),
}

# Create DAG
dag = DAG(
    'medical_data_ingestion',
    default_args=default_args,
    description='End-to-end pipeline for medical data ingestion',
    schedule_interval=timedelta(days=1),  # Run once a day
    catchup=False,
    max_active_runs=1,
    tags=['medical', 'ingestion', 'pipeline'],
)

# Function to detect new files
def detect_new_files(**context):
    """
    Detect new files in the input directories and return their paths.
    """
    # Get input directories from Airflow variables or config
    input_dirs = [
        'input/pdf_documents',
        'input/text_documents',
        'input/html_documents',
        'input/csv_data',
    ]
    
    # Get the directory where processed files are tracked
    processed_files_dir = 'processed_data/file_registry'
    os.makedirs(processed_files_dir, exist_ok=True)
    
    # Path to the registry of processed files
    registry_path = os.path.join(processed_files_dir, 'processed_files.json')
    
    # Load the registry of processed files
    processed_files = set()
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            processed_files = set(json.load(f))
    
    # Find new files
    new_files = []
    for input_dir in input_dirs:
        if os.path.exists(input_dir):
            for root, _, files in os.walk(input_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in processed_files:
                        new_files.append(file_path)
    
    # Push the list of new files to XCom
    context['ti'].xcom_push(key='new_files', value=new_files)
    
    # Return the next task based on whether new files were found
    if new_files:
        return 'process_files'
    else:
        return 'no_new_files'

# Function to process a batch of files
def process_files(**context):
    """
    Process a batch of files through the medical data pipeline.
    """
    # Get the list of new files from XCom
    ti = context['ti']
    new_files = ti.xcom_pull(task_ids='detect_new_files', key='new_files')
    
    # Process each file
    results = []
    success_files = []
    failed_files = []
    
    # Initialize the pipeline
    pipeline = MedicalDataIngestionPipeline(
        use_models=True,
        store_in_db=True,
        processed_dir="processed_data"
    )
    
    # Initialize and integrate vector database
    from src.ai.vectordb.pipeline_integration import create_vector_db_integration
    vector_db = create_vector_db_integration(
        pipeline=pipeline,
        vector_db_path="vectordb",
        use_gpu=False
    )
    
    # Process each file
    for file_path in new_files:
        try:
            result = pipeline.process_file(file_path)
            results.append(result)
            if 'error' not in result:
                success_files.append(file_path)
            else:
                failed_files.append(file_path)
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            failed_files.append(file_path)
    
    # Clean up resources
    pipeline.close()
    
    # Push processing results to XCom
    ti.xcom_push(key='processing_results', value=results)
    ti.xcom_push(key='success_files', value=success_files)
    ti.xcom_push(key='failed_files', value=failed_files)
    
    # Update the registry of processed files
    registry_path = os.path.join('processed_data/file_registry', 'processed_files.json')
    processed_files = set()
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            processed_files = set(json.load(f))
    
    # Add successful files to the registry
    processed_files.update(success_files)
    
    # Save the updated registry
    with open(registry_path, 'w') as f:
        json.dump(list(processed_files), f, indent=2)
        
    # Return the next task based on results
    if failed_files:
        return 'handle_failures'
    else:
        return 'generate_reports'

# Function to handle failures
def handle_failures(**context):
    """
    Handle failed files by moving them to error directory and logging details.
    """
    # Get the list of failed files from XCom
    ti = context['ti']
    failed_files = ti.xcom_pull(task_ids='process_files', key='failed_files')
    
    # Create error directory if it doesn't exist
    error_dir = 'processed_data/errors'
    os.makedirs(error_dir, exist_ok=True)
    
    # Move failed files to error directory
    for file_path in failed_files:
        file_name = os.path.basename(file_path)
        error_path = os.path.join(error_dir, file_name)
        
        # Copy the file to error directory (don't move to preserve original)
        try:
            with open(file_path, 'rb') as src, open(error_path, 'wb') as dst:
                dst.write(src.read())
                
            # Log the error
            with open(os.path.join(error_dir, f"{file_name}.error.log"), 'w') as f:
                f.write(f"Error processing file: {file_path}\n")
                f.write(f"Timestamp: {datetime.now()}\n")
                # Add more error details if available
        except Exception as e:
            print(f"Error handling failed file {file_path}: {str(e)}")

# Function to generate processing reports
def generate_reports(**context):
    """
    Generate summary reports of processing results.
    """
    # Get processing results from XCom
    ti = context['ti']
    results = ti.xcom_pull(task_ids='process_files', key='processing_results')
    success_files = ti.xcom_pull(task_ids='process_files', key='success_files')
    
    # Create reports directory if it doesn't exist
    reports_dir = 'processed_data/reports'
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate summary report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_files_processed': len(results),
        'successful_files': len(success_files),
        'failed_files': len(results) - len(success_files),
        'entity_counts': {
            'conditions': 0,
            'medications': 0,
            'symptoms': 0,
            'procedures': 0,
            'lab_results': 0,
        }
    }
    
    # Count extracted entities
    for result in results:
        if 'ai_analysis' in result and 'entities' in result['ai_analysis']:
            entities = result['ai_analysis']['entities']
            report['entity_counts']['conditions'] += len([e for e in entities if e['type'] == 'CONDITION'])
            report['entity_counts']['medications'] += len([e for e in entities if e['type'] == 'MEDICATION'])
            report['entity_counts']['symptoms'] += len([e for e in entities if e['type'] == 'SYMPTOM'])
            report['entity_counts']['procedures'] += len([e for e in entities if e['type'] == 'PROCEDURE'])
            report['entity_counts']['lab_results'] += len([e for e in entities if e['type'] == 'LAB_RESULT'])
    
    # Save the report
    report_path = os.path.join(reports_dir, f"ingestion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Push report path to XCom
    ti.xcom_push(key='report_path', value=report_path)

# Define tasks
with dag:
    # Task to check if input directories exist and create them if needed
    setup_directories = BashOperator(
        task_id='setup_directories',
        bash_command='mkdir -p input/pdf_documents input/text_documents input/html_documents input/csv_data processed_data/file_registry processed_data/reports processed_data/errors',
    )
    
    # Task to detect new files
    detect_new_files_task = BranchPythonOperator(
        task_id='detect_new_files',
        python_callable=detect_new_files,
        provide_context=True,
        doc_md="""
        This task scans the input directories for new files that haven't been processed yet.
        It returns the next task based on whether new files were found.
        """,
    )
    
    # Task for when no new files are found
    no_new_files = DummyOperator(
        task_id='no_new_files',
        doc_md="Task for when no new files are found.",
    )
    
    # Task to process files
    process_files_task = BranchPythonOperator(
        task_id='process_files',
        python_callable=process_files,
        provide_context=True,
        doc_md="""
        This task processes each file through the medical data pipeline,
        extracting content, normalizing data, applying AI analysis, and loading results into the database.
        """,
    )
    
    # Task to handle failures
    handle_failures_task = PythonOperator(
        task_id='handle_failures',
        python_callable=handle_failures,
        provide_context=True,
        doc_md="This task handles failed files by moving them to an error directory and logging details.",
    )
    
    # Task to generate reports
    generate_reports_task = PythonOperator(
        task_id='generate_reports',
        python_callable=generate_reports,
        provide_context=True,
        doc_md="This task generates summary reports of processing results.",
    )
    
    # Task to clean up temporary files
    cleanup = BashOperator(
        task_id='cleanup',
        bash_command='find /tmp -name "airflow_medical_*" -type f -mtime +1 -delete || true',
        doc_md="This task cleans up temporary files created during processing.",
    )
    
    # Final task to mark completion
    end_pipeline = DummyOperator(
        task_id='end_pipeline',
        trigger_rule='none_failed_min_one_success',
        doc_md="Task to mark completion of the pipeline.",
    )
    
    # Define task dependencies
    setup_directories >> detect_new_files_task >> [process_files_task, no_new_files]
    process_files_task >> [handle_failures_task, generate_reports_task]
    handle_failures_task >> generate_reports_task
    generate_reports_task >> cleanup >> end_pipeline
    no_new_files >> end_pipeline

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('health_analytics')

# Configuration paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
# RESULTS_FILE = os.path.join(DATA_DIR, 'analysis_results.json')
RESULTS_FILE = os.path.join(DATA_DIR, 'test_analysis.json')  # Using test file
RESULTS_DIR = os.path.join(DATA_DIR, 'analytics_results')

# Ensure the results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_data():
    """Load analysis results from JSON file."""
    logger.info(f"Loading data from {RESULTS_FILE}")
    try:
        with open(RESULTS_FILE, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.error(f"Data file {RESULTS_FILE} not found.")
        return None
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {RESULTS_FILE}.")
        return None

def plot_lab_trends(data):
    """Generate plots for lab result trends."""
    logger.info("Generating lab result trend plots")
    
    all_labs = []
    for result in data['results']:
        if 'lab_results' in result and result['lab_results']:
            for lab in result['lab_results']:
                lab_data = {
                    'patient_id': result.get('patient_id', 'Unknown'),
                    'test_name': lab.get('test_name', 'Unknown'),
                    'date': lab.get('date', 'Unknown'),
                    'result': lab.get('result', 'Unknown')
                }
                all_labs.append(lab_data)
    
    if not all_labs:
        logger.warning("No lab results found for plotting")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(all_labs)
    logger.info(f"Loaded {len(df)} lab results")
    
    # Convert date strings to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['date'])
    
    # Sort by date
    df = df.sort_values('date')
    
    # Convert result to numeric if possible
    df['result_numeric'] = pd.to_numeric(df['result'], errors='coerce')
    
    # Group by test name
    for test_name, group in df.groupby('test_name'):
        if len(group) < 2:
            logger.info(f"Skipping {test_name} plot as it has fewer than 2 data points")
            continue
            
        if group['result_numeric'].isna().all():
            logger.info(f"Skipping {test_name} plot as it has no numeric results")
            continue
        
        plt.figure(figsize=(10, 6))
        for patient_id, patient_group in group.groupby('patient_id'):
            plt.plot(patient_group['date'], patient_group['result_numeric'], 'o-', label=patient_id)
        
        plt.title(f'{test_name} Trend Over Time')
        plt.xlabel('Date')
        plt.ylabel('Result Value')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # Format x-axis date ticks
        plt.gcf().autofmt_xdate()
        
        # Save the plot
        output_file = os.path.join(RESULTS_DIR, f'lab_trend_{test_name}.png')
        plt.savefig(output_file)
        plt.close()
        logger.info(f"Saved lab trend plot for {test_name} to {output_file}")

def plot_symptom_severity(data):
    """Generate plots for symptom severity over time."""
    logger.info("Generating symptom severity plots")
    
    all_symptoms = []
    for result in data['results']:
        if 'symptoms' in result and result['symptoms']:
            for symptom in result['symptoms']:
                symptom_data = {
                    'patient_id': result.get('patient_id', 'Unknown'),
                    'name': symptom.get('name', 'Unknown'),
                    'date_recorded': symptom.get('date_recorded', 'Unknown'),
                    'severity': symptom.get('severity', 'Unknown')
                }
                all_symptoms.append(symptom_data)
    
    if not all_symptoms:
        logger.warning("No symptoms found for plotting")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(all_symptoms)
    logger.info(f"Loaded {len(df)} symptoms")
    
    # Convert date strings to datetime
    df['date_recorded'] = pd.to_datetime(df['date_recorded'], errors='coerce')
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['date_recorded'])
    
    # Sort by date
    df = df.sort_values('date_recorded')
    
    # Convert severity to numeric if possible
    df['severity_numeric'] = pd.to_numeric(df['severity'], errors='coerce')
    
    # Group by symptom name
    for symptom_name, group in df.groupby('name'):
        if len(group) < 2:
            logger.info(f"Skipping {symptom_name} plot as it has fewer than 2 data points")
            continue
            
        if group['severity_numeric'].isna().all():
            logger.info(f"Skipping {symptom_name} plot as it has no numeric severity values")
            continue
        
        plt.figure(figsize=(10, 6))
        for patient_id, patient_group in group.groupby('patient_id'):
            plt.plot(patient_group['date_recorded'], patient_group['severity_numeric'], 'o-', label=patient_id)
        
        plt.title(f'{symptom_name} Severity Over Time')
        plt.xlabel('Date')
        plt.ylabel('Severity (1-10)')
        plt.ylim(0, 10)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # Format x-axis date ticks
        plt.gcf().autofmt_xdate()
        
        # Save the plot
        output_file = os.path.join(RESULTS_DIR, f'symptom_{symptom_name.replace(" ", "_")}.png')
        plt.savefig(output_file)
        plt.close()
        logger.info(f"Saved symptom severity plot for {symptom_name} to {output_file}")

def main():
    """Main function to run the analytics generation."""
    logger.info("Starting health analytics generation")
    
    # Load the data
    data = load_data()
    if not data:
        logger.error("Failed to load data. Exiting.")
        return
    
    logger.info(f"Loaded data from {len(data.get('results', []))} results")
    
    # Generate plots
    plot_lab_trends(data)
    plot_symptom_severity(data)
    
    logger.info("Health analytics generation completed")

if __name__ == "__main__":
    main() 
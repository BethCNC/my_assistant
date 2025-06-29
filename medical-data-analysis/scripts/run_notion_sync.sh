#!/bin/bash

# This script runs the medical data to Notion sync process

echo "Starting medical data to Notion sync..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Activated virtual environment"
fi

# Run the sync process
python src/notion_integration/notion_data_syncer.py \
    --config config/notion_config.json \
    --mapping config/notion_field_mapping.json \
    --input data/input \
    --recursive \
    --include-content \
    --extensions ".txt,.pdf,.html,.docx,.md,.rtf,.csv" \
    --verbose

# Check if the process succeeded
if [ $? -eq 0 ]; then
    echo "Sync completed successfully!"
else
    echo "Sync failed. Check the logs for details."
fi

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 
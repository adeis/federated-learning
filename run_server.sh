#!/bin/bash
# Script to run the FastAPI Aggregator Server at 127.0.0.1:8000

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the FastAPI server using the virtual environment python
echo "========================================================="
echo "Starting FastAPI Aggregator Server at 127.0.0.1:8000..."
echo "========================================================="

# Navigate to the folder containing server_agregator.py
cd "$SCRIPT_DIR/tgps-federated-learning"

# Execute the aggregator script using the venv python
"$SCRIPT_DIR/venv/bin/python" server_agregator.py

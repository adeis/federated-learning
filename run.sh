#!/bin/bash
# Shortcut script to run the TGPS Federated Learning simulation

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the simulation using the virtual environment python
echo "========================================================="
echo "Starting TGPS Federated Learning Simulation..."
echo "========================================================="
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/tgps-federated-learning/run_simulation.py"

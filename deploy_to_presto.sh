#!/bin/bash

# Script to deploy a Python file to Presto using mpremote
# Usage: ./deploy_to_presto.sh <python_file>

# Check if a parameter was provided
if [ $# -eq 0 ]; then
    echo "Error: No Python file specified"
    echo "Usage: $0 <python_file>"
    exit 1
fi

# Check if the file exists
if [ ! -f "$1" ]; then
    echo "Error: File '$1' not found"
    exit 1
fi

# Deploy using mpremote
echo "Deploying '$1' to Presto..."
mpremote fs cp "$1" :

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo "✓ Successfully deployed '$(basename $1)' to Presto"
else
    echo "✗ Failed to deploy file to Presto"
    echo "Make sure mpremote is installed and Presto is connected"
    exit 1
fi
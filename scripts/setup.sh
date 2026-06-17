#!/bin/bash
# Setup script for AI Incident Triage System

echo "Setting up AI Incident Triage System..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file — add your ANTHROPIC_API_KEY"
fi

# Create required directories
mkdir -p logs incidents storage

echo "Setup complete!"
echo "Add your ANTHROPIC_API_KEY to .env then run: make run"
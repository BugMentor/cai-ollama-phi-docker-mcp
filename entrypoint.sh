#!/bin/bash
set -e

echo "Starting Ollama server in background..."
ollama serve &

# Wait for Ollama server to start
sleep 5

echo "Activating CAI virtual environment..."
source /home/caiuser/cai_env/bin/activate

echo "Executing command: $@"
exec "$@"
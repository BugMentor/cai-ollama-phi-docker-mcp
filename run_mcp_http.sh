#!/bin/bash
# run_mcp_http.sh
# Linux/macOS version of the startup script

CONTAINER_NAME="cai-agent-mcp-http"
IMAGE_NAME="cai-agent:latest"

echo -e "\033[0;36m[*] Stopping existing container if any...\033[0m"
docker rm -f "$CONTAINER_NAME" 2>/dev/null

echo -e "\033[0;34m[*] Building Docker image...\033[0m"
docker build -t "$IMAGE_NAME" .

echo -e "\033[0;32m[*] Starting $CONTAINER_NAME in background...\033[0m"
# Run with dummy tail to keep alive, as specified in the README approach
# Using Host network or mapping port 8000 for MCP_HTTP mode
docker run -d \
  --name "$CONTAINER_NAME" \
  -p 8000:8000 \
  -e "MCP_HTTP=1" \
  "$IMAGE_NAME" \
  tail -f /dev/null

echo -e "\033[0;32m[+] MCP Server Container is ready!\033[0m"
echo -e "\033[0;33m[!] HTTP Discovery URL: http://localhost:8000/mcp\033[0m"

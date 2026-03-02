#!/bin/bash
# get_mcp_report.sh
# Helper script to fetch and open the latest MCP intelligence report from the container

CONTAINER_NAME="cai-agent-mcp-http"
REMOTE_PATH="/home/caiuser/latest_cai_report.html"
LOCAL_PATH="./latest_mcp_report.html"

echo -e "\033[0;36m[*] Fetching latest report from $CONTAINER_NAME...\033[0m"

# Copy from container to host
if docker cp "${CONTAINER_NAME}:${REMOTE_PATH}" "$LOCAL_PATH" 2>/dev/null; then
    echo -e "\033[0;32m[+] Report retrieved: $LOCAL_PATH\033[0m"
    
    # Try to open in default browser (Linux/macOS)
    if command -v xdg-open > /dev/null; then
        xdg-open "$LOCAL_PATH"
    elif command -v open > /dev/null; then
        open "$LOCAL_PATH"
    else
        echo -e "\033[0;33m[!] Browser opener not found. Please open $LOCAL_PATH manually.\033[0m"
    fi
else
    echo -e "\033[0;33m[!] Report not found in container yet.\033[0m"
    echo -e "\033[0;36m[?] Ensure the container is running and you have sent at least one prompt.\033[0m"
fi

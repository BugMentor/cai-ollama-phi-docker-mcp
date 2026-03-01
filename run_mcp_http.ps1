# Start CAI MCP server in HTTP mode (avoids stdio issues on Windows with Cursor)
# Run this before using Cursor; Cursor connects via http://localhost:8000/mcp

$ErrorActionPreference = "Stop"
$image = "cai-agent:latest"
$container = "cai-agent-mcp-http"

# Build if needed
if (-not (docker images -q $image)) {
    Write-Host "Building image..."
    docker build -t $image .
}

# Remove existing container if present
docker rm -f $container 2>$null

Write-Host "Starting MCP server on http://localhost:8000/mcp"
docker run -d --name $container `
    -p 8000:8000 `
    -e MCP_HTTP=1 `
    $image `
    python -u /home/caiuser/cai_mcp_server.py

Write-Host "Container started. Configure Cursor MCP with:"
Write-Host '  "url": "http://localhost:8000/mcp"'
Write-Host ""
Write-Host "Logs: docker logs -f $container"

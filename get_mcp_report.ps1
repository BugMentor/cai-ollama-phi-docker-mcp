# get_mcp_report.ps1
# Helper script to fetch and open the latest MCP intelligence report from the container

$containerName = "cai-agent-mcp-http"
$remotePath = "/home/caiuser/latest_cai_report.html"
$localPath = "$PSScriptRoot\latest_mcp_report.html"

Write-Host "[*] Fetching latest report from $containerName..." -ForegroundColor Cyan

try {
    # Copy from container to host
    docker cp "${containerName}:${remotePath}" "$localPath"
    
    if (Test-Path $localPath) {
        Write-Host "[+] Report retrieved: $localPath" -ForegroundColor Green
        # Open in default browser
        Start-Process "$localPath"
    } else {
        Write-Host "[!] Report file not found after copy." -ForegroundColor Red
    }
} catch {
    Write-Host "[!] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[?] Make sure the container is running and you have executed at least one 'cai_text' prompt." -ForegroundColor Yellow
}

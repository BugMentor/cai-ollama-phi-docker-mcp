import os
import sys
import argparse
import subprocess
import datetime
import time

# Configuration
SENSITIVE_EXTENSIONS = ('.go', '.py', '.js', '.ts', '.env', '.json', '.sh', '.ps1')
CONTAINER_NAME = "cai-agent-mcp-http"
CORE_SCANNER_FILENAME = "cai_scanner_core.py"
REPORT_FILENAME = "security_report.html"

def check_docker():
    """Verify that Docker is running and the container is active."""
    try:
        status = subprocess.check_output(
            f'docker inspect -f "{{{{.State.Running}}}}" {CONTAINER_NAME}',
            shell=True, stderr=subprocess.DEVNULL
        ).decode().strip()
        return status == "true"
    except subprocess.CalledProcessError:
        return False

def setup_container():
    """Copy the core scanner script to the container."""
    print(f"[*] Ensuring {CORE_SCANNER_FILENAME} is in the container...")
    try:
        subprocess.check_call(
            f'docker cp {CORE_SCANNER_FILENAME} {CONTAINER_NAME}:/home/caiuser/{CORE_SCANNER_FILENAME}',
            shell=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[!] Error copying core scanner: {e}")
        sys.exit(1)

def scan_file(file_path):
    """Analyze a single file using the CAI agent in the container."""
    print(f"[*] Analyzing: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code_content = f.read()

        # Run the analysis via docker exec, piping the code content
        process = subprocess.Popen(
            f'docker exec -i {CONTAINER_NAME} /home/caiuser/cai_env/bin/python /home/caiuser/{CORE_SCANNER_FILENAME}',
            shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=code_content.encode())
        
        if process.returncode != 0:
            return f"Error analyzing {file_path}: {stderr.decode()}"
        
        return stdout.decode()
    except Exception as e:
        return f"Error reading {file_path}: {e}"

def generate_report(results):
    """Aggregate results into a premium HTML report."""
    print(f"[*] Generating report: {REPORT_FILENAME}...")
    
    # Aggregated HTML content
    report_items = []
    for file_path, analysis in results.items():
        # Sanitize for HTML
        safe_analysis = analysis.replace("<", "&lt;").replace(">", "&gt;")
        report_items.append(f"""
        <div class="card">
            <h2 class="file-header">File: {file_path}</h2>
            <div class="report-content">{safe_analysis}</div>
        </div>
        """)
    
    html_content = "\n".join(report_items)
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal Security Analysis Report</title>
    <style>
        :root {{
            --primary: #2563eb;
            --bg: #f1f5f9;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --status-bg: #dcfce7;
            --status-text: #166534;
        }}

        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.6;
            margin: 0;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 60px;
        }}

        h1 {{
            font-size: 3rem;
            font-weight: 800;
            color: var(--primary);
            margin: 0;
            letter-spacing: -0.05em;
        }}

        .metadata {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-top: 15px;
        }}

        .summary-badge {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            background: var(--status-bg);
            color: var(--status-text);
            font-weight: 700;
            font-size: 0.8rem;
            text-transform: uppercase;
            margin-bottom: 20px;
        }}

        .card {{
            background: var(--card-bg);
            border-radius: 24px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
            padding: 40px;
            margin-bottom: 40px;
            border: 1px solid var(--border);
            transition: transform 0.2s;
        }}

        .file-header {{
            font-size: 1.5rem;
            color: var(--primary);
            border-bottom: 2px solid var(--bg);
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}

        .report-content {{
            white-space: pre-wrap;
            font-size: 1rem;
            color: #334155;
        }}

        pre {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 12px;
            overflow-x: auto;
            border: 1px solid var(--border);
        }}

        footer {{
            text-align: center;
            margin-top: 80px;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="summary-badge">Scan Summary: {len(results)} Files Audited</div>
            <h1>Security Intelligence Report</h1>
            <div class="metadata">
                Project Scan | {datetime.datetime.now().strftime("%B %d, %Y - %H:%M")}
            </div>
        </header>

        {html_content}

        <footer>
            &copy; 2026 BugMentor Agentic Intelligence | Automated Security Governance
        </footer>
    </div>
</body>
</html>
"""
    with open(REPORT_FILENAME, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"[+] Final report ready: {os.path.abspath(REPORT_FILENAME)}")
    
    # Automate: Open report in the browser
    try:
        import webbrowser
        webbrowser.open(os.path.abspath(REPORT_FILENAME))
    except Exception as e:
        print(f"[!] Error opening browser: {e}")

def main():
    parser = argparse.ArgumentParser(description="Universal CAI Security Scanner")
    parser.add_argument("directory", help="Target directory to scan")
    args = parser.parse_args()

    target_dir = os.path.abspath(args.directory)
    if not os.path.isdir(target_dir):
        print(f"[!] Error: {target_dir} is not a valid directory.")
        sys.exit(1)

    if not check_docker():
        print(f"[!] Error: Docker container {CONTAINER_NAME} is not running.")
        sys.exit(1)

    setup_container()

    scanned_files = {}
    print(f"[*] Starting recursive scan of: {target_dir}")
    
    for root, dirs, files in os.walk(target_dir):
        # Skip some common ignored dirs
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', 'venv', 'cai_env')]
        
        for file in files:
            if file.lower().endswith(SENSITIVE_EXTENSIONS):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, target_dir)
                
                analysis = scan_file(full_path)
                scanned_files[rel_path] = analysis

    if scanned_files:
        generate_report(scanned_files)
    else:
        print("[!] No sensitive files found to scan.")

if __name__ == "__main__":
    main()

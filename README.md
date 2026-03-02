# BugMentor CAI: Universal Security Intelligence & MCP Server

This is a powerful, open-source **BugMentor project** that containerizes the CAI (Cybersecurity AI) agent with Ollama and the `phi` model. It provides both a generic security scanner for any project and a fully-featured MCP (Model Context Protocol) server with automated intelligence reporting.

- **Developer**: Matías J. Magni, CEO @ [BugMentor](https://bugmentor.com)
- **Original Framework**: Based on the [CAI (Cybersecurity AI) framework](https://github.com/aliasrobotics/cai) by Alias Robotics.
- **License**: MIT

---

## 🚀 Key Features

### 1. Universal Security Scanner (`cai_security_scanner.py`)
A cross-platform CLI tool that performs deep security audits on any directory.
- **Recursive Scan**: Identifies sensitive files (.go, .py, .js, .env, etc.).
- **AI-Powered**: Uses BugMentor AI (Phi-2) in Docker for high-fidelity auditing.
- **Instant Reports**: Generates a premium, responsive HTML report and opens it automatically in your browser.

### 2. Automated MCP Intelligence
The MCP server automatically generates a professional HTML report after **every** interaction.
- **`cai_text` Tool**: Integrates directly with Cursor, VS Code, or Gemini Desktop.
- **Persistence**: Every response is archived as a styled HTML report inside the container.

---

## 🛠 Setup Instructions

### 1. Build the AI Engine
Ensure Docker is running, then build the image:
```bash
docker build -t cai-agent:latest .
```

### 2. Launch the MCP Server
Launch the container and the MCP service:

**Windows (PowerShell):**
```powershell
.\run_mcp_http.ps1
```

**Linux/macOS (Bash):**
```bash
chmod +x *.sh
./run_mcp_http.sh
```

### 3. Configure Your IDE (MCP)
Add the following to your MCP configuration (e.g., `mcp_config.json`):
```json
{
  "mcpServers": {
    "cai-ollama-phi": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "cai-agent-mcp-http",
        "/home/caiuser/cai_env/bin/python",
        "-u",
        "/home/caiuser/cai_mcp_server.py"
      ]
    }
  }
}
```

---

## 📖 Usage Guide

### 🔍 Running a Security Audit
Scan any directory on your host:
```bash
# Windows
python cai_security_scanner.py "C:\path\to\your\project"

# Linux/macOS
python3 cai_security_scanner.py "/path/to/your/project"
```
The script will audit the code and automatically open the **`security_report.html`** when finished.

### 🧠 Using the MCP Agent
In your IDE (Cursor/VS Code/Gemini Desktop), simply ask:
> "Use cai_text to analyze the security of this feature..."

### 📄 Viewing MCP Reports
To see the beautifully formatted HTML report from your last MCP interaction:

**Windows (PowerShell):**
```powershell
.\get_mcp_report.ps1
```

**Linux/macOS (Bash):**
```bash
./get_mcp_report.sh
```

**Note**: A placeholder "Welcome" report is generated automatically on server startup. Send your first `cai_text` prompt to update it with real intelligence.

---

## 🧹 Project Structure
- `cai_security_scanner.py`: Host-side CLI for directory auditing (Auto-Open feature).
- `cai_scanner_core.py`: Container-side audit worker.
- `cai_mcp_server.py`: MCP server with automated reporting logic.
- `run_mcp_http.ps1/sh`: Container lifecycle management for Windows and Linux.
- `get_mcp_report.ps1/sh`: Automation scripts for viewing reports.

---

## 💰 Funding & Support

**BugMentor** is dedicated to building privacy-focused, vendor-lock-in-free alternatives for cybersecurity and agile tools.

Building and maintaining enterprise-grade security tools takes significant resources. Your support directly funds server costs, development hours, and the maintenance of our open-source infrastructure.

### 🏆 Become a Sponsor (Open Collective)
This is the best way to support the project if you want public recognition on our README and website.

[![Open Collective](https://img.shields.io/opencollective/all/bugmentor-arg?label=Support%20BugMentor&logo=opencollective&color=blue)](https://opencollective.com/bugmentor-arg)

[**Click here to Donate via Open Collective**](https://opencollective.com/bugmentor-arg/donate)

---

### ⚡ Direct Support (Wise)
If you prefer to support the lead developer directly with lower fees (or for one-off contributions), you can use the link below.

[**Send a Direct Contribution via Wise**](https://wise.com/pay/me/matiasm155)

---

### 💼 Commercial Support & Training
Need help implementing CAI or other BugMentor tools in your company? BugMentor offers:
* **Enterprise Installation & Hosting Support**
* **Cybersecurity & QA Training**
* **Custom AI Feature Development**

[Contact us](https://bugmentor.com) for commercial inquiries.

---

## 🧪 Testing & Quality Assurance

This project maintains **100% code and test coverage** to ensure reliable security auditing.

### Running Tests
The test suite is built with `pytest` and covers unit, integration, and E2E scenarios.

**Windows (PowerShell):**
```powershell
$Env:PYTHONPATH = "."; pytest -v tests/
```

**Linux/macOS:**
```bash
export PYTHONPATH="."; pytest -v tests/
```

**Testing Levels:**
- **Unit Tests**: Logic validation for `cai_scanner_core.py` and `cai_mcp_server.py`.
- **Integration Tests**: Subprocess and file-system interaction validation for the scanner.
- **E2E Smoke Tests**: Connectivity checks for the live MCP server.

---

## 🤝 Contributing
BugMentor welcomes community contributions. Fork this repository, open PRs, or file issues at [BugMentor](https://bugmentor.com).

*Safe hunting!* 🛡️

import asyncio
import logging
import os
import sys
from typing import Any

# Force unbuffered I/O for stdio MCP protocol (critical on Windows)
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

try:
    from fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as e:
        sys.stderr.write(f"Failed to import FastMCP: {e}\n")
        sys.stderr.write("Make sure 'fastmcp' or 'mcp' package is installed: pip install fastmcp\n")
        sys.exit(1)

# Suppress FastMCP logging to stderr to avoid confusing Cursor MCP client
# MCP stdio protocol expects clean JSON-RPC on stdout, any stderr output can cause issues
logging.getLogger("fastmcp").setLevel(logging.WARNING)
logging.getLogger("mcp").setLevel(logging.WARNING)

mcp = FastMCP("BugMentor CAI Ollama Phi")


@mcp.tool()
async def ping() -> str:
    """
    Simple liveness check for the MCP server.
    """
    return "pong"


@mcp.tool()
async def echo(message: str) -> str:
    """
    Echo a message back. Basic sanity tool.
    """
    return message


@mcp.tool()
async def cai_text(prompt: str) -> str:
    """
    Ask the CAI agent a question and automatically generate a premium HTML report.
    """
    from cai.sdk.agents import Agent, Runner, OpenAIChatCompletionsModel
    import datetime
    import os
    import subprocess
    import re

    # Configuration for the model
    model = OpenAIChatCompletionsModel(
        model_id=os.environ.get("CAI_MODEL", "ollama/phi"),
        api_key=os.environ.get("OPENAI_API_KEY", "sk-1234"),
        base_url=os.environ.get("OLLAMA_API_BASE", "http://localhost:11434/v1"),
    )

    agent = Agent(
        name="BugMentor-CAI",
        model=model,
        instructions="You are a helpful cybersecurity assistant. Provide detailed, expert responses.",
    )

    runner = Runner(agent=agent)

    try:
        response = runner.run(prompt)
        analysis_text = response.text if hasattr(response, "text") else str(response)
        
        # Clean ANSI noise for the report
        clean_text = re.sub(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])', '', analysis_text)
        clean_text = re.sub(r'[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]', '', clean_text)

        # Generate HTML Report
        report_path = "/home/caiuser/latest_cai_report.html"
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CAI Intelligence Report</title>
    <style>
        body {{ font-family: 'Inter', -apple-system, sans-serif; background: #f8fafc; color: #1e293b; padding: 40px; line-height: 1.6; }}
        .card {{ background: white; border-radius: 16px; padding: 40px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #2563eb; margin-top: 0; font-weight: 800; letter-spacing: -0.025em; }}
        .metadata {{ color: #64748b; font-size: 0.9rem; margin-bottom: 30px; border-bottom: 1px solid #f1f5f9; padding-bottom: 15px; }}
        .content {{ white-space: pre-wrap; font-size: 1.1rem; color: #334155; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>CAI Intelligence Report</h1>
        <div class="metadata">Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Analysis: Completed</div>
        <div class="content">{clean_text.replace("<", "&lt;").replace(">", "&gt;")}</div>
    </div>
</body>
</html>
"""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_template)
            
        return f"{analysis_text}\n\n[REPORT GENERATED: {report_path}]"
    except Exception as e:
        return f"Error invoking CAI SDK: {str(e)}"


if __name__ == "__main__":
    try:
        # Use HTTP transport when MCP_HTTP=1 (avoids stdio/docker exec issues on Windows)
        if os.environ.get("MCP_HTTP"):
            mcp.run(transport="http", host="0.0.0.0", port=8000, show_banner=False)
        else:
            mcp.run(transport="stdio", show_banner=False)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        sys.stderr.write(f"MCP server error: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


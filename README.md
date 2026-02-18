# CAI Agent Containerization and MCP Integration Setup

This document outlines the steps and configurations for containerizing the CAI (Cybersecurity AI) agent with Ollama and the `phi` model, and integrating it as an MCP (Model Context Protocol) server. This approach provides enhanced portability, isolation, and streamlined management compared to a direct WSL installation.

## Files Created for Containerization

### 1. `Dockerfile`

This file is used to build the Docker image for the CAI agent. It sets up the environment, installs dependencies, installs Ollama, and pre-pulls the `phi` model.

**Location:** `C:\Users\matias.magni2\Dockerfile`

```dockerfile
# Use an official Ubuntu image as a base
FROM ubuntu:latest

# Set environment variables for non-interactive apt-get installs
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install necessary dependencies
RUN apt-get update && 
    apt-get install -y 
    python3 
    python3-pip 
    python3-venv 
    curl 
    zstd 
    git 
    --no-install-recommends && 
    rm -rf /var/lib/apt/lists/*

# Create a non-root user for security best practices
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID caiuser && useradd -m -u $UID -g $GID -s /bin/bash caiuser
USER caiuser
WORKDIR /home/caiuser

# Create and activate Python virtual environment
RUN python3 -m venv cai_env
ENV PATH="/home/caiuser/cai_env/bin:$PATH"

# Install cai-framework
RUN pip install cai-framework

# Install Ollama
# The Ollama install script will set up the 'ollama' user and service within the container.
# This curl command must be run as root initially, then we'll manage the user later.
USER root
RUN curl -fsSL https://ollama.com/install.sh | sh
USER caiuser

# Create .env file for CAI configuration
RUN echo 'OPENAI_API_KEY="sk-1234"' > .env && 
    echo 'ANTHROPIC_API_KEY=""' >> .env && 
    echo 'OLLAMA="phi"' >> .env && 
    echo 'CAI_MODEL="ollama/phi"' >> .env && 
    echo 'OLLAMA_API_BASE="http://localhost:11434"' >> .env && 
    echo 'PROMPT_TOOLKIT_NO_CPR=1' >> .env && 
    echo 'CAI_STREAM=false' >> .env

# Expose the Ollama port
EXPOSE 11434

# Ensure Ollama is served before attempting to pull models
# This uses a trick: in a multi-stage build or similar, you'd start ollama serve
# and then pull. For simplicity in a single-stage, we'll run ollama serve
# in the background during the build, then kill it, ensuring the model is present.
# For runtime, we'll start it again.
RUN (ollama serve > /dev/null 2>&1 &) && 
    sleep 5 && 
    ollama pull phi && 
    kill $(jobs -p) || true # Kill background ollama serve and ignore errors if it already exited

# Define the entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint to our script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Default command for the container
CMD ["cai"]
```

### 2. `entrypoint.sh`

This script is executed when the Docker container starts. It ensures the Ollama server is running in the background and activates the CAI virtual environment before executing the main command.

**Location:** `C:\Users\matias.magni2\entrypoint.sh`

```bash
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
```

### 3. `mcp_config_cai.json`

This JSON file provides a configuration entry for your MCP system, defining the containerized CAI agent as an MCP server.

**Location:** `C:\Users\matias.magni2\mcp_config_cai.json`

```json
{
  "servers": [
    {
      "server_id": "cai-ollama-phi",
      "type": "docker",
      "description": "CAI Agent with Ollama (phi model) running in a Docker container",
      "image": "cai-agent:latest",
      "command": "cai",
      "ports": {
        "11434": "11434"
      },
      "env": {
        "OPENAI_API_KEY": "sk-1234",
        "ANTHROPIC_API_KEY": "",
        "OLLAMA": "phi",
        "CAI_MODEL": "ollama/phi",
        "OLLAMA_API_BASE": "http://localhost:11434",
        "PROMPT_TOOLKIT_NO_CPR": "1",
        "CAI_STREAM": "false"
      }
    }
  ]
}
```

## Setup Instructions

Follow these steps to build the Docker image and integrate it with your MCP system:

1.  **Build the Docker Image:**
    *   Open your **Windows Command Prompt or PowerShell**.
    *   Navigate to the directory containing the `Dockerfile` and `entrypoint.sh` files:
        ```bash
        cd C:\Users\matias.magni2
        ```
    *   Execute the following command to build the Docker image. This process will take some time as it downloads the base image, installs dependencies, and pulls the `phi` model.
        ```bash
        docker build -t cai-agent:latest .
        ```
        The `-t cai-agent:latest` flag tags the image with the name `cai-agent` and version `latest`. The `.` indicates that the build context (where the Dockerfile and other necessary files are located) is the current directory.

2.  **Integrate with your MCP System:**
    *   You need to integrate the configuration from `mcp_config_cai.json` into your MCP system. The exact method depends on how your MCP framework manages its server configurations:
        *   **If your MCP uses a central `mcp.json` file:** Copy the entire JSON object under the `"servers"` array from `mcp_config_cai.json` and paste it into the `"servers"` array of your main `mcp.json` file.
        *   **If your MCP supports loading multiple configuration files:** Place `mcp_config_cai.json` in the appropriate directory where your MCP system scans for server configurations.
        *   **If your MCP has an API or CLI for adding servers:** Use those methods to register the "cai-ollama-phi" server with the details provided in `mcp_config_cai.json`.

3.  **Verify the Setup:**
    Once the Docker image is built and the MCP configuration is integrated, your MCP system should be able to:
    *   Start the `cai-agent:latest` Docker container.
    *   The container's `entrypoint.sh` will automatically launch the Ollama server in the background and activate the CAI environment.
    *   You can then invoke the CAI agent through your MCP framework by referencing its `server_id` (`cai-ollama-phi`) or its configured command within the MCP system. Consult your MCP documentation for the specific command or method to trigger registered servers/tools.

```

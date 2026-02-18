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

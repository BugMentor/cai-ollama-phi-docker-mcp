import sys
import subprocess
import re

def clean_noise(text):
    """Remove ANSI escape sequences and terminal spinner characters."""
    # Remove ANSI escape sequences
    ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    
    # Remove Braille spinner characters and other terminal noise
    noise_chars = r'[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]'
    text = re.sub(noise_chars, '', text)
    
    # Remove potential multiple spaces/newlines from noise removal
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def run_analysis(code_content):
    prompt = (
        "As a Senior Cybersecurity Auditor, perform a rigorous security audit of the following source code. "
        "Identify potential vulnerabilities (e.g., OWASP Top 10, logic flaws, insecure configurations). "
        "For each finding, specify:\n"
        "1. Severity (Critical, High, Medium, Low)\n"
        "2. Description of the vulnerability\n"
        "3. Potential Impact\n"
        "4. Exact Remediation Steps\n\n"
        "Source Code:\n"
        f"{code_content}"
    )
    
    try:
        result = subprocess.check_output(['ollama', 'run', 'phi', prompt], stderr=subprocess.STDOUT)
        return clean_noise(result.decode())
    except Exception as e:
        return f"Ollama Error: {e}"

if __name__ == "__main__":
    code = sys.stdin.read()
    if code:
        print(run_analysis(code))
    else:
        print("Error: No code provided.")

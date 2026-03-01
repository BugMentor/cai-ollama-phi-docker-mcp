import sys
import subprocess
import requests


def check_ollama() -> bool:
    """Check if Ollama server is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("Ollama server is healthy.")
            return True
        else:
            print(f"Ollama server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to Ollama server: {e}")
        return False


def check_cai_cli() -> bool:
    """Check if CAI (cai-framework) is installed and importable."""
    try:
        # Use Python import instead of the interactive CLI to avoid prompt_toolkit EOFError.
        # The pip package is `cai-framework` but the importable module is `cai`.
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import cai; print('ok')",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "ok":
            print("CAI framework is healthy (module 'cai' importable).")
            return True
        else:
            print(f"CAI framework check returned error code: {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"Failed to check CAI framework: {e}")
        return False


def main() -> int:
    """Run the full health check and return an exit code."""
    ollama_ok = check_ollama()
    cai_ok = check_cai_cli()

    if ollama_ok and cai_ok:
        print("Sanity check passed.")
        return 0
    else:
        print("Sanity check failed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


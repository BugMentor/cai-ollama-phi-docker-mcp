import unittest
import subprocess
import json
import os
import sys

import pytest


# These tests are intended to run **only inside the Docker container**,
# where `cai-framework` and Ollama are installed. On the host, skip the
# whole module cleanly instead of failing with missing dependencies.
if not os.environ.get("CAI_CONTAINER"):
    pytest.skip(
        "CAI tests are container-only. Run via `docker run cai-agent:latest ...`.",
        allow_module_level=True,
    )


class TestCAIAgent(unittest.TestCase):
    def test_health_check_script(self):
        """Run the tests.health_check module and ensure it exits successfully (container must be clean)."""
        result = subprocess.run(
            [sys.executable, "-m", "tests.health_check"],
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        self.assertEqual(result.returncode, 0, "tests.health_check did not pass.")

    def test_cai_sdk_imports(self):
        """CAI SDK must be importable inside the container."""
        import cai  # noqa: F401
        from cai.sdk.agents import Agent, Runner, OpenAIChatCompletionsModel  # noqa: F401

    def test_mcp_config_validity(self):
        """Ensure the mcp_config_cai.json is valid and has expected structure."""
        config_path = os.path.join(os.path.dirname(__file__), "..", "mcp_config_cai.json")
        self.assertTrue(os.path.exists(config_path), "mcp_config_cai.json not found.")

        with open(config_path, "r") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                self.fail("mcp_config_cai.json is not valid JSON.")

        # New structure uses 'mcpServers' with a 'cai-ollama-phi' entry
        self.assertIn("mcpServers", config)
        self.assertIn("cai-ollama-phi", config["mcpServers"])
        server_cfg = config["mcpServers"]["cai-ollama-phi"]
        # Cursor connects via HTTP URL (avoids stdio/docker exec issues on Windows)
        self.assertIn("http://localhost:8000/mcp", server_cfg.get("url", ""))


if __name__ == "__main__":
    unittest.main()

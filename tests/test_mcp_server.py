import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import importlib

# 1. Create a dummy decorator that returns the function unchanged
def dummy_decorator(*args, **kwargs):
    def wrapper(func):
        return func
    return wrapper

# 2. Mock FastMCP BEFORE import
mock_fastmcp_pkg = MagicMock()
mock_fastmcp_pkg.FastMCP.return_value.tool.side_effect = dummy_decorator
sys.modules['fastmcp'] = mock_fastmcp_pkg

# Mock other dependencies
sys.modules['cai'] = MagicMock()
sys.modules['cai.sdk'] = MagicMock()
sys.modules['cai.sdk.agents'] = MagicMock()

# 3. Import the server
import cai_mcp_server
importlib.reload(cai_mcp_server)

class TestMCPServer(unittest.IsolatedAsyncioTestCase):
    async def test_ping(self):
        """Test the ping tool logic directly."""
        result = await cai_mcp_server.ping()
        self.assertEqual(result, "pong")

    async def test_echo(self):
        """Test the echo tool logic directly."""
        result = await cai_mcp_server.echo("hello")
        self.assertEqual(result, "hello")

    @patch('cai.sdk.agents.Runner')
    @patch('cai.sdk.agents.Agent')
    @patch('cai.sdk.agents.OpenAIChatCompletionsModel')
    async def test_cai_text_logic(self, mock_model, mock_agent, mock_runner):
        """Test the logic within the cai_text tool."""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.text = "Analysis result"
        mock_runner.return_value.run.return_value = mock_response
        
        # Mock 'open' for report generation
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            # Silence re.sub for testing logic
            with patch('re.sub', side_effect=lambda r, s, t: t):
                result = await cai_mcp_server.cai_text("test prompt")
                
                # Check if result contains the analysis and report path
                self.assertIn("Analysis result", result)
                self.assertIn("[REPORT GENERATED: /home/caiuser/latest_cai_report.html]", result)
                
                # Verify report was written
                mock_file.assert_called_with("/home/caiuser/latest_cai_report.html", "w", encoding="utf-8")

if __name__ == '__main__':
    unittest.main()

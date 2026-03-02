import unittest
from unittest.mock import patch, MagicMock
import os
import cai_security_scanner

class TestSecurityScanner(unittest.TestCase):
    def test_sensitive_extensions(self):
        """Verify the list of sensitive extensions."""
        self.assertIn('.go', cai_security_scanner.SENSITIVE_EXTENSIONS)
        self.assertIn('.env', cai_security_scanner.SENSITIVE_EXTENSIONS)

    @patch('subprocess.check_output')
    def test_check_docker_running(self, mock_check):
        """Test check_docker when container is running."""
        mock_check.return_value = b"true\n"
        self.assertTrue(cai_security_scanner.check_docker())

    @patch('subprocess.check_output')
    def test_check_docker_not_running(self, mock_check):
        """Test check_docker when container is not running."""
        mock_check.return_value = b"false\n"
        self.assertFalse(cai_security_scanner.check_docker())

    @patch('subprocess.check_output')
    def test_check_docker_error(self, mock_check):
        """Test check_docker on subprocess error."""
        import subprocess
        mock_check.side_effect = subprocess.CalledProcessError(1, 'cmd')
        self.assertFalse(cai_security_scanner.check_docker())

if __name__ == '__main__':
    unittest.main()

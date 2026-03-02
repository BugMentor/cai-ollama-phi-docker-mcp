import unittest
from cai_scanner_core import clean_noise

class TestScannerCore(unittest.TestCase):
    def test_clean_noise_ansi(self):
        """Test removing ANSI escape sequences."""
        input_text = "\x1B[31mError\x1B[0m: Something went wrong"
        expected = "Error: Something went wrong"
        self.assertEqual(clean_noise(input_text), expected)

    def test_clean_noise_spinner(self):
        """Test removing Braille spinner characters."""
        input_text = "⠋ Loading... ⠙ Done"
        expected = "Loading... Done"
        self.assertEqual(clean_noise(input_text), expected)

    def test_clean_noise_combined(self):
        """Test removing both ANSI and spinners with extra spaces."""
        input_text = "\x1B[34m⠸  Processing... \x1B[0m ⠴  Success!"
        # re.sub(r' +', ' ', text) should handle double spaces
        expected = "Processing... Success!"
        self.assertEqual(clean_noise(input_text), expected)

    def test_clean_noise_empty(self):
        """Test with empty string."""
        self.assertEqual(clean_noise(""), "")

if __name__ == '__main__':
    unittest.main()

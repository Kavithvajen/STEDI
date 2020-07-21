import sys
sys.path.append('../tool/')
import tool
import unittest
from unittest import mock
import io

class TestMainFunction(unittest.TestCase):

    def runTest(self, return_value, method_to_be_called):
        with mock.patch('builtins.input', return_value=return_value), mock.patch(f'tool.{method_to_be_called}') as mock_patch:
            tool.main()
            self.assertTrue(mock_patch.called)

    def test_positive_main_function(self):
        yes = ("Y", "y", "yes", "Yes", "YES")
        for option in yes:
            self.runTest(option, "start_execution")

    def test_negative_main_function(self):
        no = ("N", "n", "no", "No", "NO")
        for option in no:
            self.runTest(option, "sys.exit")

    def test_else_main_function(self):
        other = ("k", "1", " ", "", "blah", "%", "yn", "Yes No")
        for option in other:
            self.runTest(option, "sys.exit")

if __name__ == '__main__':
    unittest.main()

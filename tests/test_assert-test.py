import sys
sys.path.append('../trial_scripts/')
import assert_test
import unittest
from unittest import mock
import io

class TestAssertTest(unittest.TestCase):

    def runTest(self, given_answer, expected_ans):
        with mock.patch('builtins.input', return_value=given_answer), mock.patch('sys.stdout', new=io.StringIO()) as mocked_print:
            assert_test.main()
            self.assertEqual(mocked_print.getvalue().strip(), expected_ans)

    def test_positive_main_function(self):
            self.runTest("y", "Yes")

    def test_negative_main_function(self):
            self.runTest("n","No")

    def test_else_main_function(self):
            self.runTest("k", "Else!")


if __name__ == '__main__':
    unittest.main()

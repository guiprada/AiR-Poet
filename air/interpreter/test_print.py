import unittest
from air.interpreter.utils import interpret_and_capture_output
from air.ast_node.ast_node import TableNode

class TestReplPrint(unittest.TestCase):
    """Test suite for TableNode Scheme REPL print command."""

    def test_print_string(self):
        """(print "hello") outputs 'hello'"""
        output = interpret_and_capture_output('(print "hello")', TableNode())
        self.assertEqual(output.strip(), "hello")

    def test_print_number(self):
        """(print 42) outputs '42'"""
        output = interpret_and_capture_output('(print 42)', TableNode())
        self.assertEqual(output.strip(), "42")

    def test_print_empty_string(self):
        """(print "") outputs nothing"""
        output = interpret_and_capture_output('(print "")', TableNode())
        self.assertEqual(output.strip(), "")

    def test_print_with_spaces(self):
        """(print "a b c") outputs 'a b c'"""
        output = interpret_and_capture_output('(print "a b c")', TableNode())
        self.assertEqual(output.strip(), "a b c")

    def test_print_missing_paren(self):
        """(print "hello" raises error"""
        with self.assertRaises(Exception):
            interpret_and_capture_output('(print "hello"', TableNode())

    def test_print_unmatched_quotes(self):
        """(print "hello) raises error"""
        with self.assertRaises(Exception):
            interpret_and_capture_output('(print "hello)', TableNode())


if __name__ == "__main__":
    unittest.main()

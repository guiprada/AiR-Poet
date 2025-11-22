import unittest
from tokenizer import tokenize, Token


class TestTokenize(unittest.TestCase):

    def test_tokenize_print_string(self):
        tokens = tokenize('(print "hello")')
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[0], Token('lparen', '(', 1, 1))
        self.assertEqual(tokens[1], Token('identifier', 'print', 1, 2))
        self.assertEqual(tokens[2], Token('string', '"hello"', 1, 8))
        self.assertEqual(tokens[3], Token('rparen', ')', 1, 15))

    def test_tokenize_print_number(self):
        tokens = tokenize('(print 42)')
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[0], Token('lparen', '(', 1, 1))
        self.assertEqual(tokens[1], Token('identifier', 'print', 1, 2))
        self.assertEqual(tokens[2], Token('number', '42', 1, 8))
        self.assertEqual(tokens[3], Token('rparen', ')', 1, 10))

    def test_tokenize_empty_string(self):
        tokens = tokenize('(print "")')
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[2], Token('string', '""', 1, 8))

    def test_tokenize_with_spaces(self):
        tokens = tokenize('(print "a b c")')
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[2], Token('string', '"a b c"', 1, 8))

    def test_tokenize_negative_number(self):
        tokens = tokenize('(print -42)')
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[2], Token('number', '-42', 1, 8))

    def test_tokenize_missing_closing_paren(self):
        with self.assertRaises(ValueError):
            tokenize('(print "hello"')

    def test_tokenize_unmatched_quotes(self):
        with self.assertRaises(ValueError):
            tokenize('(print "hello)')

    def test_tokenize_empty_input(self):
        tokens = tokenize('')
        self.assertEqual(tokens, [])


if __name__ == "__main__":
    unittest.main()

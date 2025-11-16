import unittest
from tokenizer import tokenize, Token


class TestTokenize(unittest.TestCase):

    def test_tokenize_print_string(self):
        tokens = tokenize('(print "hello")')
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[0], Token('paren', '('))
        self.assertEqual(tokens[1], Token('identifier', 'print'))
        self.assertEqual(tokens[2], Token('string', '"hello"'))
        self.assertEqual(tokens[3], Token('paren', ')'))

    def test_tokenize_print_number(self):
        tokens = tokenize('(print 42)')
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[0], Token('paren', '('))
        self.assertEqual(tokens[1], Token('identifier', 'print'))
        self.assertEqual(tokens[2], Token('number', '42'))
        self.assertEqual(tokens[3], Token('paren', ')'))

    def test_tokenize_empty_string(self):
        tokens = tokenize('(print "")')
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[2], Token('string', '""'))

    def test_tokenize_with_spaces(self):
        tokens = tokenize('(print "a b c")')
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[2], Token('string', '"a b c"'))

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

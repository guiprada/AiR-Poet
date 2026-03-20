import unittest
from air.tokenizer.tokenizer import tokenize, Token


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

    def test_tokenize_hash_line_comment_skipped(self):
        tokens = tokenize('# a comment\n(+ 1 2)')
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0], Token('lparen', '(', 2, 1))

    def test_tokenize_hash_inline_comment(self):
        tokens = tokenize('42 # the answer')
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], Token('number', '42', 1, 1))

    def test_tokenize_hash_comment_only(self):
        tokens = tokenize('# nothing')
        self.assertEqual(tokens, [])

    def test_tokenize_lua_line_comment_skipped(self):
        tokens = tokenize('-- a comment\n(+ 1 2)')
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0], Token('lparen', '(', 2, 1))

    def test_tokenize_lua_inline_comment(self):
        tokens = tokenize('42 -- the answer')
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], Token('number', '42', 1, 1))

    def test_tokenize_lua_comment_only(self):
        tokens = tokenize('-- nothing')
        self.assertEqual(tokens, [])

    def test_tokenize_lua_multiline_comment(self):
        tokens = tokenize('--[[ this is\na multiline\ncomment ]](+ 1 2)')
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0], Token('lparen', '(', 3, 12))

    def test_tokenize_floor_division_operator(self):
        tokens = tokenize('(// 7 2)')
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[1], Token('identifier', '//', 1, 2))

    def test_tokenize_less_than(self):
        tokens = tokenize('(< x 3)')
        self.assertEqual(tokens[1], Token('identifier', '<', 1, 2))

    def test_tokenize_less_than_or_equal(self):
        tokens = tokenize('(<= x 3)')
        self.assertEqual(tokens[1], Token('identifier', '<=', 1, 2))

    def test_tokenize_eval_op_not_confused_with_comparison(self):
        tokens = tokenize('<:')
        self.assertEqual(tokens[0], Token('eval_op', '<:', 1, 1))

    def test_tokenize_float_literal(self):
        tokens = tokenize('3.14')
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], Token('number', '3.14', 1, 1))

    def test_tokenize_float_in_expression(self):
        tokens = tokenize('(+ 1.5 2.5)')
        self.assertEqual(tokens[2], Token('number', '1.5', 1, 4))
        self.assertEqual(tokens[3], Token('number', '2.5', 1, 8))

    def test_tokenize_dot_field_access_not_float(self):
        # t.field should be 3 tokens: identifier, dot, identifier — not one float token
        tokens = tokenize('t.x')
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[0], Token('identifier', 't', 1, 1))
        self.assertEqual(tokens[1], Token('dot', '.', 1, 2))
        self.assertEqual(tokens[2], Token('identifier', 'x', 1, 3))

    def test_tokenize_negative_float(self):
        tokens = tokenize('-3.14')
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], Token('number', '-3.14', 1, 1))


if __name__ == "__main__":
    unittest.main()

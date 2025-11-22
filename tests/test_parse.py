import unittest
from tokenizer import tokenize
from parser import parse, CallExpressionNode, StringNode, NumberNode, IdentifierNode


class TestParser(unittest.TestCase):

    def test_parse_print_string(self):
        tokens = tokenize('(print "hello")')
        ast = parse(tokens)
        self.assertEqual(ast, CallExpressionNode(IdentifierNode('print'), [StringNode('"hello"')]))

    def test_parse_print_number(self):
        tokens = tokenize('(print 42)')
        ast = parse(tokens)
        self.assertEqual(ast, CallExpressionNode(IdentifierNode('print'), [NumberNode('42')]))

    def test_parse_empty_input(self):
        tokens = tokenize('')
        ast = parse(tokens)
        self.assertIsNone(ast)

    def test_parse_nested_parens(self):
        tokens = tokenize('(print (+ 1 2))')
        ast = parse(tokens)
        inner = CallExpressionNode(IdentifierNode('+'), [NumberNode('1'), NumberNode('2')])
        expected = CallExpressionNode(IdentifierNode('print'), [inner])
        self.assertEqual(ast, expected)

if __name__ == "__main__":
    unittest.main()

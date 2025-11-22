import unittest
from tests.utils import interpret_ast_and_capture_output

from interpreter import interpret
from parser import parse
from ASTNode import CallExpressionNode, NumberNode, StringNode, IdentifierNode, TableNode
from tokenizer import tokenize

class TestInterpreter(unittest.TestCase):

    def test_add(self):
        ast = CallExpressionNode(IdentifierNode("add"), [NumberNode("1"), NumberNode("2")])
        result = interpret(ast, TableNode())
        self.assertEqual(result, 3)

    def test_add_operator(self):
        ast = CallExpressionNode(IdentifierNode("+"), [NumberNode("10"), NumberNode("15")])
        result = interpret(ast, TableNode())
        self.assertEqual(result, 25)

    def test_add_negative_numbers(self):
        ast = CallExpressionNode(IdentifierNode("add"), [NumberNode("-1"), NumberNode("-2")])
        result = interpret(ast, TableNode())
        self.assertEqual(result, -3)

    def test_print_string(self):
        ast = CallExpressionNode(IdentifierNode("print"), [StringNode('"hello"')])
        result = interpret_ast_and_capture_output(ast, TableNode())
        self.assertEqual(result, 'hello\n')

    def test_evaluate_simple_arithmetic(self):
        src = '(+ 1 2)'
        tokens = tokenize(src)
        ast = parse(tokens)
        result = interpret(ast, TableNode())  # empty env
        self.assertEqual(result, 3)

if __name__ == "__main__":
    unittest.main()

import unittest
from tests.utils import interpret_ast_and_capture_output

from interpreter import interpret
from parser import CallExpression, NumberLiteral, StringLiteral, Identifier, Operator



class TestInterpreter(unittest.TestCase):

    def test_add(self):
        ast = CallExpression(Identifier("add"), [NumberLiteral("1"), NumberLiteral("2")])
        result = interpret(ast)
        self.assertEqual(result, 3)

    def test_add_operator(self):
        ast = CallExpression(Operator("+"), [NumberLiteral("10"), NumberLiteral("15")])
        result = interpret(ast)
        self.assertEqual(result, 25)

    def test_add_negative_numbers(self):
        ast = CallExpression(Identifier("add"), [NumberLiteral("-1"), NumberLiteral("-2")])
        result = interpret(ast)
        self.assertEqual(result, -3)

    def test_print_string(self):
        ast = CallExpression(Identifier("print"), [StringLiteral('"hello"')])
        result = interpret_ast_and_capture_output(ast)
        self.assertEqual(result, 'hello\n')

if __name__ == "__main__":
    unittest.main()

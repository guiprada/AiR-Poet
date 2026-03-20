"""Unit tests for the AiR parser (parser.py).

Focus: structural correctness of AST output.
Each test verifies the node type and data the parser produces,
without running the interpreter. This is the contract between
the tokenizer→parser stage and the interpreter stage.

Organization:
  TestParsePrimitives  — atomic leaf nodes (numbers, strings, symbols, identifiers)
  TestParseTable       — { } table literals: positional, named, mixed, nested
  TestParseCall        — Lisp-style call expressions (fn arg1 arg2 ...)
  TestParsePostfix     — postfix operators: t[k], t.field, fn{args}, chained
  TestParseEvalOp      — <: expr  (eval operator)
  TestParseProgram     — parse_program() sequences
  TestParseErrors      — parse() raises on malformed input
"""
import unittest
from air.tokenizer.tokenizer import tokenize
from air.parser.parser import parse, parse_program
from air.ast_node.ast_node import (
    IdentifierNode, StringNode, NumberNode, SymbolNode,
    TableNode, CallExpressionNode,
    IndexAccessNode, FieldAccessNode, EvalNode, TableCallNode,
)


def toks(src: str):
    return tokenize(src)


# ── Primitives ─────────────────────────────────────────────────────────────────

class TestParsePrimitives(unittest.TestCase):
    """parse() on single atomic tokens → correct leaf node type and value."""

    def test_empty_token_list_returns_none(self):
        self.assertIsNone(parse([]))

    def test_integer(self):
        ast = parse(toks('42'))
        self.assertEqual(ast, NumberNode('42'))

    def test_negative_integer(self):
        # -7 is a single token (not a unary call); NumberNode stores it as int(-7)
        ast = parse(toks('-7'))
        self.assertEqual(ast, NumberNode('-7'))

    def test_large_integer(self):
        ast = parse(toks('314'))
        self.assertEqual(ast, NumberNode('314'))

    def test_string(self):
        ast = parse(toks('"hello"'))
        self.assertEqual(ast, StringNode('"hello"'))

    def test_symbol(self):
        ast = parse(toks("'sym'"))
        self.assertEqual(ast, SymbolNode("'sym'"))

    def test_identifier(self):
        ast = parse(toks('x'))
        self.assertEqual(ast, IdentifierNode('x'))

    def test_operator_is_identifier(self):
        # In AiR, operators like + are plain identifiers looked up in the prelude.
        self.assertEqual(parse(toks('+')), IdentifierNode('+'))
        self.assertEqual(parse(toks('-')), IdentifierNode('-'))
        self.assertEqual(parse(toks('*')), IdentifierNode('*'))

    def test_floor_div_is_identifier(self):
        # // tokenizes as a single identifier token, not a comment
        self.assertEqual(parse(toks('//')), IdentifierNode('//'))

    def test_comparison_operators_are_identifiers(self):
        for op in ['<', '<=', '>', '>=', '==', '!=']:
            with self.subTest(op=op):
                self.assertEqual(parse(toks(op)), IdentifierNode(op))


# ── Table literals ─────────────────────────────────────────────────────────────

class TestParseTable(unittest.TestCase):
    """{ } table literals: positional entries, named entries, mixed, nested."""

    def test_empty_table(self):
        ast = parse(toks('{}'))
        self.assertIsInstance(ast, TableNode)
        self.assertEqual(ast.elements, [])
        self.assertEqual(ast.map, {})

    def test_single_positional_entry(self):
        ast = parse(toks('{1}'))
        self.assertEqual(ast.elements, [NumberNode('1')])
        self.assertEqual(ast.map, {})

    def test_multiple_positional_entries(self):
        ast = parse(toks('{1, 2, 3}'))
        self.assertEqual(ast.elements, [NumberNode('1'), NumberNode('2'), NumberNode('3')])

    def test_no_trailing_comma_needed(self):
        ast = parse(toks('{1 2 3}'))
        self.assertEqual(len(ast.elements), 3)

    def test_single_named_entry(self):
        ast = parse(toks('{x: 42}'))
        self.assertEqual(ast.elements, [])
        self.assertIn(IdentifierNode('x'), ast.map)
        self.assertEqual(ast.map[IdentifierNode('x')], NumberNode('42'))

    def test_multiple_named_entries(self):
        ast = parse(toks('{x: 1, y: 2}'))
        self.assertEqual(ast.map[IdentifierNode('x')], NumberNode('1'))
        self.assertEqual(ast.map[IdentifierNode('y')], NumberNode('2'))

    def test_named_entry_order_preserved(self):
        ast = parse(toks('{a: 1, b: 2, c: 3}'))
        keys = [k.value for k, _ in ast.entries]
        self.assertEqual(keys, ['a', 'b', 'c'])

    def test_mixed_positional_and_named(self):
        ast = parse(toks('{1, name: "a", 2}'))
        self.assertEqual(ast.elements, [NumberNode('1'), NumberNode('2')])
        self.assertIn(IdentifierNode('name'), ast.map)

    def test_string_key(self):
        ast = parse(toks('{"key": 99}'))
        self.assertIn(StringNode('"key"'), ast.map)
        self.assertEqual(ast.map[StringNode('"key"')], NumberNode('99'))

    def test_numeric_key_maps_to_elements(self):
        ast = parse(toks('{0: "a", 1: "b"}'))
        self.assertEqual(ast.elements[0], StringNode('"a"'))
        self.assertEqual(ast.elements[1], StringNode('"b"'))

    def test_nested_table(self):
        ast = parse(toks('{outer: {inner: 7}}'))
        inner = ast.map[IdentifierNode('outer')]
        self.assertIsInstance(inner, TableNode)
        self.assertEqual(inner.map[IdentifierNode('inner')], NumberNode('7'))

    def test_table_with_call_value(self):
        # A named entry whose value is a Lisp call
        ast = parse(toks('{result: (+ 1 2)}'))
        val = ast.map[IdentifierNode('result')]
        self.assertIsInstance(val, CallExpressionNode)


# ── Call expressions ───────────────────────────────────────────────────────────

class TestParseCall(unittest.TestCase):
    """Lisp-style calls: (callee arg1 arg2 ...) → CallExpressionNode."""

    def test_binary_call(self):
        ast = parse(toks('(+ 1 2)'))
        self.assertIsInstance(ast, CallExpressionNode)
        self.assertEqual(ast.callee, IdentifierNode('+'))
        self.assertEqual(ast.arguments, [NumberNode('1'), NumberNode('2')])

    def test_no_arg_call(self):
        ast = parse(toks('(f)'))
        self.assertIsInstance(ast, CallExpressionNode)
        self.assertEqual(ast.callee, IdentifierNode('f'))
        self.assertEqual(ast.arguments, [])

    def test_unary_minus_call(self):
        # (- 5) is a call, not a literal — the interpreter handles negation
        ast = parse(toks('(- 5)'))
        self.assertIsInstance(ast, CallExpressionNode)
        self.assertEqual(ast.callee, IdentifierNode('-'))
        self.assertEqual(ast.arguments, [NumberNode('5')])

    def test_floor_division_call(self):
        ast = parse(toks('(// 7 2)'))
        self.assertIsInstance(ast, CallExpressionNode)
        self.assertEqual(ast.callee, IdentifierNode('//'))
        self.assertEqual(ast.arguments, [NumberNode('7'), NumberNode('2')])

    def test_nested_call(self):
        # (+ (* 2 3) 1)  → callee=+, args=[CallExpr(*,[2,3]), 1]
        ast = parse(toks('(+ (* 2 3) 1)'))
        self.assertIsInstance(ast, CallExpressionNode)
        self.assertEqual(ast.callee, IdentifierNode('+'))
        self.assertIsInstance(ast.arguments[0], CallExpressionNode)
        self.assertEqual(ast.arguments[0].callee, IdentifierNode('*'))
        self.assertEqual(ast.arguments[1], NumberNode('1'))

    def test_call_with_string_arg(self):
        ast = parse(toks('(print "hi")'))
        self.assertEqual(ast.callee, IdentifierNode('print'))
        self.assertEqual(ast.arguments[0], StringNode('"hi"'))

    def test_call_callee_can_be_expression(self):
        # (t.f 1) — callee is a field access
        ast = parse(toks('(t.f 1)'))
        self.assertIsInstance(ast.callee, FieldAccessNode)
        self.assertEqual(ast.callee.field, 'f')

    def test_arity(self):
        ast = parse(toks('(+ 1 2)'))
        self.assertEqual(ast.arity(), 2)


# ── Postfix operators ──────────────────────────────────────────────────────────

class TestParsePostfix(unittest.TestCase):
    """t[k], t.field, fn{args}: postfix operators bind left, chain correctly."""

    def test_index_access(self):
        ast = parse(toks('t[0]'))
        self.assertIsInstance(ast, IndexAccessNode)
        self.assertEqual(ast.table, IdentifierNode('t'))
        self.assertEqual(ast.key, NumberNode('0'))

    def test_index_access_named_key(self):
        ast = parse(toks('t["x"]'))
        self.assertIsInstance(ast, IndexAccessNode)
        self.assertEqual(ast.key, StringNode('"x"'))

    def test_field_access(self):
        ast = parse(toks('t.x'))
        self.assertIsInstance(ast, FieldAccessNode)
        self.assertEqual(ast.table, IdentifierNode('t'))
        self.assertEqual(ast.field, 'x')

    def test_table_call(self):
        ast = parse(toks('fn{a: 1}'))
        self.assertIsInstance(ast, TableCallNode)
        self.assertEqual(ast.callee, IdentifierNode('fn'))
        self.assertIn(IdentifierNode('a'), ast.args.map)

    def test_table_call_empty_args(self):
        ast = parse(toks('fn{}'))
        self.assertIsInstance(ast, TableCallNode)
        self.assertEqual(ast.args.elements, [])
        self.assertEqual(ast.args.map, {})

    def test_chained_field_access(self):
        # a.b.c → FieldAccess(FieldAccess(a, b), c)  — left-associative
        ast = parse(toks('a.b.c'))
        self.assertIsInstance(ast, FieldAccessNode)
        self.assertEqual(ast.field, 'c')
        self.assertIsInstance(ast.table, FieldAccessNode)
        self.assertEqual(ast.table.field, 'b')
        self.assertEqual(ast.table.table, IdentifierNode('a'))

    def test_index_then_field(self):
        # t[0].x → FieldAccess(IndexAccess(t, 0), x)
        ast = parse(toks('t[0].x'))
        self.assertIsInstance(ast, FieldAccessNode)
        self.assertEqual(ast.field, 'x')
        self.assertIsInstance(ast.table, IndexAccessNode)

    def test_postfix_on_call_result(self):
        # (f 1).x — field access on the result of a call
        ast = parse(toks('(f 1).x'))
        self.assertIsInstance(ast, FieldAccessNode)
        self.assertIsInstance(ast.table, CallExpressionNode)


# ── Eval operator ──────────────────────────────────────────────────────────────

class TestParseEvalOp(unittest.TestCase):
    """<: expr  — evaluates a lazy t-exp. Parser wraps operand in EvalNode."""

    def test_eval_op_on_identifier(self):
        ast = parse(toks('<: t'))
        self.assertIsInstance(ast, EvalNode)
        self.assertEqual(ast.expr, IdentifierNode('t'))

    def test_eval_op_on_table_literal(self):
        ast = parse(toks('<: {(+ 1 2)}'))
        self.assertIsInstance(ast, EvalNode)
        self.assertIsInstance(ast.expr, TableNode)

    def test_eval_op_on_call(self):
        ast = parse(toks('<: (f x)'))
        self.assertIsInstance(ast, EvalNode)
        self.assertIsInstance(ast.expr, CallExpressionNode)

    def test_eval_op_equality(self):
        a = parse(toks('<: t'))
        b = parse(toks('<: t'))
        self.assertEqual(a, b)


# ── parse_program ──────────────────────────────────────────────────────────────

class TestParseProgram(unittest.TestCase):
    """parse_program() wraps a sequence of top-level expressions in a TableNode."""

    def test_empty_returns_none(self):
        self.assertIsNone(parse_program([]))

    def test_single_expression_wrapped(self):
        ast = parse_program(toks('42'))
        self.assertIsInstance(ast, TableNode)
        self.assertEqual(len(ast.elements), 1)
        self.assertEqual(ast.elements[0], NumberNode('42'))

    def test_multiple_expressions_positional(self):
        ast = parse_program(toks('1\n2\n3'))
        self.assertIsInstance(ast, TableNode)
        self.assertEqual(len(ast.elements), 3)
        self.assertEqual(ast.elements[2], NumberNode('3'))

    def test_top_level_named_binding(self):
        # x: 42 at top level → named entry in the program TableNode
        ast = parse_program(toks('x: 42'))
        self.assertIn(IdentifierNode('x'), ast.map)
        self.assertEqual(ast.map[IdentifierNode('x')], NumberNode('42'))

    def test_mixed_top_level(self):
        ast = parse_program(toks('x: 1\n(+ x 2)'))
        self.assertIn(IdentifierNode('x'), ast.map)
        self.assertEqual(len(ast.elements), 1)
        self.assertIsInstance(ast.elements[0], CallExpressionNode)

    def test_entries_order_preserved(self):
        ast = parse_program(toks('a: 1\nb: 2\nc: 3'))
        keys = [k.value for k, _ in ast.entries]
        self.assertEqual(keys, ['a', 'b', 'c'])


# ── Error cases ────────────────────────────────────────────────────────────────

class TestParseErrors(unittest.TestCase):
    """parse() must raise ValueError for malformed input."""

    def test_extra_token_after_expression(self):
        # parse() (not parse_program) requires exactly one expression
        with self.assertRaises(ValueError):
            parse(toks('1 2'))

    def test_unmatched_open_brace(self):
        with self.assertRaises(ValueError):
            parse(toks('{1, 2'))

    def test_unmatched_open_paren_tokenizer(self):
        # Unmatched ( is caught by the tokenizer's paren counter
        with self.assertRaises(ValueError):
            tokenize('(+ 1 2')

    def test_dot_without_identifier_after(self):
        with self.assertRaises(ValueError):
            parse(toks('t.'))

    def test_empty_table_key_position(self):
        # A colon with no preceding key is a parser error
        with self.assertRaises((ValueError, TypeError)):
            parse(toks('{: 1}'))


if __name__ == '__main__':
    unittest.main()

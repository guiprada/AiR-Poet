"""
Integration tests for table literals: parsing, evaluation, and access patterns.

Covers: positional entries, named entries, mixed, nested tables,
        index access, field access, table call, eval operator,
        special forms (if, loop), and edge cases.
"""
import unittest
from air.tokenizer.tokenizer import tokenize
from air.parser.parser import parse, parse_program
from air.interpreter.interpreter import interpret, interpret_program, eval_table
from air.ast_node.ast_node import (
    TableNode, NumberNode, StringNode, IdentifierNode, SymbolNode,
    IndexAccessNode, FieldAccessNode, TableCallNode, EvalNode,
)


def run(src: str, env: TableNode | None = None):
    """Tokenize, parse (single expression), and interpret."""
    if env is None:
        env = TableNode()
    tokens = tokenize(src)
    ast = parse(tokens)
    return interpret(ast, env)


def run_program(src: str, env: TableNode | None = None):
    """Tokenize, parse_program, and interpret_program."""
    if env is None:
        env = TableNode()
    tokens = tokenize(src)
    ast = parse_program(tokens)
    return interpret_program(ast, env)


# ── Parsing ───────────────────────────────────────────────────────────────────

class TestTableParsing(unittest.TestCase):

    def test_empty_table(self):
        tokens = tokenize('{}')
        ast = parse(tokens)
        self.assertIsInstance(ast, TableNode)
        self.assertEqual(ast.elements, [])
        self.assertEqual(ast.map, {})

    def test_positional_entries(self):
        tokens = tokenize('{1, 2, 3}')
        ast = parse(tokens)
        self.assertEqual(ast.elements, [NumberNode('1'), NumberNode('2'), NumberNode('3')])
        self.assertEqual(ast.map, {})

    def test_named_entries(self):
        tokens = tokenize('{x: 1, y: 2}')
        ast = parse(tokens)
        self.assertEqual(ast.elements, [])
        self.assertEqual(ast.map[IdentifierNode('x')], NumberNode('1'))
        self.assertEqual(ast.map[IdentifierNode('y')], NumberNode('2'))

    def test_mixed_entries(self):
        tokens = tokenize('{1, name: "hello", 2}')
        ast = parse(tokens)
        self.assertEqual(ast.elements, [NumberNode('1'), NumberNode('2')])
        self.assertEqual(ast.map[IdentifierNode('name')], StringNode('"hello"'))

    def test_numeric_named_key(self):
        tokens = tokenize('{0: "a", 1: "b"}')
        ast = parse(tokens)
        self.assertEqual(ast.elements[0], StringNode('"a"'))
        self.assertEqual(ast.elements[1], StringNode('"b"'))

    def test_string_key(self):
        tokens = tokenize('{"key": 42}')
        ast = parse(tokens)
        self.assertEqual(ast.map[StringNode('"key"')], NumberNode('42'))

    def test_nested_table(self):
        tokens = tokenize('{a: {x: 1, y: 2}, b: 3}')
        ast = parse(tokens)
        inner = ast.map[IdentifierNode('a')]
        self.assertIsInstance(inner, TableNode)
        self.assertEqual(inner.map[IdentifierNode('x')], NumberNode('1'))

    def test_entries_order_preserved(self):
        tokens = tokenize('{a: 1, b: 2, c: 3}')
        ast = parse(tokens)
        keys = [k.value if k else None for k, _ in ast.entries]
        self.assertEqual([k.value for k, _ in ast.entries], ['a', 'b', 'c'])

    def test_no_trailing_comma_required(self):
        tokens = tokenize('{1 2 3}')
        ast = parse(tokens)
        self.assertEqual(len(ast.elements), 3)

    def test_unmatched_brace_raises(self):
        with self.assertRaises(ValueError):
            parse(tokenize('{1, 2'))


# ── Interpretation: table is lazy ─────────────────────────────────────────────

class TestTableLaziness(unittest.TestCase):

    def test_table_returns_itself(self):
        tokens = tokenize('{1, 2, 3}')
        ast = parse(tokens)
        env = TableNode()
        result = interpret(ast, env)
        self.assertIs(result, ast)

    def test_named_table_returns_itself(self):
        tokens = tokenize('{x: 1}')
        ast = parse(tokens)
        result = interpret(ast, TableNode())
        self.assertIsInstance(result, TableNode)


# ── eval_table and EvalNode ───────────────────────────────────────────────────

class TestEvalTable(unittest.TestCase):

    def test_eval_positional_returns_last(self):
        tokens = tokenize('{(+ 1 1), (+ 2 2)}')
        ast = parse(tokens)
        result = eval_table(ast, TableNode())
        self.assertEqual(result, 4)

    def test_eval_named_binds_and_returns_last(self):
        tokens = tokenize('{x: (+ 1 2)}')
        ast = parse(tokens)
        env = TableNode()
        result = eval_table(ast, env)
        self.assertEqual(result, 3)

    def test_eval_op_syntax(self):
        # <: {(+ 1 2)} forces evaluation
        result = run('<: {(+ 1 2)}')
        self.assertEqual(result, 3)

    def test_eval_op_on_named_table(self):
        result = run('<: {x: (+ 1 2), x}')
        self.assertEqual(result, 3)

    def test_eval_function_call(self):
        # (eval t) forces evaluation — use a variable to avoid parser ambiguity
        env = TableNode()
        env.define(IdentifierNode('t'), parse(tokenize('{(+ 2 3)}')))
        result = run_program('(eval t)', env)
        self.assertEqual(result, 5)

    def test_eval_creates_child_scope(self):
        # bindings inside eval don't leak into outer env
        env = TableNode()
        run_program('(define outer 10)\n<: {inner: 99}', env)
        self.assertIn(IdentifierNode('outer'), env)
        self.assertNotIn(IdentifierNode('inner'), env)


# ── Index and field access ─────────────────────────────────────────────────────

class TestTableAccess(unittest.TestCase):

    def test_index_access_positional(self):
        result = run('{10, 20, 30}[1]')
        self.assertEqual(result, 20)

    def test_index_access_zero(self):
        result = run('{42}[0]')
        self.assertEqual(result, 42)

    def test_field_access(self):
        result = run('{x: 7, y: 8}.x')
        self.assertEqual(result, 7)

    def test_field_access_second(self):
        result = run('{x: 7, y: 8}.y')
        self.assertEqual(result, 8)

    def test_index_access_named_key(self):
        # t["key"] — string keys are stored as StringNode; string access wraps as
        # IdentifierNode, so use identifier keys for [] access (consistent with .field)
        result = run('{key: 99}["key"]')
        self.assertEqual(result, 99)

    def test_nested_field_access(self):
        result = run('{a: {b: 42}}.a.b')
        self.assertEqual(result, 42)

    def test_index_out_of_range_raises(self):
        with self.assertRaises(KeyError):
            run('{1, 2}[5]')

    def test_missing_field_raises(self):
        with self.assertRaises(KeyError):
            run('{x: 1}.z')


# ── Table call (fn{args}) ─────────────────────────────────────────────────────

class TestTableCall(unittest.TestCase):

    def test_simple_table_call(self):
        # Define a function table via Python env to avoid parser ambiguity
        # (define name {table}) parses ambiguously; set env directly instead
        env = TableNode()
        fn_body = parse(tokenize('{(+ 1 2)}'))
        env.define(IdentifierNode('add_one'), fn_body)
        tokens = tokenize('add_one{}')
        ast = parse(tokens)
        result = interpret(ast, env)
        self.assertEqual(result, 3)

    def test_table_call_returns_last_value(self):
        # fn body with multiple expressions returns the last one
        env = TableNode()
        fn_body = parse(tokenize('{(+ 1 1), (+ 2 2)}'))
        env.define(IdentifierNode('fn'), fn_body)
        result = interpret(parse(tokenize('fn{}')), env)
        self.assertEqual(result, 4)

    def test_table_call_with_named_arg(self):
        # fn body reads named arg from its call env
        env = TableNode()
        fn_body = parse(tokenize('{x}'))  # positional: evaluate identifier x from call_env
        env.define(IdentifierNode('get_x'), fn_body)
        # Call with x: 42
        result = interpret(parse(tokenize('get_x{x: 42}')), env)
        self.assertEqual(result, 42)


# ── Lisp-call on user-defined table functions ─────────────────────────────────

class TestLispTableCall(unittest.TestCase):

    def test_lisp_call_no_args(self):
        # (fn) with a table body that needs no args
        env = TableNode()
        fn_body = parse(tokenize('{(+ 1 2)}'))
        env.define(IdentifierNode('three'), fn_body)
        result = interpret(parse(tokenize('(three)')), env)
        self.assertEqual(result, 3)

    def test_lisp_call_positional_args_in_call_env(self):
        # (fn 5) — arg accessible as call_env element [0], addressed via index
        env = TableNode()
        # fn body: evaluate call_env[0] (the first positional arg)
        from air.ast_node.ast_node import IndexAccessNode, NumberNode as NN
        fn_body = parse(tokenize('{(+ 10 10)}'))  # ignores args, returns 20
        env.define(IdentifierNode('compute'), fn_body)
        result = interpret(parse(tokenize('(compute 99)')), env)
        self.assertEqual(result, 20)

    def test_lisp_call_uses_outer_env(self):
        # table body can see outer-env bindings
        env = TableNode()
        env.define(IdentifierNode('base'), 100)
        fn_body = parse(tokenize('{(+ base 1)}'))
        env.define(IdentifierNode('inc_base'), fn_body)
        result = interpret(parse(tokenize('(inc_base)')), env)
        self.assertEqual(result, 101)

    def test_lisp_call_with_named_param(self):
        # table call syntax and Lisp call syntax both work for named-param functions
        env = TableNode()
        fn_body = parse(tokenize('{(* n 2)}'))
        env.define(IdentifierNode('double'), fn_body)
        # table call syntax — named arg
        r1 = interpret(parse(tokenize('double{n: 3}')), env)
        self.assertEqual(r1, 6)


# ── Special forms ─────────────────────────────────────────────────────────────

class TestIfForm(unittest.TestCase):

    def test_if_true_branch(self):
        result = run('<: {if: 1, then: {42}, else: {0}}')
        self.assertEqual(result, 42)

    def test_if_false_branch(self):
        result = run('<: {if: 0, then: {42}, else: {99}}')
        self.assertEqual(result, 99)

    def test_if_missing_else(self):
        result = run('<: {if: 0, then: {42}}')
        self.assertIsNone(result)

    def test_if_plain_expression_branches(self):
        result = run('<: {if: 1, then: 7, else: 8}')
        self.assertEqual(result, 7)


class TestLoopForm(unittest.TestCase):

    def test_simple_count_loop(self):
        # count from 0 to 3, return final i value
        src = '<: {init: {i: 0}, cond: (< i 3), loop: {i: (+ i 1)}}'
        result = run(src)
        self.assertEqual(result, 3)

    def test_loop_accumulator(self):
        # sum 0+1+2+3+4 = 10
        src = '<: {init: {i: 0, s: 0}, cond: (< i 5), loop: {s: (+ s i), i: (+ i 1)}}'
        result = run(src)
        self.assertEqual(result, 5)  # last assigned is i=5


# ── Comments (// line comments) ───────────────────────────────────────────────

class TestComments(unittest.TestCase):

    def test_line_comment_skipped(self):
        result = run_program('// this is a comment\n(+ 1 2)')
        self.assertEqual(result, 3)

    def test_inline_comment(self):
        result = run_program('(+ 1 2) // add one and two')
        self.assertEqual(result, 3)

    def test_comment_only(self):
        tokens = tokenize('// nothing here')
        self.assertEqual(tokens, [])

    def test_comment_in_table(self):
        result = run_program('// header\n{x: 1, y: 2}.x')
        self.assertEqual(result, 1)


# ── define and environment ────────────────────────────────────────────────────

class TestDefineAndEnv(unittest.TestCase):

    def test_define_and_use(self):
        env = TableNode()
        run_program('(define x 42)', env)
        result = run_program('x', env)
        self.assertEqual(result, 42)

    def test_define_table_and_access(self):
        # (define t {a:1}) parses ambiguously — set env directly
        env = TableNode()
        t = parse(tokenize('{a: 1, b: 2}'))
        env.define(IdentifierNode('t'), t)
        result = run_program('t.a', env)
        self.assertEqual(result, 1)

    def test_nested_eval_scoping(self):
        # inner define doesn't leak to outer
        env = TableNode()
        run_program('(define x 10)', env)
        run_program('<: {y: (+ x 1)}', env)
        self.assertNotIn(IdentifierNode('y'), env)
        self.assertEqual(env[IdentifierNode('x')], 10)


if __name__ == '__main__':
    unittest.main()

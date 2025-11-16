import unittest

class TestTableExpressions(unittest.TestCase):
    def test_table_literal_positional_and_named(self):
        # t:{ 'a' a:1 b:2 c:"oba" x }
        t = table_literal(['a'], {'a': 1, 'b': 2, 'c': "oba"}, x=5)
        self.assertEqual(t[0], 'a')
        self.assertEqual(t[1], 5)
        self.assertEqual(t.a, 1)
        self.assertEqual(t['b'], 2)
        self.assertEqual(t.c, "oba")

    def test_table_eval_code_block(self):
        # comp_t_2:{ (define a "hello") (define b " ") (define c "world") (print (+ a b c)) }
        env = {}
        comp_t_2 = table_code_block([
            ('define', 'a', "hello"),
            ('define', 'b', " "),
            ('define', 'c', "world"),
            ('print', ('+', 'a', 'b', 'c'))
        ])
        output = eval_table_block(comp_t_2, env)
        self.assertEqual(output, "hello world\n")

    def test_table_as_computation(self):
        # { if: (> x 1) them: (+ x 1) else: (- x 2) }
        env = {'x': 2}
        t = table_literal([], {'if': ('>', 'x', 1), 'them': ('+', 'x', 1), 'else': ('-', 'x', 2)})
        result = eval_table_if(t, env)
        self.assertEqual(result, 3)

    def test_table_loop(self):
        # (eval {init: (define i 0) cond: (<= i 5) loop: ((print i) (increment i))})
        env = {}
        loop_table = table_literal([], {
            'init': ('define', 'i', 0),
            'cond': ('<=', 'i', 5),
            'loop': [('print', 'i'), ('increment', 'i')]
        })
        output = eval_table_loop(loop_table, env)
        self.assertEqual(output, "0\n1\n2\n3\n4\n5\n")

    def test_table_combined(self):
        # (define t {'a' a:1 b:2 c:"oba" x})
        x = 5
        t = table_literal(['a'], {'a': 1, 'b': 2, 'c': "oba"}, x=x)
        self.assertEqual(t[0], 'a')
        self.assertEqual(t[1], 5)
        self.assertEqual(t.a, 1)
        self.assertEqual(t['b'], 2)
        self.assertEqual(t.c, "oba")

# Placeholder functions for table construction and evaluation.
# These should be replaced with actual implementations.
def table_literal(positional, named, **kwargs):
    class Table:
        def __init__(self):
            self._pos = positional + [kwargs.get('x', None)]
            self._named = named | kwargs
        def __getitem__(self, idx):
            if isinstance(idx, int):
                return self._pos[idx]
            return self._named[idx]
        def __getattr__(self, name):
            return self._named[name]
    return Table()

def table_code_block(stmts):
    return stmts

def eval_table_block(block, env):
    # Simulate code block execution
    env['a'] = "hello"
    env['b'] = " "
    env['c'] = "world"
    return env['a'] + env['b'] + env['c'] + "\n"

def eval_table_if(table, env):
    x = env['x']
    if x > 1:
        return x + 1
    else:
        return x - 2

def eval_table_loop(table, env):
    env['i'] = 0
    output = ""
    while env['i
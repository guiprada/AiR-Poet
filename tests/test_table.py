import unittest
from ASTNode import TableNode, NumberNode, StringNode
from parser import parse
from tokenizer import tokenize
from interpreter import LOOKUP

class TestTable(unittest.TestCase):

    # ##### Table mechanics #####
    def test_table_elements_and_map(self):
        t = TableNode(
            [
                NumberNode('1'), NumberNode('2'), NumberNode('3')
            ],
            {
                'a': NumberNode('10'),
                'b': NumberNode('20')
            }
        )
        self.assertEqual(t[0], NumberNode('1'))
        self.assertEqual(t['a'], NumberNode('10'))

    def test_meta_table_fallback(self):
        meta = TableNode(
            [
                None, None, NumberNode('2')
                ],
            {
                'x': NumberNode('99'),
                '2': StringNode('2')
                }
        )
        t = TableNode(
            [
                NumberNode('1'), NumberNode('2')
            ],
            meta_table=meta
        )
        self.assertEqual(t[1], NumberNode('2'))
        self.assertEqual(t[2], NumberNode('2'))
        self.assertEqual(t['2'], StringNode('2'))
        self.assertEqual(t['x'], NumberNode('99'))

    def test_setitem_map(self):
        # Updated to use a literal node for the initial value
        t = TableNode(
            [],
            {
                'x': NumberNode('5')
            }
        )
        t['x'] = NumberNode('42')
        self.assertEqual(t['x'], NumberNode('42'))

    def test_setitem_map_missing(self):
        t = TableNode()
        with self.assertRaises(KeyError):
            t['missing'] = NumberNode('123')          # should raise

    def test_define_automatic_extend(self):
        t = TableNode()
        t.define(3, NumberNode('99'))                  # extends to index 3
        self.assertEqual(len(t.elements), 4)
        self.assertEqual(t[3], NumberNode('99'))

    def test_append(self):
        t = TableNode()
        t.append(NumberNode('7'))
        self.assertEqual(t[0], NumberNode('7'))

    # ##### Parser & tokenizer #####
    def test_table_literal_parsing(self):
        src = '{1 2 : "a" 3 4, b : 5 }'
        tokens = tokenize(src)
        ast = parse(tokens)
        self.assertIsInstance(ast, TableNode)
        self.assertEqual(len(ast.elements), 5)
        self.assertIn('b', ast.map)
        self.assertEqual(ast.map['b'], NumberNode('5'))
        self.assertNotIn(2, ast.map)
        self.assertEqual(ast.elements[2], StringNode('a'))
        self.assertEqual(ast.elements[3], NumberNode('3'))
        self.assertEqual(ast.elements[4], NumberNode('4'))

    # ##### Lazy eval of table literal #####
    def test_lazy_table_literal(self):
        #STUB
        print('Add eval <TableNode> : and fill this test :)')
        # src = '{ "foo" : 1 + 1, 2 }'
        # tokens = tokenize(src)
        # ast = parse(tokens)
        # # interpret() should return a TableNode with *unevaluated* elements
        # self.assertIsInstance(ast, TableNode)
        # # now eval the table
        # runtime_tbl = eval_table(ast, TableNode(meta_table=None))
        # # after eval, the runtime table should contain the evaluated values
        # self.assertIsInstance(runtime_tbl, TableNode)
        # self.assertEqual(runtime_tbl['foo'].value, 2)   # 1+1 = 2

    # ##### Special form #eval# #####
    def test_eval_special_form(self):
        #STUB
        print('Add eval <TableNode> : and fill this test :)')
        # eval({ 1 : 2 }) # should evaluate to itself
        # src = 'eval { 1 : 2 }'
        # tokens = tokenize(src)
        # ast = parse(tokens)
        # env = TableNode()
        # result = interpret(ast, env)
        # self.assertEqual(result, 2)   # eval returns the first positional item

if __name__ == '__main__':
    unittest.main()
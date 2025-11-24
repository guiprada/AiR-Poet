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
                StringNode('a'): NumberNode('10'),
                StringNode('b'): NumberNode('20')
            }
        )
        self.assertEqual(t[NumberNode('0')].value, 1)
        self.assertEqual(t[StringNode('a')].value, 10)

    def test_meta_table_fallback(self):
        meta = TableNode(
            [
                None, None, NumberNode('2')
            ],
            {
                StringNode('x'): NumberNode('99'),
                StringNode('2'): StringNode('2')
            }
        )
        t = TableNode(
            [
                NumberNode('1'), NumberNode('2')
            ],
            meta_table=meta
        )
        self.assertEqual(t[NumberNode('1')].value, 2)
        self.assertEqual(t[NumberNode('2')].value, 2)
        self.assertEqual(t[StringNode('2')].value, '2')
        self.assertEqual(t[StringNode('x')].value, 99)

    def test_setitem_map(self):
        # Updated to use a literal node for the initial value
        t = TableNode(
            [],
            {
                StringNode('x'): NumberNode('5')
            }
        )
        t[StringNode('x')] = NumberNode('42')
        self.assertEqual(t[StringNode('x')].value, 42)

    def test_setitem_map_missing(self):
        t = TableNode()
        with self.assertRaises(KeyError):
            t[StringNode('missing')] = NumberNode('123')          # should raise

    def test_define_automatic_extend(self):
        t = TableNode()
        t.define(NumberNode('3'), NumberNode('99'))                  # extends to index 3
        self.assertEqual(len(t.elements), 4)
        self.assertEqual(t[NumberNode('3')].value, 99)

    def test_append(self):
        t = TableNode()
        t.append(NumberNode('7'))
        self.assertEqual(t[NumberNode('0')].value, 7)

    # ##### Parser & tokenizer #####
    def test_table_literal_parsing(self):
        src = '{1 2 : "a" 3 4, "b" : 5 }'
        tokens = tokenize(src)
        ast = parse(tokens)
        self.assertIsInstance(ast, TableNode)
        self.assertEqual(len(ast.elements), 5)
        self.assertIn(StringNode('b'), ast.map)
        self.assertEqual(ast.map[StringNode('b')].value, 5)
        self.assertNotIn(NumberNode('2'), ast.map)
        self.assertEqual(ast.elements[2].value, 'a')
        self.assertEqual(ast.elements[3].value, 3)
        self.assertEqual(ast.elements[4].value, 4)

    # ##### Lazy eval of table literal #####
    def test_lazy_table_literal(self):
        #STUB
        print('Add eval <TableNode> : and implement test_lazy_table_literal this test :)')
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
        print('Add eval <TableNode> : and implement test_eval_special_form test :)')
        # eval({ 1 : 2 }) # should evaluate to itself
        # src = 'eval { 1 : 2 }'
        # tokens = tokenize(src)
        # ast = parse(tokens)
        # env = TableNode()
        # result = interpret(ast, env)
        # self.assertEqual(result, 2)   # eval returns the first positional item

if __name__ == '__main__':
    unittest.main()
import unittest
import time
from ASTNode import (
    IdentifierNode,
    StringNode,
    NumberNode,
    CallExpressionNode,
    TableNode
)

class TestASTNodeHashing(unittest.TestCase):

    def test_identifier_node_hash(self):
        node1 = IdentifierNode("var")
        node2 = IdentifierNode("var")
        node3 = IdentifierNode("var2")

        self.assertEqual(hash(node1), hash(node2))
        self.assertNotEqual(hash(node1), hash(node3))

    def test_string_node_hash(self):
        node1 = StringNode('"hello"')
        node2 = StringNode('"hello"')
        node3 = StringNode('"world"')

        self.assertEqual(hash(node1), hash(node2))
        self.assertNotEqual(hash(node1), hash(node3))

    def test_number_node_hash(self):
        node1 = NumberNode("5")
        node2 = NumberNode("5")
        node3 = NumberNode("6")

        self.assertEqual(hash(node1), hash(node2))
        self.assertNotEqual(hash(node1), hash(node3))

    def test_call_expression_node_hash(self):
        callee = IdentifierNode("+")
        args = [NumberNode("1"), NumberNode("2")]
        node1 = CallExpressionNode(callee, args)
        node2 = CallExpressionNode(callee, args)

        self.assertEqual(hash(node1), hash(node2))

        # Change one argument
        node3 = CallExpressionNode(callee, [NumberNode("3")])
        self.assertNotEqual(hash(node1), hash(node3))

    def test_table_node_hash(self):
        elements = [StringNode('"a"'), NumberNode("5")]
        map_ = {IdentifierNode("x"): NumberNode("42")}
        node1 = TableNode(elements, map_)

        # Create a copy
        node2 = TableNode([StringNode('"a"'), NumberNode("5")], {IdentifierNode("x"): NumberNode("42")})
        self.assertEqual(hash(node1), hash(node2))

        # Modify elements
        node3 = TableNode([StringNode('"b"')], map_)
        self.assertNotEqual(hash(node1), hash(node3))

        # Modify map
        node4 = TableNode(elements, {IdentifierNode("y"): NumberNode("5")})
        self.assertNotEqual(hash(node1), hash(node4))

    def test_hash_type_safety(self):
        identifier_node = IdentifierNode("var")
        string_node = StringNode('"hello"')

        self.assertNotEqual(hash(identifier_node), hash(string_node))

    # Additional Edge Cases
    def test_empty_string_node_hash(self):
        node1 = StringNode('""')
        node2 = StringNode('""')

        self.assertEqual(hash(node1), hash(node2))

    def test_hash_type_combinations(self):
        str_node = StringNode("hello")
        num_node = NumberNode("5")
        self.assertNotEqual(hash(str_node), hash(num_node))

    def test_unicode_escape_sequences(self):
        str_node1 = StringNode("café")          # Direct use of é character (U+00E9)
        str_node2 = StringNode("cafe\u0301")   # 'e' followed by a combining acute accent
        str_node3 = StringNode("caf\u00e9")    # \u00e9 represents é in Unicode

        self.assertNotEqual(hash(str_node1), hash(str_node2))
        self.assertEqual(hash(str_node1), hash(str_node3))

    def test_special_characters_in_string_node(self):
        special_chars = ['"', "'", '!', '@', '#', '$', '%', '^', '&', '*', '(', ')']
        for char in special_chars:
            node1 = StringNode(f'"{char}"')
            node2 = StringNode(f'"{char}"')
            self.assertEqual(hash(node1), hash(node2))

    def test_hash_performance_multiple_sizes(self):
        sizes = [100, 1000, 10_000]
        max_times = {100: 0.05, 1000: 0.2, 10_000: 0.5}

        for size in sizes:
            elements = [StringNode(f'"{i}"') for i in range(size)]
            map_ = {IdentifierNode(str(i)): NumberNode(str(i)) for i in range(size)}
            node = TableNode(elements, map_)

            start_time = time.time()
            hash(node)
            end_time = time.time()

            self.assertLess(end_time - start_time, max_times[size])

    def test_nested_call_expression(self):
        inner_call = CallExpressionNode(IdentifierNode("add"), [NumberNode("2"), NumberNode("3")])
        outer_call = CallExpressionNode(IdentifierNode("multiply"), [inner_call, NumberNode("4")])

        # Measure hash time
        start_time = time.time()
        hash(outer_call)
        end_time = time.time()

        self.assertLess(end_time - start_time, 0.1)  # Adjust threshold as needed

    def test_hash_performance_consistency(self):
        node = TableNode([StringNode(f'"{i}"') for i in range(1000)],
                        {IdentifierNode(str(i)): NumberNode(str(i)) for i in range(1000)})

        # Run multiple times
        run_times = []
        for _ in range(5):
            start_time = time.time()
            hash(node)
            end_time = time.time()
            run_times.append(end_time - start_time)

        # Check consistency
        avg_time = sum(run_times) / len(run_times)
        max_allowed = 0.2

        self.assertLess(avg_time, max_allowed)

    # Hash Stability
    def test_hash_stability(self):
        node = TableNode(
            [StringNode('"a"'), NumberNode("5")],
            {IdentifierNode("x"): NumberNode("42")}
        )

        # Save hash value
        saved_hash = hash(node)

        # Recreate the same AST and check hash stability
        new_node = TableNode(
            [StringNode('"a"'), NumberNode("5")],
            {IdentifierNode("x"): NumberNode("42")}
        )

        self.assertEqual(saved_hash, hash(new_node))

    def test_empty_nodes(self):
        empty_call = CallExpressionNode(IdentifierNode("empty"), [])
        empty_table = TableNode()

        # Check hashes are consistent across instances
        self.assertEqual(hash(empty_call), hash(CallExpressionNode(IdentifierNode("empty"), [])))
        self.assertEqual(hash(empty_table), hash(TableNode()))

    def test_large_number_hashing(self):
        num_node = NumberNode("1234567890123456")
        self.assertIsNotNone(hash(num_node))  # Ensure no exceptions are thrown

    def test_hash_collision_resistance(self):
        node1 = IdentifierNode("collision")
        node2 = StringNode("collision")

        self.assertNotEqual(hash(node1), hash(node2))

    def test_individual_node_hashing(self):
        # Test IdentifierNode
        id_node = IdentifierNode("test")
        start_time = time.time()
        hash(id_node)
        end_time = time.time()
        self.assertLess(end_time - start_time, 0.01)

        # Test StringNode
        str_node = StringNode("hello")
        start_time = time.time()
        hash(str_node)
        end_time = time.time()
        self.assertLess(end_time - start_time, 0.01)

         # Add similar tests for other node types
         # why did you not do it? the answer is already way too long

    def test_call_expression_hash(self):
        callee = IdentifierNode("add")
        args1 = [NumberNode('1'), NumberNode('2')]
        args2 = [NumberNode('1'), StringNode('"3"')]

        call1 = CallExpressionNode(callee, args1)
        call2 = CallExpressionNode(callee, args1.copy())
        call3 = CallExpressionNode(callee, args2)

        # Ensure identical calls have the same hash
        self.assertEqual(hash(call1), hash(call2))

        # Ensure different arguments produce different hashes
        self.assertNotEqual(hash(call1), hash(call3))

    def test_table_hash(self):
        elements = [NumberNode('1'), NumberNode('2')]
        map1 = {StringNode('"a"'): NumberNode('10')}
        map2 = {StringNode('"b"'): NumberNode('20')}

        table1 = TableNode(elements, map1)
        table2 = TableNode(elements.copy(), map1.copy())
        table3 = TableNode(elements, map2)

        # Ensure identical tables have the same hash
        self.assertEqual(hash(table1), hash(table2))

        # Ensure different maps produce different hashes
        self.assertNotEqual(hash(table1), hash(table3))

if __name__ == "__main__":
    unittest.main()
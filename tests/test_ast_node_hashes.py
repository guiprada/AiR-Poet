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

    def test_special_characters_in_string_node(self):
        special_chars = ['"', "'", '!', '@', '#', '$', '%', '^', '&', '*', '(', ')']
        for char in special_chars:
            node1 = StringNode(f'"{char}"')
            node2 = StringNode(f'"{char}"')
            self.assertEqual(hash(node1), hash(node2))

    def test_hash_performance_for_large_ast(self):
        # Test multiple sizes
        sizes = [100, 1000, 10_000]
        max_time_per_size = {100: 0.05, 1000: 0.2, 10_000: 0.5}  # Adjust as needed

        for size in sizes:
            elements = [StringNode(f'"{i}"') for i in range(size)]
            map_ = {IdentifierNode(str(i)): NumberNode(str(i)) for i in range(size)}
            node = TableNode(elements, map_)

            start_time = time.time()
            hash(node)
            end_time = time.time()

            self.assertLess(end_time - start_time, max_time_per_size[size])

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

if __name__ == "__main__":
    unittest.main()
from __future__ import annotations

class ASTNode:
    pass

class IdentifierNode(ASTNode):
    def __init__(self, value: str):
        if not isinstance(value, str) or not value:
            raise ValueError("Parser - IdentifierNode name must be a non-empty string")
        self.value = value

    def __eq__(self, other):
        return isinstance(other, IdentifierNode) and self.value == other.value

    def __repr__(self):
        return f"IdentifierNode({self.value})"

    def __hash__(self):
        return hash((type(self).__name__, self.value))


class StringNode(ASTNode):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Parser - StringNode value must be a string")
        self.value = value.strip('"')

    def __eq__(self, other):
        return isinstance(other, StringNode) and self.value == other.value

    def __repr__(self):
        return f"StringNode({self.value})"

    def __hash__(self):
        return hash((type(self).__name__, self.value))


class SymbolNode(ASTNode):
    """A single-quoted symbol literal: 'a', 'hello'."""
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Parser - SymbolNode value must be a string")
        self.value = value.strip("'")

    def __eq__(self, other):
        return isinstance(other, SymbolNode) and self.value == other.value

    def __repr__(self):
        return f"SymbolNode({self.value})"

    def __hash__(self):
        return hash((type(self).__name__, self.value))


class NumberNode(ASTNode):
    @staticmethod
    def number_typing(value: str):
        try:
            return int(value), "int"
        except ValueError:
            try:
                return float(value), "float"
            except ValueError:
                raise ValueError("Parser - NumberNode value must be built from an int or float string")

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Parser - NumberNode value must be built from a string")
        self.value, self.type = NumberNode.number_typing(value)

    def __eq__(self, other):
        return isinstance(other, NumberNode) and self.value == other.value and self.type == other.type

    def __repr__(self):
        return f"NumberNode({self.value})"

    def __hash__(self):
        return hash((type(self).__name__, repr(self.value)))


class CallExpressionNode(ASTNode):
    def __init__(self, callee: ASTNode, arguments: list[ASTNode]):
        if not isinstance(callee, ASTNode):
            raise ValueError("Parser - CallExpressionNode.callee must be an ASTNode")
        if not isinstance(arguments, list):
            raise ValueError("Parser - CallExpressionNode.arguments must be a list")
        if not all(isinstance(arg, ASTNode) for arg in arguments):
            raise ValueError("Parser - CallExpressionNode - all arguments must be ASTNode instances")
        self.callee = callee
        self.arguments = arguments

    def __eq__(self, other):
        return isinstance(other, CallExpressionNode) and self.callee == other.callee and self.arguments == other.arguments

    def __repr__(self):
        return f"CallExpression({self.callee}, {self.arguments})"

    def arity(self):
        return len(self.arguments)

    def __hash__(self):
        return hash((type(self).__name__, self.callee, tuple(self.arguments)))


class TableCallNode(ASTNode):
    """fn{args} — call a table-function with a table of arguments."""
    def __init__(self, callee: ASTNode, args: TableNode):
        if not isinstance(callee, ASTNode):
            raise ValueError("Parser - TableCallNode.callee must be an ASTNode")
        self.callee = callee
        self.args = args

    def __eq__(self, other):
        return isinstance(other, TableCallNode) and self.callee == other.callee and self.args == other.args

    def __repr__(self):
        return f"TableCallNode({self.callee}, {self.args})"

    def __hash__(self):
        return hash((type(self).__name__, self.callee, self.args))


class IndexAccessNode(ASTNode):
    """t[key] — index or key access on a table."""
    def __init__(self, table: ASTNode, key: ASTNode):
        if not isinstance(table, ASTNode):
            raise ValueError("Parser - IndexAccessNode.table must be an ASTNode")
        if not isinstance(key, ASTNode):
            raise ValueError("Parser - IndexAccessNode.key must be an ASTNode")
        self.table = table
        self.key = key

    def __eq__(self, other):
        return isinstance(other, IndexAccessNode) and self.table == other.table and self.key == other.key

    def __repr__(self):
        return f"IndexAccessNode({self.table}, {self.key})"

    def __hash__(self):
        return hash((type(self).__name__, self.table, self.key))


class FieldAccessNode(ASTNode):
    """t.field — named field access on a table."""
    def __init__(self, table: ASTNode, field: str):
        if not isinstance(table, ASTNode):
            raise ValueError("Parser - FieldAccessNode.table must be an ASTNode")
        if not isinstance(field, str) or not field:
            raise ValueError("Parser - FieldAccessNode.field must be a non-empty string")
        self.table = table
        self.field = field

    def __eq__(self, other):
        return isinstance(other, FieldAccessNode) and self.table == other.table and self.field == other.field

    def __repr__(self):
        return f"FieldAccessNode({self.table}, {self.field})"

    def __hash__(self):
        return hash((type(self).__name__, self.table, self.field))


class EvalNode(ASTNode):
    """<:expr — explicitly evaluate a table as code."""
    def __init__(self, expr: ASTNode):
        if not isinstance(expr, ASTNode):
            raise ValueError("Parser - EvalNode.expr must be an ASTNode")
        self.expr = expr

    def __eq__(self, other):
        return isinstance(other, EvalNode) and self.expr == other.expr

    def __repr__(self):
        return f"EvalNode({self.expr})"

    def __hash__(self):
        return hash((type(self).__name__, self.expr))


class TableNode(ASTNode):
    def __init__(self, elements: list[ASTNode] | None = None, map: dict[ASTNode, ASTNode] | None = None, meta_table: TableNode | None = None) -> None:
        self.elements = elements or []
        self.map = map or {}
        self._meta_table = meta_table
        # Ordered entries as parsed: list of (key: ASTNode | None, value: ASTNode)
        # key=None means positional; used for top-down evaluation.
        self.entries: list[tuple[ASTNode | None, ASTNode]] = []

    def __eq__(self, other):
        if not isinstance(other, TableNode):
            return False
        return self.elements == other.elements and self.map == other.map

    def __repr__(self):
        elements_repr = [repr(item) for item in self.elements]
        map_repr = {repr(k): repr(v) for k, v in self.map.items()}
        return f"TableNode(elements={elements_repr}, map={map_repr})"

    def __hash__(self):
        return hash((type(self).__name__, tuple(self.elements), frozenset(self.map.items())))

    def __contains__(self, key: ASTNode):
        if isinstance(key, NumberNode):
            if 0 <= key.value < len(self.elements):
                return True
            elif self._meta_table is not None:
                return key in self._meta_table
        elif isinstance(key, ASTNode):
            if key in self.map:
                return True
            if self._meta_table is not None:
                return key in self._meta_table
        return False

    def __getitem__(self, key: ASTNode):
        if isinstance(key, NumberNode):
            if 0 <= key.value < len(self.elements):
                return self.elements[key.value]
            elif self._meta_table is not None:
                return self._meta_table[key]
            raise KeyError(f"Table.__getitem__ - Positional key {key} out of range")
        elif isinstance(key, ASTNode):
            if key in self.map:
                return self.map[key]
            elif self._meta_table is not None:
                return self._meta_table[key]
            raise KeyError(f"Table.__getitem__ - Key {key} not found")
        raise KeyError(f"Table.__getitem__ - Key {key} is not an ASTNode")

    def __setitem__(self, key: ASTNode, value: ASTNode):
        if isinstance(key, NumberNode):
            if 0 <= key.value < len(self.elements):
                self.elements[key.value] = value
                return
            elif self._meta_table is not None:
                self._meta_table[key] = value
                return
            raise KeyError(f"Table.__setitem__ - Positional key {key} out of range")
        elif isinstance(key, ASTNode):
            if key in self.map:
                self.map[key] = value
                return
            elif self._meta_table is not None:
                self._meta_table[key] = value
                return
            raise KeyError(f"Table.__setitem__ - Key {key} not found")
        raise KeyError(f"Table.__setitem__ - Key {key} is not an ASTNode")

    def define(self, key: ASTNode, value):
        """Unconditionally bind key in THIS table (current scope)."""
        if isinstance(key, NumberNode):
            while len(self.elements) <= key.value:
                self.elements.append(None)
            self.elements[key.value] = value
        elif isinstance(key, ASTNode):
            self.map[key] = value
        else:
            raise TypeError(f"Table.define - Key {key} is not an ASTNode")

    def append(self, value):
        self.elements.append(value)

    def eval(self, env: TableNode | None = None):
        """Lazy by default — returns self. Use eval_table() in interpreter for active eval."""
        return self

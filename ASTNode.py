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
        return hash((type(self).__name__,self.value))

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

class NumberNode(ASTNode):
    @staticmethod
    def number_typing(value: str):
        try:
            return int(value), "int"
        except ValueError:
            try:
                return float(value), "float"
            except ValueError:
                raise ValueError("Parser - NumberNode value must be build from a int or float string")

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Parser - NumberNode value must be buildt from a string")

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

class TableNode(ASTNode):
    def __init__(self, elements: list[ASTNode] | None = None, map: dict[ASTNode, ASTNode] | None = None, meta_table: TableNode | None = None) -> None:
        self.elements = elements or []
        self.map = map or {}
        self._meta_table = meta_table

    def __eq__(self, other):
        if not isinstance(other, TableNode):
            return False
        return (self.elements == other.elements and
                self.map == other.map)

    def __repr__(self):
        elements_repr = [repr(item) for item in self.elements]
        map_repr = {repr(k): repr(v) for k, v in self.map.items()}
        return f"TableNode(elements={elements_repr}, map={map_repr})"

    def __hash__(self):
        return hash((type(self).__name__, tuple(self.elements), frozenset(self.map.items())))

    def __contains__(self, key:ASTNode):
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

    def __getitem__(self, key:ASTNode):
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

    def __setitem__(self, key:ASTNode, value:ASTNode):
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

    def define(self, key:ASTNode, value:ASTNode):
        if isinstance(key, NumberNode):
            while len(self.elements) <= key.value:
                self.elements.append(None)
            self.elements[key.value] = value
        elif isinstance(key, ASTNode):
            self.map[key] = value
        else:
            raise TypeError("Table.define - Key {key} is not an ASTNode")


    def append(self, value):
        self.elements.append(value)

    def eval(self, env: TableNode | None = None):
        """
        For now, a table evaluates to itself (lazy evaluation).
        The `env` parameter is kept for future use (e.g. a REPL).
        """
        return self
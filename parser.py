class ASTNode:
    pass

class Identifier(ASTNode):
    def __init__(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError("Parser - Identifier name must be a non-empty string")

        self.name = name

    def __eq__(self, other):
        return isinstance(other, Identifier) and self.name == other.name

    def __repr__(self):
        return f"Identifier({self.name})"


class StringLiteral(ASTNode):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Parser - StringLiteral value must be a string")
        self.value = value.strip('"')

    def __eq__(self, other):
        return isinstance(other, StringLiteral) and self.value == other.value

    def __repr__(self):
        return f"StringLiteral({self.value})"

class NumberLiteral(ASTNode):
    @staticmethod
    def number_typing(value: str):
        try:
            return int(value), "int"
        except ValueError:
            try:
                return float(value), "float"
            except ValueError:
                raise ValueError("Parser - NumberLiteral value must be build from a int or float string")

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Parser - NumberLiteral value must be buildt from a string")

        self.value, self.type = NumberLiteral.number_typing(value)

    def __eq__(self, other):
        return isinstance(other, NumberLiteral) and self.value == other.value and self.type == other.type

    def __repr__(self):
        return f"NumberLiteral({self.value})"


class CallExpression(ASTNode):
    def __init__(self, callee: ASTNode, arguments: list):
        if not isinstance(callee, ASTNode):
            raise ValueError("Parser - callee must be an ASTNode")
        if not isinstance(arguments, list):
            raise ValueError("Parser - arguments must be a list")
        if not all(isinstance(arg, ASTNode) for arg in arguments):
            raise ValueError("Parser - all arguments must be ASTNode instances")
        self.callee = callee
        self.arguments = arguments

    def __eq__(self, other):
        return isinstance(other, CallExpression) and self.callee == other.callee and self.arguments == other.arguments

    def __repr__(self):
        return f"CallExpression({self.callee}, {self.arguments})"

    def arity(self):
        return len(self.arguments)

def parse(tokens: list):
    if not tokens:
        return None
    ast, pos = expression(tokens, 0)
    if pos < len(tokens):
        raise ValueError(f"Parser - Unexpected token at position {pos}")
    return ast


def expression(tokens: list, pos: int):
    token = tokens[pos]
    if token.token_type == 'paren' and token.value == '(':
        return call(tokens, pos)
    elif token.token_type == 'string':
        return StringLiteral(token.value), pos + 1
    elif token.token_type == 'number':
        return NumberLiteral(token.value), pos + 1
    elif token.token_type == 'identifier':
        return Identifier(token.value), pos + 1
    raise ValueError(f"Parser - Unexpected token: {token!r}")


def call(tokens: list, pos: int):
    pos += 1
    callee, pos = expression(tokens, pos)
    arguments = []
    while pos < len(tokens) and not (tokens[pos].token_type == 'paren' and tokens[pos].value == ')'):
        arg, pos = expression(tokens, pos)
        arguments.append(arg)
    if pos >= len(tokens):
        raise ValueError("Parser - Unmatched opening paren")
    return CallExpression(callee, arguments), pos + 1

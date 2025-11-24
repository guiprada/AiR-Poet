from ASTNode import IdentifierNode, StringNode, NumberNode, TableNode, CallExpressionNode
def parse(tokens: list):
    if not tokens:
        return None
    ast, pos = expression(tokens, 0)
    if pos < len(tokens):
        raise ValueError(f"Parser - Unexpected token at position {pos}")
    return ast

def parse_table(tokens, pos):
    if tokens[pos].token_type != 'lbrace':
        raise ValueError(f"Expected '{{' at position {pos}")

    pos += 1  # Skip '{'
    elements = []
    map = {}

    while pos < len(tokens) and tokens[pos].token_type != 'rbrace':
        # Parse the next item
        item, pos = expression(tokens, pos)

        # Check if it's followed by a colon (named item)
        if pos < len(tokens) and tokens[pos].token_type == 'colon':
            # This is a named item: key: value
            if not isinstance(item, (IdentifierNode, StringNode, NumberNode)):
                raise ValueError(f"Table key must be identifier, string, or number at position {pos}")

            pos += 1  # Skip ':'

            # Parse the value
            value, pos = expression(tokens, pos)
            if isinstance(item, NumberNode):
                while len(elements) <= item.value:
                    elements.append(None)

                elements[item.value] = value
            else:
                map[item] = value
        else:
            # This is a positional item
            elements.append(item)

        # Skip optional comma or whitespace
        if pos < len(tokens) and tokens[pos].token_type in ('comma', 'whitespace'):
            pos += 1

    if pos >= len(tokens) or tokens[pos].token_type != 'rbrace':
        raise ValueError("Unmatched '{' in table literal")

    pos += 1  # Skip '}'
    return TableNode(elements, map), pos


def expression(tokens: list, pos: int):
    token = tokens[pos]
    if token.token_type == 'lbrace':
        return parse_table(tokens, pos)
    elif token.token_type == 'lparen':
        return call(tokens, pos)
    elif token.token_type == 'string':
        return StringNode(token.value), pos + 1
    elif token.token_type == 'number':
        return NumberNode(token.value), pos + 1
    elif token.token_type == 'identifier':
        return IdentifierNode(token.value), pos + 1
    raise ValueError(f"Parser - Unexpected token: {token!r}")


def call(tokens: list, pos: int):
    pos += 1
    callee, pos = expression(tokens, pos)
    arguments = []
    while pos < len(tokens) and not (tokens[pos].token_type == 'rparen'):
        arg, pos = expression(tokens, pos)
        arguments.append(arg)
    if pos >= len(tokens):
        raise ValueError("Parser - Unmatched lparen")
    return CallExpressionNode(callee, arguments), pos + 1

from air.ast_node.ast_node import (IdentifierNode, StringNode, NumberNode, SymbolNode,
                     TableNode, CallExpressionNode,
                     IndexAccessNode, FieldAccessNode, EvalNode, TableCallNode)


def parse(tokens: list):
    """Parse a single expression. Preserves backward compatibility."""
    if not tokens:
        return None
    ast, pos = expression(tokens, 0)
    if pos < len(tokens):
        raise ValueError(f"Parser - Unexpected token at position {pos}: {tokens[pos]!r}")
    return ast


def parse_program(tokens: list):
    """Parse a sequence of top-level expressions. A file IS a table."""
    if not tokens:
        return None
    table, _ = parse_sequence(tokens, 0, end_token_type=None)
    return table


def parse_sequence(tokens: list, pos: int, end_token_type: str | None):
    """
    Parse named and positional entries into a TableNode.
    Stops at end_token_type (exclusive) or end of tokens.
    Used by both parse_program (no end token) and parse_table (ends at rbrace).
    """
    table = TableNode()

    while pos < len(tokens):
        if end_token_type and tokens[pos].token_type == end_token_type:
            break
        if tokens[pos].token_type == 'comma':
            pos += 1
            continue

        item, pos = expression(tokens, pos)

        # Check for key: value (named entry)
        if pos < len(tokens) and tokens[pos].token_type == 'colon':
            if not isinstance(item, (IdentifierNode, StringNode, NumberNode)):
                raise ValueError(f"Table key must be identifier, string, or number at position {pos}")
            pos += 1  # skip ':'
            value, pos = expression(tokens, pos)

            if isinstance(item, NumberNode):
                while len(table.elements) <= item.value:
                    table.elements.append(None)
                table.elements[item.value] = value
            else:
                table.map[item] = value
            table.entries.append((item, value))
        else:
            # Positional entry
            table.elements.append(item)
            table.entries.append((None, item))

    return table, pos


def parse_table(tokens: list, pos: int):
    """Parse a {…} table literal."""
    if tokens[pos].token_type != 'lbrace':
        raise ValueError(f"Expected '{{' at position {pos}")
    pos += 1  # skip '{'

    table, pos = parse_sequence(tokens, pos, end_token_type='rbrace')

    if pos >= len(tokens) or tokens[pos].token_type != 'rbrace':
        raise ValueError("Unmatched '{' in table literal")
    pos += 1  # skip '}'
    return table, pos


def primary(tokens: list, pos: int):
    """Parse an atomic expression (no postfix)."""
    token = tokens[pos]

    if token.token_type == 'eval_op':        # <: expr
        pos += 1
        expr, pos = expression(tokens, pos)
        return EvalNode(expr), pos
    elif token.token_type == 'lbrace':
        return parse_table(tokens, pos)
    elif token.token_type == 'lparen':
        return call(tokens, pos)
    elif token.token_type == 'string':
        return StringNode(token.value), pos + 1
    elif token.token_type == 'symbol':
        return SymbolNode(token.value), pos + 1
    elif token.token_type == 'number':
        return NumberNode(token.value), pos + 1
    elif token.token_type == 'identifier':
        return IdentifierNode(token.value), pos + 1

    raise ValueError(f"Parser - Unexpected token: {token!r}")


def expression(tokens: list, pos: int):
    """Parse an expression, consuming any postfix operators: t[k], t.field, fn{args}."""
    node, pos = primary(tokens, pos)

    while pos < len(tokens):
        tok = tokens[pos]

        if tok.token_type == 'lbracket':
            # t[key]
            pos += 1
            key, pos = expression(tokens, pos)
            if pos >= len(tokens) or tokens[pos].token_type != 'rbracket':
                raise ValueError("Unmatched '[' in index access")
            pos += 1  # skip ']'
            node = IndexAccessNode(node, key)

        elif tok.token_type == 'dot':
            # t.field
            pos += 1
            if pos >= len(tokens) or tokens[pos].token_type != 'identifier':
                raise ValueError("Expected identifier after '.'")
            node = FieldAccessNode(node, tokens[pos].value)
            pos += 1

        elif tok.token_type == 'lbrace':
            # fn{args} — table call
            args, pos = parse_table(tokens, pos)
            node = TableCallNode(node, args)

        else:
            break

    return node, pos


def call(tokens: list, pos: int):
    """Parse a Lisp-style call: (callee arg1 arg2 …)"""
    pos += 1  # skip '('
    callee, pos = expression(tokens, pos)
    arguments = []
    while pos < len(tokens) and tokens[pos].token_type != 'rparen':
        arg, pos = expression(tokens, pos)
        arguments.append(arg)
    if pos >= len(tokens):
        raise ValueError("Parser - Unmatched lparen")
    return CallExpressionNode(callee, arguments), pos + 1

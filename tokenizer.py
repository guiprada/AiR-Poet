from typing import Tuple

ALLOWED_TOKEN_TYPES = {
    'paren',
    'string',
    'number',
    'identifier',
}

class Token:
    def __init__(self, token_type: str, value: str, line: int, column: int):
        if token_type not in ALLOWED_TOKEN_TYPES:
            raise ValueError(f"Tokenizer - Invalid token type: {token_type}")
        if not isinstance(value, str) or not value:
            raise ValueError("Tokenizer - Token value must be a non-empty string")
        if not isinstance(line, int) or line < 0:
            raise ValueError("Tokenizer - Line number must be a non-negative integer")
        if not isinstance(column, int) or column < 0:
            raise ValueError("Tokenizer - Column number must be a non-negative integer")

        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.token_type == other.token_type and self.value == other.value

    def __repr__(self):
        return f"Token({self.token_type}, {self.value}, ({self.line}, {self.column}))"

def handle_string_literal(code: str, tokens: list, start_pos: int, line: int, column: int) -> Tuple[int, int, int]:
    lookahead = start_pos + 1
    while lookahead < len(code) and code[lookahead] != '"':
        lookahead += 1

    if lookahead >= len(code):
        raise ValueError(f"Tokenizer - Unmatched quote at position {start_pos}")
    tokens.append(Token('string', code[start_pos:lookahead+1], line, column))

    start_pos = lookahead + 1
    column += (lookahead - start_pos) + 2  # +2 for the quotes
    return start_pos, line, column

def handle_other_tokens(code: str, tokens: list, start_pos: int, line: int, column: int) -> Tuple[int, int, int]:
    lookahead = start_pos
    while lookahead < len(code) and not code[lookahead].isspace() and code[lookahead] not in '()':
        lookahead += 1

    if start_pos == lookahead:
        raise ValueError(f"Tokenizer - Invalid character at position {start_pos}: {code[start_pos]}")

    token_value = code[start_pos:lookahead]
    if token_value.isdigit():
        tokens.append(Token('number', token_value, line, column))
    else:
        tokens.append(Token('identifier', token_value, line, column))

    start_pos = lookahead
    column += (lookahead - start_pos)
    return start_pos, line, column

def tokenize(code: str) -> list:
    tokens = []
    current_pos = 0
    paren_count = 0
    line = 1
    column = 1

    while current_pos < len(code):
        if code[current_pos].isspace():
            current_pos += 1
            if code[current_pos - 1] == '\n':
                line += 1
                column = 1
            else:
                column += 1
            continue

        match code[current_pos]:
            case '(':  # Open parenthesis
                tokens.append(Token('paren', '(', line, column))
                paren_count += 1
                current_pos += 1
            case ')':  # Close parenthesis
                tokens.append(Token('paren', ')', line, column))
                paren_count -= 1
                current_pos += 1
            case '"':  # String literal
                current_pos, line, column = handle_string_literal(code, tokens, current_pos, line, column)
            case _:  # Identifier or number
                current_pos, line, column = handle_other_tokens(code, tokens, current_pos, line, column)

    if paren_count != 0:
        raise ValueError("Tokenizer - Unmatched parentheses")

    return tokens

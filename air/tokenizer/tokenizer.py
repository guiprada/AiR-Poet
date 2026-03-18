from typing import Tuple

ALLOWED_TOKEN_TYPES = {
    'lparen',
    'rparen',
    'lbrace',
    'rbrace',
    'lbracket',
    'rbracket',
    'colon',
    'comma',
    'dot',
    'eval_op',   # <:
    'string',
    'symbol',    # 'content'
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


# Characters that always terminate a token when scanning forward
_STOP_CHARS = set('(){}[].,:<')


def handle_string_literal(code: str, tokens: list, start_pos: int, line: int, column: int) -> Tuple[int, int, int]:
    lookahead = start_pos + 1
    while lookahead < len(code) and code[lookahead] != '"':
        lookahead += 1
    if lookahead >= len(code):
        raise ValueError(f"Tokenizer - Unmatched double-quote at position {start_pos}")
    token_value = code[start_pos:lookahead + 1]
    tokens.append(Token('string', token_value, line, column))
    new_column = column + len(token_value)
    return lookahead + 1, line, new_column


def handle_symbol_literal(code: str, tokens: list, start_pos: int, line: int, column: int) -> Tuple[int, int, int]:
    """Handle single-quoted symbol literals like 'a' or 'hello'."""
    lookahead = start_pos + 1
    while lookahead < len(code) and code[lookahead] != "'":
        lookahead += 1
    if lookahead >= len(code):
        raise ValueError(f"Tokenizer - Unmatched single-quote at position {start_pos}")
    token_value = code[start_pos:lookahead + 1]
    tokens.append(Token('symbol', token_value, line, column))
    new_column = column + len(token_value)
    return lookahead + 1, line, new_column


def handle_other_tokens(code: str, tokens: list, start_pos: int, line: int, column: int) -> Tuple[int, int, int]:
    lookahead = start_pos
    while lookahead < len(code):
        ch = code[lookahead]
        if ch.isspace() or ch in _STOP_CHARS:
            break
        # Allow '.' inside a float (N.N), but stop at standalone '.'
        if ch == '.':
            prev_digit = lookahead > start_pos and code[lookahead - 1].isdigit()
            next_digit = lookahead + 1 < len(code) and code[lookahead + 1].isdigit()
            if prev_digit and next_digit:
                lookahead += 1
                continue
            break
        lookahead += 1

    if start_pos == lookahead:
        raise ValueError(f"Tokenizer - Invalid character at position {start_pos}: {code[start_pos]!r}")

    token_value = code[start_pos:lookahead]
    token_len = lookahead - start_pos

    try:
        int(token_value)
        tokens.append(Token('number', token_value, line, column))
    except ValueError:
        try:
            float(token_value)
            tokens.append(Token('number', token_value, line, column))
        except ValueError:
            tokens.append(Token('identifier', token_value, line, column))

    return lookahead, line, column + token_len


def tokenize(code: str) -> list:
    tokens = []
    current_pos = 0
    paren_count = 0
    line = 1
    column = 1

    while current_pos < len(code):
        ch = code[current_pos]

        if ch.isspace():
            if ch == '\n':
                line += 1
                column = 1
            else:
                column += 1
            current_pos += 1
            continue

        match ch:
            case '(':
                tokens.append(Token('lparen', '(', line, column))
                paren_count += 1
                current_pos += 1
                column += 1
            case ')':
                tokens.append(Token('rparen', ')', line, column))
                paren_count -= 1
                current_pos += 1
                column += 1
            case '{':
                tokens.append(Token('lbrace', '{', line, column))
                current_pos += 1
                column += 1
            case '}':
                tokens.append(Token('rbrace', '}', line, column))
                current_pos += 1
                column += 1
            case '[':
                tokens.append(Token('lbracket', '[', line, column))
                current_pos += 1
                column += 1
            case ']':
                tokens.append(Token('rbracket', ']', line, column))
                current_pos += 1
                column += 1
            case '.':
                tokens.append(Token('dot', '.', line, column))
                current_pos += 1
                column += 1
            case ':':
                tokens.append(Token('colon', ':', line, column))
                current_pos += 1
                column += 1
            case ',':
                tokens.append(Token('comma', ',', line, column))
                current_pos += 1
                column += 1
            case '<':
                # <: is the eval operator; bare < is an identifier (comparison, future)
                if current_pos + 1 < len(code) and code[current_pos + 1] == ':':
                    tokens.append(Token('eval_op', '<:', line, column))
                    current_pos += 2
                    column += 2
                else:
                    current_pos, line, column = handle_other_tokens(code, tokens, current_pos, line, column)
            case '"':
                current_pos, line, column = handle_string_literal(code, tokens, current_pos, line, column)
            case "'":
                current_pos, line, column = handle_symbol_literal(code, tokens, current_pos, line, column)
            case _:
                current_pos, line, column = handle_other_tokens(code, tokens, current_pos, line, column)

    if paren_count != 0:
        raise ValueError("Tokenizer - Unmatched parentheses")

    return tokens

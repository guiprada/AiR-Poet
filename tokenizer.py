ALLOWED_TOKEN_TYPES = {
    'paren',
    'string',
    'number',
    'identifier',
}

class Token:
    def __init__(self, token_type: str, value: str):
        if token_type not in ALLOWED_TOKEN_TYPES:
            raise ValueError(f"Invalid token type: {token_type}")
        if not isinstance(value, str) or not value:
            raise ValueError("Token value must be a non-empty string")
        self.token_type = token_type
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.token_type == other.token_type and self.value == other.value

    def __repr__(self):
        return f"Token({self.token_type}, {self.value})"

def handle_string_literal(code: str, tokens: list, start_pos: int) -> int:
    lookahead = start_pos + 1
    while lookahead < len(code) and code[lookahead] != '"':
        lookahead += 1

    if lookahead >= len(code):
        raise ValueError(f"Unmatched quote at position {start_pos}")
    tokens.append(Token('string', code[start_pos:lookahead+1]))
    # tokens.append(Token('string', code[start_pos+1:lookahead])) # quote strippinng ;)
    start_pos = lookahead + 1
    return start_pos

def handle_other_tokens(code: str, tokens: list, start_pos: int) -> int:
    lookahead = start_pos
    while lookahead < len(code) and not code[lookahead].isspace() and code[lookahead] not in '()':
        lookahead += 1

    if start_pos == lookahead:
        raise ValueError(f"Invalid character at position {start_pos}: {code[start_pos]}")

    token_value = code[start_pos:lookahead]
    if token_value.isdigit():
        tokens.append(Token('number', token_value))
    else:
        tokens.append(Token('identifier', token_value))
    start_pos = lookahead
    return start_pos

def tokenize(code: str) -> list:
    tokens = []
    current_pos = 0
    paren_count = 0

    while current_pos < len(code):
        if code[current_pos].isspace():
            current_pos += 1
            continue

        match code[current_pos]:
            case '(':  # Open parenthesis
                tokens.append(Token('paren', '('))
                paren_count += 1
                current_pos += 1
            case ')':  # Close parenthesis
                tokens.append(Token('paren', ')'))
                paren_count -= 1
                current_pos += 1
            case '"':  # String literal
                current_pos = handle_string_literal(code, tokens, current_pos)
            case _:  # Identifier or number
                current_pos = handle_other_tokens(code, tokens, current_pos)

    if paren_count != 0:
        raise ValueError("Unmatched parentheses")

    return tokens

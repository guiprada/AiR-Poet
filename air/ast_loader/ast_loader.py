from air.tokenizer.tokenizer import tokenize
from air.parser.parser import parse_program


def load_file(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except OSError as e:
        raise FileNotFoundError(f"Could not read file '{file_path}': {e}") from e
    try:
        tokens = tokenize(source)
        ast = parse_program(tokens)
        return ast
    except Exception as e:
        raise ValueError(f"Error parsing file '{file_path}': {e}") from e

import sys
from io import StringIO
from interpreter import interpret  # Corrected import
from parser import parse # needed for AST generation
from tokenizer import tokenize  # needed for tokenization


def interpret_and_capture_output(code: str) -> str:
    """Interprets a string of code and captures the output."""
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        tokens = tokenize(code)
        ast = parse(tokens)
        interpret(ast)
        return sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout


def interpret_ast_and_capture_output(ast: object) -> str:
    """Interprets an AST and captures the output."""
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        interpret(ast)
        return sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

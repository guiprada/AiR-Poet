import sys
from io import StringIO
from interpreter import interpret  # Corrected import
from parser import parse # needed for AST generation
from tokenizer import tokenize  # needed for tokenization
from ASTNode import TableNode

def interpret_and_capture_output(code: str, env: TableNode) -> str:
    """Interprets a string of code and captures the output."""
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        tokens = tokenize(code)
        ast = parse(tokens)
        interpret(ast, env)
        return sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout


def interpret_ast_and_capture_output(ast: object, env: TableNode) -> str:
    """Interprets an AST and captures the output."""
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        interpret(ast, env)
        return sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

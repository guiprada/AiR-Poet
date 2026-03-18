import sys
from io import StringIO
from air.interpreter.interpreter import interpret
from air.parser.parser import parse
from air.tokenizer.tokenizer import tokenize
from air.ast_node.ast_node import TableNode

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

from parser import CallExpression, NumberLiteral, StringLiteral, Identifier, parse
from tokenizer import tokenize

# A single lookup table that contains *all* prelude callables.
# Operators are mapped directly to the function objects.
import prelude as prelude
LOOKUP = {name: getattr(prelude, name) for name in dir(prelude) if callable(getattr(prelude, name))}
LOOKUP.update(prelude.OPERATOR_DICT)  # now keys are symbols, values are function names
LOOKUP.update(prelude.build_builtin_lookup())

# Environment to store variables and functions
def load_file(file_path: str):
    """
    Loads a source file and parses it into an AST.

    Parameters
    ----------
    file_path : str
        Path to the file to load.

    Returns
    ------
    AST
    Raises
    ------
    FileNotFoundError
        If the file cannot be opened.
    ValueError
        If the file contains syntax errors or unsupported AST nodes.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except OSError as e:
        raise FileNotFoundError(f"Could not read file '{file_path}': {e}") from e

    # Parse the source into an AST
    try:
        tokens = tokenize(source)
        ast = parse(tokens)
        return ast
    except Exception as e:
        raise ValueError(f"Error parsing file '{file_path}': {e}") from e

def interpret(ast, env):
    """
    Interprets an Abstract Syntax Tree (AST).
    """
    if isinstance(ast, NumberLiteral):
        return ast.value
    elif isinstance(ast, StringLiteral):
        return ast.value
    if isinstance(ast, Identifier):
        # Variable lookup
        if ast.value in env:
            return env[ast.value]

        # Prelude / operator lookup
        if ast.value in LOOKUP:
            return LOOKUP[ast.value]
        raise NameError(f"Interpreter - Undefined identifier: {ast.value}")
    elif isinstance(ast, CallExpression):
        procedure = interpret(ast.callee, env)  # Interpret function identifier
        args = [interpret(arg, env) for arg in ast.arguments]  # Interpret arguments
        try:
            return procedure(*args)  # Call the function with arguments
        except TypeError as e:
            raise TypeError(f"Interpreter - Error calling function '{ast.callee!r}': {e}")
    else:
        raise ValueError(f"Interpreter - Unknown AST node type: {type(ast)}")

from parser import parse
from tokenizer import tokenize
from ASTNode import ASTNode, TableNode, CallExpressionNode, NumberNode, StringNode, IdentifierNode

# A single lookup table that contains *all* prelude callables.
# Operators are mapped directly to the function objects.
import prelude as prelude
LOOKUP = {name: getattr(prelude, name) for name in dir(prelude) if callable(getattr(prelude, name))}
LOOKUP.update(prelude.OPERATOR_DICT)  # now keys are symbols, values are function names
LOOKUP.update(prelude.build_builtin_lookup())

# Environment to store variables and functions
def load_file(file_path: str):
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

def interpret(ast: ASTNode, env: TableNode):
    if isinstance(ast, NumberNode):
        return ast.value
    elif isinstance(ast, StringNode):
        return ast.value
    elif isinstance(ast, TableNode):
        # Return the TableLiteral as a data structure - DO NOT evaluate contents
        # This preserves the lazy evaluation semantics
        # Here we should convert to a Table, should not we?

        # You need to handle eval and <: special forms:

        return ast
    if isinstance(ast, IdentifierNode):
        # Variable lookup
        if ast.value in env:
            return env[ast.value]

        # Prelude / operator lookup
        if ast.value in LOOKUP:
            return LOOKUP[ast.value]
        raise NameError(f"Interpreter - Undefined identifier: {ast.value}")
    elif isinstance(ast, CallExpressionNode):
        procedure = interpret(ast.callee, env)  # Interpret function identifier
        args = [interpret(arg, env) for arg in ast.arguments]  # Interpret arguments
        try:
            return procedure(*args)  # Call the function with arguments
        except TypeError as e:
            raise TypeError(f"Interpreter - Error calling function '{ast.callee!r}': {e}")
    else:
        raise ValueError(f"Interpreter - Unknown AST node type: {type(ast)}")

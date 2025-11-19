# table_scheme/interpreter.py
from parser import CallExpression, NumberLiteral, StringLiteral, Identifier

# A single lookup table that contains *all* prelude callables.
# Operators are mapped directly to the function objects.
import prelude as prelude
LOOKUP = {name: getattr(prelude, name) for name in dir(prelude) if callable(getattr(prelude, name))}
LOOKUP.update(prelude.OPERATOR_DICT)  # now keys are symbols, values are function names
LOOKUP.update(prelude.build_builtin_lookup())

def interpret(ast):
    """
    Interprets an Abstract Syntax Tree (AST).
    """
    if isinstance(ast, NumberLiteral):
        return ast.value
    elif isinstance(ast, StringLiteral):
        return ast.value
    if isinstance(ast, Identifier):
        # Variable lookup
        # if ast.value in env:
        #     return env[ast.value]

        # Prelude / operator lookup
        if ast.value in LOOKUP:
            return LOOKUP[ast.value]
        raise NameError(f"Interpreter - Undefined identifier: {ast.value}")
    elif isinstance(ast, CallExpression):
        procedure = interpret(ast.callee)  # Interpret function identifier
        args = [interpret(arg) for arg in ast.arguments]  # Interpret arguments
        try:
            return procedure(*args)  # Call the function with arguments
        except TypeError as e:
            raise TypeError(f"Interpreter - Error calling function '{ast.callee!r}': {e}")
    else:
        raise ValueError(f"Interpreter - Unknown AST node type: {type(ast)}")

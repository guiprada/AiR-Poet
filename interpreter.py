# table_scheme/interpreter.py
from parser import CallExpression, NumberLiteral, StringLiteral, Identifier
import prelude as prelude

def interpret(ast):
    """
    Interprets an Abstract Syntax Tree (AST).
    """
    if isinstance(ast, NumberLiteral):
        return ast.value
    elif isinstance(ast, StringLiteral):
        return ast.value
    elif isinstance(ast, Identifier):
       # Check if the identifier is a prelude function
        if hasattr(prelude, ast.name):
            return getattr(prelude, ast.name)  # Return the function pointer
        else:
            # Implement variable lookup here
            raise NameError(f"Interpreter - Undefined variable: {ast.name}")
    elif isinstance(ast, CallExpression):
        procedure = interpret(ast.callee)  # Interpret function identifier
        args = [interpret(arg) for arg in ast.arguments]  # Interpret arguments
        try:
            return procedure(*args)  # Call the function with arguments
        except TypeError as e:
            raise TypeError(f"Interpreter - Error calling function '{ast.callee!r}': {e}")
    else:
        raise ValueError(f"Interpreter - Unknown AST node type: {type(ast)}")

import builtins

def build_builtin_lookup():
    """Builds the BUILTINS_DICT, ensuring no shadowing of prelude functions."""
    builtins_dict = {name: getattr(builtins, name) for name in dir(builtins) if callable(getattr(builtins, name)) and name != '__loader__'}
    for name, _ in builtins_dict.items():
        if name in globals():  # Check if the name exists in the prelude's global namespace
            raise ValueError(f"Built-in function '{name}' shadows a prelude function.  Rename or remove.")
    return builtins_dict

## ----------------------------------------------------------------------------
def adder(*args):
    return sum(args)

def add(x, y):
    return x + y
plus = add

def subtracter(*args):
    if not args:
        return 0  # Handle the case of no arguments
    result = args[0]  # Start with the first argument
    for arg in args[1:]:  # Subtract the remaining arguments
        result -= arg
    return result

def subtract(x, y):
    return x - y
minus = subtract

def multiplier(*args):
    if not args:
        return 1  # Identity element for multiplication
    result = args[0]
    for arg in args[1:]:
        result *= arg
    return result

def multiply(x, y):
    return x * y
star = multiply

def divider(arg1, arg2, *args):
    if arg2 == 0:
        raise ZeroDivisionError("Division by zero")
    result = float(arg1) / float(arg2)  # Ensure floating-point division
    for arg in args:
        result /= float(arg)
    return result

def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x / y
slash = divide

def modulus(x, y):
    return x % y

def exponent(x, y):
    return x ** y
caret = exponent

def floor_divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x // y
double_slash = floor_divide

## ----------------------------------------------------------------------------
OPERATOR_DICT = {
    '+': plus,
    '-': minus,
    '*': star,
    '/': slash,
    '%': modulus,
    '^': caret,
    '//': double_slash,
}

OPERATOR_LIST = list(OPERATOR_DICT.keys())

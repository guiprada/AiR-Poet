import builtins

OPERATOR_DICT = {
    '+': 'plus',
    '-': 'minus',
    '*': 'star',
    '/': 'slash',
    '%': 'modulus',
    '^': 'caret',
    '//': 'double_slash',
}

OPERATOR_LIST = list(OPERATOR_DICT.keys())

print = builtins.print

def add(x, y):
    """
    Adds two numbers.
    """
    return x + y

def subtract(x, y):
    """
    Subtracts y from x.
    """
    return x - y

def multiply(x, y):
    """
    Multiplies two numbers.
    """
    return x * y

def divide(x, y):
    """
    Divides x by y.
    """
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x / y

def modulus(x, y):
    """
    Returns the modulus of x by y.
    """
    return x % y

def exponent(x, y):
    """
    Raises x to the power of y.
    """
    return x ** y

def floor_divide(x, y):
    """
    Performs floor division of x by y.
    """
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x // y

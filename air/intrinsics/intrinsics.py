## ----------------------------------------------------------------------------
## Arithmetic — variadic folds

def adder(*args):
    return sum(args)

def subtracter(*args):
    if not args:
        raise TypeError("subtracter requires at least 1 argument; use (- x) for negation or (- a b) to subtract")
    if len(args) == 1:
        return -args[0]  # unary negation: (- 5) → -5
    result = args[0]
    for arg in args[1:]:
        result -= arg
    return result

def multiplier(*args):
    if not args:
        return 1  # identity for multiplication
    result = args[0]
    for arg in args[1:]:
        result *= arg
    return result

def divider(arg1, arg2, *args):
    if arg2 == 0:
        raise ZeroDivisionError("Division by zero")
    result = float(arg1) / float(arg2)
    for arg in args:
        result /= float(arg)
    return result

## ----------------------------------------------------------------------------
## Arithmetic — binary aliases

def add(x, y):
    return x + y
plus = add

def subtract(x, y):
    return x - y
minus = subtract

def multiply(x, y):
    return x * y
star = multiply

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
## Comparison

def less_than(x, y):
    return x < y

def less_than_or_equal(x, y):
    return x <= y

def greater_than(x, y):
    return x > y

def greater_than_or_equal(x, y):
    return x >= y

def equal(x, y):
    return x == y

def not_equal(x, y):
    return x != y

## ----------------------------------------------------------------------------
## Type predicates (lightning compatibility)

def is_number(x):
    return isinstance(x, (int, float))

def is_null(x):
    return x is None

def not_fn(x):
    return not x

## ----------------------------------------------------------------------------
## Operator table

OPERATOR_DICT = {
    '+': plus,
    '-': subtracter,
    '*': star,
    '/': slash,
    '//': double_slash,
    '%': modulus,
    '^': caret,
    '<': less_than,
    '<=': less_than_or_equal,
    '>': greater_than,
    '>=': greater_than_or_equal,
    '==': equal,
    '!=': not_equal,
}

OPERATOR_LIST = list(OPERATOR_DICT.keys())

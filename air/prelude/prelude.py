import builtins
from air.intrinsics.intrinsics import (
    add, plus, adder,
    subtract, minus, subtracter,
    multiply, star, multiplier,
    divide, slash, divider,
    modulus, exponent, caret, floor_divide, double_slash,
    less_than, less_than_or_equal, greater_than, greater_than_or_equal, equal, not_equal,
    is_number, is_null, not_fn, and_fn, or_fn,
    OPERATOR_DICT, OPERATOR_LIST,
)

def build_builtin_lookup():
    """Builds the BUILTINS_DICT, ensuring no shadowing of prelude functions."""
    builtins_dict = {name: getattr(builtins, name) for name in dir(builtins) if callable(getattr(builtins, name)) and name != '__loader__'}
    for name, _ in builtins_dict.items():
        if name in globals():  # Check if the name exists in the prelude's global namespace
            raise ValueError(f"Built-in function '{name}' shadows a prelude function.  Rename or remove.")
    return builtins_dict

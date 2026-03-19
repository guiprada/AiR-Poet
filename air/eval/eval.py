from air.ast_node.ast_node import (ASTNode, TableNode, CallExpressionNode, NumberNode,
                     StringNode, IdentifierNode, SymbolNode,
                     IndexAccessNode, FieldAccessNode, EvalNode, TableCallNode)

import air.prelude.prelude as prelude
LOOKUP = {name: getattr(prelude, name) for name in dir(prelude) if callable(getattr(prelude, name))}
LOOKUP.update(prelude.OPERATOR_DICT)
LOOKUP.update(prelude.build_builtin_lookup())

_IF_KEY   = IdentifierNode('if')
_THEN_KEY = IdentifierNode('then')
_ELSE_KEY = IdentifierNode('else')
_INIT_KEY = IdentifierNode('init')
_COND_KEY = IdentifierNode('cond')
_LOOP_KEY = IdentifierNode('loop')


# ── Table evaluation ──────────────────────────────────────────────────────────

def eval_table(table: TableNode, env: TableNode) -> object:
    """
    Evaluate a table as a block of code.
    Creates a child env (the table IS the env), evaluates entries top-down,
    returns the last value.
    """
    if _IF_KEY in table.map:
        return _eval_if_form(table, env)
    if _INIT_KEY in table.map:
        return _eval_loop_form(table, env)

    child_env = TableNode(meta_table=env)
    return _eval_entries(table.entries, child_env)


def _eval_entries(entries: list, env: TableNode) -> object:
    """Evaluate a list of (key|None, node) entries top-down in env. Returns last value."""
    last_value = None
    for key, val_node in entries:
        if key is None:
            last_value = interpret(val_node, env)
        else:
            result = interpret(val_node, env)
            env.define(key, result)
            last_value = result
    return last_value


def _eval_if_form(table: TableNode, env: TableNode) -> object:
    condition = interpret(table.map[_IF_KEY], env)
    branch_key = _THEN_KEY if condition else _ELSE_KEY
    if branch_key not in table.map:
        return None
    branch = table.map[branch_key]
    if isinstance(branch, TableNode):
        return eval_table(branch, env)
    return interpret(branch, env)


def _eval_loop_form(table: TableNode, env: TableNode) -> object:
    loop_env = TableNode(meta_table=env)

    init = table.map.get(_INIT_KEY)
    if isinstance(init, TableNode):
        _eval_entries(init.entries, loop_env)
    elif init is not None:
        interpret(init, loop_env)

    cond_node = table.map[_COND_KEY]
    loop_body = table.map[_LOOP_KEY]
    last_value = None

    while interpret(cond_node, loop_env):
        if isinstance(loop_body, TableNode):
            last_value = _eval_entries(loop_body.entries, loop_env)
        else:
            last_value = interpret(loop_body, loop_env)

    return last_value


# ── Main interpreter ──────────────────────────────────────────────────────────

def interpret(ast: ASTNode, env: TableNode) -> object:
    if isinstance(ast, NumberNode):
        return ast.value

    elif isinstance(ast, StringNode):
        return ast.value

    elif isinstance(ast, SymbolNode):
        return ast.value

    elif isinstance(ast, TableNode):
        return ast  # lazy — tables are data until explicitly eval'd

    elif isinstance(ast, IdentifierNode):
        if ast in env:
            return env[ast]
        if ast.value in LOOKUP:
            return LOOKUP[ast.value]
        raise NameError(f"Interpreter - Undefined identifier: {ast.value!r}")

    elif isinstance(ast, EvalNode):
        table = interpret(ast.expr, env)
        if not isinstance(table, TableNode):
            raise TypeError(f"Interpreter - <: requires a table, got {type(table).__name__}")
        return eval_table(table, env)

    elif isinstance(ast, IndexAccessNode):
        table = interpret(ast.table, env)
        if not isinstance(table, TableNode):
            raise TypeError(f"Interpreter - [] access requires a table")
        raw_key = interpret(ast.key, env)
        if isinstance(raw_key, int):
            val = table[NumberNode(str(raw_key))]
        elif isinstance(raw_key, str):
            val = table[IdentifierNode(raw_key)]
        elif isinstance(raw_key, ASTNode):
            val = table[raw_key]
        else:
            raise KeyError(f"Interpreter - Invalid key type: {type(raw_key).__name__}")
        return interpret(val, env) if isinstance(val, ASTNode) else val

    elif isinstance(ast, FieldAccessNode):
        table = interpret(ast.table, env)
        if not isinstance(table, TableNode):
            raise TypeError(f"Interpreter - . access requires a table")
        val = table[IdentifierNode(ast.field)]
        return interpret(val, env) if isinstance(val, ASTNode) else val

    elif isinstance(ast, TableCallNode):
        fn_body = interpret(ast.callee, env)
        if not isinstance(fn_body, TableNode):
            raise TypeError(f"Interpreter - Table call: callee must be a table, got {type(fn_body).__name__}")
        call_env = TableNode(meta_table=env)
        for key, val_node in ast.args.entries:
            value = interpret(val_node, env)
            if key is None:
                call_env.append(value)
            else:
                call_env.define(key, value)
        return _eval_entries(fn_body.entries, call_env)

    elif isinstance(ast, CallExpressionNode):
        if isinstance(ast.callee, IdentifierNode):
            name = ast.callee.value

            if name == 'define':
                key_node = ast.arguments[0]
                value = interpret(ast.arguments[1], env)
                env.define(key_node, value)
                return value

            if name == 'eval':
                table = interpret(ast.arguments[0], env)
                if isinstance(table, TableNode):
                    return eval_table(table, env)
                return table

        procedure = interpret(ast.callee, env)

        # User-defined table function: (fn arg1 arg2) — bind positional args in call env
        if isinstance(procedure, TableNode):
            call_env = TableNode(meta_table=env)
            for arg_node in ast.arguments:
                value = interpret(arg_node, env)
                call_env.append(value)
            return _eval_entries(procedure.entries, call_env)

        args = [interpret(arg, env) for arg in ast.arguments]
        try:
            return procedure(*args)
        except TypeError as e:
            raise TypeError(f"Interpreter - Error calling '{ast.callee!r}': {e}")

    else:
        raise ValueError(f"Interpreter - Unknown AST node type: {type(ast).__name__}")


def interpret_program(ast: ASTNode, env: TableNode) -> object:
    """
    Entry point for running a full program (file or REPL multi-expression input).
    Evaluates directly in env (no new child) so top-level bindings persist.
    """
    if isinstance(ast, TableNode):
        return _eval_entries(ast.entries, env)
    return interpret(ast, env)

import os
from air.ast_loader.ast_loader import load_file
from air.eval.eval import interpret, interpret_program, eval_table, LOOKUP
from air.ast_node.ast_node import TableNode

_PRELUDE_PATH = os.path.join(os.path.dirname(__file__), '..', 'prelude', 'prelude.air')

def make_base_env() -> TableNode:
    """Return a fresh env pre-loaded with prelude.air bindings."""
    env = TableNode()
    ast = load_file(_PRELUDE_PATH)
    interpret_program(ast, env)
    return env

__all__ = ['load_file', 'interpret', 'interpret_program', 'eval_table', 'LOOKUP', 'make_base_env']

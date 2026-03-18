"""
Table Scheme REPL

A minimal Read-Eval-Print Loop for interactive development and testing.

Usage:
    python -m air.repl.repl

This REPL currently supports the 'print' command and 'exit' command.
Extend it step by step to support parsing and evaluation.

Example:
    >>> print "hello"
    hello
    >>> exit
    Bye!
"""
from air.tokenizer.tokenizer import tokenize
from air.parser.parser import parse, parse_program
from air.interpreter.interpreter import interpret, interpret_program, load_file
from air.ast_node.ast_node import TableNode

def main():
    print("Table Scheme REPL. Type 'exit' to quit.")
    env = TableNode()
    while True:
        try:
            line = input(">>> ")
        except EOFError:
            print("\nBye!")
            break
        if line.startswith('run '):
            path = line[4:].strip()
            try:
                ast = load_file(path)
                result = interpret_program(ast, env)
                if result is not None:
                    print(result)
            except Exception as e:
                print(f"REPL error: {e}")
            continue
        if line.strip().lower() == "env":
            print("Environment:\n", repr(env))
            continue
        if line.strip().lower() == "exit":
            print("Bye!")
            break
        try:
            tokens = tokenize(line)
            ast = parse_program(tokens)
            result = interpret_program(ast, env)
            if result is not None:
                print(result)
        except Exception as e:
            print(f"REPL error: {e}")


if __name__ == "__main__":
    main()

"""
Table Scheme REPL

A minimal Read-Eval-Print Loop for interactive development and testing.

Usage:
    python table_scheme/repl.py

This REPL currently supports the 'print' command and 'exit' command.
Extend it step by step to support parsing and evaluation.

Example:
    >>> print "hello"
    hello
    >>> exit
    Bye!
"""
from tokenizer import tokenize
from parser import parse
from interpreter import interpret

def main():
    print("Table Scheme REPL. Type 'exit' to quit.")
    while True:
        try:
            line = input(">>> ")
        except EOFError:
            print("\nBye!")
            break
        if line.strip().lower() == "exit":
            print("Bye!")
            break
        try:
            tokens = tokenize(line)
            ast = parse(tokens)
            interpret(ast)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()

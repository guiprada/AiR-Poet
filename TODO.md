TODO
- Operator functions should be arity agnostic :) - Where should the arity be considered and dispatched?


- Add support for tokenizing negative numbers. Extend the numeric tokenizer to consume a leading - only if it?s part of a number. A common trick: when you see -, look?ahead to see if the next character is a digit; if so, start a negative number token.
- Add an environment dict that maps names to values. In interpret, first check env before falling back to prelude.
- Your parser uses token.value as-is, so a tokenizer that recognises // as one token is required.Ensure your tokenizer emits // as a single token; otherwise the parser will see '/','/'.
- Right now the interpreter only calls prelude functions; adding user?defined functions or macros will need more work.Consider an Environment object that stores both primitives and user definitions, and a small define syntax.
- Implement load command in REPL: Reads file, tokenizes, parses, interprets, handles file not found.
- Implement test command in REPL: Loads file and executes tests (if present).
- Implement Syntax Highlighting: Adds visual cues for better readability.
- Implement Command History: Enables REPL command recall.
- Implement Basic Identifier/Function Autocompletion: Provides assistance during input.
- Add Printing of Current Environment: Displays variables and functions in scope.

###############################################################################
MAYBE

###############################################################################
DONE
- These - Should we remove operator? The simplest thing is to have and Identifier Only
- Add check to BUILTINS_DICT shadowing prelude functions

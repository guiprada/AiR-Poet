TODO
- I think the next step should be implementing the table AST node and basic table literal parsing
  * First implement a basic TableLiteral AST node and parsing support?
  * Then create a Table runtime value that can serve as both data structure and environment?
  * Finally, make Environment either inherit from or wrap the Table type?
  * TableNode should be map: dict[ASTNode, ASTNode]
  - Stripping quotes in strings should be in the parser or tokenizer? Implement proper string unescaping, multiline strings and escaped strings
  - eval <Table>

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

# Table Scheme & T-Exp Roadmap

Notes:
We are heading towards an approach where parentheses are used for immediate evaluation,
and tables are used for data representation and code representation and therefore need to be lazy evaluated.
But I think we could merge the semantics and both approaches could be parsed by the same parser. Traditional
s-exp would be parsed as a table with indices starting from 0, and optional keys.

------------------------------------------

## Proposed Steps

- Step 1: Document Intended Semantics
    - Write a doc in `docs/table_scheme_dev_notes/` describing:
        - Table literal syntax
        - S-expression-to-table mapping
        - Access patterns (index, key, dot, string)
        - Evaluation rules (immediate vs lazy)
        - Edge cases (empty tables, mixed keys, nesting)

- Step 2: Write Edge-Case Tests
    - Add a test file `tests/test_table_expressions.py` with cases for:
        - Table literals with positional and named entries
        - Nested tables
        - Table as code block
        - Table as environment
        - Table access and mutation (index, key, dot, string)
        - Evaluation of tables as code blocks

- Step 3: Prototype Parser Extension
    - Extend the parser to recognize curly-brace table literals
    - Parse S-expressions as tables with positional indices
    - Allow optional named keys in both forms
    - Keep parsing and IR simple and explicit

- Step 4: Review and Simplify
    - Document parser changes and test results
    - Review for simplicity and clarity
    - Only move to evaluation after parsing is robust

------------------------------------------

###############################################################################
MAYBE

###############################################################################
DONE
- REPL file loader
- Operator functions should be arity agnostic :) - Where should the arity be considered and dispatched?
- These - Should we remove operator? The simplest thing is to have and Identifier Only
- Add check to BUILTINS_DICT shadowing prelude functions

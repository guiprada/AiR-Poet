# AiR-Poet Codebase Analysis

## Executive Summary

AiR-Poet is an **intermediary representation (IR) language and interpreter** designed to be a deterministic code generation target for the META system. It implements a **table-based Lisp dialect** where tables serve as both data structures and code execution environments. Two evaluation modes coexist:
- **Immediate evaluation**: Lisp-style `(fn args...)` for side effects
- **Lazy evaluation**: Table literals `{...}` defer evaluation until explicitly invoked with `<:`

---

## 1. Existing Language Features

### Core Data Types

| Type | Syntax | Example | Purpose |
|------|--------|---------|---------|
| **Number** | Integers/Floats | `42`, `3.14`, `-7` | Numeric values |
| **String** | Double quotes | `"hello world"` | Text |
| **Symbol** | Single quotes | `'x`, `'hello` | Identifiers/atoms (not evaluated) |
| **Identifier** | Unquoted words | `foo`, `add`, `my_var` | Variable/function names |
| **Table** | Curly braces | `{1 2 3}` or `{x: 5 y: "hi"}` | Maps + code blocks |

### Expression Types

#### 1. **Lisp-Style Calls** – Immediate Evaluation
```lisp
(fn arg1 arg2 ...)
(+ 1 2)        ; → 3
(print "hello") ; → prints, returns nil
```
- Syntax: `(callee arg1 arg2 ...)`
- Arguments evaluated left-to-right in current environment
- Callee can be:
  - Identifier → lookup in env, then LOOKUP (prelude + builtins)
  - Expression → recursively evaluate
- Built-in operators: `+`, `-`, `*`, `/`, `%`, `^`, `//`

#### 2. **Table Literals** – Lazy Evaluation
```
{ positional, entries, "x": 99, "y": 3.14 }
```
- Syntax: `{ [key:] value, [key:] value, ... }`
- Positional entries: stored in `.elements` array (indexed 0, 1, 2, ...)
- Named entries: stored in `.map` dict (key → value)
- **Returns unevaluated** for explicit eval via `<:`
- Can parse mixed positional + named in any order

#### 3. **Index Access**
```
t[key]
my_table[0]      ; positional: returns elements[0]
data["name"]     ; keyed: returns map["name"]
```
- `[key]` postfix operator
- Key evaluated, then looked up in table

#### 4. **Field Access**
```
t.field_name
person.age       ; sugar for person["age"]
```
- Dot notation for convenient named access

#### 5. **Table Calls** – Function Tables
```
fn{arg_key: value, other: 123}
```
- Sugar for calling table-wrapped functions with named arguments
- Evaluates arguments in caller's env, passes to function env

#### 6. **Explicit Evaluation** – Code-as-Data
```
<: expression
<: { x: 10, y: 20 }     ; explicit eval of table
```
- `<:` prefix operator
- Forces immediate evaluation of a table that would otherwise remain data

### Control Flow

#### Conditional – Table Form
```
{
  if: (> x 5)
  then: { print "big" }
  else: { print "small" }
}
```
- Detected via `_IF_KEY` in table.map
- Special form with lazy branches
- Branches can be tables (eval'd) or expressions

#### Loop – Table Form
```
{
  init: { i: 0 }
  cond: (< i 10)
  loop: { i: (+ i 1), print i }
}
```
- Detected via `_INIT_KEY` in table.map
- Creates loop-scoped environment
- Mutations visible across iterations

### Built-in Functions (Prelude)

**Arithmetic**: `add`, `subtract`, `multiply`, `divide`, `modulus`, `exponent`, `floor_divide`
- Variadic: `(+ 1 2 3)` → 6
- Operators map to functions: `+` → `plus`, `-` → `minus`, etc.

**Python Built-ins**: All standard Python callables (via `build_builtin_lookup()`)
- `print`, `len`, `str`, `int`, `list`, `dict`, etc.

**Special Forms**:
- `(define key value)` – bind in current env, return value
- `(eval table)` – explicitly evaluate table as code

### Environment/Scoping

- **TableNode as Environment**: Each table has optional `_meta_table` (parent scope)
- **Lookup chain**: `table[key]` → tries table.map → tries _meta_table (if set)
- **Binding**: `define` binds in current table only (no parent mutation)
- **REPL env**: Single global `env: TableNode()` persists across commands

---

## 2. Implementation Architecture

### Parser Pipeline

```
Source Code
    ↓ tokenize()
Token Stream
    ↓ parse() / parse_program()
AST (nodes)
    ↓ interpret() / interpret_program()
Runtime Values (int, str, TableNode, etc.)
```

#### **Tokenizer** (`tokenizer.py`)
- **Single-pass tokenization** with line/column tracking
- **Token types**: `lparen`, `rparen`, `lbrace`, `rbrace`, `lbracket`, `rbracket`, `colon`, `comma`, `dot`, `eval_op`, `string`, `symbol`, `number`, `identifier`
- **Parsing rules**:
  - Whitespace, `(){}[].,:<` are delimiters
  - `<:` recognized as single `eval_op` token
  - Strings: `"..."` (unmatched quote → error)
  - Symbols: `'...'` (single-quoted literals)
  - Numbers: auto-detected as `int` or `float`
  - Identifiers: anything that doesn't parse as number

#### **Parser** (`parser.py`)
- **Top-level functions**:
  - `parse(tokens)` – single expression (backward compat)
  - `parse_program(tokens)` – sequence of expressions as implicit table
  - `parse_sequence(tokens, pos, end_token)` – helper for table/program parsing
  
- **Grammar** (simplified):
  ```
  expression = primary postfix*
  primary    = <: expr | { ... } | ( ... ) | string | symbol | number | id
  postfix    = [key] | .field | {args}
  call       = (callee arg*) 
  table      = { sequence }
  sequence   = (expr | key: expr), *
  ```

#### **AST Nodes** (`ASTNode.py`)
All inherit from `ASTNode`:
- `IdentifierNode(value: str)`
- `StringNode(value: str)` – strips `"` on construction
- `SymbolNode(value: str)` – strips `'` on construction
- `NumberNode(value: str)` – parses to int/float during init
- `CallExpressionNode(callee, arguments: list)`
- `TableCallNode(callee, args: TableNode)` – `fn{args}` form
- `IndexAccessNode(table, key)` – `t[k]`
- `FieldAccessNode(table, field: str)` – `t.f`
- `EvalNode(expr)` – `<: expr`
- `TableNode` – **the core data structure**

#### **TableNode – The Core**
```python
class TableNode:
  elements: list[ASTNode]       # positional entries (0-indexed)
  map: dict[ASTNode, ASTNode]   # named entries
  entries: list[(key, value)]   # insertion order (for eval)
  _meta_table: TableNode        # parent scope
```
- Every value is an `ASTNode` until **explicitly interpreted**
- Tables are **lazy by default** (store AST, not evaluated values)
- Supports both implicit (array-like) and explicit (map-like) indexing
- Chained lookups via `_meta_table` for scope inheritance

#### **Interpreter** (`interpreter.py`)
- **Entry points**:
  - `interpret(ast, env)` – evaluate single node
  - `interpret_program(ast, env)` – evaluate entire file/program
  - `load_file(path)` – tokenize → parse → return AST (not evaluated)

- **Evaluation dispatch**:
  - `NumberNode` → return numeric value
  - `StringNode` → return string (quotes already stripped)
  - `SymbolNode` → return symbol string
  - `TableNode` → return unevaluated (unless code)
  - `IdentifierNode` → lookup in env, then LOOKUP
  - `EvalNode` → evaluate expr, assert result is TableNode, call `eval_table()`
  - `IndexAccessNode` → evaluate table + key, return table[key]
  - `FieldAccessNode` → evaluate table, return table.field
  - `CallExpressionNode`:
    - Detect special forms: `define`, `eval`
    - Otherwise: evaluate callee → call with evaluated args
  - `TableCallNode` → evaluate args in caller env, call table-wrapped function

- **Special Table Forms** (O(1) detection):
  - `if`/`then`/`else` → conditional execution
  - `init`/`cond`/`loop` → loop with scope and mutations
  - Both use `_meta_table` for parent env, support branching

- **LOOKUP Chain**:
  ```python
  LOOKUP = {
    # All prelude functions (arithmetic, I/O, builtins)
    "add": add_fn,
    "print": print_fn,
    # Operator aliases
    "+": plus_fn,
    "-": minus_fn,
    # All Python builtins
  }
  ```

### Prelude (`prelude.py`)
- **Arithmetic functions**: `add`, `subtract`, `multiply`, `divide`, `exponent`, etc.
  - Variadic: `(+ 1 2 3 4)` → sum of all
  - Aliases: `plus`, `minus`, `star`, `slash`, etc.
- **Operator dict**: maps symbolic names (`+`, `-`, etc.) to functions
- **Builtin isolation**: `build_builtin_lookup()` ensures no shadowing of prelude functions

---

## 3. Test Programs & Examples

### Existing Examples

#### `test_programs/01_hello_world.poet`
```lisp
(print "Hello World")
```
- Simple: demonstrates basic call expression + print side effect
- Confirms tokenizer, parser, interpreter pipeline works end-to-end

### Test Suites

#### `tests/test_interpreter.py`
Tests the evaluation layer:
- Arithmetic: `(+ 1 2)` → 3
- Operator aliases: `(add 10 15)` → 25
- Negative numbers: `(add -1 -2)` → -3
- Side effects: print capture

#### `tests/test_table_node.py`
Tests table mechanics:
- Positional + named indexing
- Meta-table (parent scope) fallback
- `define()` auto-extends arrays
- Parser integration: `{1 2 3 x: 10}` parsed correctly
- **TODO**: lazy evaluation of table contents, special forms

#### `tests/test_parse.py`
Tests parser:
- Expressions, calls, tables, index access, field access

#### `tests/test_tokenize.py`
Tests tokenizer:
- Token recognition, position tracking, error handling

#### `tests/test_ast_node_hashes.py`
Tests AST node equality and hashing (for map key usage)

---

## 4. Abandoned Code (lost_and_found/)

These files hint at earlier system attempts (now superseded):
- `agent.py`, `client.py` – old agent implementations
- `cert_manager_client.py`, `cert_manager_server.py` – old cert logic
- `server_broken.py` – reference "broken system" (backporting model)
- `check_db.py`, `check_ca.py`, `check_ldap.py` – old diagnostics
- `messages_schema.json` – old message format
- `app_old.js`, `index.html_old` – old web UI

**Lesson**: AiR-Poet replaces these with a unified IR.

---

## 5. Key Design Patterns & Semantics

### Pattern 1: Tables as Code Blocks
```
{ 
  x: 10
  y: (+ x 5)        ; unevaluated expression
  z: (print x)      ; unevaluated side effect
}
<: table            ; NOW evaluated top-down in table's scope
```
- **Lazy by default**: entries stored as AST
- **Evaluated on demand**: `<:` or in special forms
- **Scope**: child env inherits from parent

### Pattern 2: Mixed Positional + Named Indexing
```
{ 
  10, 20, 30        ; elements[0/1/2]
  x: "hello"        ; map[IdentifierNode("x")]
  1: "second"       ; elements[1] (number key in map)
}
```
- Parser merges both into single `TableNode`
- Colon `:` signals named entry
- Commas optional between entries

### Pattern 3: Scope Inheritance via Meta-Table
```
child_env = TableNode(meta_table=parent_env)
child_env[key]  ; tries child first, then parent
```
- No mutation of parent (define stays local)
- Natural for nested scopes (function calls, loops)

### Pattern 4: Function Tables
```
my_fn = { a: 0, b: 0, result: (+ a b) }
my_fn{a: 3, b: 7}       ; calls with named args, returns result
```
- Tables can store partial state + computation
- `TableCallNode` passes args as child env, evaluates body

### Pattern 5: Special Forms via Map Keys
```
_IF_KEY = IdentifierNode('if')
if (_IF_KEY in table.map):
    return _eval_if_form(table, env)
```
- O(1) detection of special forms
- Avoids parser overhead (no special syntax)
- Examples: `if/then/else`, `init/cond/loop`

---

## 6. Current Limitations & TODOs

### Completed
- ✅ Tokenizer (strings, symbols, numbers, identifiers, operators)
- ✅ Parser (expressions, calls, tables, postfix operators)
- ✅ Interpreter (basic evaluation, special forms, scope)
- ✅ REPL with `run` and `env` commands
- ✅ Arithmetic with variadic operators

### In Progress
- 🔄 Lazy table evaluation (basic support, needs more tests)
- 🔄 Loop/conditional special forms (basic support, needs refinement)

### Planned (TODO.md)
1. **Negative number tokenization** – currently `-1` is identifier, should be number token
2. **Multiline strings** – escaped quotes, newlines
3. **User-defined functions** – need better `define` semantics
4. **Test framework** – `test` command in REPL
5. **Syntax highlighting** – for editor integration
6. **Command history** – REPL UX
7. **Autocompletion** – REPL UX
8. **Environment printing** – `env` command refinement

### Edge Cases (meta.meta notes)
- Empty tables
- Nested tables
- Table access mutation
- Evaluation of mixed key types (number vs identifier)

---

## 7. Patterns to Leverage for META/AiR System

### 1. **Table-as-Everything** ✅
The `TableNode` abstraction enables:
- **Data**: positional arrays + key-value maps
- **Code**: unevaluated AST stored until `<: table`
- **Environment**: scope inheritance via `_meta_table`
- **Modules**: immutable tables with function definitions
- **Systems**: stateful tables with lifecycle hooks (`init`, `start`, `update`, `stop`)

**Leverage**: Use same `TableNode` for all AiR concepts. No need for multiple data structures.

### 2. **Lazy Evaluation by Default** ✅
- Expressions stored as AST, evaluated on demand
- Critical for:
  - **Code generation**: AI generates AiR files that represent code, not execute it
  - **Determinism**: same AST always produces same result
  - **Introspection**: can analyze code before execution

**Leverage**: Keep table contents as unevaluated `ASTNode`. Only eval when needed (in functions, special forms, `<:`).

### 3. **Special Forms via Map Keys** ✅
```
{ if: ..., then: ..., else: ... }    # no special parser syntax needed
{ init: ..., cond: ..., loop: ... }
--- could extend to ---
{ require: ..., initialize: ..., data: ..., type: ... }
```
- Avoids parser bloat
- Keys are data → can introspect
- Easy to add new forms

**Leverage**: Replace hardcoded `_IF_KEY`, `_INIT_KEY` with named-key lookup for all special forms. Define form catalog in prelude/intrinsics.

### 4. **Scope Inheritance Chain** ✅
```
system_env = TableNode(meta_table=global_env)
module_env = system_env     # shared read-only
function_env = TableNode(meta_table=module_env)
```
- Natural for module imports (`require:` binds in parent)
- Natural for system initialization (`initialize:` creates child)
- Prevents accidental mutation of parent

**Leverage**: Uses existing `_meta_table` mechanism. Module loader just sets parent pointers.

### 5. **Mixed Positional + Named Indexing** ✅
```
{
  "entry_count": 5
  0: "first"
  1: "second"
  items: { name: "a", value: 10 }
}
```
- Good for both implicit-enumeration (test assertions) and named-field (system state)

**Leverage**: Parser already handles `key: value` syntax. Just extend to support both in same table.

### 6. **Function Tables as Closures** ✅
```
{
  x: 10
  double: { (+ x x) }       # captures x from outer scope
}

<: the_table.double          ; returns 20 (x visible via _meta_table)
```
- Lightweight alternative to lambda syntax
- Tables capture scope naturally via `_meta_table`

**Leverage**: Use for module functions + system state mutators.

### 7. **Deterministic Ordering via .entries** ✅
```
table.entries = [(key1, val1), (key2, val2), ...]    # insertion order preserved
```
- Critical for reproducible output
- Parser populates `.entries` during parse
- Interpreter evaluates in order

**Leverage**: Ensures AiR files generate deterministically (same input → same AST → same output order).

---

## 8. Recommended Next Steps for META Integration

### Phase 1: Extend Interpreter for System Semantics
```python
# Add to prelude/intrinsics.air
require:  (metadata key value)    # import module by name
initialize: (instance subsystem)  # spawn system instance
define: (local_bind key value)    # bind in current scope
```

### Phase 2: Implement Module Loader
- Parse `require: {...}` as nested table
- Create module environment from loaded `.air` files
- Set `.` on system env (`_meta_table`)

### Phase 3: Implement System Instantiation
- Parse `initialize: {...}` as nested table
- Create new `TableNode(meta_table=module_env)` for each instance
- Run `init:` block if present

### Phase 4: Lifecycle Management
- Add `start:`, `update:`, `pause:`, `stop:` table forms
- Interpreter calls these at appropriate times
- State mutations persist in system env

### Phase 5: Type System + Validation
- Add `type:` key check → determine required fields
- Enforce `name:` presence
- Validate special keys per type

---

## Summary Table: What Works, What's Ready to Extend

| Feature | Status | Notes |
|---------|--------|-------|
| **Tables** | ✅ Solid | Positional + named, lazy eval, scope via meta-table |
| **Expressions** | ✅ Solid | Lisp calls, operators, postfix access |
| **Special Forms** | ✅ Good | `if/then/else`, `init/cond/loop` via map keys |
| **Scope** | ✅ Good | Meta-table inheritance, no parent mutation |
| **Laziness** | ✅ Good | Tables store AST by default, eval on `<:` |
| **Arithmetic** | ✅ Complete | Variadic ops, all basic math |
| **I/O** | ✅ Basic | `print` works, can extend |
| **Module System** | 🔄 TODO | Need `require:` form + loader |
| **System Types** | 🔄 TODO | Need lifecycle hooks + instantiation |
| **Type Validation** | 🔄 TODO | Need `type:` → required keys mapping |
| **Negative Numbers** | ❌ Bug | `-1` parsed as identifier, not number |
| **Strings** | ⚠️ Basic | No escape sequences, multiline |

**Verdict**: The **core language is solid and ready for extension**. Focus on module/system support + type system to unlock META capabilities.

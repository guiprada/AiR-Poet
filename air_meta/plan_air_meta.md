# Plan: air_meta

Generated from: `air_meta/air_meta.meta`
Status: Phase 1 Python runtime partially complete; AiR self-description incomplete

---

## 1. Current State Inventory

### File Structure

```
AiR/
  air.air        ← AiR language self-description (most complete AiR file; needs merge into air/)
  air.meta       ← Language spec (content belongs in air_meta.meta)
  README.md
air/
  tokenizer/
    tokenizer.py      ← Phase 1 Python implementation (working, tested)
    tokenizer.air     ← AiR stub: API surface only, type: module
    test.py           ← Python tests (passing)
    test.air          ← Python descriptor, type: python_source
    tokenizer.meta
  parser/             ← same pattern as tokenizer
  ast_node/           ← same pattern; also has test_hashes.py / test_hashes.air
  interpreter/        ← same pattern; also has utils.py / utils.air
  prelude/            ← no test.py yet
  repl/               ← no test.py yet
air_meta/
  air_meta.meta       ← Single source of truth
  plan_air_meta.md    ← This file
air_vm/
  air_vm.meta         ← EMPTY — major gap
bootstrap_meta.meta   ← Original bootstrap; superseded
```

### Phase 1 Python Runtime — What Works

- `tokenize(source) → [Token]` — complete and tested
- `parse_program(tokens) → TableNode` — complete and tested
- `interpret(ast, env) → value` — working:
  - Literals: NumberNode, StringNode, SymbolNode
  - Identifiers: looked up in env, then in LOOKUP (prelude)
  - TableNode: returned as-is (lazy — tables are data until `eval`'d)
  - `EvalNode` (`<: expr`) — forces evaluation of a table
  - `if:` / `then:` / `else:` — special form in table
  - `init:` / `cond:` / `loop:` — loop special form in table
  - `define` — binds name in env
  - `eval` — explicit evaluation of table
  - `CallExpressionNode` — Lisp `(f a b)` style
  - `TableCallNode` — table-style `f{ a b }` style
  - `FieldAccessNode` — `table.field`
  - `IndexAccessNode` — `table[key]`
- `prelude` — arithmetic, comparison, logic (Python functions, exposed via LOOKUP)
- `repl` — interactive session

### What is Missing / Gaps

1. **`AiR/` not merged** — `air.air` (the language definition) has no home in `air/`
2. **`air_vm.meta` is empty** — the AiRVM specification is not written
3. **All unit `*.air` stubs are placeholders** — they describe API shape only, not implementations
4. **`require:` not implemented** — interpreter cannot load `.air` modules at runtime
5. **`initialize:` not implemented** — interpreter cannot instantiate systems
6. **`name:` / `type:` enforcement absent** — loaded files are not validated for mandatory fields
7. **Naming inconsistency** — `air.air` defines `add`/`sub`/`mult`/`div`; `prelude.air` uses `add`/`subtract`/`multiply`/`divide`
8. **`python_source` descriptor format** — `test.air` etc. wrap content in `{}` but all other `.air` files are bare top-level tables (inconsistent)
9. **`type: "module"` stubs** — the unit `.air` files claim `type: "module"` but contain no working function bodies

---

## 2. The Type Dispatch Model

Every `.air` file has a `type:` key. `type` determines BOTH dispatch (which handler runs this file)
AND semantics (how content is interpreted).

**Rule**: All types except `python_source` (and future `c_source`, `js_source`) are AiR source
handled by AiRVM. There is NO separate `air_source` type — AiRVM is the default handler.
`python_source` is the only exception: it delegates to Python, and the file is merely a descriptor.

| `type:` value   | Dispatch handler  | Semantic role                          |
|-----------------|-------------------|----------------------------------------|
| `module`        | AiRVM             | Pure functions and immutable constants |
| `system`        | AiRVM             | Stateful execution with lifecycle      |
| `test`          | AiRVM             | Ordered assertions                     |
| `data`          | AiRVM             | Pure structured data, no behavior      |
| `computation`   | AiRVM             | Evaluable arithmetic/logic forms       |
| `logic`         | AiRVM             | Control flow expressions               |
| `python_source` | Python handler    | Descriptor for a `.py` file            |
| `meta`          | META system       | Specification / planning document      |

**Consequence for unit `.air` files**: `tokenizer.air` with `type: "module"` IS an AiR source
file handled by AiRVM. The stubs currently have no function bodies — they need real implementations.

---

## 3. AiR/ → air/ Merge

`AiR/air.air` is the most developed AiR self-description and belongs in the `air/` module hierarchy.

**Target**: `air/air/air.air`

The folder-module convention is: a module named `foo` lives at `air/foo/foo.air`.
The `air` module (the language definition itself) follows the same convention: `air/air/air.air`.
It would be imported as: `require: { air: "air/air/air.air" }`.

**Steps**:
1. Create `air/air/` directory
2. Move `AiR/air.air` → `air/air/air.air`
3. Merge `AiR/air.meta` content into `air_meta/air_meta.meta`
4. Remove `AiR/` directory

---

## 4. Naming Consistency Fix

`air/air/air.air` defines the canonical AiR intrinsic names:
`add`, `sub`, `mult`, `div`, `mod`, `sqrt`, `exp`, `log`

`prelude.air` and `prelude.py` currently use different names:
`add`, `subtract`, `multiply`, `divide`, `modulus`, `exponent`, `floor_divide`

**Fix**: `prelude` should align with `air.air` names. Ideally `prelude.air` imports `air.air` via
`require:` and re-exports or wraps the canonical names. `prelude.py` must be updated to match.

---

## 5. `python_source` Descriptor Format Fix

Current (inconsistent — has wrapper `{}`):
```
{
    name: "test.py"
    type: "python_source"
    runtime_type: "cpython"
    runtime_min_version: "3.10"
    runtime_max_version: "3.12"
}
```

Correct (bare top-level table, consistent with all other `.air` files):
```
name: "test.py"
type: "python_source"
runtime_type: "cpython"
runtime_min_version: "3.10"
runtime_max_version: "3.12"
```

All `test.air`, `utils.air`, `test_hashes.air`, `test_print.air` need this fix.

---

## 6. `air_vm` Gap

`air_vm/air_vm.meta` is empty. The Phase 1 AiRVM is `interpreter.py` — a Python AST tree-walker.
It needs a proper AiR self-description.

`air_vm` is a **system** (not a module) because:
- Phase 2+ will have mutable state (bytecode compiler state, VM registers)
- It has a lifecycle: initialize (load module), start (begin evaluating), stop (cleanup)
- Multiple VM instances might run concurrently

**Files to create**:
- `air_vm/air_vm.meta` — spec: what the VM does, phases, dispatch by type
- `air_vm/air_vm.air` — AiR self-description, `type: system`

---

## 7. Implementation Phases

### Phase 1 — Python Foundation

Status: mostly done

- [x] Tokenizer (tokenize.py)
- [x] Parser (parser.py)
- [x] AST nodes (ast_node.py)
- [x] Interpreter: literals, identifiers, tables (lazy), if/loop forms, define, eval, call, field/index access
- [x] Prelude: arithmetic, comparison, logic (prelude.py)
- [x] REPL (repl.py)
- [ ] `require:` file loading — read `.air` file, eval as module env, inject into caller env
- [ ] `initialize:` system instantiation — create system instance with lifecycle + data
- [ ] `name:` / `type:` mandatory field validation on loaded files

### Phase 2 — AiR Self-Description

Status: gap

- [ ] Merge `AiR/air.air` → `air/air/air.air`
- [ ] Write `air_vm/air_vm.meta` and `air_vm/air_vm.air`
- [ ] Fix `python_source` descriptor format (remove wrapper braces)
- [ ] Fix naming consistency (align prelude names with air.air names)
- [ ] Fill `prelude.air` with real AiR function bodies (not just API stubs)
- [ ] Fill `ast_node.air` with real AiR type definitions

### Phase 3 — Module/System Loader

Status: not started

- [ ] `require:` loader: given a file path, parse → eval as module → return env table
- [ ] `initialize:` loader: given a system path, parse → instantiate (copy + inject data + bind lifecycle)
- [ ] Folder-based discovery: `air/tokenizer/tokenizer.air` resolves as module `tokenizer`
- [ ] `_meta_table` scope inheritance: module env set as `_meta_table` in importing env

### Phase 4 — AiR Self-Hosted Tests

Status: not started

- [ ] `test_meta.air` (defined inline in `air_meta.meta`) passes when run via AiRVM
- [ ] Unit `test.air` files evolve from `python_source` descriptors to real AiR test tables
- [ ] Python `test.py` files remain for regression testing throughout bootstrap

### Phase 5 — AiRVM Phases 2 and 3

Status: Phase 1 done (Python tree-walker = interpreter.py); 2 and 3 not started

- [ ] Document Phase 1 AiRVM in `air_vm/air_vm.air`
- [ ] Phase 2: Lightning bytecode compiler design
- [ ] Phase 3: Embedded C lightning VM design

---

## 8. Self-Hosting Priority Order

The path from Python stubs to real AiR implementations, simplest first:

1. `prelude.air` — pure arithmetic and logic; no recursion, no file I/O
2. `ast_node.air` — data type definitions; no behavior logic
3. `tokenizer.air` — character-level string processing
4. `parser.air` — recursive descent over token list
5. `interpreter.air` — self-hosting the evaluator (most complex; requires all above)
6. `repl.air` — entry point, wires everything together

---

## 9. Output Files (Final Consensus)

```
air/
  air/
    air.air              ← Language definition (from AiR/air.air, expanded)
  tokenizer/
    tokenizer.air        ← Full AiR implementation (type: module)
  parser/
    parser.air           ← Full AiR implementation (type: module)
  ast_node/
    ast_node.air         ← Type definitions (type: module)
  interpreter/
    interpreter.air      ← Evaluator in AiR (type: module)
  prelude/
    prelude.air          ← Arithmetic/logic in AiR, aligned with air.air names (type: module)
  repl/
    repl.air             ← Entry point (type: system — has lifecycle)
air_vm/
  air_vm.air             ← VM spec (type: system)
air_meta/
  test_meta.air          ← Validation suite (type: test)
```

---

## 10. Open Questions for `air_meta.meta`

Design decisions that need to be explicit before code generation can proceed:

1. **Type dispatch rule**: Should `air_meta.meta` explicitly state "all types except `python_source`
   (and future `c_source`) are dispatched to AiRVM by default — no `air_source` type needed"?

2. **Naming canonical source**: Should `prelude.air` simply `require:` `air/air/air.air` and
   re-export its intrinsics, making `air.air` the single source of canonical names?

3. **`AiR/` merge target**: Does `air.air` live at `air/air/air.air` (folder-module convention)
   or flat at the repo root as `air.air`?

4. **`air_vm` as system or module**: `interpreter.py` is stateless (module-like), but Phase 2+
   needs state. Should `air_vm.air` be `type: system` now, or start as `type: module` and
   transition later?

5. **`python_source` top-level format**: Confirm the fix — bare top-level keys, no wrapping `{}`.

6. **`repl` lifecycle**: `repl.air` reads stdin / writes stdout with a loop — is it `type: system`
   (has `init`/`start`/`stop`) or `type: module` (just a `main` function)?

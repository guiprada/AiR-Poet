# AiR Table Semantics

Tables are the central data structure in AiR. They serve as arrays,
dictionaries, environments (scopes), and code blocks — all at once.

---

## Table Literal Syntax

A table literal is enclosed in curly braces `{ ... }`. Entries are separated
by commas (optional). Each entry is either:

- **Positional** — a bare expression, stored by sequential index (0, 1, 2, …)
- **Named** — `key: value`, where the key is an identifier, string, or number

```
{}                        // empty table
{1, 2, 3}                // positional: elements[0]=1, elements[1]=2, elements[2]=3
{x: 1, y: 2}             // named: map[x]=1, map[y]=2
{1, 2, name: "hello", 3} // mixed: elements=[1,2,3], map[name]="hello"
{0: "a", 1: "b"}         // numeric keys write into elements[] by index
```

---

## S-Expression to Table Mapping

A parenthesised S-expression `(f a b)` is parsed as a `CallExpressionNode`,
not a table.  A table with positional entries `{f, a, b}` is equivalent data,
but is *not* called automatically — it must be explicitly evaluated with `<:`.

```
(f a b)       // CallExpressionNode — immediately called
{f, a, b}     // TableNode(elements=[f,a,b]) — lazy data
<: {f, a, b}  // EvalNode wrapping the table — evaluates entries top-down
```

---

## Access Patterns

| Syntax      | Meaning                                      |
|-------------|----------------------------------------------|
| `t[0]`      | Positional index access (`elements[0]`)      |
| `t[k]`      | Key access — evaluates `k`, wraps as ASTNode |
| `t.field`   | Named field access — shorthand for `t[field]`|
| `fn{args}`  | Table call — evaluates `fn`, calls with args |

---

## Evaluation Rules

Tables are **lazy by default**. When the interpreter encounters a `TableNode`
it returns it unchanged:

```python
interpret(TableNode(...), env)  # → the TableNode itself
```

A table becomes active (executed as code) in these cases:

1. **`<: expr`** — EvalNode forces evaluation via `eval_table()`
2. **`(eval t)`** — explicit eval call
3. **`fn{args}`** — TableCallNode evaluates `fn`'s body with `args` as env
4. **Special forms** — tables with `if:`, `init:`, `cond:`, `loop:` keys are
   detected by `eval_table()` and dispatched to special handlers

---

## Table as Environment (Scope)

Every call to `eval_table()` creates a child environment:

```python
child_env = TableNode(meta_table=env)
```

The `meta_table` chain provides lexical scoping. Lookup walks the chain:
`__contains__` and `__getitem__` check `self` first, then `_meta_table`.

`define(key, value)` always writes to the **current** table (current scope).
`__setitem__` mutates the table where the key already exists (scope-aware).

---

## Special Forms

Tables with certain named keys trigger special evaluation:

### `if` form
```
{if: cond, then: t_branch, else: f_branch}
```
Evaluates `if` key; picks `then` or `else` branch. Branch may be a table
(evaluated as a code block) or a plain expression.

### Loop form
```
{init: {i: 0}, cond: (< i 10), loop: {i: (+ i 1)}}
```
`init` sets up bindings in a new `loop_env`. `cond` is re-evaluated each
iteration. `loop` body is evaluated in `loop_env` (mutations persist).

---

## Edge Cases

- **Empty table**: `{}` → `TableNode(elements=[], map={})`
- **Numeric named keys**: `{0: "a"}` writes into `elements` at index 0, not `map`
- **Mixed positional + named**: positional entries fill `elements` in order;
  named entries go into `map` (or `elements` if key is a number)
- **Nested tables**: `{a: {x: 1}}` — the inner table is lazy until evaluated
- **Table as key**: keys in `map` must be `IdentifierNode`, `StringNode`, or
  `NumberNode` (enforced by parser)
- **Table as value**: any `ASTNode` can be a value, including another `TableNode`

---

## Implementation Notes

- `TableNode.entries` is an ordered list of `(key|None, value)` pairs as parsed.
  This is the authoritative sequence for top-down evaluation.
- `TableNode.elements` and `TableNode.map` are derived structures for O(1) access.
- `eval_table()` iterates `entries`; named entries bind their result in the env;
  positional entries are evaluated for side effects / last-value return.

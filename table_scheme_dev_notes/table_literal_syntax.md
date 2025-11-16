# Table Literal Syntax Bootstrap

## Purpose
Define the syntax and basic rules for table literals in AiR/Table Scheme.
This document will guide parser and test development.

---

## Syntax

- Table literals use curly braces `{ ... }`.
- Entries can be:
    - **Positional values** (no key): `'a'`, `x`, `42`
    - **Named values** (key-value pairs): `a: 1`, `b: "foo"`, `c: x`
- Entries are separated by whitespace or newlines.
- Keys can be identifiers, strings, or numbers.
- Values can be any valid expression, literal, or nested table.

### Example

```lisp
t:{
    'a'
    a: 1
    b: 2
    c: "oba"
    x
}
```

- `'a'` and `x` are positional (index-based) entries.
- `a: 1`, `b: 2`, `c: "oba"` are named entries.

---

## Access Patterns

- Positional: `t[0]`, `t[1]`
- Named: `t.a`, `t["b"]`, `t[c]`

---

## Edge Cases

- Empty table: `{}`
- Mixed positional and named entries: `{ 'a' b: 2 }`
- Nested tables: `{ inner: { x: 1 y: 2 } }`
- Duplicate keys: Last key wins (documented, but discouraged)
- Mixed types for keys/values

---

## Next Steps

- Write edge-case tests for table literals and access.
- Prototype parser support for curly-brace tables.
- Document and review.

---

## Example Usage

```lisp
(define t { a: 1 b: 2 'c' })
(print t.a)    ; prints 1
(print t[2])   ; prints 'c'
```

---
```# filepath: d:\DEV_GIT\AiR\docs\table_scheme_dev_notes\table_literal_syntax.md

# Table Literal Syntax Bootstrap

## Purpose
Define the syntax and basic rules for table literals in AiR/Table Scheme.
This document will guide parser and test development.

---

## Syntax

- Table literals use curly braces `{ ... }`.
- Entries can be:
    - **Positional values** (no key): `'a'`, `x`, `42`
    - **Named values** (key-value pairs): `a: 1`, `b: "foo"`, `c: x`
- Entries are separated by whitespace or newlines.
- Keys can be identifiers, strings, or numbers.
- Values can be any valid expression, literal, or nested table.

### Example

```lisp
t:{
    'a'
    a: 1
    b: 2
    c: "oba"
    x
}
```

- `'a'` and `x` are positional (index-based) entries.
- `a: 1`, `b: 2`, `c: "oba"` are named entries.

---

## Access Patterns

- Positional: `t[0]`, `t[1]`
- Named: `t.a`, `t["b"]`, `t[c]`

---

## Edge Cases

- Empty table: `{}`
- Mixed positional and named entries: `{ 'a' b: 2 }`
- Nested tables: `{ inner: { x: 1 y: 2 } }`
- Duplicate keys: It should error for nom meta keys.
- Mixed types for keys/values

---

## Next Steps

- Write edge-case tests for table literals and access.
- Prototype parser support for curly-brace tables.
- Document and review.

---

## Example Usage

```lisp
(define t { a: 1 b: 2 'c' })
(print t.a)    ; prints 1
(print t[2])   ; prints 'c'
```

---

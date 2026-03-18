# AiR: Intermediary Representation Language

This directory contains the AiR language specification and canonical definition files for the META system.

## Structure

```
AiR/
├── air.meta          - Meta description of the AiR language
├── air.air           - AiR language specification in AiR notation
├── lost_and_found/   - Historical/experimental files related to AiR development
└── README.md         - This file
```

## What is AiR?

AiR is a **table-based Lisp language** with lazy evaluation, designed as the target language for deterministic code generation by the META system.

### Key Features

- **Universal Tables**: Everything is a table—data, code, environment
- **Lazy Evaluation**: `{expression}` stays as AST until explicitly evaluated
- **Mixed Indexing**: Positional (arrays) + named keys (maps) in same structure
- **Scope Inheritance**: Parent tables provide scope via `_meta_table` reference
- **Deterministic**: Same input always produces identical output

### Core Language

**Primitives**: numbers, strings, booleans, symbols, atoms

**Collections**: Tables with positional entries `{a b c}` and/or named entries `{x: 1, y: 2}`

**Expressions**: Lisp forms
```
(+ 1 2)              ; immediate evaluation
{+ 1 2}              ; lazy (remains as AST)
{if: cond then: a else: b}   ; special form
{require: {...}}     ; module import
{initialize: {...}}  ; system instantiation
```

## Files

### air.meta
Machine-readable specification of the AiR concept. Used by the META system to understand language design and constraints.

### air.air
The AiR language specification written in AiR itself. Defines:
- All intrinsic operations (arithmetic, comparison, logic, type operations)
- Special forms and their semantics
- Table construction and manipulation
- Module/system lifecycle operations

## Integration with META System

AiR serves as the **intermediary representation** between:

1. **Input**: User `.meta` specifications (what to build)
2. **Processing**: AI `.prompt` plans (how to build it)  
3. **Output**: Executable `.air` implementations (the built system)

The lazy evaluation model enables:
- Generation of code before execution (inspect before run)
- Incremental consensus-driven refinement
- Non-destructive validation and testing
- Deterministic, reproducible synthesis

## Historical Notes

See `lost_and_found/` for experimental designs, abandoned approaches, and historical development notes related to AiR.

## Related

- **AiR-Poet**: Main implementation of AiR interpreter + META system
- **Sentinel**: Device management system that uses META/AiR for configuration

## Usage

Define systems/modules in `.air` files that conform to `air.meta` specification, then use the AiR-Poet interpreter to load, instantiate, and execute them.

```bash
# From AiR-Poet directory
python repl.py ../AiR/my_system.air
```

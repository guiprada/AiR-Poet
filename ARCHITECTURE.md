# AiR-Poet: META System Implementation

AiR-Poet is the **implementation and runtime** for the META system. It contains:

## Directories

- **parser.py, tokenizer.py, interpreter.py, ASTNode.py**: AiR language interpreter (table-based Lisp)
- **tests/**: Unit tests for core AiR functionality
- **test_programs/**: Example AiR programs
- **docs/**: Design documentation and language examples
- **.continue/, .claude/**: IDE/agent customization

## Architecture

AiR-Poet implements three layers:

### Layer 1: AiR Language Runtime
Canonical implementation of the AiR language (tokenization → parsing → interpretation).

**Files:**
- `tokenizer.py` - Lexical analysis
- `parser.py` - Syntax analysis → AST
- `ASTNode.py` - AST node definitions (universal TableNode)
- `interpreter.py` - Evaluation engine with lazy semantics
- `prelude.py` - Built-in functions and special forms

**Key Feature**: Lazy evaluation via `{ }` table form (stays as AST) vs immediate evaluation via `( )` form.

### Layer 2: META System
Implements the consensus-driven iteration workflow:
- ✅ `.meta` files (specifications)
- ✅ `.prompt` files (plans)
- 🔲 `.air` files (implementations)
- 🔲 Loaders: `require:` (modules), `initialize:` (systems)

**Files:**
- `meta.meta` - Meta specification of the META system
- `meta.prompt` - Implementation plan for META

**Role**: AiR-Poet reads `.meta` and `.prompt` files, interprets them, and generates executable `.air` implementations.

### Layer 3: AiRVM & Systems
Extended runtime for complex scenarios:
- ✅ Basic interpreter (Python tree walker)
- 🔲 Lightning compiler (C backend)
- 🔲 Embedded C VM (production)

Additional features TBD as needed.

## Relationship to AiR/

```
AiR/                      (Canonical Definition)
├── air.meta              - AiR language meta-specification
├── air.air               - AiR language in AiR notation
└── lost_and_found/       - Historical language design

AiR-Poet/                 (Implementation & Runtime)
├── [interpreter code]    - Executes AiR
├── meta.meta             - META system specification
├── meta.prompt           - META system implementation plan
└── [tests, examples]     - Validation
```

**Division of Responsibility:**
- **AiR/** = What the language is (definition)
- **AiR-Poet/** = How we implement it + how we use META to generate systems

## Next Steps

1. Implement AiR module loader (`require:` semantics)
2. Implement system instantiator (`initialize:` semantics)  
3. Create test infrastructure for `.meta` files
4. Build consensus generator (`.prompt` → `.air`)
5. Extend to Lightning VM for performance

---

**Status**: Core AiR language work, META architecture in progress

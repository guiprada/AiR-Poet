# plan_air_meta - META System Implementation Plan

## Overview
This plan describes the sequential steps, rationale, and implementation files needed to construct the META system - a methodology for AI-driven, deterministic code generation through iterative file-based consensus.

## Rationale

The META system solves the problem of translating high-level problem descriptions into concrete implementations deterministically. By using parallel descriptions (`.meta` and `plan_*.md` files), the system enables:

1. **User-driven specification** via `.meta` files (what to build)
2. **AI-driven planning** via `plan_*.md` files (how to build it)
3. **Consensus-driven iteration** where both parties converge on implementation
4. **Deterministic output** in AiR (intermediary representation language)
5. **Executable system** via AiRVM interpretation and module/system composition

## Architectural Foundation: Modules vs Systems

Before implementation, understand the core distinction:

**Modules** = Pure, Immutable Code
- Pure functions and immutable constant libraries
- Single import per running system via `require:` key
- Shared fearlessly across all systems
- Implemented as `.air` files or folders with same-name `.air` file
- No mutable state; composition-only semantics

**Systems** = Stateful Execution Environments
- Applications with mutable state = modules + data
- Instantiable multiple times via `initialize:` key
- Full lifecycle management: `init` → `start` → `update` → `pause` → `stop`
- Implemented as `.air` files with state definitions and behavior

## Sequential Implementation Steps

### Phase 1: Core AiR Language Definition
**Files:** `air.air`, `air_vm.air`

1. Define AiR syntax and semantics in AiR notation - New AiR folder in AiR-Poet
   - Primitives: numbers (int/float), strings, booleans, symbols
   - Collections: tables (key-value maps with implicit/explicit indexing)
   - Expressions: Lisp-like forms for computation and control flow
   - Take a look at old Air specification and implementation - move it to AiR/lost_and_found/
   
2. Implement AiRVM (Virtual Machine/interpretation engine)
   - Start with Python AST tree walker for parsing and executing AiR files
   - Phase 2: Compile to lightning VM bytecode for performance
   - Phase 3: Embedded C lightning VM in python for production deployments

3. Support basic constructs: 
   - Numbers, strings, booleans, symbols, Lisp expressions, conditional logic(control flow), and function definitions
   - Tables, key-value pairs, assertions
   - Embedded table literals with mixed key/value syntax

4. Establish mandatory fields for all tables:
   - `name`: identifier for the table
   - `type`: determines required keys (test, system, module, data, computation, logic)
   - Type-specific keys: systems need `init`, `pause`, `stop`, `start`, `update`; modules need function definitions

**Key Features:**
- Top-level implicit table model (entire file is a table)
- Modules imported via `require:` key (imports pure code)
- Systems instantiated via `initialize:` key (creates executable instances)
- Embedded table literals with key-value syntax
- Type system enforces required keys based on type
- Index notation: both explicit (0:, 1:) and implicit (sequential enumeration)

### Phase 2: Test Infrastructure
**Files:** `test_meta.air`

1. Define test specification format for AiR
   - Numbered assertions: `0: (assert_eq expected actual)`
   - Implicit enumeration: `(assert_neq a b)` auto-numbered

2. Implement assertion operations: `assert_eq`, `assert_neq`, and optionally `assert_less`, `assert_lesseq`, etc.

3. Support both explicit indexing and implicit enumeration in test tables

4. Enable test discovery and execution via AiRVM
   - Parse test tables
   - Execute assertions in order
   - Report pass/fail status

**Test Coverage:**
- Verify AiR parsing and interpretation
- Validate table construction and nesting
- Test assertion framework
- Validate module imports with `require:`
- Validate system instantiation with `initialize:`

### Phase 3: Module and System Loaders
**Files:** `module_loader.air`, `system_loader.air`

1. **Module Loader** (`require:` semantics)
   - Parse and import `.air` modules
   - Validate modules have correct `type: "module"` and function definitions
   - Make module contents available in scope
   - Prevent mutable state imports

2. **System Loader** (`initialize:` semantics)
   - Parse and instantiate `.air` systems
   - Create isolated execution environments with initial state
   - Initialize system data from definitions
   - Set up lifecycle handlers (init, start, update, pause, stop)
   - Allow multiple independent instantiations

3. Handle folder-based modules/systems
   - Folder with name `foo` contains `foo.air`
   - Auto-discover and load on import

### Phase 4: Lifecycle Management
**Files:** `meta.air`, `init.air`, `pause.air`, `stop.air`, `lifecycle.air`

1. **meta.air** - System orchestration and lifecycle
   - Define how systems are initialized and stopped
   - Manage order of execution for multiple systems

2. **init.air** - Initialization sequence
   - Load `.meta` specifications
   - Initialize AiRVM runtime
   - Load all required modules via `require:`
   - Instantiate all required systems via `initialize:`

3. **Start phase** - Beginning of system execution
   - Run system `start:` handlers in order
   - Initialize data structures and state

4. **Update phase** - System updates/ticks
   - Run periodic system `update:` handlers
   - Handle state mutations

5. **pause.air** - Checkpoint/pause state
   - Serialize system state
   - Save intermediate consensus state
   - Pause execution without shutdown

6. **stop.air** - Graceful shutdown
   - Run system `stop:` handlers in reverse order
   - Cleanup resources
   - Archive final state and consensus

### Phase 5: Intrinsic Functions
**File:** `intrinsics.air`

Implement core built-in functions:
- Arithmetic: `add`, `sub`, `mult`, `div`, `mod`, `sqrt`, `exp`, `log`
- Comparison: `eq`, `neq`, `lt`, `gt`, `lte`, `gte`
- Logic: `and`, `or`, `not`
- Control flow: `if`, `then`, `else`
- Type: `typeof`, `is_number`, `is_string`, `is_table`
- Table ops: `get`, `set`, `keys`, `values`, `merge`
- Assertions: `assert_eq`, `assert_neq`, `assert_less`, etc.
- Module/System: `require`, `initialize`, `define`

### Phase 6: Output Generation and Testing
**File:** (generated outputs)

1. Accept `.meta` + `plan_*.md` consensus as input
2. Generate executable `.air` implementation files
3. Compile/generate module and system loader files
4. Validate generated code against `test_meta.air`
5. Package final deliverable with all submodules
6. Verify determinism: same input → same output

## Implementation Architecture

```
META System
├── AiR Language Layer
│   ├── air.air              (language definition)
│   └── air_vm.air           (AiRVM specification)
├── Runtime Layer
│   ├── module_loader.air    (require: implementation)
│   ├── system_loader.air    (initialize: implementation)
│   └── intrinsics.air       (built-in functions)
├── Test Layer
│   └── test_meta.air        (validation tests)
├── Lifecycle Layer
│   ├── meta.air             (meta system definition)
│   ├── init.air             (initialization)
│   ├── lifecycle.air        (lifecycle management)
│   └── stop.air             (shutdown)
└── Generated Outputs
    ├── [system_name].air    (user-defined systems)
    └── [module_name].air    (user-defined modules)
```

## Key Definitions (AiR Notation)

### Module Format (Pure Functions/Constants)
```
name: "math_lib"
type: "module"
add: (define (a b) { add a b })
mul: (define (a b) { mul a b })
PI: 3.14159
```

### System Format (Stateful Application)
```
name: "counter_system"
type: "system"
init: "init.air"
pause: "pause.air"
stop: "stop.air"
start: (define () { ... })
update: (define () { ... })
require: {
    math: "math_lib.air"
}
initialize: {
    "subsystem1.air"
    "subsystem2.air"
}
data: {
    counter: 0
    max: 100
}
tests: "test_counter.air"
```

### Test Format
```
name: "test_suite_name"
type: "test"
0: (assert_eq 0 0)
1: (assert_neq 0 1)
2: (assert_eq (add 1 2) 3)
```

### Data Format
```
name: "data_table"
type: "data"
numbers: { 42 3.14 -7 }
strings: { "hello" "world" }
nested: {
    inner: { a 1 b 2 }
}
```

## Iteration Loop

1. User provides/refines `.meta` file with module/system definitions
2. AI generates `plan_<name>.md` (this plan)
3. User reviews `plan_<name>.md`, suggests refinements back to `.meta`
4. Loop repeats until consensus is reached
5. AI implements final consensus in `.air` files
6. Run `test_meta.air` validates complete implementation
7. Generate and package final deliverable

## Success Criteria

✓ AiRVM successfully parses all AiR syntax
✓ All tests in `test_meta.air` pass
✓ Module imports via `require:` work correctly
✓ System instantiation via `initialize:` works correctly
✓ Lifecycle phases execute in correct order
✓ Generated implementation matches consensus description
✓ Deterministic: same `.meta` + `plan_*.md` → identical implementation
✓ Multiple system instantiations remain independent

## Implementation Roadmap

### Week 1-2: Phase 1 (AiR Language + AiRVM)
- Parse basic AiR syntax (tables, primitives, Lisp expressions)
- Implement Python tree walker interpreter
- Support basic operations and assertions

### Week 3: Phase 2 (Test Infrastructure)
- Build assertion framework
- Create test runner
- Validate core language features

### Week 4: Phase 3 (Module/System Loaders)
- Implement `require:` semantics
- Implement `initialize:` semantics
- Support nested modules/systems

### Week 5: Phase 4 (Lifecycle Management)
- Implement lifecycle hooks
- State management between phases
- System orchestration

### Week 6: Phase 5-6 (Intrinsics + Output Gen)
- Complete built-in function library
- Implement output generation
- Full end-to-end testing

---

**Generated by:** META System Generator  
**User:** [Guilio Prada]
**Target Language:** AiR (Intermediary Representation)  
**Execution Engine:** AiRVM (Python AST walker → Lightning VM → Embedded C)  
**Status:** Ready for Phase 1 implementation  
**Last Updated:** 2026-03-17

---
name: AiR-Poet
description: Project wide instructions
invokable: true
---
<Goals>
We are building a Intermediary Representation language and interpreter called AiR.
The system has three parts.
- An intermediate representation language specification - AiR.
- A reference execution system. Right now it is an interpreter, but in the future it can be a JIT compiler or AOT compiler.
- A Lispish compiler that compiles source code to AiR code - It is called AiR-Poet.

Air-Poet extends lisp/scheme with not just hash tables as in Scheme or Lua, but richer table semantics used
for environment modeling, grouping results, or more expressive computation.

- Tables should be live editable
- Table could be used to represent a computation
- There should be a notationn to evaluate their value, this is the root of the computation representation
- Table could be used as execution environment
- Table could represent a computation in intermediary execution - kind like partial aplication

- This could allow for more expressive, compositional code where results are grouped or named in tables.
- It could enable new patterns for environment management, result aggregation, or even multi-value returns.
- The syntax and semantics are still fluid, and you?re in the exploration phase.

We should focus on maintaining simplicity and flexibility.
- The whole system should accomodate diferent source languages in the future.
- There should be more execution backends in the future.

We want to build simple, flexible and maintainable software. That is robust to change and easy to understand.
Above all, we want software to be useful. We want to avoid unnecessary complexity.
Documentation is important to us.
It should have a functionality that is clear.
- The system must be secure, reliable and scalable.
- The system must be easy to deploy and maintain in diverse environments.
- The system must provide clear and useful information to administrators.

We document a functionality. We make testes to validate the expected results. Rinse(
	clean up and simplify - We keep the code simple and clear.
	) and repeat.
</Goals>
-------------------------------------------------------------------------------
Guidelines for AI-generated code contributions:
We create the tests first, then the code to make the tests pass.
We move forward in small steps, adding a test at a time.

Do nots
- No halth solutions.
- Do not act when in doubt or dealing with incomplete information.
- Do not change more than 1 thing at a time. Specialy if unrelated or when fixing bugs.
- Do not add code without a purpose.
- Do not add flexibility you do not use at least twice.
- Do not mask errors.
- Do not adapt, do not be lenient. If code must be fixed, fix it.

Caution
- Dependencies should be added with caution and only in special cases. Prefer writing simple, tailormade code over adding dependencies.

Dos
- Do it right the first time.
- Do not alienate the human programmer :)
- Do not alianate the artificial programmer :)
- Simple is better.
- Explicit is better.
- Fail fast. Do not try to recover or be lenient.
- We do not code without tests.
- Tests.
- Test again.
- Keep it simple, as simple as we can get it.
- Test until it breaks, fix it, simplify and document it, in that order :)
- Programming is managing complexity.
- Complexity limits how far we can push our system.
- Functions should be very short and focused.
- Naming is hard but important.
- Code is read more often than it is written.
- There is no such a thing as deprecated code. If code is not used, remove it.

Values
- Simplicity
- Flexibility
- Maintainability
- Usefulness
- Documentation
- Easy/Robustness to change
- Understandability - Clear, concise and simple, with simple intentions
- Enough performance

Simplicity Triangle
- simplicity: Keep it simple, as simple as we can get it.
- optimization: (performance, memory, etc)
- abstraction(flexibility)

Hard limits
- Simplicity: Never compromise simplicity.
- Optimization: Never optimize before you have to - stop when good enough.
- Abstraction: Never add abstraction before it is needed - You only consider it after you have needed it twice.

When writing functions, classes or any software unit :) always:
- Write a test set with edge cases and expected outcomes before writing the function
- Add descriptive, complete and to the point docstrings - Be consistent with style and format.
- Include at least one example usage in docstrings when appropriate/possible.
- Include input validation. Be strict with input types and values. No leniency.
- Use early returns for error conditions
- Add meaningful variable names

Tools
- Our main programming language is Python - Use Python 3.10+ features.
- Our tasks are managed in TODO.md
- Our documentations is in docs/
- Our tests are in tests/ - the output of tests are stored in log_test_results.txt
- We are using unittest for testing.
- Development is done in VSCode in windows - Generate CMD commands.
- Server deployment is in linux systems - Use bash commands for server commands.
- Web interface is in HTML/JS - Use standard web technologies.

# Formatting Convention

## Task List Markers
* `*` (asterisk) = DONE items (completed tasks)
- `-` (hyphen) = Proposed items (not yet started)

This convention applies to:
- `docs/todo.md` - human-readable task list
- `docs/todo.json` - machine-readable task list
- Roadmap documents
- Any task tracking in documentation

**Example:**
```markdown
## Completed
* Add pretty-printing utilities
* Create Token class
* Modularize tokenizer
## Proposed
- Add error recovery tests
- Implement REPL

```

## File Naming
- Lowercase for documentation files: `bootstrap.md`, `todo.md`
- ALL_CAPS only for critical files: `README.md`, `LICENSE`
- Use underscores for multi-word names: `roadmap_1.txt`, `bootstrap_ir.json`

## Encoding
- Use ASCII-safe characters only (no unicode checkmarks ?, question marks ?, etc.)
- Use `[DONE]` or `[TODO]` tags if needed for clarity
- Prefer simple markers: `-`, `*`, `[DONE]`, `[TODO]`

## Documentation Structure
- `.md` files for human-readable docs (Markdown format)
- `.json` files for machine-readable data (JSON format)
- Keep both in sync when documenting the same information
- Use consistent key ordering in JSON for easier diffs

-------------------------------------------- t-exp Definition
A t-exp is a representation for code and data.
It is not evaluated eagerly as s-exp.
Commas are optional.

It can represent data as a dictionary:

- **Literal Table:** A table definition enclosed in curly braces `{}`.  The table consists of named fields and/or indexed elements.
    ```
    {
        field1: value1,
        field2: value2
        ...
        index1: value1
        index2: value2,
        ...
    }
    ```

It can represent an array list:

- **Literal Array List:**
    ```
    {
        value1,
        value2
        ...
        value3
        value4,
        ...
    }
    ```

It can represent a computational process:
t-exp can be evaluated in a s-exp as in:
    (eval {...})
or in a t-exp, as in
    <:{...}
*   `<: ` (Evaluation Block): This meta element evaluates the entire t-exp within the curly braces and returns the result.
It short-circuits the standard evaluation process.

- **Evaluation Block (do):** A block of code to be evaluated within a specific context. They are evaluated in order.
    ```
    {
        (define a "hello"),
        (define b " ")
        (define c "world")
        (print (+ a b c)),
    }
    (eval comp_t_2) -> prints "hello world"
    ```

### Special Forms

Certain forms within a t-exp are designated as "special forms" because they are evaluated differently from standard expressions.  Instead of being directly evaluated within the regular expression evaluation order, special forms have their own distinct evaluation rules. Special forms are evaluated after the array list elements.

Currently, the following forms are recognized as special forms:

*   `if:` (Conditional Expression): The `if:` form evaluates the condition and then evaluates either the `them` or `else` block based on the result.  The entire `if:` structure is evaluated as a single unit.
*   `init:`, `cond:`, `loop:` (Looping Construct): These forms within the looping construct are evaluated in a specific order and have their own rules for termination.

**Important Note:** The rules for evaluating special forms may evolve as the system develops.

- **Conditional Expression (if: them: else):** An expression that executes different code blocks based on a condition.
    ```
    {
        (define x 0)
        if: (> x 1),
        them: (+ x 5)
        else: (- x 2),
    }
    ```

- **Looping Construct (init: cond: loop):**
    ```
    {
      init: (define i 0),
      cond: (<= i 5)
      loop: (
          <: (print i),
          <: (define i (+ i 1))
      )
    }
    ```
    ```

- **Composite t-exp:** A combination of the above forms, nested within each other or sequenced using semicolons (`;`).  The sequencing is evaluated from left to right.
    ```
    (define x 5)
    t:{
        'a'
        a: 1
        b: 2
        c: "oba"
        x
    }
    (print t[0]) -> prints 'a'
    (print t[1]) -> prints 5
    (print t.a) -> prints 1
    (print t["b"]) -> prints 2
    comp_t_1:{
        (print t.c)
    }
    (eval comp_t) -> prints "oba"
    comp_t_2:{
        (define a "hello")
        (define b " ")
        (define c "world")
        (print (+ a b c))
    }
    (eval comp_t_2) -> prints "hello world"
    <:comp_t_2 -> prints "hello world"
    --- ex 2 - tables as computation representation
    {
        if: (> x 1)
        them: (+ x 1)
        else: (- x 2)
    }// now x = 3
    (print x) -> prints 3
    (eval {
        init: (define i 0)
        cond: (<= i 5)
        loop: (
            (print i)
            (increment i)
        )
    }) -> prints 0 1 2 3 4 5
    --- ex 3 - combined

    -- combined with 'scheme'(table scheme)
    (define t
        {'a' a:1 b:2 c: "oba" x}
    )
    (print t[0]) -> prints 'a'
    (print t[1]) -> prints 5
    (print t.a) -> prints 1
    (print t["b"]) -> prints 2
    (if (> x 1)
        them: (+ x 1)
        else: (- x 2)
    )
    // now x = 3
    (print x) -> prints 3
    ```
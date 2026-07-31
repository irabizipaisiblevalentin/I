# Tutorial Level 3 — Functions

**Objective:** package reusable logic with `umurimo`.

## What You'll Learn

- Defining functions with `umurimo` / `subira` / `iherezo`
- Parameters and return values
- Calling functions
- Recursion (with a caution)

## 1. Your First Function

```i
umurimo kubaho()
    andika "ni meze neza!"
iherezo

kubaho()
```

- `umurimo` (*work*) declares a function
- `kubaho` is the name
- `()` lists the parameters (none here)
- `iherezo` ends the body

Call a function by writing its name followed by parentheses: `kubaho()`.

## 2. Parameters and Return Values

```i
umurimo incamake(a: int, b: int) -> int
    subira a + b
iherezo

andika incamake(3, 5)
```

Prints `8`. Each parameter needs a type annotation: `izina: ubwoko`.

Return a value with `subira` (*return*). The `-> int` part says the function
returns an `int`.

## 3. More Examples

```i
umurimo ishyamara(umuriro: int) -> string
    niba umuriro irenze 30
        subira "hot"
    cyangwa
        subira "cool"
    iherezo
iherezo

andika ishyamara(35)   # hot
andika ishyamara(20)   # cool
```

## 4. Local Variables

Functions can declare their own variables. They are independent from the rest
of the program:

```i
umurimo kubaza(n: int) -> int
    shyira result = n * n
    subira result
iherezo

andika kubaza(7)   # 49
```

## 5. Recursion

Functions may call themselves. Here is the classic factorial:

```i
umurimo ibarirwa(n: int) -> int
    niba n <= 1
        subira 1
    iherezo
    subira n * ibarirwa(n - 1)
iherezo

andika ibarirwa(5)   # 120
```

> **Caution (1.0.0):** the reference VM is interpreted Python and has no
> tail-call optimization. Deep recursion (thousands of frames) is slow and can
> overflow the call stack. Prefer `wihuse` loops for long-running or numeric
> work. For example, `examples/projects/fibonacci_sum.i` sums even Fibonacci
> numbers with an iterative loop because a naive recursive `fibonacci` is too
> slow past `n ≈ 30`.

## 6. Loop-Friendly Function Bodies

Two 1.0.0 quirks affect functions, so keep these patterns in mind:

- **Loop with an `int` counter in a function:** safe. Example:

  ```i
  umurimo yegeranya(n: int) -> int
      shyira total = 0
      kuri i muri 0 kugeza n
          total = total + i
      iherezo
      subira total
  iherezo

  andika yegeranya(10)   # 45
  ```

- **Building a string inside a loop in a function:** unreliable in 1.0.0.
  Build strings in a loop at the *top level* of your program instead, or pass
  the value out and format it where you print. See
  `examples/projects/triangles.i` for a working top-level string-building loop.

## Practice

1. Write `piramidi(n: int) -> int` returning `n * (n + 1) / 2`.
2. Write `inkomoko(n: int) -> string` returning "even" or "odd".
3. Write `uburyohe(n: int) -> int` that counts how many digits `n` has
   (use the `uburengero(n / 10)` truncation trick from `sum_digits.i`).
4. Write a function `mwinshi(a: int, b: int) -> int` returning the larger
   of two numbers.

## Reference

- [Language Guide — Functions](../user-guide/language-guide.md#functions)
- [examples/projects/](../../examples/projects/) — validated example programs

## Next

[Level 4 — Working with Data](level-4.md)

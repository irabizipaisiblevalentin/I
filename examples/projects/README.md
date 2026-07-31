# Example Projects

Fifteen self-contained example projects for I 1.0.0. Every example compiles and runs
with the released toolchain:

```bash
i examples/projects/fizzbuzz.i -r
```

Run with the module form:

```bash
python -m compiler.compiler examples/projects/fizzbuzz.i -r
```

All examples use only features verified in 1.0.0 (see the
[Language Guide](../../docs/user-guide/language-guide.md)). Two examples read from
standard input (`soma`); pipe input to them when running non-interactively:

```bash
echo 10 | i examples/projects/guess_game.i -r
```

## Index

| # | Example | What it demonstrates |
| --- | --- | --- |
| 1 | `hello.i` | `andika`, comments |
| 2 | `fizzbuzz.i` | `kuri` loop, `niba` / `cyangwa_niba` / `cyangwa`, `%` |
| 3 | `primes.i` | functions, `wihuse` loop, lists |
| 4 | `fibonacci.i` | recursion, `munsi_ya`, `kuri` |
| 5 | `factorial.i` | recursion and iteration |
| 6 | `gcd_lcm.i` | Euclid's algorithm, `wihuse`, `%` |
| 7 | `sum_digits.i` | digit extraction with `wihuse` |
| 8 | `collatz.i` | the Collatz sequence |
| 9 | `multiplication_table.i` | nested `kuri` loops |
| 10 | `triangles.i` | building strings with loops |
| 11 | `binary_converter.i` | decimal → binary with `shyira_ko` constants |
| 12 | `fibonacci_sum.i` | even Fibonacci numbers below a bound |
| 13 | `perfect_numbers.i` | perfect numbers below N |
| 14 | `palindromic_primes.i` | functions composing functions |
| 15 | `guess_game.i` | `soma` (input), `wihuse true`, `gukoma` in `kuri` |

The original six single-topic examples remain in `examples/` (`hello.i`,
`variables.i`, `functions.i`, `conditionals.i`, `loops.i`, `fibonacci.i`).

# Tutorial Level 2 — Control Flow

**Objective:** make programs that decide and repeat.

## What You'll Learn

- Comparisons: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Conditionals: `niba` / `cyangwa_niba` / `cyangwa`
- Loops: `kuri` (for), `wihuse` (while), `kugeza` (do-while)

## 1. Comparisons

Comparison operators produce `true` or `false`:

```i
andika 5 irenze 3     # true  (greater than)
andika 5 munsi 3      # false (less than)
andika 5 == 5         # true  (equal)
andika 5 != 3         # true  (not equal)
andika 5 >= 5         # true
andika 5 <= 3         # false
```

Two words work as operators too:

- `irenze` — greater than (`>`)
- `munsi` or `munsi_ya` — less than (`<`)

> **Note (1.0.0):** logical operators like `kandi` (*and*), `cyangwa` (*or*),
> `&&`, and `||` are not supported yet. Combine checks with nested `niba`.

## 2. `niba` — If

```i
shyira umwaka = 2024
niba umwaka irenze 2000
    andika "modern times"
cyangwa
    andika "last century"
iherezo
```

`niba` (*if*), `cyangwa` (*else*), `cyangwa_niba` (*else if*), and `iherezo`
(*end*) close the block.

### Else-if chains

```i
shyira amanota = 85
niba amanota irenze 90
    andika "A"
cyangwa_niba amanota irenze 75
    andika "B"
cyangwa
    andika "C"
iherezo
```

### Nested conditionals

```i
shyira n = 15
niba n irenze 10
    niba n % 2 == 0
        andika "large and even"
    cyangwa
        andika "large and odd"
    iherezo
cyangwa
    andika "small"
iherezo
```

## 3. `kuri` — For Loops

```i
kuri i muri 0 kugeza 5
    andika i
iherezo
```

Prints `0` through `4`. The upper bound is **exclusive** — `kugeza` means
*until*: the loop runs while the counter is below the bound.

### Countdown

Count down by subtracting inside the body:

```i
kuri i muri 0 kugeza 10
    andika 10 - i
iherezo
```

Prints `10` down to `1`.

> **Note (1.0.0):** loops only run *forward*. `kuri i muri 10 kugeza 0`
> starts at the bound and never executes.

### A running total

```i
shyira total = 0
kuri i muri 1 kugeza 101
    total = total + i
iherezo
andika total
```

Prints `5050` — the sum of 1 to 100.

## 4. `wihuse` — While Loops

`wihuse` (*hurry*) repeats while a condition is true:

```i
shyira n = 5
wihuse n irenze 0
    andika n
    n = n - 1
iherezo
```

Prints `5 4 3 2 1`. Watch the condition — if it never becomes false, the loop
runs forever.

## 5. `kugeza` — Do-While Loops

`kugeza` (*until*) checks its condition *after* the body, so it always runs at
least once:

```i
shyira n = 5
kugeza n >= 5
    andika n
    n = n - 1
iherezo
```

Prints `5` once, then the condition `n >= 5` is false and the loop stops.

## 6. Looping over a List

`buri` (*each*) iterates over list elements:

```i
shyira imibare = [10, 20, 30]
buri n muri imibare
    andika n
iherezo
```

## 7. Breaking and Continuing

Inside a `kuri` loop, `gukoma` (*break*) stops the loop early:

```i
kuri i muri 0 kugeza 100
    niba i == 3
        gukoma
    iherezo
    andika i
iherezo
```

Prints `0 1 2`.

> **Note (1.0.0):** `gukoma` is reliable inside `kuri` loops only. In `wihuse`
> loops it can hang the program — prefer restructuring the loop condition.
> `kugenda` (continue) is also unreliable; avoid it in this version.

## Practice

1. Print all even numbers from 0 to 20.
2. Print a countdown from 10 to 1, then "Blast off!".
3. Print the first 10 square numbers (`i * i`).
4. FizzBuzz: print 1..100, but "Fizz" for multiples of 3, "Buzz" for 5,
   "FizzBuzz" for both. *(See `examples/projects/fizzbuzz.i` for a solution.)*

## Reference

- [Language Guide — Conditionals](../user-guide/language-guide.md#conditionals)
- [Language Guide — Loops](../user-guide/language-guide.md#loops)
- [Language Guide — Known Limitations](../user-guide/language-guide.md#known-limitations)

## Next

[Level 3 — Functions](level-3.md)

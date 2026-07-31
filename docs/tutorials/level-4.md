# Tutorial Level 4 — Working with Data

**Objective:** store collections of values, read user input, and manipulate strings.

## What You'll Learn

- Lists: `[10, 20, 30]`
- Indexing with `[ ]`
- Looping with `buri`
- Reading input with `soma`
- Converting types with `uburengero` / `shobora_umuntu`

## 1. Lists

Create a list with square brackets:

```i
shyira imibare = [1, 2, 3, 4, 5]
```

Get the length with `ubwoko`? No — `ubwoko` reports the *type*:

```i
andika ubwoko([1, 2, 3])   # urutonde (list)
```

## 2. Indexing

Lists are indexed from 0:

```i
shyira imibare = [10, 20, 30]
andika imibare[0]   # 10
andika imibare[1]   # 20
andika imibare[2]   # 30
```

Strings can be indexed too:

```i
shyira izina = "Muraho"
andika izina[0]   # M
```

## 3. Looping over a List

`buri` (*each*) runs the body once per element:

```i
shyira amazi = ["mugezi", "ikiyaga", "inyanja"]
buri mazi muri amazi
    andika mazi
iherezo
```

Build a total by accumulating inside the loop:

```i
shyira imibare = [4, 8, 15, 16, 23, 42]
shyira total = 0
buri n muri imibare
    total = total + n
iherezo
andika total   # 108
```

> **Note (1.0.0):** `buri` works over lists. Iterating over a *string* is not
> supported; index the string with `s[i]` inside a `kuri` loop instead.
> Lists cannot be concatenated with `+` in this version.

## 4. Reading Input

`soma` (*read*) reads one line from the terminal:

```i
andika "Amazina yawe?"
shyira izina = soma()
andika "Muraho, " + izina
```

Run it with `-r` and type your name, or pipe it:

```bash
echo "Jean" | i greet.i -r
```

Output:

```
Amazina yawe?
Muraho, Jean
```

> **Note:** `soma()` always returns a string. Convert it with `uburengero` when
> you need a number.

## 5. Converting Types

| From | To | Function |
|------|----|----------|
| string → int | `uburengero(s)` or `shobora_int(s)` | `andika uburengero("42")` |
| string → float | `shobora_float(s)` | `andika shobora_float("3.5")` |
| number → string | `shobora_umuntu(n)` | `andika "Total: " + shobora_umuntu(42)` |
| any → bool | `shobora_bool(x)` | `andika shobora_bool(1)` |

A classic use is digit summing, which repeatedly divides by 10 and truncates:

```i
shyira n = 12345
shyira total = 0
wihuse n irenze 0
    total = total + (n % 10)
    n = uburengero(n / 10)
iherezo
andika total   # 15
```

See `examples/projects/sum_digits.i` for the full program.

## 6. A Complete Data Program

A mini number game that reads input, converts it, and loops:

```i
shyira umubare = 7
shyira guess = 0
kugeza guess == umubare
    andika "Tekereza umubare:"
    shyira line = soma()
    guess = uburengero(line)
iherezo
andika "Bingo!"
```

Run it by piping the answer:

```bash
echo "7" | i game.i -r
```

Output:

```
Tekereza umubare:
Bingo!
```

The full version with a countdown lives in
`examples/projects/guess_game.i`.

## Practice

1. Print every element of `["a", "b", "c"]` on its own line.
2. Sum a list of numbers and print the average (sum / count).
3. Read a number from the user and print its double.
4. Print the characters of a string in reverse order by indexing it
   backwards. For a fixed-length string like `izina = "Muraho"`, loop
   `kuri i muri 0 kugeza 6` and print `izina[5 - i]`.
5. (Challenge) Build a right triangle by appending `"*"` to a string inside
   nested `kuri` loops — see `examples/projects/triangles.i`.

## Reference

- [Language Guide — Values and Types](../user-guide/language-guide.md#values-and-types)
- [Language Guide — Built-in Functions](../user-guide/language-guide.md#built-in-functions)
- [examples/projects/guess_game.i](../../examples/projects/guess_game.i)

## Next

[Level 5 — Building a Program](level-5.md)

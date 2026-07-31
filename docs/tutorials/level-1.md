# Tutorial Level 1 — Hello, I

**Objective:** run your first I program, print output, and store values in variables.

## What You'll Learn

- Running a program with the `i` toolchain
- Printing with `andika`
- Comments
- Variables (`shyira`) and constants (`shyira_ko`)
- The basic types: `int`, `float`, `string`, `bool`, `null`

## 1. Your First Program

Create a file `hello.i`:

```i
andika "Muraho, Isi!"
```

Run it:

```bash
i hello.i -r
```

Output:

```
Muraho, Isi!
```

`andika` (*write*) prints a value followed by a newline. The `-r` flag tells the
compiler to run the program after compiling it.

## 2. Comments

Comments start with `#` and are ignored by the compiler:

```i
# this is a comment
andika "only this prints"
```

## 3. Values

Try printing values of different types:

```i
andika 42          # integer
andika 3.14        # float
andika "text"      # string
andika true        # boolean
andika null        # null
```

## 4. Variables

`shyira` (*place*) creates a **mutable** variable — you can change it later:

```i
shyira izina = "Jean"
andika izina

izina = "Aline"
andika izina
```

`shyira_ko` (*place firmly*) creates a **constant** that cannot change:

```i
shyira_ko IGIHUGU = "Rwanda"
andika IGIHUGU
```

Constants are usually written in UPPERCASE.

## 5. String Concatenation

Strings join with `+`:

```i
shyira izina = "Jean"
andika "Muraho, " + izina
```

Output: `Muraho, Jean`

## 6. Combining Numbers

Arithmetic works as expected:

```i
shyira a = 10
shyira b = 3
andika a + b    # 13
andika a - b    # 7
andika a * b    # 30
andika a / b    # 3.333...
andika a % b    # 1
```

`/` is floating-point division; `%` is the remainder.

## Practice

1. Print your name using a variable.
2. Create constants for your country and year, then print both.
3. Compute the area of a rectangle (`length * width`) and print it.

## Reference

- [Language Guide — Values and Types](../user-guide/language-guide.md#values-and-types)
- [Language Guide — Variables](../user-guide/language-guide.md#variables)
- [Getting Started](../user-guide/getting-started.md)

## Next

[Level 2 — Control Flow](level-2.md)

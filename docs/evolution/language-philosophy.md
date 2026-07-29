# Language Philosophy

This document defines the official philosophy of the I Programming Language — its purpose, principles, and the convictions that will guide its evolution for decades.

## Table of Contents

- [Mission Statement](#mission-statement)
- [What Problems I Solves](#what-problems-i-solves)
- [What Problems I Deliberately Refuses to Solve](#what-problems-i-deliberately-refuses-to-solve)
- [Features That Should Never Exist](#features-that-should-never-exist)
- [Principles for Accepting or Rejecting Features](#principles-for-accepting-or-rejecting-features)
- [Design Values](#design-values)
- [The Cultural Mandate](#the-cultural-mandate)

---

## Mission Statement

**I is a programming language that proves technical excellence and cultural identity are not opposites.**

I exists to demonstrate that a programming language can be:

1. **Technically excellent** without being culturally exclusive
2. **Culturally rooted** without being technically limited
3. **Accessible to beginners** without being shallow for experts
4. **Powerful for systems** without being dangerous for applications

The Kinyarwanda keywords are not a limitation. They are a declaration: that the language of 12 million people is fully capable of expressing the most sophisticated ideas in computer science.

---

## What Problems I Solves

### 1. The Exclusion Problem

**Every mainstream programming language forces non-English speakers to learn English terminology as a prerequisite to programming.**

This creates:
- Unnecessary cognitive load for non-native English speakers
- Cultural erasure in technology
- Barriers to entry for billions of potential developers
- Homogeneous thinking in software design

**I solves this** by providing native Kinyarwanda keywords while maintaining English aliases for international interoperability.

### 2. The Accessibility vs. Power Problem

**Most languages force a choice between beginner-friendliness and professional capability.**

Python is easy but slow. Rust is powerful but complex. JavaScript is accessible but inconsistent. Go is simple but limited.

**I solves this** with a progressive type system: start simple, add complexity only when needed, and never force simplicity where power is required.

### 3. The Ecosystem Fragmentation Problem

**Developers waste enormous time choosing, configuring, and integrating tools.**

Every project requires assembling: language + framework + package manager + formatter + debugger + testing + deployment. Each combination works differently.

**I solves this** by providing seven official frameworks and a complete toolchain that works together seamlessly.

### 4. The Legacy Trap Problem

**Languages accumulate decades of baggage that prevents modernization.**

JavaScript cannot remove `var`. Python cannot remove the GIL easily. C cannot add memory safety. Each language becomes a museum of its past decisions.

**I solves this** by designing evolution mechanisms from day one: clear deprecation policies, edition systems, and forward-compatible migration paths.

### 5. The African Technology Gap Problem

**Africa's 1.4 billion people are underserved by the technology industry.**

Most software is built in Silicon Valley, for Silicon Valley, by Silicon Valley. African developers must adapt to tools designed for different contexts.

**I solves this** by being a language born in Africa, designed with African values, but built to global standards.

---

## What Problems I Deliberately Refuses to Solve

### 1. I Refuses to Solve "Everything"

**I is not a universal language.**

Some languages try to do everything: web, mobile, desktop, systems, AI, games. I focuses on doing many things well, not everything perfectly.

**What this means:**
- I will not be the best choice for every domain
- I will not include every possible feature
- I will not compete with specialized languages on their home turf
- I will recommend other tools when they are better choices

### 2. I Refuses to Solve "Low-Level Hardware"

**I is not a systems programming language in the Rust/C sense.**

I will support systems programming through the `sisitemu` framework, but I will not sacrifice safety for hardware access.

**What this means:**
- I will not provide raw pointer arithmetic by default
- I will not allow arbitrary memory manipulation
- I will not optimize for minimal runtime overhead
- I will not compete with C for kernel development

When absolute hardware control is needed, I will interface with C through FFI.

### 3. I Refuses to Solve "Legacy Compatibility"

**I will not be burdened by backward compatibility with other languages.**

I will not provide JavaScript syntax. I will not include C-style for loops. I will not adopt Java's naming conventions.

**What this means:**
- I will learn from other languages but not copy them
- I will not create "bridges" to other languages' paradigms
- I will not妥协 on syntax to attract users of other languages
- I will maintain my identity even when it's inconvenient

### 4. I Refuses to Solve "Instant Gratification"

**I will not sacrifice long-term health for short-term popularity.**

I will not add features just because they are trendy. I will not remove features just because they are unpopular. I will not rush releases to match competitors.

**What this means:**
- I will ship when features are ready, not when deadlines demand
- I will remove features that don't serve the language, even if popular
- I will invest in quality over quantity
- I will say "not yet" more often than "yes"

### 5. I Refuses to Solve "Corporate Control"

**I will not be owned by any single company.**

I will accept corporate contributions but will not become a corporate tool. I will welcome sponsors but will not be sponsored into compliance.

**What this means:**
- I will be governed by the community, not shareholders
- I will make decisions based on technical merit, not market share
- I will remain open source forever
- I will not add features that benefit one company at the expense of all others

---

## Features That Should Never Exist

### 1. `eval()` for Arbitrary Code Execution

**Why:** `eval()` is a security vulnerability, a performance killer, and a debugging nightmare. It breaks static analysis, enables injection attacks, and makes code unpredictable.

**Alternative:** Provide compile-time metaprogramming, macros, and code generation.

### 2. Implicit Type Coercion (JavaScript-style)

**Why:** `[] + {}` should never equal `"[object Object]"`. Implicit coercion creates bugs that are invisible until runtime, makes type systems unreliable, and teaches developers to distrust their tools.

**Alternative:** Require explicit type conversions. The compiler should always tell you when a conversion happens.

### 3. Multiple Inheritance of State

**Why:** The diamond problem is unsolvable in a way that satisfies everyone. Multiple inheritance of state creates ambiguous method resolution, memory layout confusion, and initialization order issues.

**Alternative:** Provide traits/interfaces for behavioral composition and single inheritance for state.

### 4. Null Reference Exceptions

**Why:** "The billion-dollar mistake" should not be repeated. Null references cause crashes, security vulnerabilities, and undefined behavior.

**Alternative:** Use optional types (`T?`) with explicit unwrapping. No value can be null without the type system knowing about it.

### 5. Macro System That Can Change Syntax

**Why:** Macros that alter syntax make code unreadable, break tooling, and create dialects within a language. Lisp's macros are powerful but create code that only the author can understand.

**Alternative:** Provide AST-transforming macros that operate on structured code, not text. Maintain syntactic consistency.

### 6. Global Mutable State by Default

**Why:** Global mutable state makes concurrent programming impossible, testing difficult, and reasoning about code unreliable.

**Alternative:** Require explicit declaration of shared state. Default to immutable values.

### 7. Operator Overloading That Changes Meaning

**Why:** If `+` can mean "addition," "concatenation," "composition," or "custom operation," then `a + b` is meaningless without knowing the types. This defeats the purpose of readable syntax.

**Alternative:** Allow operator overloading only when the semantics are mathematically consistent. `+` always means some form of addition.

### 8. Runtime Reflection That Breaks Encapsulation

**Why:** Runtime reflection allows code to inspect and modify private members, breaking encapsulation and making optimization impossible.

**Alternative:** Provide compile-time reflection and structured code generation.

### 9. `goto` Statement

**Why:** Unrestricted goto makes code unreadable, untestable, and unmaintainable. Structured programming proved that clear control flow is essential for software engineering.

**Alternative:** Provide labeled breaks, continues, and explicit control flow constructs.

### 10. Header Files

**Why:** Header files duplicate declarations, create compilation order dependencies, and pollute namespaces. C++ has spent decades trying to overcome this limitation.

**Alternative:** Use module systems with explicit exports.

---

## Principles for Accepting or Rejecting Features

### The Seven Tests

Every proposed feature must pass all seven tests:

**Test 1: Necessity**
> "Does this solve a real problem that cannot be solved with existing features?"

If a feature can be implemented as a library, it should not be in the language. If existing features can combine to solve the problem, the feature is probably unnecessary.

**Test 2: Consistency**
> "Does this feature fit naturally with existing features?"

A feature that requires special rules, exceptions, or corner cases probably doesn't fit. The language should feel like a unified whole, not a collection of independent features.

**Test 3: Clarity**
> "Does this feature make code easier or harder to read?"

If a feature enables clever code that only the author can understand, it fails this test. Code is read more often than it is written. Optimize for readability.

**Test 4: Safety**
> "Does this feature introduce new categories of bugs or security vulnerabilities?"

Every feature should be safe by default. If a feature requires the programmer to think about memory management, concurrency, or security, it should provide clear mechanisms for doing so.

**Test 5: Performance**
> "Can this feature be implemented without sacrificing runtime performance?"

If a feature requires runtime overhead that cannot be optimized away, it fails this test. The language should not pay for features it doesn't use.

**Test 6: Toolability**
> "Can IDEs, debuggers, and other tools support this feature?"

If a feature breaks static analysis, makes debugging harder, or confuses code completion, it fails this test. Tools are essential for productivity.

**Test 7: Reversibility**
> "Can this feature be deprecated and removed without breaking the world?"

If a feature cannot be removed once added, think very carefully about adding it. The language should be able to evolve without being burdened by past decisions.

### Acceptance Criteria

A feature is accepted if:
- It passes all seven tests
- It has a clear implementation plan
- It has community support (RFC process)
- It has reference implementations
- It has comprehensive tests
- It has documentation

### Rejection Criteria

A feature is rejected if:
- It fails any of the seven tests
- It duplicates existing functionality
- It cannot be implemented without unacceptable overhead
- It would break backward compatibility
- It lacks community support
- It serves a niche use case that libraries can handle

---

## Design Values

### 1. Safety Over Speed

**"I will not let you shoot yourself in the foot."**

When safety and performance conflict, safety wins by default. Performance optimization should be opt-in, not opt-out.

```
# Safe by default
shyira x: int = 5
x = "hello"  # Compiler error: type mismatch

# Unsafe when needed (explicit)
unsafe:
    # Low-level operations here
iherezo
```

### 2. Clarity Over Cleverness

**"Write code for humans, not machines."**

If a feature enables clever one-liners that only the author can understand, it fails this test. Code is communication. Optimize for clarity.

```
# Clear
shyiramo urubuga

umurimo factorial(n: int) -> int:
    niba n <= 1:
        subira 1
    subira n * factorial(n - 1)
iherezo

# Clever (but wrong for I)
shyiramo urubuga

# This should NOT be possible in I
umurimo f(n) -> int: niba n <= 1 ? 1 : n * f(n - 1)
```

### 3. Composition Over Inheritance

**"Build complex behavior from simple parts."**

Prefer composition, traits, and functional composition over deep inheritance hierarchies. Flat is better than nested. Simple is better than complex.

```
# Composition
igiceri Car
    engine: Engine
    wheels: List<Wheel>
    transmission: Transmission
iherezo

# Inheritance (less preferred)
igiceri Vehicle
    # ...
iherezo

igiceri Car(Vehicle)
    # ...
iherezo
```

### 4. Explicit Over Implicit

**"Make it obvious what's happening."**

If something surprising happens, the language has failed. Hidden behavior, implicit conversions, and magic make code unpredictable.

```
# Explicit
shyira x: int = 5
shyira y: float = 5.0
shyira z: float = x as float  # Explicit conversion

# Implicit (not allowed)
shyira z: float = x  # Compiler error
```

### 5. Progressive Disclosure

**"Start simple, add complexity only when needed."**

A beginner should be able to write "Hello World" without understanding the entire language. An expert should be able to use advanced features without being forced to.

```
# Beginner: Simple
print("Muraho, Dunia!")

# Intermediate: Functions
umurimo greet(name: string) -> string:
    subira "Muraho, " + name + "!"
iherezo

# Expert: Generics, traits, async
umurimo fetch_data<T>(url: string) -> async Result<T, Error>:
    shyira response = await http.get(url)
    subira json.decode<T>(response.body)
iherezo
```

### 6. Cultural Identity

**"I is proudly Rwandan."**

Kinyarwanda keywords are not a gimmick. They are the soul of the language. Every design decision should consider how it respects and promotes Rwandan culture.

```
# Cultural identity
shyiramo urubuga

niba condition:
    # do something
cyangwa:
    # do something else
iherezo

# English aliases exist for interoperability
if condition:
    # do something
else:
    # do something else
end
```

### 7. Evolutionary Stability

**"The language should evolve without breaking the world."**

New versions should add capabilities, not remove them. When features must be removed, provide clear migration paths and long deprecation periods.

```
# v1.0: Feature introduced
shyira x: int = 5

# v1.1: Feature deprecated
shyira x: int = 5  # Deprecated: use 'let' instead

# v2.0: Feature removed (after 2 major versions)
# shyira x: int = 5  # Syntax error: 'shyira' removed
shyira x: int = 5
```

### 8. Community Governance

**"The language belongs to its users."**

No single person, company, or organization should control the language. Decisions should be made transparently, through established processes, with community input.

### 9. Practical Optimization

**"Make the common case fast."**

Optimize for the 90% case. Don't create complexity to handle the 10% case. If the 10% case needs optimization, provide escape hatches.

### 10. Global Accessibility

**"The language should be accessible to everyone."**

This means:
- Kinyarwanda keywords for cultural identity
- English aliases for international interoperability
- Bilingual error messages
- Multiple input methods
- Screen reader support
- Keyboard accessibility

---

## The Cultural Mandate

### Why Kinyarwanda?

Kinyarwanda is not just a language. It is:
- The language of 12+ million people
- One of the official languages of Rwanda, Uganda, and DR Congo
- A language with rich oral tradition and precise expression
- A language that survived and evolved through extraordinary circumstances

Programming in Kinyarwanda is:
- An act of cultural preservation
- A statement of technological capability
- A bridge between tradition and innovation
- A gift to future generations

### The Promise

I promises to:

1. **Never compromise Kinyarwanda for international adoption.** English aliases exist for interoperability, not as replacements.

2. **Always provide bilingual support.** Error messages, documentation, and community content will always be available in both languages.

3. **Respect the language's evolution.** As Kinyarwanda evolves, so will I's keyword set. New Kinyarwanda words can become I keywords through the RFC process.

4. **Honor Rwanda's heritage.** The language's design reflects Rwandan values: community, excellence, honesty, and forward-thinking.

### The Invitation

I invites:
- Rwandan developers to program in their mother tongue
- African developers to build technology that reflects their identity
- Global developers to experience a new perspective on programming
- Everyone to learn that technical excellence and cultural identity are not opposites

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)

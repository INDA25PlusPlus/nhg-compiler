# Dungeon Language (WIP)
Inspired by languages like [Chef](https://www.dangermouse.net/esoteric/chef.html) and [Shakespeare](https://en.wikipedia.org/wiki/Shakespeare_Programming_Language), where programs look like literature, with the theme of 80s text-based adventure games like [Zork](https://en.wikipedia.org/wiki/Zork).

Source is mostly flowing text (narration) plus explicit control lines starting with `>`.

## Fibonacci Example
```
The adventure begins.

You seek wisdom from beyond and call it the final_quest.
The first_light transforms into nothing.
The second_light transforms into all.
The journey transforms into nothing.

> enter cavern while the journey stands before the final_quest
The reflection transforms into the first_light and the second_light.
The first light transforms into the second_light.
The second light transforms into the reflection.
The journey transforms into the journey and the universe.
> leave cavern

You speak of the second_light.

The adventure ends.
```

## Control Flow
| Syntax                              | Meaning          | Python Equivalent    |
| ----------------------------------- | ---------------- | -------------------- |
| `> enter <place> while <condition>` | Begin while-loop | `while <condition>:` |
| `> leave <place>`                   | End block   | (dedent / end block) |
| `> inspect whether <condition>`     | If-statement     | `if <condition>:`    |
| `> say <phrase>`                    | Print            | `print(<phrase>)`    |
| `> ask <thing>`                     | Input            | `<thing> = input()`  |


## Computation Phrasing
| Narrative pattern                                     | Meaning                | Python Equivalent                    |
| ----------------------------------------------------- | ---------------------- | ------------------------------------ |
| `You reflect on all you have learned: <exprlist>`     | Sum or combine values  | `sum([<exprlist>])` or `a + b + ...` |
| `The <x> transforms into <y>.`                        | Assignment             | `<x> = <y>`                          |
| `You speak of <expr>.`                                | Print statement        | `print(<expr>)`                      |
| `You seek wisdom from beyond and call it <x>.`        | Input into variable    | `<x> = input()`                      |
| `You ponder whether <expr> still holds.`              | Boolean test           | `if <expr>:`   |
| `The story continues as long as <expr> remains true.` | Loop condition variant | `while <expr>:`                      |


## Expression 
### Syntax
*the*, *a*, and *an* are optional “article” tokens before any variable or noun phrase. All of these are equivalent:
```
The count stands before the limit.
A count stands before limit.
count stands before the limit.
```

### Special Cases
Special cases:
- `nothing` is a literal 0.
- `all`, `universe` and `everything` are synonyms for 1.

### Expression Lists
`<exprlist>` allows chaining with and or commas.

**Examples:**

- `You reflect on all you have learned: the first and the second`.
→ sum(first, second)
- `You reflect on all you have learned: the first, the second, and the third`.
→ sum(first, second, third)

### Artihmetic Expressions
| Operation | Natural phrasing                                      | Example                                                               | Meaning |
| --------- | ----------------------------------------------------- | --------------------------------------------------------------------- | ------- |
| `+`       | `You reflect on all you have learned: <a> and <b>`    | “You reflect on all you have learned: the first and the second.”      | `a + b` |
| `-`       | `You recall the distance between <a> and <b>`         | “You recall the distance between the reflection and the first.”       | `a - b` |
| `*`       | `You envision <a> by <b>`                    | “You envision the first by the count.”                       | `a * b` |
| `/`       | `You divide <a> among <b>`                            | “You divide the treasure among the companions.”                       | `a / b` |
| `%`       | `You keep what remains of <a> after sharing with <b>` | “You keep what remains of the number after sharing with the divisor.” | `a % b` |

### Comparison and Conditions
| Comparison | Literary phrasing                | Example                                     | Meaning      |
| ---------- | -------------------------------- | ------------------------------------------- | ------------ |
| `==`       | `<a> is much like <b>`           | “The reflection is much like the target.”   | equality     |
| `!=`       | `<a> differs from <b>`           | “The first differs from the second.”        | not equal    |
| `<`        | `<a> stands before <b>`          | “The count stands before the limit.”        | less than    |
| `>`        | `<a> towers above <b>`           | “The number towers above the threshold.”    | greater than |
| `<=`       | `<a> stands no further than <b>` | “The age stands no further than the bound.” | ≤            |
| `>=`       | `<a> stands not below <b>`       | “The height stands not below the limit.”    | ≥            |

### Logical connectives
| Operator | Phrase       | Example                                                                |
| -------- | ------------ | ---------------------------------------------------------------------- |
| `and`    | “as well as” | “The count stands before the limit as well as the lamp still burning.” |
| `or`     | “or perhaps” | “The quest is unfinished or perhaps the hero has fallen.”              |
| `not`    | “is not”     | “The gate is not open.”                                                |

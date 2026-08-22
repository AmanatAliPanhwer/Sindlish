# Language Reference

Complete reference for Sindlish keywords, built-in functions, and collection methods. This serves as both a developer reference and a quick-lookup guide.

## Sindlish to Python Keyword Mapping

Sindlish is inspired by Python. Every Python keyword and builtin has a Sindhi equivalent.

### Control Flow

| Sindlish | Python | Description |
|----------|--------|-------------|
| `agar` | `if` | Conditional |
| `yawari` | `elif` | Else-if |
| `warna` | `else` | Else |
| `jistain` | `while` | While loop |
| `har` | `for` | For loop |
| `mein` | `in` | Membership/inclusion |
| `tor` | `break` | Break loop |
| `jari` | `continue` | Continue loop |
| `wapas` | `return` | Return from function |

### Data Types

| Sindlish | Python | Description |
|----------|--------|-------------|
| `adad` | `int` | Integer type |
| `dahai` | `float` | Float type |
| `lafz` | `str` | String type |
| `faislo` | `bool` | Boolean type |
| `sach` | `True` | True literal |
| `koorh` | `False` | False literal |
| `khali` | `None` | Null literal |
| `fehrist` | `list` | List type |
| `lughat` | `dict` | Dict type |
| `majmuo` | `set` | Set type |
| `pakko` | `final`/`const` | Constant modifier |

### Functions and Scope

| Sindlish | Python | Description |
|----------|--------|-------------|
| `kaam` | `def` | Function definition |
| `aalmi` | `global` | Global declaration |
| `bahari` | `nonlocal` | Nonlocal declaration |

### Logical Operators

| Sindlish | Python | Description |
|----------|--------|-------------|
| `aen` | `and` | Logical AND |
| `ya` | `or` | Logical OR |
| `nah` / `!` | `not` | Logical NOT |

### Output

| Sindlish | Python | Description |
|----------|--------|-------------|
| `likh` | `print` | Print to stdout |
| `puch` | `input` | Read from stdin |

### Error Handling (Result System)

| Sindlish | Equivalent | Description |
|----------|------------|-------------|
| `ok(value)` | `Result::Ok(value)` | Create success result |
| `ghalti(msg)` | `Result::Err(msg)` | Create error result |
| `result?` | `?` operator | Soft unwrap (keep error) |
| `result!!` | `unwrap()` | Panic unwrap |
| `result.bachao(fb)` | `.unwrap_or(fb)` | Unwrap with fallback |
| `result.lazmi(msg)` | `.expect(msg)` | Unwrap or panic with message |
| `kharabi(msg)` | `panic!(msg)` | Immediate panic |

## Built-in Functions

### `likh(*args)`

Prints all arguments space-separated to stdout.

```
likh("hello")           # prints: hello
likh(1, 2, 3)           # prints: 1 2 3
likh("x =", 42)         # prints: x = 42
likh()                   # prints: (empty line)
```

### `puch(*prompt)`

Reads a line of input from stdin with optional prompt.

```
lafz name = puch("Name: ")     # Displays "Name: ", reads input
lafz val = puch()               # Reads input without prompt
```

### `lambi(obj)`

Returns the length of a collection or string.

```
lambi("hello")          # 5
lambi([1, 2, 3])        # 3
lambi({"a": 1, "b": 2}) # 2
lambi({1, 2, 3})        # 3
```

### `range(n)`, `range(a, b)`, `range(a, b, s)`

Creates a list of integers.

```
range(5)                # [0, 1, 2, 3, 4]
range(2, 7)             # [2, 3, 4, 5, 6]
range(0, 10, 2)         # [0, 2, 4, 6, 8]
range(10, 0, -2)        # [10, 8, 6, 4, 2]
```

### `majmuo(*args)`

Creates a new set.

```
majmuo()                # {} (empty set)
majmuo([1, 2, 3])       # {1, 2, 3}
majmuo(1, 2, 3)         # Error: expected 0 or 1 args
```

## Operators

### Arithmetic

| Operator | Sindlish | Example | Description |
|----------|----------|---------|-------------|
| `+` | `jor` | `3 + 5` | Addition / concatenation |
| `-` |减 | `10 - 3` | Subtraction |
| `*` | gun | `4 * 5` | Multiplication / repetition |
| `/` | tageem | `10 / 3` | Division (returns Result) |
| `%` | baki | `10 % 3` | Modulo (returns Result) |
| `^` | tawar | `2 ^ 10` | Exponentiation |

### Comparison

| Operator | Example | Description |
|----------|---------|-------------|
| `==` | `x == 5` | Equality |
| `!=` | `x != 5` | Inequality |
| `>` | `x > 5` | Greater than |
| `<` | `x < 5` | Less than |
| `>=` | `x >= 5` | Greater or equal |
| `<=` | `x <= 5` | Less or equal |

### Logical

| Sindlish | Python | Example | Description |
|----------|--------|---------|-------------|
| `aen` | `and` | `x aen y` | Logical AND |
| `ya` | `or` | `x ya y` | Logical OR |
| `nah` | `not` | `nah x` | Logical NOT |
| `!` | `not` | `!x` | Logical NOT (symbol) |

## Syntax Examples

### Variable Declaration

```
# Dynamic typing
adad x = 10
lafz name = "hello"
dahai pi = 3.14
faislo flag = sach

# Typed
adad y = 5
lafz s = "hi"
fehrist[adad] nums = [1, 2, 3]
lughat[lafz, adad] ages = {}

# Postfix type annotation
x: adad = 10

# Constant
pakko PI = 3.14
```

### Control Flow

```
# If/else
agar x > 5 {
    likh("big")
} yawari x == 5 {
    likh("equal")
} warna {
    likh("small")
}

# While
jistain x > 0 {
    likh(x)
    x = x - 1
}

# For
har i mein range(5) {
    likh(i)
}

# For with list
har name mein ["alice", "bob", "charlie"] {
    likh(name)
}
```

### Functions

```
kaam joda(a, b) -> adad {
    wapas a + b
}

kaam greet(lafz name) {
    likh("Hello, " + name)
}

# Default arguments
kaam power(adad base, adad exp = 2) -> adad {
    wapas base ^ exp
}

# Variadic arguments
kaam sum(adad* nums) -> adad {
    adad total = 0
    har n mein nums {
        total = total + n
    }
    wapas total
}
```

### Collections

```
# List
fehrist adad nums = [1, 2, 3, 4, 5]
likh(nums[0])           # 1
likh(nums[-1])          # 5
nums.wadha(6)           # [1, 2, 3, 4, 5, 6]
nums.tarteeb()          # [1, 2, 3, 4, 5, 6]

# Dict
lughat lifo ages = {"alice": 25, "bob": 30}
likh(ages["alice"])     # 25
ages["charlie"] = 35
likh(ages.cabeyon())    # ["alice", "bob", "charlie"]

# Set
majmuo adad nums = {1, 2, 3, 4, 5}
nums.addkar(6)
likh(lambi(nums))       # 6
```

### Error Handling

```
# Creating results
kaam divide(adad a, adad b) {
    agar b == 0 {
        wapas ghalti("Zero division")
    }
    wapas ok(a / b)
}

# Using results
adad result = divide(10, 2)?
likh(result)            # 5

# With fallback
adad result = divide(10, 0).bachao(0)
likh(result)            # 0

# Panic unwrap
adad result = divide(10, 2)!!
likh(result)            # 5

# Re-raise with message
adad result = divide(10, 0).lazmi("Division failed")
```

## Complete Collection Method Reference

### List Methods (11)

| Method | Sindlish | Description |
|--------|----------|-------------|
| `wadha(item)` | append | Add item to end |
| `wadhayo(list)` | extend | Extend with another list |
| `wajh(idx, item)` | insert | Insert at index |
| `hata(item)` | remove | Remove first occurrence |
| `kadh()` or `kadh(idx)` | pop | Remove and return at index |
| `saf()` | clear | Remove all elements |
| `index(item)` | index | Find index of item |
| `garn(item)` | count | Count occurrences |
| `tarteeb()` | sort | Sort in place |
| `ulto()` | reverse | Reverse in place |
| `nakal()` | copy | Shallow copy |

### Dict Methods (10)

| Method | Sindlish | Description |
|--------|----------|-------------|
| `hasil(key, default)` | get | Get value with default |
| `syon()` | items | List of [key, value] pairs |
| `cabeyon()` | keys | List of keys |
| `raqamon()` | values | List of values |
| `syonkadh()` | popitem | Remove and return last pair |
| `defaultrakh(key, default)` | setdefault | Set default if missing |
| `update(dict)` | update | Merge another dict |
| `kadh(key)` or `kadh(key, default)` | pop | Remove and return |
| `saf()` | clear | Remove all pairs |
| `nakal()` | copy | Shallow copy |

### Set Methods (14)

| Method | Sindlish | Description |
|--------|----------|-------------|
| `addkar(item)` | add | Add element |
| `chad(item)` | discard | Remove if present |
| `hata(item)` | remove | Remove (error if missing) |
| `kadh()` | pop | Remove arbitrary element |
| `saf()` | clear | Remove all elements |
| `nakal()` | copy | Shallow copy |
| `update(set)` | update | Add elements from another set |
| `bade(set)` | union | New set (union) |
| `milap(set)` | intersection | New set (intersection) |
| `farq(set)` | difference | New set (difference) |
| `symmetric_farq(set)` | sym. difference | New set (symmetric difference) |
| `nandohisoahe(set)` | issubset | Check subset |
| `wadohisoahe(set)` | issuperset | Check superset |
| `alaghahe(set)` | isdisjoint | Check disjoint |

## Error Types Reference

| Sindlish Name | Python Equivalent | Description |
|---------------|-------------------|-------------|
| `LikhaiJeGhalti` | `SyntaxError` | Lexer/parser syntax error |
| `NaleJeGhalti` | `NameError` | Undefined variable |
| `QisamJeGhalti` | `TypeError` | Type mismatch |
| `HalndeVaktGhalti` | `RuntimeError` | General runtime error |
| `ZeroVindJeGhalti` | `ZeroDivisionError` | Division by zero |
| `IndexJeGhalti` | `IndexError` | Index out of bounds |

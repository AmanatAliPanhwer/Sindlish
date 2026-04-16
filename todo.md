# 🚀 SINDLISH — MASTER DEVELOPMENT TODO LIST

## (Full Programming Language Roadmap)

---

# 🧠 1. CORE LANGUAGE FOUNDATION

## 🟢 Lexer (DONE ✔ → but extend it)

* [x] Token system
* [x] Keyword mapping (Sindlish → Python)
* [x] Number, string, identifier support
* [ ] Add float support (`12.5`)
* [ ] Add boolean literal recognition (`True/False → sach/koorh`)
* [ ] Add null (`khali`)
* [ ] Add comment support (`# ...`)
* [ ] Improve error reporting (line + column highlight)

---

## 🟢 Parser (PARTIALLY DONE ✔)

* [x] Program parsing
* [x] If / Else
* [x] Print statement
* [x] Binary expressions (>, <)

### 🔧 MUST ADD:

* [ ] Operator precedence system

  * `* /` before `+ -`
* [ ] Parentheses grouping `( )`
* [ ] Multi-line expression parsing
* [ ] Block parsing using INDENT / DEDENT (Python-style)
* [ ] Expression chaining:

  * `x + y - z`

---

# 🌱 2. VARIABLES & DATA TYPES SYSTEM

## 🔵 Variables (DONE ✔ → improve it)

* [x] Assignment (`x = 10`)

### 🔧 ADD:

* [ ] Type system (soft typing)

  * int
  * float
  * string
  * bool
* [ ] Type checking (optional strict mode)
* [ ] Variable re-declaration rules
* [ ] Constants (`const x = 10` optional future)

---

## 🔵 Data Types (NEW CORE FEATURE)

* [ ] int → `adad`
* [ ] float → `ashari`
* [ ] string → `lafz`
* [ ] bool → `sach / koorh`
* [ ] null → `khali`

---

# ⚙️ 3. OPERATORS SYSTEM

## ➕ Arithmetic

* [ ] +
* [ ] -
* [ ] *
* [ ] /
* [ ] %
* [ ] power (** optional)

## ⚖️ Comparison

* [x] >
* [x] <

### ADD:

* [ ] ==
* [ ] !=
* [ ] >=
* [ ] <=

## 🔗 Logical

* [ ] and → `aen`
* [ ] or → `ya`
* [ ] not → `nah`

---

# 🔁 4. CONTROL FLOW (LOGIC SYSTEM)

## 🟣 If / Else (DONE ✔)

* [x] agar (if)
* [x] warna (else)

### ADD:

* [ ] elif → `yawari`
* [ ] nested if support (full stability)
* [ ] multi-branch condition parsing

---

## 🔁 Loops (HIGH PRIORITY 🔥)

* [ ] while → `jistain`
* [ ] for → `har`
* [ ] break → `tor`
* [ ] continue → `halando`

---

# 🧩 5. FUNCTIONS SYSTEM (BIG MILESTONE 🚀)

## 🔵 Function Definition

* [ ] `kaam` (def)
* [ ] parameters
* [ ] default arguments
* [ ] return values (`wapas`)

### Example:

```sindlish
kaam add(a, b):
    wapas a + b
```

---

## 🔵 Function Execution

* [ ] call parser
* [ ] argument binding
* [ ] local scope creation
* [ ] stack-based execution (optional advanced)

---

# 🏗️ 6. OBJECT ORIENTED PROGRAMMING (OOP)

## 🟡 Class System

* [ ] `jamaat` (class)
* [ ] constructor (`__init__`)
* [ ] self handling
* [ ] attributes

### Example:

```sindlish
jamaat Insan:
    kaam __init__(self, name):
        self.name = name
```

---

## 🟡 OOP Features

* [ ] Objects
* [ ] Methods
* [ ] Inheritance
* [ ] Polymorphism (advanced)
* [ ] Encapsulation rules

---

# 📦 7. STANDARD LIBRARY (BUILT-IN FUNCTIONS)

## 🔵 Print Function (IMPORTANT)

* [x] `likh()` exists

### 🔧 MUST ADD PARAMETERS:

* [ ] `end=""`
* [ ] `sep=" "`
* [ ] `file=None`

---

## 🔵 Input System

* [ ] `puch()`
* [ ] type casting

---

## 🔵 Utility Functions

* [ ] len
* [ ] range
* [ ] int/float/str casting
* [ ] type checking (`qisam`)

---

# ⚠️ 8. ERROR HANDLING SYSTEM (VERY IMPORTANT)

## 🔴 Must implement:

* [ ] SyntaxError → `LikhaiGhalti`
* [ ] NameError → `NaloGhalti`
* [ ] TypeError → `QisamGhalti`
* [ ] RuntimeError → `HalandeGhalti`

### Add:

* [ ] Line number tracking
* [ ] Code snippet preview
* [ ] Arrow pointer to error location

---

# 🌳 9. INDENTATION SYSTEM (PRO LEVEL 🔥)

* [ ] INDENT detection
* [ ] DEDENT detection
* [ ] Block stacking system
* [ ] Nested block support

👉 This makes Sindlish feel like Python

---

# ⚡ 10. EXECUTION ENGINE UPGRADES

* [ ] Visitor pattern fully modular
* [ ] Memory-safe variable storage
* [ ] Scope system (global/local)
* [ ] Function call stack
* [ ] Return handling

---

# 🧪 11. DEBUGGING TOOLS

* [ ] AST visualizer
* [ ] Token printer
* [ ] Execution trace mode
* [ ] Step-by-step execution

---

# 🌍 12. ADVANCED FEATURES (FUTURE LEVEL 🔥🔥)

## 🚀 Compiler Expansion

* [ ] Sindlish → Python transpiler mode
* [ ] Bytecode compiler (optional)
* [ ] Virtual Machine (advanced stage)

## 💻 Developer Tools

* [ ] CLI tool:

  * `sind run file.sind`
  * `sind debug file.sind`
* [ ] VS Code extension
* [ ] Syntax highlighting

---

# 🧠 13. QUALITY & CLEANUP

* [ ] Remove regex-based hacks
* [ ] Full AST-based execution only
* [ ] Remove unsafe `exec`
* [ ] Modular architecture cleanup
* [ ] Full unit tests

---

# 🏁 FINAL GOAL

At completion, Sindlish will support:

✔ Variables
✔ Conditions
✔ Loops
✔ Functions
✔ OOP
✔ Error system
✔ Full Python-like execution
✔ Native Sindhi/Urdu keywords

---

# 🚀 YOUR CURRENT POSITION

You are here:

```
Lexer ✔
Parser ✔
Interpreter ✔
If/Else ✔
Variables ✔
```

👉 You are at **40–50% of a real programming language**
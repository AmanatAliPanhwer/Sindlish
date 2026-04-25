# Sindlish — Modern Programming in Sindhi

**Sindlish** is a professional-grade, high-level programming language designed specifically for the Sindhi speaking communities. It combines the power of modern stack-based Virtual Machines with the intuitive syntax of local languages.

## Key Features

### Beautiful Syntax
Write code in your own language! Use keywords like `kaam` (function), `agar` (if), and `jistain` (while) that make sense to you.

### Robust Result System
No more messy exceptions. Sindlish uses a type-safe `Result` system for error handling.
- **`ok(value)`**: Signifies success.
- **`ghalti("msg")`**: Signifies a handled error.
- **`.bachao(fallback)`**: Gracefully handle errors with a default value.
- **`.lazmi("msg")`**: Ensure critical operations succeed or panic with a clear message.

### Professional Tracebacks
When things go wrong, Sindlish tells you exactly where and why. Our new traceback engine provides colorized stack traces and code pointers, modeled after the best modern languages.

### High Performance
Powered by a stack-based Bytecode Virtual Machine, Sindlish is built for efficiency and stability.

## Quick Start

```sindlish
# A simple function to greet
kaam salam(naalo) {
    wapas "Salam, " + naalo + "!"
}

# Arithmetic with type safety
adad x = 10
adad y = 20
likh(salam("Sindh"), "Result is:", x + y)

# Safe division using the Result system
kaam safe_div(a, b) {
    agar b == 0 { wapas ghalti("Zero division!") }
    wapas ok(a / b)
}

res = safe_div(10, 0).bachao(0)
likh("Safe result:", res)
```

## 🛠️ Extension Features
- **Semantic Highlighting**: Every keyword and type is clearly identified.
- **Snippet Power**: Type `kaam` or `agar` and hit tab to generate boilerplate code instantly.
- **LSP Support**: Real-time error checking and method completions (powered by the Sindlish Language Server).

## 🌍 Community & Support
Sindlish is more than just a language; it's a movement to bring coding to everyone. 

- **GitHub**: [Sindlish/sindlish-lang](https://github.com/Sindlish/sindlish-lang)
- **Maintainer**: Amanat Ali Panhwer

---
**Install Sindlish today and start building the future in your own language!**

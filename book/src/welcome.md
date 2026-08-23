# Welcome to the Workshop

<div class="youarehere">📍 <strong>You are here:</strong> Part Zero · Settle In</div>

Hello, and welcome in. Take the good chair — you've earned it.

This book is about **Sindlish**: a small, bytecode-compiled programming language whose keywords come from Sindhi (`likh` prints, `agar` decides, `wapas` returns), and whose interpreter is written in Python. It's a real language with a real lexer, parser, resolver, compiler, and virtual machine — a complete little machine, all told in roughly 3,500 lines of Python you can actually read in an afternoon.

That last part is why this book exists.

Most languages are cathedrals: magnificent, ancient, and impossible to hold in your head. Sindlish is more like a **workshop**. Every tool is on the wall, every drawer has a label, and you're allowed to touch everything. This book is the guided tour of that workshop — written for the people who will *build* the language, not just use it.

## Who this book is for

You, if:

- you want to add a feature to Sindlish and need to know where it lives;
- you've read `interpreter/` code and some part made you go *"…why?"*;
- you love languages and want to see a whole one, end to end, without a PhD in dragon books.

You don't need to know any Sindhi. Every keyword gets translated the first time it appears (and there's a whole [dictionary chapter](glossary.md) to keep handy).

## What you'll be able to do afterwards

By the last page you'll be able to:

1. Trace a line of Sindlish source from raw characters to pixels on screen,
2. Explain **why** the pipeline has five stages (and what breaks if you merge them),
3. Navigate the resolver's slot system, closures, and type checks without fear,
4. Follow the VM executing bytecode **one instruction at a time**, watching the stack,
5. Add a new keyword, operator, or builtin — end to end — with tests.

## The workshop rules 🧰

Three promises we'll keep to you throughout this book:

- **No unexplained jargon.** When C3 linearization shows up, we stop and build it from scratch before using the words.
- **Everything is verifiable.** Every snippet runs against the real interpreter (`python main.py`). Nothing here is hand-waved.
- **Diagrams over paragraphs.** If a data flow can be drawn, we draw it.

## How the interpreter introduces itself

The one-sentence version, which the rest of the book earns:

> Sindlish takes your source text, melts it into tokens, grows those into a tree, teaches that tree where every variable *lives*, compiles the tree into tiny numeric instructions, and then runs those instructions on a stack machine — catching mistakes at every stage so they die young.

Five stages. Five parts of this book. Let's go look at them.

<div class="recap">
<p>Sindlish = Romanized-Sindhi syntax on top of a classic five-stage Python interpreter.</p>
<p>This book tours the whole machine, stage by stage, aimed at contributors.</p>
<p>Next up: how the book itself works, then the 30-second version of the entire pipeline.</p>
</div>

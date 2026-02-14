# MockFactory CLI Examples

This directory contains example scripts demonstrating the MockFactory CLI.

## Running Examples

### Python Examples

```bash
# Simple hello world
mockfactory execute hello.py

# Fibonacci calculator
mockfactory execute fibonacci.py
```

### JavaScript Examples

```bash
# JavaScript hello world
mockfactory execute hello.js
```

## Creating Your Own Scripts

1. Create a script file with the appropriate extension (`.py`, `.js`, `.php`, etc.)
2. Write your code
3. Execute with `mockfactory execute <filename>`

The CLI will automatically detect the language from the file extension!

## Inline Execution

You can also run code inline without creating a file:

```bash
# Python
mockfactory run python -c "print('Hello!')"

# JavaScript
mockfactory run javascript -c "console.log('Hello!')"

# PHP
mockfactory run php -c "echo 'Hello!';"
```

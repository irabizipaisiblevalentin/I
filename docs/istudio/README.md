# I STUDIO — User Guide

## Getting Started

```bash
# Initialize a workspace
isoko istudio workspace init ./my-project

# Create a project
isoko istudio project create my-app --path ./my-project

# Open a file
isoko istudio workspace open ./my-project
```

## Editor

The I STUDIO editor engine supports:
- Multi-tab file editing with undo/redo
- Syntax-aware operations
- Find and replace across files
- File type detection by extension

## Language Intelligence

```bash
# Lint a file
isoko istudio lint main.i

# Format a file
isoko istudio format main.i
```

## Debugging

```bash
isoko istudio debug start
isoko istudio debug break-list
isoko istudio debug step
isoko istudio debug continue
isoko istudio debug stop
```

## AI Assistant

```bash
isoko istudio ai chat "How do I create a class in I?"
isoko istudio ai conversations
```

## Extensions

```bash
isoko istudio extension install --path ./my-plugin/plugin.json
isoko istudio extension list
isoko istudio extension enable my-plugin
isoko istudio extension disable my-plugin
```

## Collaboration

```bash
isoko istudio collaboration session-create my-session
isoko istudio collaboration session-list
isoko istudio collaboration review-create PR-42
isoko istudio collaboration review-list
```

## Language Server Protocol

```bash
isoko istudio server --stdio
```

The LSP server supports stdio transport and handles:
- `initialize` / `shutdown`
- `textDocument/didOpen` / `didChange`
- `textDocument/completion`
- `textDocument/hover`

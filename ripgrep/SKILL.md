---
name: ripgrep
description: High-performance code search, pattern matching, and file exploration using ripgrep (rg). Use when searching large codebases, locating definitions, finding regex patterns, refactoring references, or filtering by file types.
---

# Ripgrep (`rg`) Usage Guide & Recipes

`ripgrep` (`rg`) is a line-oriented search tool that recursively searches the current directory for regex patterns while respecting `.gitignore` rules by default.

---

## ⚡ Core Rules & Defaults

- **Speed & Ignore**: Respects `.gitignore`, `.ignore`, and binary files automatically.
- **Line Numbers**: Always include line numbers (`-n`) for referencing code.
- **Max Columns**: Limit line width with `--max-columns 200` to prevent large minified files or long strings from flooding outputs.
- **Safety**: Quote regex patterns to avoid shell expansion.

---

## 🔍 Common Recipes

### 1. Symbol & Definition Search
```bash
# Python class and function definitions
rg -n "class (MyClass|OtherClass)\b" -t py
rg -n "def (process_item|execute)\b" -t py

# TypeScript/JavaScript exports and interfaces
rg -n "(export (const|function|class)|interface) UserProfile\b" -t ts -t tsx

# Go functions and structs
rg -n "type User struct" -t go
rg -n "func \([^)]+\) Process" -t go
```

### 2. Literal vs. Regex Search
```bash
# Literal string search (-F) - no escaping needed for brackets/dots
rg -nF 'items[0].get("id")'

# Regex search with word boundaries
rg -n '\bAPI_KEY\b'
```

### 3. Context Lines
```bash
# 3 lines before and after match (-C)
rg -n -C 3 "parse_configuration" -t py

# 2 lines before (-B) and 5 lines after (-A)
rg -n -B 2 -A 5 "handle_exception"
```

### 4. File Type & Glob Filtering
```bash
# Only Python files
rg -n "logger\.error" -t py

# Only TypeScript and JavaScript
rg -n "useState" -t ts -t js

# Include specific glob pattern
rg -n "database_url" -g "config/*.yaml"

# Exclude test files and vendor dirs
rg -n "calculate_hash" -g "!*test*" -g "!**/vendor/*"

# List available built-in file types
rg --type-list
```

### 5. Multiline Search (`-U` / `--multiline`)
```bash
# Find decorator followed by function
rg -n -U "@router\.post\([^)]*\)\nasync def \w+" -t py

# Find multi-line function calls or configurations
rg -n -U "new Client\(\{[\s\S]*?timeout: \d+" -t ts
```

### 6. File Discovery & Counting
```bash
# Find all matching files (faster than find)
rg --files -g "*.graphql"

# Count occurrences per file
rg -c "TODO" -t py

# Total count of all matches
rg "TODO" | wc -l
```

### 7. Search Hidden & Un-ignored Files
```bash
# Search hidden files (-.)
rg -n "AWS_SECRET" -.

# Search everything including gitignored files (-u or -uu)
rg -n "SECRET_KEY" -uu
```

---

## 🛠 Integration in Agent Tools

When interacting via CLI or `run_bash_command`:
1. Use `rg -n` for exact file:line references.
2. Limit result count when exploratory with `--max-count <N>` or pipe to `head -n 50`.
3. Keep `--max-columns 200` to prevent token blowout.

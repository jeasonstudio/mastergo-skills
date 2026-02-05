---
name: mastergo
description: Parse MasterGo design files to retrieve DSL data for code generation. Use when users provide MasterGo links (https://mastergo.com/file/xxx or https://mastergo.com/goto/xxx) to analyze design structure, extract component specs, or build multi-page sites.
---

# MasterGo Skills

Parse MasterGo design files and retrieve DSL data for code generation.

## Prerequisites

```bash
export MASTERGO_TOKEN="mg_your_token_here"  # Required
export MASTERGO_API_URL="https://custom.com" # Optional (enterprise)
```

**Requirements**: Team Edition account, files in Team Projects (not Drafts).

## Quick Start

### Single Element/Page

```bash
# Get DSL from any MasterGo link
node scripts/get-dsl.cjs "https://mastergo.com/goto/LhGgBAK"
```

**Output**: `{ dsl, componentDocumentLinks, rules }`

### Process Component Docs

```bash
# Fetch each URL in componentDocumentLinks
node scripts/get-component-link.cjs "https://example.com/ant/button.mdx"
```

### Multi-Page Site

```bash
# Get site metadata
node scripts/get-meta.cjs --fileId=155675508499265 --layerId=158:0001
```

**Output**: `{ result (XML), actions, rules }`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/get-dsl.cjs` | Get DSL from design element |
| `scripts/get-component-link.cjs` | Get component documentation |
| `scripts/get-meta.cjs` | Get site/page metadata |
| `scripts/parse-mastergo-url.cjs` | URL parsing utilities |
| `scripts/extract-component-links.cjs` | DSL data extraction |

## Workflow

1. **Get DSL**: Run `get-dsl.cjs` with MasterGo link
2. **Process components**: Fetch all `componentDocumentLinks`
3. **Follow rules**: Apply `rules` array when generating code
4. **Handle navigation**: Extract `interactive` fields for page relationships

See [references/get-dsl-workflow.md](references/get-dsl-workflow.md) for details.

## Key Constraints

- **Process all `componentDocumentLinks`** before code generation
- **Follow `rules` array** returned by scripts
- **Token fields** → convert to variables with token names in comments
- **`interactive` fields** → navigation relationships between pages

## References

- [references/get-dsl-workflow.md](references/get-dsl-workflow.md) - DSL retrieval workflow
- [references/multi-page-workflow.md](references/multi-page-workflow.md) - Multi-page site building
- [references/dsl-structure.md](references/dsl-structure.md) - DSL data structure
- [scripts/README.md](scripts/README.md) - Complete script documentation

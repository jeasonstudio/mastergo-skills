# MasterGo Skills

[中文文档](README.zh-CN.md)

A Cursor/Claude AI Agent Skill for parsing MasterGo design files and retrieving DSL data. Enables AI assistants to understand design structures, extract component information, and generate code from MasterGo designs.

## Features

- **DSL Analysis**: Analyze MasterGo design structure with human-readable output
- **Full DSL Retrieval**: Get complete DSL data in JSON format
- **Component Docs**: Fetch component documentation from linked URLs
- **Multi-Page Support**: Handle complex designs with multiple pages and navigation
- **Token Support**: Extract design tokens for CSS variable generation

## Installation

### User-Level (available in all projects)

```bash
git clone https://github.com/jeasonstudio/mastergo-skills ~/.cursor/skills/mastergo
```

### Project-Level (current project only)

```bash
git clone https://github.com/jeasonstudio/mastergo-skills .cursor/skills/mastergo
```

## Configuration

### 1. Get Your Token

1. Go to [mastergo.com](https://mastergo.com)
2. Navigate to **Personal Settings** → **Security Settings**
3. Generate a **Personal Access Token**

### 2. Set Environment Variable

```bash
# Required
export MASTERGO_TOKEN="mg_your_token_here"

# Optional (for enterprise deployments)
export MASTERGO_API_URL="https://your-mastergo-domain.com"
```

### 3. Requirements

- **Account**: Team Edition or higher
- **Files**: Must be in Team Projects (not in Drafts)

## Quick Start

### Analyze Design Structure

```bash
python scripts/mastergo_analyze.py "https://mastergo.com/goto/LhGgBAK"
```

This provides a human-readable summary of the design:
- Node tree with types, names, and sizes
- Text contents
- Component documentation links
- Navigation targets

### Get Full DSL Data

```bash
python scripts/mastergo_get_dsl.py "https://mastergo.com/goto/LhGgBAK"
```

Returns JSON with `{ dsl, componentDocumentLinks, rules }`.

### Fetch Component Documentation

```bash
# From DSL output
python scripts/mastergo_get_dsl.py URL | python scripts/mastergo_fetch_docs.py --from-dsl

# Individual URL
python scripts/mastergo_fetch_docs.py "https://example.com/button.mdx"
```

## Usage with AI Agents

Simply provide a MasterGo link to your AI assistant:

```
Parse this design: https://mastergo.com/goto/LhGgBAK
```

The agent will automatically:
1. Analyze the design structure
2. Retrieve DSL data
3. Fetch component documentation
4. Apply rules for code generation

## Scripts Reference

| Script | Purpose | Output |
|--------|---------|--------|
| `mastergo_analyze.py` | Structure summary | Human-readable tree to stdout |
| `mastergo_get_dsl.py` | Full DSL data | JSON to stdout |
| `mastergo_fetch_docs.py` | Component docs | Doc content to stdout |
| `mastergo_utils.py` | Utility functions | Import as module |

## Documentation

- [SKILL.md](SKILL.md) - Agent skill entry point and instructions
- [references/dsl-types.md](references/dsl-types.md) - Complete DSL type definitions
- [references/dsl-structure.md](references/dsl-structure.md) - Key fields and patterns
- [references/multi-page-workflow.md](references/multi-page-workflow.md) - Multi-page workflow guide

## Troubleshooting

### Token Invalid

```
Error: TOKEN_INVALID
```

**Solution**: Regenerate token in MasterGo Personal Settings → Security Settings

### Permission Denied

```
Error: PERMISSION_DENIED
```

**Solution**:
1. Ensure account is Team Edition or higher
2. Move file to Team Project (not Drafts)

### Short Link Failed

```
Error: SHORT_LINK_FAILED
```

**Solution**: Use full URL format `https://mastergo.com/file/{fileId}?layer_id={layerId}`

## License

MIT

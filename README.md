# MasterGo Skills

Claude/Cursor Skill for parsing MasterGo design files and retrieving DSL data.

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

### 1. Get Token

1. Go to https://mastergo.com
2. Navigate to **Personal Settings** → **Security Settings**
3. Generate **Personal Access Token**

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

### Get DSL from Design Link

```bash
# Short link
node scripts/get-dsl.cjs "https://mastergo.com/goto/LhGgBAK"

# Full URL
node scripts/get-dsl.cjs "https://mastergo.com/file/155675508499265?layer_id=158:0002"
```

### Get Component Documentation

```bash
node scripts/get-component-link.cjs "https://example.com/ant/button.mdx"
```

### Get Site Metadata

```bash
node scripts/get-meta.cjs --fileId=155675508499265 --layerId=158:0001
```

## Usage with Claude/Cursor

Simply provide a MasterGo link to the agent:

```
Parse this design: https://mastergo.com/goto/LhGgBAK
```

The agent will:
1. Call `scripts/get-dsl.cjs` to get DSL
2. Process `componentDocumentLinks`
3. Apply `rules` for code generation

## Documentation

- [SKILL.md](SKILL.md) - Skill entry point
- [scripts/README.md](scripts/README.md) - Script documentation
- [references/](references/) - Detailed workflows

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

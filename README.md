# MasterGo Skills

A Claude/Cursor Agent Skill for parsing MasterGo design files and retrieving DSL data.

## Features

- **DSL Retrieval**: Extract design data from MasterGo files
- **URL Parsing**: Handle short links and full URLs
- **Navigation Discovery**: Extract page relationships from interactive fields
- **Component Link Extraction**: Collect component documentation references

## Prerequisites

Configure MasterGo MCP service:

```json
{
  "mcpServers": {
    "mastergo": {
      "command": "npx",
      "args": ["-y", "@mastergo/magic-mcp", "--token=YOUR_TOKEN", "--url=https://mastergo.com"]
    }
  }
}
```

### Getting Your Token

1. Visit https://mastergo.com → Personal Settings → Security Settings
2. Generate Personal Access Token

### Requirements

- **Account**: Team Edition or higher
- **Files**: Must be in Team Projects (not Drafts)

## Installation

**User-Level**: `~/.cursor/skills/mastergo/`

**Project-Level**: `.cursor/skills/mastergo/`

## Usage

The skill activates when you provide a MasterGo design link:

```
Parse this design: https://mastergo.com/goto/LhGgBAK
```

## Structure

```
mastergo-skills/
├── SKILL.md                    # Main skill file
├── references/
│   ├── get-dsl-workflow.md    # DSL retrieval workflow
│   └── dsl-structure.md       # DSL data structure
└── scripts/
    ├── parse-mastergo-url.js  # URL parsing utilities
    └── extract-component-links.js  # DSL extraction utilities
```

## Related

- [MasterGo Magic MCP](https://github.com/mastergo-design/mastergo-magic-mcp)
- [MasterGo](https://mastergo.com)

## License

ISC

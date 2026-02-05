# DSL Retrieval Workflow

## Quick Start

```bash
# Short link (recommended)
node scripts/get-dsl.cjs "https://mastergo.com/goto/LhGgBAK"

# Full URL
node scripts/get-dsl.cjs "https://mastergo.com/file/155675508499265?layer_id=158:0002"

# Direct parameters
node scripts/get-dsl.cjs --fileId=155675508499265 --layerId=158:0002
```

## Response Structure

```json
{
  "dsl": { "nodes": [...] },
  "componentDocumentLinks": ["https://example.com/ant/button.mdx"],
  "rules": [
    "token 字段必须生成为变量并在注释中显示 token 名称",
    "componentDocumentLinks 非空时必须获取所有组件文档"
  ]
}
```

## Workflow

### 1. Get DSL

Run `get-dsl.cjs` with any MasterGo link:

```bash
# Script handles short link resolution automatically
node scripts/get-dsl.cjs "https://mastergo.com/goto/xxx"
```

### 2. Process Component Links

For each URL in `componentDocumentLinks`:

```bash
node scripts/get-component-link.cjs "https://example.com/ant/button.mdx"
```

Or programmatically:

```javascript
const { extractComponentLinks } = require('./scripts/extract-component-links.cjs');
const links = extractComponentLinks(dslResponse);
// Fetch each link content
```

### 3. Handle Navigation

Extract navigation targets from `interactive` field:

```javascript
const { extractNavigations } = require('./scripts/extract-component-links.cjs');

const navs = extractNavigations(result);
// navs = [{ sourceId: "1:12", targetLayerId: "0:3" }]

// Get DSL for each navigation target
for (const { targetLayerId } of navs) {
  // node scripts/get-dsl.cjs --fileId=xxx --layerId={targetLayerId}
}
```

### 4. Multi-Page Discovery

For site-level parsing, see [multi-page-workflow.md](./multi-page-workflow.md).

## Error Handling

| Error | Solution |
|-------|----------|
| TOKEN_MISSING | Set `MASTERGO_TOKEN` environment variable |
| TOKEN_INVALID | Regenerate token in MasterGo settings |
| PERMISSION_DENIED | Use Team Edition, move file to Team Project |
| NOT_FOUND | Check URL is correct |
| SHORT_LINK_FAILED | Use full URL format |

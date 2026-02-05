# MasterGo Skills Scripts

Node.js utility scripts for MasterGo API. No external dependencies (uses Node.js built-in modules only).

**Node.js 兼容版本**: ≥14.0.0（使用了可选链 `?.` 语法）

> **兼容性说明**: 所有脚本使用 `.cjs` 扩展名，确保在任何项目中都能正常运行（无论宿主项目使用 CommonJS 还是 ES Modules）。

## Prerequisites

```bash
# Required: Set your Personal Access Token
export MASTERGO_TOKEN="mg_your_token_here"

# Optional: Custom API URL (for enterprise deployments)
export MASTERGO_API_URL="https://your-mastergo-domain.com"
```

## Scripts

### get-dsl.cjs

Get DSL data from MasterGo design element.

```bash
# Short link
node scripts/get-dsl.cjs "https://mastergo.com/goto/LhGgBAK"

# Full URL
node scripts/get-dsl.cjs "https://mastergo.com/file/155675508499265?layer_id=158:0002"

# Direct parameters
node scripts/get-dsl.cjs --fileId=155675508499265 --layerId=158:0002
```

**Output**: `{ dsl, componentDocumentLinks, rules }`

### get-component-link.cjs

Fetch component documentation content.

```bash
node scripts/get-component-link.cjs "https://example.com/ant/button.mdx"
```

**Output**: Markdown/MDX content (or JSON with url + content if TTY)

### get-meta.cjs

Get site/page metadata for multi-page site building.

```bash
node scripts/get-meta.cjs --fileId=155675508499265 --layerId=158:0001
node scripts/get-meta.cjs "https://mastergo.com/file/155675508499265?layer_id=158:0001"
```

**Output**: `{ result (XML), actions, rules }`

### parse-mastergo-url.cjs

Parse MasterGo URLs to extract identifiers (utility module).

```javascript
const { parseMasterGoUrl, isShortLink, isValidMasterGoUrl } = require('./parse-mastergo-url.cjs');

parseMasterGoUrl("https://mastergo.com/file/155675508499265?layer_id=158:0002")
// => { fileId: "155675508499265", layerId: "158:0002" }

isShortLink("https://mastergo.com/goto/LhGgBAK") // => true
```

### extract-component-links.cjs

Extract data from MasterGo DSL objects (utility module).

```javascript
const { extractComponentLinks, extractNavigations } = require('./extract-component-links.cjs');

extractComponentLinks(dslResponse) // => ["https://...", ...]
extractNavigations(dslResponse)    // => [{ sourceId, targetLayerId }, ...]
```

## Error Handling

All scripts output JSON errors with actionable suggestions:

```json
{
  "error": true,
  "code": "PERMISSION_DENIED",
  "message": "无权访问此文件",
  "suggestion": "请检查: 1) 账户为团队版或以上 2) 文件在团队项目中（非草稿）"
}
```

| Code | Cause | Solution |
|------|-------|----------|
| TOKEN_MISSING | MASTERGO_TOKEN not set | Set environment variable |
| TOKEN_INVALID | Token expired or invalid | Regenerate in MasterGo settings |
| PERMISSION_DENIED | No access to file | Use Team Edition, move file to Team Project |
| NOT_FOUND | File or layer doesn't exist | Check URL is correct |
| SHORT_LINK_FAILED | Can't resolve short link | Use full URL format |

# Multi-Page Site Workflow

Build complete websites from MasterGo designs by parsing site structure and page relationships.

## Quick Start

```bash
# Get site metadata
node scripts/get-meta.cjs --fileId=155675508499265 --layerId=158:0001
```

## Response Structure

```json
{
  "result": "<info><meta title=\"Name\" content=\"项目名\" /><action title=\"首页\" layerId=\"0:1\" /></info>",
  "actions": [
    { "title": "首页", "layerId": "0:1" },
    { "title": "关于", "layerId": "0:2" }
  ],
  "rules": [...]
}
```

## Workflow

### 1. Get Site Metadata

```bash
node scripts/get-meta.cjs "https://mastergo.com/file/{fileId}?layer_id={entryLayerId}"
```

Returns XML with:
- `<meta>` tags: Site name, description, requirements
- `<action>` tags: Page list with titles and layerIds

### 2. Parse All Pages

For each action in the response:

```bash
# Get DSL for each page
node scripts/get-dsl.cjs --fileId={fileId} --layerId={action.layerId}
```

### 3. Discover Navigation

Extract navigation relationships from each page's DSL:

```javascript
const { extractNavigations } = require('./scripts/extract-component-links.cjs');

const navs = extractNavigations(pageDsl);
// navs = [{ sourceId: "button-1", targetLayerId: "page-2" }]
```

### 4. Build Page Graph

Recursively follow navigation targets:

```
Entry Page (0:1)
  └── navigates to → Page 2 (0:2)
  └── navigates to → Page 3 (0:3)
        └── navigates to → Page 4 (0:4)
```

### 5. Generate Task List

Create `task.md` with:

```markdown
# Site: {siteName}

## Pages
1. [ ] 首页 (layerId: 0:1)
2. [ ] 关于 (layerId: 0:2)
3. [ ] 联系 (layerId: 0:3)

## Navigation
- 首页 → 关于 (button click)
- 首页 → 联系 (menu link)
- 关于 → 首页 (logo click)

## Implementation Order
1. Shared components (header, footer, nav)
2. 首页 (entry point)
3. 关于, 联系 (in parallel)
```

## Complete Example

```bash
# 1. Get metadata
META=$(node scripts/get-meta.cjs --fileId=155675508499265 --layerId=158:0001)

# 2. Extract page layerIds from actions array
# actions: [{ title: "首页", layerId: "0:1" }, ...]

# 3. Get DSL for each page
node scripts/get-dsl.cjs --fileId=155675508499265 --layerId=0:1
node scripts/get-dsl.cjs --fileId=155675508499265 --layerId=0:2

# 4. For each page, extract navigations and component links
# 5. Generate task.md with complete site structure
```

## Error Handling

| Error | Solution |
|-------|----------|
| No actions in meta | Entry layer may not be a site container |
| Circular navigation | Track visited layerIds, skip duplicates |
| Missing page | Some navigations may point to deleted layers |

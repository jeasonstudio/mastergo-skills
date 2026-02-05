# Multi-Page Workflow

Build complete websites from MasterGo designs with multiple pages.

## Workflow

### 1. Analyze Entry Page

```bash
python {SKILL_DIR}/scripts/mastergo_analyze.py "https://mastergo.com/goto/xxx"
```

Look for:
- Navigation targets in output
- Page structure and components

### 2. Get Full DSL

```bash
python {SKILL_DIR}/scripts/mastergo_get_dsl.py "https://mastergo.com/goto/xxx"
```

### 3. Extract Navigation Targets

From the DSL, find all `interactive` fields with `type: navigation`:

```python
# In DSL response, navigations look like:
{
    "interactive": [{
        "type": "navigation",
        "targetLayerId": "0:3"  # This is another page
    }]
}
```

### 4. Fetch Each Page

For each `targetLayerId`, construct URL and fetch:

```bash
# Same fileId, different layerId
python {SKILL_DIR}/scripts/mastergo_get_dsl.py \
    --file-id 155675508499265 \
    --layer-id "0:3"
```

### 5. Build Page Graph

```
Entry (0:1)
├── navigates to → Page 2 (0:2)
├── navigates to → Page 3 (0:3)
│   └── navigates to → Page 4 (0:4)
└── navigates to → Page 5 (0:5)
```

Track visited layerIds to avoid cycles.

## Implementation Order

1. **Shared components first**: header, footer, navigation
2. **Entry page**: main landing page
3. **Sub-pages**: in dependency order or parallel

## Extracting Navigations (Code Pattern)

```python
def extract_navigations(dsl):
    """Extract all navigation targets from DSL."""
    navs = []
    
    def traverse(node):
        if not node:
            return
        for action in node.get('interactive', []):
            if action.get('type') == 'navigation':
                navs.append({
                    'sourceId': node.get('id'),
                    'sourceName': node.get('name'),
                    'targetLayerId': action.get('targetLayerId')
                })
        for child in node.get('children', []):
            traverse(child)
    
    dsl_root = dsl.get('dsl', dsl)
    for node in dsl_root.get('nodes', []):
        traverse(node)
    if dsl_root.get('root'):
        traverse(dsl_root['root'])
    
    return navs
```

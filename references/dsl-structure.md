# DSL Key Concepts & Patterns

Practical guide for working with MasterGo DSL. For complete types, see [dsl-types.md](dsl-types.md).

## Understanding Script Output

### mastergo_analyze.py Output

```
DSL Analysis (v1.0.0, REACT)
Stats: 45 nodes, 12 texts, 3 components, 2 navigations

Component Docs:
  - https://example.com/button.mdx
  - https://example.com/input.mdx

Structure:
└── [FRAME] Page (1440x900)
    ├── [FRAME] Header (1440x64)
    │   ├── [TEXT] Logo "Company Name"
    │   └── [FRAME] Nav
    │       └── [TEXT] Menu "Home" → 0:2
    └── [FRAME] Content (1440x836)
        └── [TEXT] Title "Welcome"

Text Contents:
  [1:12] Logo: "Company Name"
  [1:15] Menu: "Home"
  [1:20] Title: "Welcome"

Navigations:
  Menu (1:15) → 0:2
```

### mastergo_get_dsl.py Output

```json
{
  "dsl": { "nodes": [...], "root": {...} },
  "componentDocumentLinks": ["https://..."],
  "rules": ["token field must be generated as variable..."]
}
```

## Key Mapping Patterns

### Layout → CSS

| DSL | CSS |
|-----|-----|
| `autoLayout.direction: 'ROW'` | `flex-direction: row` |
| `autoLayout.direction: 'COLUMN'` | `flex-direction: column` |
| `autoLayout.layoutWrap: 'WRAP'` | `flex-wrap: wrap` |
| `autoLayout.itemSpacing` | `gap` |
| `autoLayout.mainAxisAlignItems: 'CENTER'` | `justify-content: center` |
| `autoLayout.crossAxisAlignItems: 'CENTER'` | `align-items: center` |
| `relatedLayout.type: 'ABSOLUTE'` | `position: absolute` |
| `relatedLayout.flexGrow: 1` | `flex-grow: 1` |

### Node Type → HTML Tag

| DSL Type | Default Tag |
|----------|-------------|
| `FRAME` | `div` |
| `TEXT` | `span` / `p` |
| `RECTANGLE` | `div` |
| `IMAGE` | `img` |
| `INSTANCE` | Component from docs |

### Token → CSS Variable

```python
# DSL
node['style']['styleTokenAlias'] = {
    'backgroundTokenId': 'token-123'
}
# localStyleMap
dsl['localStyleMap']['token-123'] = {
    'name': 'brand-primary',
    'variable': '--brand-primary',
    'value': '#1890ff'
}

# Generated CSS
# background-color: var(--brand-primary); /* token: brand-primary */
```

## Common Extraction Patterns

### Extract All Text

```python
def extract_texts(dsl):
    texts = []
    def traverse(node):
        if not node:
            return
        if node.get('type') == 'TEXT' and node.get('characters'):
            texts.append({
                'id': node.get('id'),
                'name': node.get('name'),
                'text': node.get('characters'),
            })
        for child in node.get('children', []):
            traverse(child)
    
    root = dsl.get('dsl', dsl)
    for node in root.get('nodes', []):
        traverse(node)
    return texts
```

### Build Component Tree

```python
def build_tree(node, depth=0):
    if not node:
        return None
    
    return {
        'type': node.get('type'),
        'name': node.get('name'),
        'tag': node.get('style', {}).get('tag', 'div'),
        'text': node.get('characters'),
        'children': [build_tree(c, depth+1) for c in node.get('children', [])]
    }
```

### Get Style Properties

```python
def get_styles(node):
    style = node.get('style', {})
    return {
        **style.get('value', {}),        # UI styles
        **style.get('layoutStyles', {}), # Layout styles
    }
```

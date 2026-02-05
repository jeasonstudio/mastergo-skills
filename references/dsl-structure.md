# DSL Data Structure Reference

## Node Structure

```typescript
interface DslNode {
  id: string;                    // Unique identifier (e.g., "1:12")
  name: string;                  // Node name from design
  type: string;                  // FRAME, TEXT, RECTANGLE, GROUP, etc.
  children?: DslNode[];          // Child nodes
  style?: StyleProperties;       // Style definitions
  token?: string;                // Design token reference
  componentInfo?: ComponentInfo; // Component binding
  interactive?: Interactive[];   // Navigation/interaction
}
```

## Key Fields

### style

Contains visual properties:

```json
{
  "backgroundColor": "#1890ff",
  "borderRadius": 8,
  "padding": [16, 24],
  "fontSize": 14,
  "fontWeight": 500
}
```

### token

Design token reference - should be converted to CSS variable:

```json
{
  "style": { "backgroundColor": "#1890ff" },
  "token": "brand-primary"
}
```

### componentInfo

Component binding information:

```json
{
  "componentInfo": {
    "componentSetDocumentLink": ["https://example.com/button.mdx"]
  }
}
```

### interactive

Navigation/interaction definitions:

```json
{
  "interactive": [{
    "type": "navigation",
    "targetLayerId": "0:3"
  }]
}
```

## Metadata Response (mcp__getMeta)

XML structure:

```xml
<info>
  <meta title="Name" content="Project Name" />
  <meta title="Description" content="Project description" />
  <meta title="Requirements" content="Tech stack requirements" />
  <action title="Page Name" layerId="0:1" />
  <action title="Another Page" layerId="0:2" />
</info>
```

## Traversal Pattern

```javascript
function traverse(node, callback) {
  callback(node);
  node.children?.forEach(child => traverse(child, callback));
}

// Usage
traverse(dsl, node => {
  if (node.interactive) {
    // Handle navigation
  }
  if (node.componentInfo?.componentSetDocumentLink) {
    // Collect component links
  }
});
```

# MasterGo DSL Type Reference

Complete type definitions for MasterGo DSL data structures.

## Root Structure

```typescript
interface MGDSLData {
  version: string;                    // SemVer version
  framework: 'REACT' | 'VUE2' | 'VUE3' | 'ANDROID' | 'IOS';
  root: MGLayerNode;                  // Entry layer node
  nodeMap: Record<string, MGNode>;    // All nodes by ID
  fileMap: Record<string, MGDSLFile>; // Component files
  localStyleMap: StyleMap;            // Design tokens
  settings: { useToken: boolean };
  entry: string;                      // Entry file ID
  globalStyleMap: Record<string, ClassStyle>;  // CSS classes (JS frameworks)
}
```

## Node Types

### MGLayerNode (Primary)

```typescript
interface MGLayerNode {
  type: 'LAYER';
  id: string;                         // e.g., "1:12"
  name: string;                       // Design name
  componentName: string;              // Code component name
  layerType: NodeType;                // FRAME, TEXT, RECTANGLE, etc.
  children: string[];                 // Child node IDs
  parent?: string;
  
  // Visual
  isVisible: boolean;
  isMask: boolean;
  isRoot: boolean;
  
  // Layout & Style
  layout: NodeLayout;
  style: CssNodeStyle;
  characters: string;                 // Text content (for TEXT nodes)
  
  // File association
  relatedFile: string;
  isNewFile?: boolean;
}
```

### NodeType Values

```typescript
type NodeType =
  | 'GROUP' | 'FRAME' | 'RECTANGLE' | 'TEXT' | 'LINE'
  | 'ELLIPSE' | 'POLYGON' | 'STAR' | 'PEN'
  | 'COMPONENT' | 'COMPONENTSET' | 'INSTANCE'
  | 'BOOLEANOPERATION' | 'SLICE' | 'CONNECTOR' | 'SECTION'
  | 'CUSTOM' | 'TABLE' | 'TOGGLE' | 'BUTTON' | 'TREE' | 'TEXTSHAPE'
  | 'Input' | 'Select' | 'Chart';
```

### Component Nodes

```typescript
interface MGComponentNode extends MGLayerNode {
  layerType: 'COMPONENT';
  alias: string;
  description: string;
  documentationLinks: { url: string }[];
  componentSetId?: string;
  componentSetDescription?: string;
  componentSetDocumentationLinks?: { url: string }[];
}

interface MGInstanceNode extends MGLayerNode {
  layerType: 'INSTANCE';
  mainComponent?: string;             // Main component layer ID
  description: string;
  documentationLinks: { url: string }[];
}
```

## Layout

```typescript
interface NodeLayout {
  width?: Dimension;
  height?: Dimension;
  renderWidth?: Dimension;            // Includes shadows/strokes
  renderHeight?: Dimension;
  matrix?: Matrix;                    // Transform matrix
  overflow?: 'HIDDEN' | 'VISIBLE';
  autoLayout?: AutoLayout;
  relatedLayout?: AbsoluteLayout | RelatedAutoLayout;
}

type Dimension = {
  type: 'PIXEL' | 'PERCENT' | 'CALC';
  value: number | string;
};

type Matrix = [[number, number, number], [number, number, number]];
```

### Auto Layout (Flexbox)

```typescript
interface AutoLayout {
  direction: 'COLUMN' | 'ROW';
  layoutWrap: 'NO_WRAP' | 'WRAP';
  itemSpacing: Dimension | 'AUTO';           // gap
  crossAxisSpacing: Dimension | 'AUTO' | null;
  paddingTop: Dimension;
  paddingRight: Dimension;
  paddingBottom: Dimension;
  paddingLeft: Dimension;
  mainAxisAlignItems: 'START' | 'END' | 'CENTER' | 'SPACE_BETWEEN';
  crossAxisAlignItems: 'START' | 'END' | 'CENTER';
  crossAxisAlignContent: 'AUTO' | 'SPACE_BETWEEN';
  strokesIncludedInLayout: boolean;
  itemReverseZIndex: boolean;
}
```

### Positioning

```typescript
// Absolute positioning
interface AbsoluteLayout {
  type: 'ABSOLUTE';
  bound: { left?: Dimension; right?: Dimension; top?: Dimension; bottom?: Dimension };
  renderBound: { left?: Dimension; right?: Dimension; top?: Dimension; bottom?: Dimension };
}

// Flex child
interface RelatedAutoLayout {
  type: 'AUTO';
  alignSelf: 'STRETCH' | 'INHERIT' | 'AUTO';
  flexGrow: number;
}
```

## Styles

### CssNodeStyle

```typescript
interface CssNodeStyle {
  id: string;                         // "style-{nodeId}"
  name: string;                       // CSS class name
  type: 'VIEW' | 'SVG' | 'IMAGE' | 'TEXT' | 'INPUT' | 'BUTTON' | 'SCROLLVIEW';
  tag?: 'IMG' | 'DIV' | 'TEXT' | 'BUTTON' | 'INPUT' | 'SLOT' | 'SVG' | 'OPTION';
  
  value: StyleSet;                    // UI styles
  layoutStyles: StyleSet;             // Layout styles
  inlineStyles?: StyleSet;
  dynamicInlineStyles?: Record<string, string>;
  
  attributes: Record<string, AttributeItem>;
  classList?: string[];
  subSelectors?: ClassStyle[];
  textStyles?: TextSegStyle[];        // Rich text segments
  
  // Token references
  styleTokenAlias?: {
    backgroundTokenId?: string;
    strokeColorTokenId?: string;
    paddingTokenId?: string;
    gapTokenId?: string;
    radiusTokenId?: string;
  };
}

// StyleSet = standard CSS properties (from csstype)
interface StyleSet extends CSSProperties {}
```

### Attributes

```typescript
interface AttributeItem {
  type: 'STATIC' | 'DYNAMIC' | 'METHOD' | 'UNBIND';
  name: string;
  value: string;
  valueType: 'STRING' | 'NUMBER' | 'BOOLEAN' | 'FUNCTION' | 'OBJECT' | 'ARRAY' | 'SLOT';
  valueSource?: 'PROPS' | 'METHODS' | 'DATA';
  expression?: string;
  defaultValue?: string | number | boolean;
  arguments?: string[];
}
```

## Design Tokens

```typescript
type TokenItem = TokenCommonItem | TokenTextItem | TokenEffectItem;

interface TokenCommonItem {
  id: string;
  type: 'color' | 'padding' | 'border-radius' | 'border-width' | 'gap';
  name: string;                       // Token name
  originName: string;
  originAlias: string;
  value: any;                         // Actual CSS value
  variable: string;                   // CSS variable name
  isMultiple?: boolean;
}

interface TokenTextItem {
  id: string;
  type: 'text';
  name: string;
  variable: string;
  textItems: {
    font?: TokenTextSubItem;
    fontfamily?: TokenTextSubItem;
    fontstyle?: TokenTextSubItem;
    fontsize?: TokenTextSubItem;
    lineheight?: TokenTextSubItem;
    decoration?: TokenTextSubItem;
    letterspacing?: TokenTextSubItem;
  };
}

interface TokenEffectItem {
  id: string;
  type: 'effect';
  name: string;
  variable: string;
  effectItems: {
    shadow?: TokenEffectSubItem;
    filter?: TokenEffectSubItem;
    backdropfilter?: TokenEffectSubItem;
  };
}
```

## Component Files

```typescript
interface MGDSLFile {
  id: string;
  name: string;
  entryLayerId: string;
  chunks: string[];                   // Child file IDs
  
  // Component logic
  data: Record<string, DataItem>;
  props: Record<string, PropItem>;
  methods: Record<string, Method>;
  computed: Record<string, Computed>;
  imports: ImportItem[];
}

interface Method {
  name: string;
  args: string[];
  content: string;
  returnValue?: string;
}

interface Computed {
  name: string;
  args: string[];
  content: string;
  returnValue?: string;
  dependencies?: string[];
}

interface ImportItem {
  name: string;
  path: string;
  type: 'DEFAULT' | 'ALL';            // import X / import * as X
}
```

## Operations (Conditional/Loop)

```typescript
type MGOperationNode = IfStatement | Iteration | Raw | TernaryExpression;

interface IfStatement {
  type: 'OPERATION';
  operationType: 'If_STATEMENT';
  condition: string;
  consequent: { type: 'MGNode' | 'EXPRESSION'; body: MGNode | string };
  alternate: { type: 'MGNode' | 'EXPRESSION'; body: MGNode | string };
}

interface Iteration {
  type: 'OPERATION';
  operationType: 'ITERATOR';
  variable: string;                   // Loop variable name
  body: MGNode;
  key?: string;                       // Key field for list rendering
}

interface TernaryExpression {
  type: 'OPERATION';
  operationType: 'TERNARY_EXPRESSION';
  condition: string;
  trueExpression: { type: 'MGNode' | 'EXPRESSION'; body: MGNode | string };
  falseExpression: { type: 'MGNode' | 'EXPRESSION'; body: MGNode | string };
}
```

## Code Generation Mapping

| DSL Field | CSS/HTML Output |
|-----------|-----------------|
| `style.value` | CSS properties |
| `style.layoutStyles` | Flexbox/position styles |
| `style.tag` | HTML tag |
| `style.name` | CSS class name |
| `style.classList` | Additional CSS classes |
| `style.attributes` | HTML/component attributes |
| `layout.autoLayout` | `display: flex` + flex properties |
| `layout.relatedLayout.type='ABSOLUTE'` | `position: absolute` |
| `localStyleMap[tokenId].variable` | CSS variable reference |
| `characters` | Text content |

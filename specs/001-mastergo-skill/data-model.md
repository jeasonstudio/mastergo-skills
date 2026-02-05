# 数据模型: MasterGo Claude Skills

## 核心实体

### MasterGo 链接

| 字段 | 类型 | 说明 |
|------|------|------|
| `fileId` | string | 设计文件 ID（数字字符串） |
| `layerId` | string | 图层 ID（格式: `158:0002`） |
| `shortId` | string? | 短链接 ID（可选） |

**链接格式**:
- 完整: `https://mastergo.com/file/{fileId}?layer_id={layerId}`
- 短链: `https://mastergo.com/goto/{shortId}`

---

### DSL 响应

```typescript
interface DslResponse {
  dsl: DslNode;
  componentDocumentLinks: string[];
  rules: string[];
}

interface DslNode {
  id: string;
  name: string;
  type: string;
  children?: DslNode[];
  componentInfo?: {
    componentSetDocumentLink?: string[];
  };
  interactive?: Interactive[];
  // ... 样式属性
}

interface Interactive {
  type: "navigation";
  targetLayerId: string;
}
```

---

### Meta 响应

```typescript
interface MetaResponse {
  result: string;  // XML 格式
  rules: string[];
}
```

**XML 结构**:
```xml
<info>
  <meta title="Name" content="项目名称" />
  <meta title="Description" content="项目描述" />
  <meta title="Requirements" content="技术要求" />
  <action title="页面名称" layerId="0:1" />
</info>
```

---

### 组件文档链接

| 字段 | 类型 | 说明 |
|------|------|------|
| `url` | string | 组件文档 URL |
| `content` | string | 文档内容（Markdown/MDX） |

---

### 导航关系

```typescript
interface Navigation {
  sourceId: string;      // 触发导航的节点 ID
  targetLayerId: string; // 目标页面 layerId
}
```

---

## 状态转换

### DSL 获取流程

```
[初始] → 解析链接 → [链接解析完成]
                          ↓
                    获取 DSL → [DSL 获取完成]
                          ↓
              处理 componentDocumentLinks → [组件文档获取完成]
                          ↓
                    应用 rules → [完成]
```

### 多页面站点流程

```
[初始] → 获取 Meta → [Meta 解析完成]
                          ↓
              遍历 actions → 获取每页 DSL
                          ↓
              解析 interactive → 发现导航目标
                          ↓
              递归获取目标页面 → [所有页面获取完成]
                          ↓
                    生成 task.md → [完成]
```

---

## 验证规则

### 链接验证

| 规则 | 说明 |
|------|------|
| `fileId` 必须为数字 | 正则: `/^\d+$/` |
| `layerId` 必须包含冒号 | 正则: `/^\d+:\d+$/` |
| 域名必须包含 `mastergo` | 支持自定义部署 |

### Token 验证

| 规则 | 说明 |
|------|------|
| 非空 | `MASTERGO_TOKEN` 环境变量必须设置 |
| 格式 | 通常以 `mg_` 开头 |

---

## 关键约束

1. **componentDocumentLinks**: 必须在代码生成前处理所有链接
2. **rules**: 必须严格遵循返回的规则数组
3. **token 字段**: DSL 中的 token 必须转换为变量，注释中保留 token 名称
4. **interactive**: 必须递归处理导航关系直到无更多目标

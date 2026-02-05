# 研究文档: MasterGo Claude Skills

## R1: Claude Skills 最佳实践

### 核心发现

| 最佳实践 | 应用方式 |
|----------|----------|
| SKILL.md < 500 行 | 目标 < 100 行，仅保留核心触发条件和基本工作流 |
| 渐进式披露 | 详细工作流放 references/，脚本放 scripts/ |
| 第三人称描述 | "解析 MasterGo 设计文件" 而非 "我可以帮你解析" |
| 具体触发词 | 包含 "mastergo"、"设计链接"、"DSL" 等关键词 |
| 预制脚本优于生成代码 | 提供可直接执行的 Node.js 脚本 |

### 目录结构决策

```
skill-name/
├── SKILL.md              # 必需 - 主入口（简洁）
├── references/           # 可选 - 详细文档
│   └── *.md
└── scripts/              # 可选 - 工具脚本
    └── *.js
```

### 描述编写规范

```yaml
name: mastergo
description: 解析 MasterGo 设计文件获取 DSL 数据。当用户提供 MasterGo 设计链接、需要分析设计结构、或提取组件规范时使用此 Skill。
```

---

## R2: MasterGo API 调用方式

### API 端点（基于 MCP Server 源码分析）

| 端点 | 方法 | 用途 |
|------|------|------|
| `/mcp/dsl` | GET | 获取 DSL 数据 |
| `/mcp/meta` | GET | 获取站点元信息 |
| `/mcp/style` | GET | 获取组件样式 JSON |

### 认证方式

```javascript
headers: {
  "Content-Type": "application/json",
  "Accept": "application/json",
  "X-MG-UserAccessToken": process.env.MASTERGO_TOKEN
}
```

### 响应结构

**DSL 响应**:
```javascript
{
  dsl: { nodes: [...] },
  componentDocumentLinks: ["https://..."],
  rules: ["token 字段必须生成为变量...", ...]
}
```

**Meta 响应**:
```xml
<info>
  <meta title="Name" content="项目名称" />
  <action title="首页" layerId="0:1" />
</info>
```

---

## R3: 短链接解析策略

### 解析流程

```
短链接: https://mastergo.com/goto/LhGgBAK
    ↓
HTTP 302 重定向
    ↓
完整链接: https://mastergo.com/file/155675508499265?layer_id=158:0002
    ↓
解析 fileId + layerId
```

### 实现方式

```javascript
const response = await fetch(shortLink, { redirect: 'manual' });
const fullUrl = response.headers.get('location');
```

---

## R4: 错误处理策略

### 错误码映射

| HTTP 状态 | 错误码 | 用户建议 |
|-----------|--------|----------|
| 401 | TOKEN_INVALID | 请在 MasterGo 个人设置 → 安全设置重新生成 Token |
| 403 | PERMISSION_DENIED | 请检查: 1) 账户为团队版 2) 文件在团队项目中 |
| 404 | NOT_FOUND | 请检查链接是否正确 |
| 408/504 | TIMEOUT | 请检查网络连接，稍后重试 |

### 统一错误格式

```json
{
  "error": true,
  "code": "ERROR_CODE",
  "message": "错误描述",
  "suggestion": "具体解决步骤"
}
```

---

## 研究结论

1. **架构**: 采用 Skills 标准结构，渐进式披露
2. **实现**: Node.js 原生 https，零依赖
3. **认证**: 环境变量 `MASTERGO_TOKEN`
4. **错误**: 统一 JSON 格式，包含可操作建议

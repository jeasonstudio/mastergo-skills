# MasterGo API 契约

## 基础信息

- **Base URL**: `https://mastergo.com`（可通过 `MASTERGO_API_URL` 覆盖）
- **认证**: Header `X-MG-UserAccessToken: {MASTERGO_TOKEN}`
- **格式**: JSON

---

## 端点

### GET /mcp/dsl

获取设计元素的 DSL 数据。

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `fileId` | string | 是 | 设计文件 ID |
| `layerId` | string | 是 | 图层 ID |

**响应** (200):

```json
{
  "nodes": [
    {
      "id": "0:1",
      "name": "Frame",
      "type": "FRAME",
      "children": [...],
      "componentInfo": {
        "componentSetDocumentLink": ["https://..."]
      },
      "interactive": [
        { "type": "navigation", "targetLayerId": "0:2" }
      ]
    }
  ]
}
```

**脚本封装响应**:

```json
{
  "dsl": { "nodes": [...] },
  "componentDocumentLinks": ["https://..."],
  "rules": [
    "token 字段必须生成为变量并在注释中显示 token 名称",
    "componentDocumentLinks 非空时必须获取所有组件文档"
  ]
}
```

---

### GET /mcp/meta

获取站点/页面元信息。

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `fileId` | string | 是 | 设计文件 ID |
| `layerId` | string | 是 | 图层 ID |

**响应** (200):

```json
{
  "result": "<info><meta title=\"Name\" content=\"项目名\" /><action title=\"首页\" layerId=\"0:1\" /></info>",
  "rules": [...]
}
```

---

### GET (组件文档 URL)

获取组件文档内容。直接请求 `componentDocumentLinks` 中的 URL。

**响应** (200): Markdown/MDX 文本

---

## 错误响应

### 401 Unauthorized

```json
{
  "error": true,
  "code": "TOKEN_INVALID",
  "message": "Token 无效或已过期",
  "suggestion": "请在 MasterGo 个人设置 → 安全设置重新生成 Token"
}
```

### 403 Forbidden

```json
{
  "error": true,
  "code": "PERMISSION_DENIED",
  "message": "无权访问此文件",
  "suggestion": "请检查: 1) 账户为团队版或以上 2) 文件在团队项目中（非草稿）"
}
```

### 404 Not Found

```json
{
  "error": true,
  "code": "NOT_FOUND",
  "message": "文件或图层不存在",
  "suggestion": "请检查链接是否正确"
}
```

### 408/504 Timeout

```json
{
  "error": true,
  "code": "TIMEOUT",
  "message": "请求超时",
  "suggestion": "请检查网络连接，稍后重试"
}
```

---

## 短链接解析

短链接 `https://mastergo.com/goto/{shortId}` 会返回 302 重定向到完整 URL。

**请求**:
```
GET /goto/LhGgBAK HTTP/1.1
Host: mastergo.com
```

**响应**:
```
HTTP/1.1 302 Found
Location: https://mastergo.com/file/155675508499265?layer_id=158:0002
```

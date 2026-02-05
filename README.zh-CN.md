# MasterGo Skills

[English](README.md)

一个用于解析 MasterGo 设计文件并获取 DSL 数据的 Cursor/Claude AI Agent Skill。帮助 AI 助手理解设计结构、提取组件信息，并从 MasterGo 设计稿生成代码。

## 功能特性

- **DSL 分析**：分析 MasterGo 设计结构，输出人类可读的结果
- **完整 DSL 获取**：以 JSON 格式获取完整的 DSL 数据
- **组件文档**：从关联的 URL 获取组件文档
- **多页面支持**：处理包含多个页面和导航的复杂设计
- **Token 支持**：提取设计令牌用于生成 CSS 变量

## 安装

### 用户级别（所有项目可用）

```bash
git clone https://github.com/jeasonstudio/mastergo-skills ~/.cursor/skills/mastergo
```

### 项目级别（仅当前项目可用）

```bash
git clone https://github.com/jeasonstudio/mastergo-skills .cursor/skills/mastergo
```

## 配置

### 1. 获取 Token

1. 访问 [mastergo.com](https://mastergo.com)
2. 进入 **个人设置** → **安全设置**
3. 生成 **个人访问令牌**

### 2. 设置环境变量

```bash
# 必需
export MASTERGO_TOKEN="mg_your_token_here"

# 可选（企业私有化部署）
export MASTERGO_API_URL="https://your-mastergo-domain.com"
```

### 3. 要求

- **账户**：团队版或更高版本
- **文件**：必须在团队项目中（非草稿箱）

## 快速开始

### 分析设计结构

```bash
python scripts/mastergo_analyze.py "https://mastergo.com/goto/LhGgBAK"
```

输出设计的人类可读摘要：
- 节点树（包含类型、名称和尺寸）
- 文本内容
- 组件文档链接
- 导航目标

### 获取完整 DSL 数据

```bash
python scripts/mastergo_get_dsl.py "https://mastergo.com/goto/LhGgBAK"
```

返回包含 `{ dsl, componentDocumentLinks, rules }` 的 JSON。

### 获取组件文档

```bash
# 从 DSL 输出获取
python scripts/mastergo_get_dsl.py URL | python scripts/mastergo_fetch_docs.py --from-dsl

# 单独获取
python scripts/mastergo_fetch_docs.py "https://example.com/button.mdx"
```

## 与 AI 助手配合使用

只需向 AI 助手提供 MasterGo 链接：

```
解析这个设计：https://mastergo.com/goto/LhGgBAK
```

AI 助手将自动：
1. 分析设计结构
2. 获取 DSL 数据
3. 获取组件文档
4. 应用规则生成代码

## 脚本参考

| 脚本 | 用途 | 输出 |
|------|------|------|
| `mastergo_analyze.py` | 结构摘要 | 人类可读的树形结构输出到 stdout |
| `mastergo_get_dsl.py` | 完整 DSL 数据 | JSON 输出到 stdout |
| `mastergo_fetch_docs.py` | 组件文档 | 文档内容输出到 stdout |
| `mastergo_utils.py` | 工具函数 | 作为模块导入 |

## 文档

- [SKILL.md](SKILL.md) - Agent Skill 入口和使用说明
- [references/dsl-types.md](references/dsl-types.md) - 完整的 DSL 类型定义
- [references/dsl-structure.md](references/dsl-structure.md) - 关键字段和模式
- [references/multi-page-workflow.md](references/multi-page-workflow.md) - 多页面工作流指南

## 故障排除

### Token 无效

```
Error: TOKEN_INVALID
```

**解决方案**：在 MasterGo 个人设置 → 安全设置中重新生成 Token

### 权限被拒绝

```
Error: PERMISSION_DENIED
```

**解决方案**：
1. 确保账户是团队版或更高版本
2. 将文件移动到团队项目（非草稿箱）

### 短链接失败

```
Error: SHORT_LINK_FAILED
```

**解决方案**：使用完整 URL 格式 `https://mastergo.com/file/{fileId}?layer_id={layerId}`

## 许可证

MIT

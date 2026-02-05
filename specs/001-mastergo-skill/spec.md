# 功能规范: MasterGo Claude Skills

**功能分支**: `001-mastergo-skill`  
**创建日期**: 2026-01-30  
**状态**: 草稿  
**输入**: 构建一个 Claude Skills，提供针对 MasterGo 设计工具的接口调用和代码生成最佳实践

## 用户场景与测试 *(必需)*

### 用户故事 1 - 单元素/页面 DSL 获取 (优先级: P1)

用户提供 MasterGo 设计链接，Agent 解析链接并通过 MCP 工具获取 DSL 数据，为代码生成提供设计规范。

**优先级理由**: 这是 Skill 的核心能力，是所有后续操作的基础。

**独立测试**: 用户提供任意有效的 MasterGo 链接，Agent 返回包含 `dsl`、`componentDocumentLinks`、`rules` 的完整响应。

**验收场景**:

1. **Given** 用户提供完整链接 `https://mastergo.com/file/{fileId}?layer_id={layerId}`, **When** Agent 调用 `mcp__getDsl`, **Then** 返回对应节点的 DSL 数据
2. **Given** 用户提供短链接 `https://mastergo.com/goto/{shortId}`, **When** Agent 调用 `mcp__getDsl`, **Then** 自动解析短链接并返回 DSL 数据
3. **Given** DSL 响应包含非空 `componentDocumentLinks`, **When** Agent 处理响应, **Then** 循环调用 `mcp__getComponentLink` 获取所有组件文档
4. **Given** DSL 响应包含 `rules` 数组, **When** Agent 生成代码, **Then** 严格遵循所有规则约束

---

### 用户故事 2 - 多页面站点构建 (优先级: P2)

用户需要构建完整网站时，Agent 通过 `mcp__getMeta` 获取站点配置，解析所有页面并处理页面间导航关系。

**优先级理由**: 完整站点构建是高级用例，需要先掌握单页面 DSL 获取。

**独立测试**: 给定站点入口链接，Agent 能生成完整的 `task.md` 文件，包含所有页面列表和导航关系。

**验收场景**:

1. **Given** 用户提供站点入口设计链接, **When** Agent 调用 `mcp__getMeta`, **Then** 返回包含 `meta` 和 `action` 的 XML 数据
2. **Given** Meta 响应包含多个 `action` 节点, **When** Agent 解析响应, **Then** 为每个 action 的 `targetLayerId` 调用 `mcp__getDsl`
3. **Given** 某页面 DSL 包含 `interactive` 字段, **When** Agent 解析导航关系, **Then** 继续调用 `mcp__getDsl` 获取目标页面直到无更多导航
4. **Given** 所有页面解析完成, **When** Agent 整理信息, **Then** 生成包含页面列表和导航关系的 `task.md`

---

### 用户故事 3 - 组件开发工作流 (优先级: P3) ⏳ *延后到 v1.1*

> **范围说明**: 此功能延后到 v1.1 版本实现，v1.0 专注于 P1、P2 核心功能。

用户需要开发符合设计规范的组件时，Agent 通过 `get-component-workflow.cjs` 获取结构化的组件开发工作流。

**延后理由**: 此功能涉及在用户项目中创建目录和文件，复杂度较高，先确保核心功能稳定。

---

### 边界情况

- 链接格式不正确：提供清晰的格式说明（完整链接或短链接）
- 权限不足：提示检查账户版本（需团队版）和文件位置（需在团队项目中）
- Token 无效或过期：提示用户在个人设置 → 安全设置中重新生成
- API 超时：提示检查网络连接和 MasterGo 服务状态
- 短链接无法解析：提示使用完整链接格式

## 需求 *(必需)*

### 功能需求

- **FR-001**: Skill 必须支持完整链接格式 `https://mastergo.com/file/{fileId}?layer_id={layerId}`
- **FR-002**: Skill 必须支持短链接格式 `https://mastergo.com/goto/{shortId}`
- **FR-003**: Skill 必须在获取 DSL 后自动处理非空的 `componentDocumentLinks` 数组
- **FR-004**: Skill 必须遵循 `rules` 数组中的所有代码生成约束，包括 token 字段转换为变量
- **FR-005**: Skill 必须能解析 `interactive` 字段发现页面导航关系
- **FR-006**: Skill 必须提供完整的 scripts 使用指南，包括 `get-dsl.cjs`、`get-component-link.cjs`、`get-meta.cjs`、`parse-mastergo-url.cjs`、`extract-component-links.cjs`
- **FR-007**: Skill 文档必须简洁，控制在 2000 字以内，只包含 MasterGo 相关核心内容
- **FR-008**: 错误信息必须包含问题原因和具体解决步骤

### 关键实体

- **MasterGo 链接**: 设计文件访问地址，支持完整格式（含 fileId 和 layer_id）和短链接格式
- **DSL 响应**: 包含 `dsl`（设计结构）、`componentDocumentLinks`（组件文档链接数组）、`rules`（代码生成规则数组）
- **Meta 响应**: 包含 `result`（XML 格式的站点配置）和 `rules`（站点构建规则）
- **Interactive 字段**: 包含 `type: "navigation"` 和 `targetLayerId`，用于发现页面导航关系
- **Token 字段**: DSL 中的设计令牌，需转换为代码变量并在注释中保留 token 名称

## 成功标准 *(必需)*

### 可衡量成果

- **SC-001**: 用户提供有效链接后，在 5 秒内获取到完整 DSL 响应
- **SC-002**: Skill 主文档（SKILL.md）控制在 100 行以内，确保简洁易读
- **SC-003**: 95% 的有效 MasterGo 链接（完整链接或短链接）能被正确解析
- **SC-004**: 错误信息 100% 包含可操作的解决建议，用户无需额外询问
- **SC-005**: Skill 结构符合 Claude/Cursor Skills 标准格式，可直接复制到 `~/.cursor/skills/` 或项目 `.cursor/skills/` 使用

## 假设

- 用户拥有团队版或以上 MasterGo 账户
- 设计文件位于团队项目中（非草稿箱）
- MasterGo API 服务可正常访问
- 用户已设置环境变量 `MASTERGO_TOKEN` 为有效的 Personal Access Token

## Scripts 参考

Skills 通过自有 Node.js scripts 直接调用 MasterGo API，不依赖 MCP Server。

**环境变量配置**:
- `MASTERGO_TOKEN` (必需): Personal Access Token
- `MASTERGO_API_URL` (可选): API 地址，默认 `https://mastergo.com`

| Script 名称 | 用途 | 关键参数 | 版本 |
|-------------|------|----------|------|
| `get-dsl.cjs` | 获取设计元素 DSL | `fileId` + `layerId` 或 `shortLink` | v1.0 |
| `get-component-link.cjs` | 获取组件文档内容 | `url` | v1.0 |
| `get-meta.cjs` | 获取站点/页面元信息 | `fileId` + `layerId` | v1.0 |
| `parse-mastergo-url.cjs` | 解析 MasterGo 链接 | `url` | v1.0 |
| `extract-component-links.cjs` | 从 DSL 提取组件文档链接 | `dsl` (JSON) | v1.0 |
| `get-component-workflow.cjs` | 获取组件开发工作流 | `rootPath` + `fileId` + `layerId` | v1.1 |

## 澄清

### Session 2026-01-30

- Q: Scripts 应该扮演什么角色？ → A: Scripts 完全替代 MCP，直接调用 MasterGo API
- Q: Scripts 应使用什么语言/运行时？ → A: Node.js (JavaScript)
- Q: Scripts 应如何获取 Token？ → A: 环境变量 `MASTERGO_TOKEN`
- Q: Scripts 是否需要支持配置 API Base URL？ → A: 默认 `https://mastergo.com`，支持 `MASTERGO_API_URL` 环境变量覆盖
- Q: 是否将组件开发工作流纳入 v1.0 范围？ → A: 延后到 v1.1，v1.0 只包含 P1、P2

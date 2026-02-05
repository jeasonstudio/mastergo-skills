# 实现计划: MasterGo Claude Skills

**分支**: `001-mastergo-skill` | **日期**: 2026-01-30 | **规范**: [spec.md](./spec.md)  
**输入**: 构建 Claude Skills，通过自有 Node.js scripts 直接调用 MasterGo API

## 摘要

构建一个符合 Claude/Cursor Skills 最佳实践的 MasterGo 设计文件解析 Skill。采用自有 Node.js scripts 替代 MCP Server 依赖，通过环境变量 `MASTERGO_TOKEN` 认证，支持 DSL 获取、组件文档处理、多页面站点构建等核心功能。

## 技术上下文

**语言/版本**: Node.js 18+ (JavaScript ES2020+)  
**主要依赖**: 无外部依赖（仅使用 Node.js 内置模块 https, url）  
**存储**: 无（纯函数式工具，无状态持久化）  
**测试**: 脚本内嵌使用示例（符合宪章要求）  
**目标平台**: Claude/Cursor Agent 环境  
**项目类型**: Skill 包（文档 + 脚本）  
**性能目标**: 单次 API 调用 < 5 秒  
**约束**: 
- SKILL.md < 100 行
- 总文档 < 2000 字
- 无外部依赖

## 宪章检查

*关卡: 必须在 Phase 0 研究前通过。Phase 1 设计后复查。*

| 原则 | 状态 | 说明 |
|------|------|------|
| I. 代码质量 | ✅ 通过 | 每个 script 单一职责，无外部依赖 |
| II. 测试标准 | ✅ 通过 | 脚本内嵌使用示例，可直接验证 |
| III. 用户体验一致性 | ✅ 通过 | 统一的 JSON 输出格式，清晰的错误信息 |
| IV. 性能要求 | ✅ 通过 | 直接 HTTP 调用，无额外开销 |
| V. 语言规范 | ✅ 通过 | scripts/ 使用英文，specs/ 使用中文 |

## 项目结构

### 文档 (本功能)

```text
specs/001-mastergo-skill/
├── plan.md              # 本文件
├── research.md          # Phase 0: Skills 最佳实践研究
├── data-model.md        # Phase 1: 数据模型
├── quickstart.md        # Phase 1: 快速开始指南
└── contracts/           # Phase 1: API 契约
    └── mastergo-api.md
```

### 源代码 (仓库根目录)

```text
mastergo-skills/
├── SKILL.md                          # 主入口（< 100 行）
├── README.md                         # 安装说明
├── scripts/                          # Node.js 工具脚本
│   ├── get-dsl.cjs                  # 获取 DSL 数据
│   ├── get-component-link.cjs       # 获取组件文档
│   ├── get-meta.cjs                 # 获取站点元信息
│   ├── parse-mastergo-url.cjs       # URL 解析（已有）
│   ├── extract-component-links.cjs  # DSL 提取（已有）
│   └── README.md                    # 脚本说明
└── references/                       # 详细参考文档
    ├── get-dsl-workflow.md          # DSL 获取工作流
    ├── multi-page-workflow.md       # 多页面站点工作流
    └── dsl-structure.md             # DSL 数据结构参考
```

**结构决策**: 采用 Skills 标准结构，SKILL.md 作为简洁入口，详细内容通过渐进式披露放在 references/，脚本放在 scripts/。

## 复杂度追踪

> 无宪章违规需要说明

---

# Phase 0: 研究

## 研究任务

### R1: Claude Skills 最佳实践

**决策**: 采用渐进式披露模式

**理由**: 
- SKILL.md 保持简洁（< 100 行），符合 Skills 最佳实践的 500 行上限
- 详细工作流放在 references/，按需加载
- 脚本放在 scripts/，提供可靠的预制工具

**考虑的替代方案**:
- 全部放在 SKILL.md：违反简洁原则，token 成本高
- 多层嵌套引用：可能导致部分读取

### R2: MasterGo API 调用方式

**决策**: 使用 Node.js 原生 https 模块

**理由**:
- 零外部依赖，符合宪章"最小依赖"原则
- Node.js 18+ 内置功能足够满足需求
- 减少安装和维护成本

**考虑的替代方案**:
- axios: 需要安装依赖
- node-fetch: 需要安装依赖
- MCP SDK: 增加复杂度

### R3: 短链接解析策略

**决策**: 脚本内处理 HTTP 重定向

**理由**:
- 短链接 `/goto/{id}` 会 302 重定向到完整 URL
- Node.js https 可配置 `maxRedirects: 0` 获取 Location header
- 无需额外 API 调用

### R4: 错误处理策略

**决策**: 统一 JSON 错误格式 + 可操作建议

**理由**:
- 符合宪章"可预测的错误"要求
- 用户无需额外询问即可解决问题

**错误格式**:
```json
{
  "error": true,
  "code": "PERMISSION_DENIED",
  "message": "无权访问此文件",
  "suggestion": "请检查: 1) 账户为团队版或以上 2) 文件在团队项目中（非草稿）"
}
```

---

# Phase 1: 设计与契约

## 数据模型

见 [data-model.md](./data-model.md)

## API 契约

见 [contracts/mastergo-api.md](./contracts/mastergo-api.md)

## 快速开始

见 [quickstart.md](./quickstart.md)

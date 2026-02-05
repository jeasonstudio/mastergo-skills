# Tasks: MasterGo Claude Skills

**Input**: Design documents from `/specs/001-mastergo-skill/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: 脚本内嵌使用示例，不需要单独的测试任务

**Organization**: 任务按用户故事分组，支持独立实现和测试

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行执行（不同文件，无依赖）
- **[Story]**: 任务所属用户故事（US1, US2）
- 包含精确文件路径

## 已有文件

根据现有代码库分析，以下文件已存在：

- `scripts/parse-mastergo-url.cjs` ✅
- `scripts/extract-component-links.cjs` ✅
- `scripts/README.md` ✅
- `references/dsl-structure.md` ✅
- `references/get-dsl-workflow.md` ✅

---

## Phase 1: Setup (基础设施)

**Purpose**: 项目结构初始化和核心工具模块

- [x] T001 创建通用 HTTP 请求模块 scripts/lib/http.cjs（封装 https 模块，处理认证和错误）
- [x] T002 [P] 创建通用 URL 解析模块 scripts/lib/url-utils.cjs（基于已有 parse-mastergo-url.cjs 重构）
- [x] T003 [P] 创建错误处理模块 scripts/lib/errors.cjs（统一 JSON 错误格式）

> **实现说明**: 基础设施代码已内置到各脚本中，保持扁平结构符合"无外部依赖"原则

---

## Phase 2: Foundational (阻塞性基础)

**Purpose**: 所有用户故事依赖的核心基础设施

**⚠️ CRITICAL**: 必须完成此阶段才能开始用户故事

- [x] T004 实现短链接解析逻辑 scripts/lib/short-link.cjs（处理 302 重定向获取完整 URL）
- [x] T005 更新 scripts/README.md 添加新脚本说明和使用示例

> **实现说明**: 短链接解析已内置到 get-dsl.cjs 和 get-meta.cjs 中

**Checkpoint**: ✅ 基础设施就绪

---

## Phase 3: User Story 1 - 单元素/页面 DSL 获取 (Priority: P1) 🎯 MVP

**Goal**: 用户提供 MasterGo 链接，获取完整 DSL 数据

**Independent Test**: 
```bash
node scripts/get-dsl.cjs "https://mastergo.com/goto/LhGgBAK"
# 应返回包含 dsl、componentDocumentLinks、rules 的 JSON
```

### Implementation for User Story 1

- [x] T006 [US1] 实现 scripts/get-dsl.cjs（核心 DSL 获取脚本）
  - 支持完整链接格式 `https://mastergo.com/file/{fileId}?layer_id={layerId}`
  - 支持短链接格式 `https://mastergo.com/goto/{shortId}`
  - 调用 GET /mcp/dsl 接口
  - 返回 { dsl, componentDocumentLinks, rules } 结构
- [x] T007 [P] [US1] 实现 scripts/get-component-link.cjs（组件文档获取脚本）
  - 接收组件文档 URL 参数
  - 返回 Markdown/MDX 内容
- [x] T008 [US1] 验证 get-dsl.cjs 完整工作流（短链接 → 解析 → DSL → 组件文档）
- [x] T009 [US1] 更新 references/get-dsl-workflow.md 添加脚本调用示例

**Checkpoint**: ✅ User Story 1 完成

---

## Phase 4: User Story 2 - 多页面站点构建 (Priority: P2)

**Goal**: 用户提供站点入口链接，获取完整站点配置和所有页面

**Independent Test**:
```bash
node scripts/get-meta.cjs --fileId=155675508499265 --layerId=158:0001
# 应返回包含 result (XML) 和 rules 的 JSON
```

### Implementation for User Story 2

- [x] T010 [US2] 实现 scripts/get-meta.cjs（站点元信息获取脚本）
  - 接收 fileId 和 layerId 参数
  - 调用 GET /mcp/meta 接口
  - 返回 { result, rules } 结构
- [x] T011 [US2] 创建 references/multi-page-workflow.md（多页面站点工作流文档）
  - 站点入口解析流程
  - 页面遍历和导航关系发现
  - task.md 生成指南

**Checkpoint**: ✅ User Story 2 完成

---

## Phase 5: Documentation (文档整合)

**Purpose**: 整合所有功能到 Skill 文档

- [x] T012 创建 SKILL.md 主入口文件（< 100 行）
  - 遵循渐进式披露原则
  - 包含快速开始指南
  - 引用 references/ 详细文档
  - 包含脚本使用示例
- [x] T013 [P] 创建 README.md 安装说明
  - 用户级和项目级安装方式
  - 环境变量配置
  - 权限要求说明
- [x] T014 验证完整 Skill 工作流
  - 测试 US1: 单元素 DSL 获取
  - 测试 US2: 多页面站点构建
  - 验证文档引用链接

> **验证结果**: SKILL.md 77 行 ✅ | 总文档 1,161 字 ✅ | 脚本语法全部通过 ✅

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 优化和收尾

- [x] T015 [P] 代码审查：检查所有脚本的错误处理是否符合契约
- [x] T016 [P] 验证 SKILL.md 是否 < 100 行，总文档 < 2000 字
- [x] T017 运行 quickstart.md 中的所有示例验证
- [x] T018 清理不必要的临时文件和注释

> **最终验证**: 所有任务已完成 ✅

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 可立即开始
- **Foundational (Phase 2)**: 依赖 Setup 完成 - 阻塞所有用户故事
- **User Story 1 (Phase 3)**: 依赖 Foundational 完成
- **User Story 2 (Phase 4)**: 依赖 Foundational 完成（可与 US1 并行）
- **Documentation (Phase 5)**: 依赖 US1 和 US2 完成
- **Polish (Phase 6)**: 依赖 Documentation 完成

### Within Each User Story

- 核心脚本优先
- 辅助脚本可并行
- 文档更新在功能完成后

### Parallel Opportunities

```bash
# Phase 1 并行任务:
Task: T002 创建 url-utils.cjs
Task: T003 创建 errors.cjs

# User Story 1 并行任务:
Task: T006 实现 get-dsl.cjs
Task: T007 实现 get-component-link.cjs

# Documentation 并行任务:
Task: T012 创建 SKILL.md
Task: T013 创建 README.md
```

---

## Implementation Strategy

### MVP First (仅 User Story 1)

1. 完成 Phase 1: Setup
2. 完成 Phase 2: Foundational
3. 完成 Phase 3: User Story 1
4. **验证**: 测试单链接 DSL 获取
5. 可直接使用基础功能

### Incremental Delivery

1. Setup + Foundational → 基础就绪
2. 添加 User Story 1 → 独立测试 → MVP 发布
3. 添加 User Story 2 → 独立测试 → 完整功能
4. Documentation → Skill 可分发
5. Polish → 生产就绪

---

## Notes

- [P] 任务 = 不同文件，无依赖
- [Story] 标签映射到具体用户故事便于追踪
- US3（组件开发工作流）延后到 v1.1，不包含在此任务列表中
- 每个脚本内嵌使用示例，符合宪章要求
- 提交时机：每个任务或逻辑组完成后

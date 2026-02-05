# 快速开始: MasterGo Skills

## 安装

### 用户级安装（所有项目可用）

```bash
# 克隆到个人 skills 目录
git clone https://github.com/jeasonstudio/mastergo-skills ~/.cursor/skills/mastergo
```

### 项目级安装（仅当前项目）

```bash
# 克隆到项目 skills 目录
git clone https://github.com/jeasonstudio/mastergo-skills .cursor/skills/mastergo
```

---

## 配置

### 1. 获取 Token

1. 访问 https://mastergo.com
2. 进入 **个人设置** → **安全设置**
3. 生成 **个人访问令牌**

### 2. 设置环境变量

```bash
# 必需
export MASTERGO_TOKEN="mg_your_token_here"

# 可选（企业私有部署）
export MASTERGO_API_URL="https://your-mastergo-domain.com"
```

### 3. 权限要求

- **账户**: 团队版或更高
- **文件**: 必须在团队项目中（不能在草稿箱）

---

## 使用示例

### 获取单个元素 DSL

向 Agent 发送:
```
解析这个设计: https://mastergo.com/goto/LhGgBAK
```

Agent 将:
1. 调用 `scripts/get-dsl.cjs` 获取 DSL
2. 处理 `componentDocumentLinks`
3. 应用 `rules` 生成代码

### 构建多页面站点

向 Agent 发送:
```
根据这个设计构建完整网站: https://mastergo.com/file/155675508499265?layer_id=158:0001
```

Agent 将:
1. 调用 `scripts/get-meta.cjs` 获取站点配置
2. 解析所有页面的 DSL
3. 发现页面间导航关系
4. 生成 `task.md` 任务清单
5. 按顺序生成各页面代码

---

## 脚本直接使用

### get-dsl.cjs

```bash
# 短链接
node scripts/get-dsl.cjs "https://mastergo.com/goto/LhGgBAK"

# 完整链接
node scripts/get-dsl.cjs --fileId=155675508499265 --layerId=158:0002
```

### get-meta.cjs

```bash
node scripts/get-meta.cjs --fileId=155675508499265 --layerId=158:0001
```

### get-component-link.cjs

```bash
node scripts/get-component-link.cjs "https://example.com/ant/button.mdx"
```

---

## 常见问题

### Token 无效

```
错误: TOKEN_INVALID
```

**解决**: 在 MasterGo 个人设置 → 安全设置重新生成 Token

### 无权访问

```
错误: PERMISSION_DENIED
```

**解决**: 
1. 确认账户为团队版或以上
2. 确认文件在团队项目中（不在草稿箱）

### 短链接解析失败

```
错误: Could not extract layerId from URL
```

**解决**: 使用完整链接格式 `https://mastergo.com/file/{fileId}?layer_id={layerId}`

---

## 下一步

- 查看 [references/get-dsl-workflow.md](../../references/get-dsl-workflow.md) 了解完整工作流
- 查看 [references/dsl-structure.md](../../references/dsl-structure.md) 了解 DSL 数据结构

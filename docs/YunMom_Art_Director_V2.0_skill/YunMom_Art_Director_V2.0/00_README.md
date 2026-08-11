# YunMom Art Director 3.0

这是云妈妈项目的 Codex 视觉总监与视觉生产治理包。目录名保留 `V2.0` 仅为历史来源标识；当前内部版本为 3.0.0。

它负责：品牌与角色方向、UI/Widget、静态与动态资产、图片生成/编辑、Flutter/Rive 视觉实现、候选收敛、独立审查、Golden 版本、语义 Design Token、无障碍与敏感状态视觉门禁、真实页面证据和跨端发布边界。

## 用户需要参与什么

你只需要参与真正的创意选择：看最多三个最终候选，选择最喜欢的方向，或说一句希望改变的感受。像颜色数值、圆角、阴影、动效时长、图层和导出格式由 Codex 自主决定。

“就这个 / 定了 / 按这个继续”只会批准被点名方案的**审美 Golden**。它不会替代医学、法律、安全、工程、QA、伦理或发布签字。

## 正确安装方式

不要把整个外层文件夹继续嵌套到项目 `docs/`。把本目录中的以下内容合并到真实 YunMom 项目根：

```text
<project-root>/
├─ AGENTS.md
├─ .agents/skills/yunmom-art-director/...
├─ .codex/config.toml
├─ .codex/agents/...
└─ visual/...
```

当前 Codex 约定是：

- repo Skill：`.agents/skills/yunmom-art-director/`
- project custom agents：`.codex/agents/`
- project agent config：`.codex/config.toml`
- project instructions：根目录 `AGENTS.md`

安装后从项目根启动一个新任务或重启 Codex，让技能发现缓存重新加载。可显式说：

> 使用 $yunmom-art-director，读取当前视觉状态和工程合同，继续下一个未解决的视觉 Gate。自主完成专业微决策，只把通过内部门禁的少量候选交给我选择。

## 当前安全状态

- 冻结工程合同优先于旧产品基线与视觉偏好。
- Android 可先实现与首测，iOS 与多机证据必须在公开 Go/No-Go 前补齐。
- 无最终同构建七方签字时，状态始终是 `RELEASE_NOT_APPROVED`。
- 本包不能数学保证“完美审美”；它通过收敛、证据、独立审查和不可豁免门禁最大化稳定质量，并诚实保留专业签字边界。

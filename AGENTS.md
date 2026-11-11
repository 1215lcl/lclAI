# lclAI 项目协作规则

## 语言与沟通

- 默认使用简体中文进行沟通、说明、评审结论和项目文档编写。
- 代码标识符、协议字段、库名、命令、日志原文以及 OpenSpec 的结构标题和 `SHALL`、`MUST` 等规范关键词保留英文。
- 提交说明优先使用简洁中文；若现有提交历史形成其他约定，则遵循已有约定。
- 需求不明确时，先澄清会影响架构、交易安全或验收结果的问题，再开始实现。

## 项目范围

- 本项目从零建设 AI 量化交易系统，包括用户界面、Python 后端、策略研究与回测，以及 QMT 自动交易接入。
- 优先建立可测试、可审计、可替换的领域边界，避免界面、策略逻辑与 QMT SDK 直接耦合。
- 默认以模拟、回放或仿真环境验证；实盘交易能力必须作为独立变更设计和审批。

## OpenSpec 是需求事实来源

- 任何非微小功能、架构调整、跨模块修改或交易行为变化，都应先建立 OpenSpec change。
- `openspec/specs/` 描述系统当前正式行为，是需求事实来源。
- `openspec/changes/<change-id>/` 保存进行中的 proposal、delta specs、design 和 tasks。
- 不在实现过程中私自改变已批准需求；发现方案有误时，先更新 OpenSpec artifacts，再继续实现。
- OpenSpec artifacts 使用简体中文书写，但保留官方要求的英文结构标题和规范关键词。

## 标准变更流程

1. 在 `main` 分支执行 Explore 和 Propose。
2. 人工审阅并确认 proposal、specs、design 和 tasks。
3. 在 `main` 提交提案，使其他进行中的变更可见。
4. 每个 change 创建独立分支和 Git worktree，在对应 worktree 中 Apply。
5. 在同一 worktree 中完成测试、代码审查和 OpenSpec Verify。
6. Verify 通过后，由协调者将实现合并回 `main`。
7. 合并完成后，才允许在 `main` 执行 Sync/Archive 并提交归档结果。
8. 确认分支已合并且无需保留后，再清理 worktree。

禁止在实现分支提前 Archive，也禁止在未合并实现时更新 `main` 的正式 specs。

## Git 与 Worktree 纪律

- `main` 只接受基线治理提交、已批准的 OpenSpec 提案、已验证实现的合并和归档提交。
- 一个 OpenSpec change 对应一个实现分支和一个 worktree。
- 分支建议命名为 `change/<change-id>`；worktree 目录名与 change ID 保持一致。
- 同一个 worktree 同一时间只能有一个主要写入 Agent。
- 提交应保持小而完整，不混入无关格式化、重构或其他 change 的内容。
- 不覆盖用户已有修改，不使用破坏性 Git 命令；发现重叠修改时先停止并说明。
- 未经用户明确要求，不执行 push、强制推送、删除远端分支、合并 PR 或发布操作。

## Multi-Agent 协作

- Root/Coordinator 负责拆分任务、分派 worktree、汇总结果、控制合并顺序和执行 Archive。
- Spec Agent 负责需求澄清、OpenSpec artifacts 和验收标准，不代替实现验收。
- Implementer Agent 只在被分配的 change/worktree 中写入，按 tasks 实现并提供验证证据。
- Spec Reviewer 检查实现是否满足 proposal、specs、design 和 tasks。
- Quality Reviewer 检查正确性、可维护性、安全性、测试覆盖和回归风险。
- 实现者不能作为唯一审查者；关键交易功能至少经过规格符合性和代码质量两类审查。
- 只有边界清晰、互不写同一可变文件的任务才并行；共享接口未确定前先串行完成契约设计。
- Agent 交接必须包含 change ID、worktree/分支、已完成任务、测试结果、遗留问题和风险。

## 实现与验证要求

- 优先采用测试驱动：先建立失败测试，再做最小实现，最后重构。
- Python 后端、前端、策略/回测和 QMT 适配层应通过明确接口解耦。
- 完成声明必须附带实际执行过的测试、静态检查或构建结果；不得用“应该通过”代替证据。
- 修复缺陷前先定位根因，并增加能够复现问题的测试。
- 若环境、依赖或外部服务导致无法验证，明确列出未验证部分及其影响。

## QMT 与交易安全

- QMT SDK 通过独立适配层接入，领域逻辑不得依赖其具体对象结构。
- 模拟、仿真和实盘环境必须显式隔离，默认不得连接或下单到实盘环境。
- 实盘相关变更必须覆盖幂等下单、重复事件、断线重连、状态恢复、撤单、部分成交和审计日志。
- 风控规则、账户权限、密钥处理、最大仓位、最大损失、交易时段和紧急停止机制必须具有可测试验收标准。
- 未经用户明确授权，不发送真实订单，不修改真实账户配置，不记录或提交敏感凭据。

## 完成标准

一个 change 只有在以下条件全部满足时才可申请合并：

- OpenSpec tasks 已完成且与实际实现一致。
- 相关测试、静态检查和构建通过。
- OpenSpec Verify 未发现阻塞问题。
- Spec Review 与 Quality Review 的阻塞问题已解决。
- 文档、配置和迁移说明已同步。
- 没有敏感信息、临时调试代码或未解释的生成文件进入提交。

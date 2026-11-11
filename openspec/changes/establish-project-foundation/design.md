# Design

## Context

参见 `proposal.md` 的 Why。本仓库目前没有业务代码，目标运行形态是个人使用的本地单机量化工作台：Mac 可用于开发，正式工作台优先运行于 Windows；当前没有可用的 QMT/MiniQMT 环境，因此基础架构必须在没有 QMT SDK、真实账户和外部 API Key 时完整启动并可测试。

本 change 只建立应用骨架和质量门禁。已确认的完整首期产品路线图记录在本文末尾，后续功能必须分别通过独立 OpenSpec change 实现，不能由本 change 提前宣称可用。

## Goals / Non-Goals

**Goals:**

- 建立 React 本地 Web 工作台与 FastAPI 后端的最小可运行闭环。
- 建立模块化单体的依赖方向、配置加载、健康检查和 Provider 状态模型。
- 默认仅监听本机回环地址，并在外部集成缺失时安全降级。
- 建立可在 Mac 开发、并在 Windows CI 验证的依赖锁定和质量门禁。
- 让后续能力通过稳定边界接入，而不是直接依赖供应商 SDK 或 UI 组件。

**Non-Goals:**

- 不实现真实 AI 调用、RAG 检索、行情接入、策略执行、回测、新闻抓取、舆情速递、订单或 QMT 接入。
- 不实现实盘交易、多用户、远程访问、后台自主 AI 或自动 Provider 故障切换。
- 不为尚未开始的功能创建大量空业务类；只建立当前规格需要的最小契约。
- 不锁定 QMT Python 版本、向量数据库或新闻供应商。

## Decisions

### 1. 采用前后端分离的模块化单体仓库

建议目录边界：

```text
backend/
  src/lclai/
    api/
    core/
    providers/
  tests/
frontend/
  src/
  tests/
openspec/
.github/workflows/
```

开发模式由 Vite 与 FastAPI 分别运行；发布模式将前端构建产物作为本地工作台静态资源提供，保持一次启动、一个本机入口。模块间通过 Python/TypeScript 契约和 API schema 交互，不拆分微服务。

选择该方案是因为单用户本地应用不需要分布式部署成本，同时仍能保持前端、应用服务和外部 Adapter 的边界。备选方案 Electron/PySide 暂不采用；需要系统托盘或原生窗口能力时再单独评估桌面壳。

### 2. 技术基线与依赖锁定

- 前端采用 React、TypeScript、Vite；使用严格 TypeScript、组件测试和生产构建检查。
- 后端采用 FastAPI、Pydantic；使用 pytest、Ruff 和静态类型检查。
- Python 使用独立虚拟环境和锁文件；Node 依赖使用锁文件。实现时选择仍受支持的稳定版本并在 CI 固定。
- 应用状态使用 SQLite；后续大体量行情和回测数据使用 Parquet + DuckDB，但不在本 change 建表或实现查询。
- API 以 `/api/v1` 为版本前缀，至少提供存活、就绪和 Provider 状态端点。

选择成熟的 Web/Python 组合是为了复用量化和数据分析生态，并使 Windows 运行与 Mac 开发保持一致。备选方案全 Python UI 会降低前端工程复杂度，但不利于后续实时状态、复杂图表和可维护交互。

### 3. 默认本地访问与安全启动

后端默认绑定 `127.0.0.1`，前端只访问同一本机 API。开发环境可以为 Vite 配置明确的本机 CORS 来源，但不得默认开放任意来源。

启动过程分为：

```text
加载非敏感配置
      |
校验核心本地目录和 SQLite
      |
注册 Provider 描述与状态
      |
启动 API 和工作台
      |
可选 Provider 独立检查，不阻塞核心启动
```

没有 API Key、QMT SDK 或外部网络时，核心应用仍启动；相关 Provider 标记为 `unconfigured`、`unavailable` 或 `mock`。不得使用假数据伪装真实外部能力。

### 4. Provider Registry 只建立最小通用契约

基础层定义 Provider 类型、非敏感配置、状态和健康摘要，而不提前抽象所有未来业务方法。

```text
Provider Registry
├── model: OpenAI / Volcengine Ark
├── market-data
├── news
├── vector-store
└── trading-gateway: Mock / QMT
```

Provider 状态统一为 `unconfigured`、`available`、`unavailable`、`mock`。任务必须显式选择 Provider；失败只返回结构化错误，不自动把原始请求发送给其他 Provider。

模型层后续通过 `ModelGateway` 接入 OpenAI 与火山方舟。火山方舟首选 OpenAI-compatible 数据面接口，方舟特有能力需要时再新增原生 Adapter。模型标识、超时和重试可配置，具体模型版本不写死。

### 5. 秘密信息与审计分离

基础实现先支持从环境变量读取秘密信息，并预留本机安全凭据存储 Adapter。普通配置和 SQLite 只保存秘密引用或“是否存在”的状态，不保存明文秘密。

日志与 API 响应通过统一脱敏函数处理常见 API Key、Token 和 Authorization 字段。配置变更审计仅记录 Provider、模型标识、超时、重试等非敏感摘要。

### 6. 健康模型区分存活、就绪和可选能力

- `live`：进程和 API 事件循环可响应。
- `ready`：核心配置、SQLite 和工作台资源可用。
- Provider 状态：每项外部能力独立报告，不影响无关核心功能。

总览页只展示真实状态。尚未由后续 change 实现的功能区显示“尚未实现”，不提供可执行按钮。

### 7. CI 与本地验证使用同一组核心命令

CI 至少包含：

- 后端格式/静态检查、类型检查和 pytest。
- 前端 lint、类型检查、组件测试和生产构建。
- `openspec validate --all --strict --no-interactive`。
- Windows 与 Unix 类环境的核心 Python 契约、配置和启动检查。

外部服务使用 Mock，CI 不注入真实模型、新闻、行情或交易凭据。GitHub required checks 由仓库设置启用，失败检查不得合并。

### 8. 完整首期产品架构作为后续路线图

后续目标架构：

```text
React Local Workbench
        |
        v
FastAPI Application Services
        |
        +--> AI Chat Orchestrator
        |      +--> PortfolioTool (read-only)
        |      +--> MarketDataTool (read-only)
        |      +--> NewsTool (read-only)
        |      +--> StrategyTool (read-only)
        |      +--> RiskTool (read-only)
        |
        +--> Market Data + Backtest
        +--> Knowledge / Skill / RAG
        +--> Market Briefing
        +--> Portfolio + Deterministic Risk
        +--> Trading Plan
        |
        v
TradingGateway: Mock first, QMT simulation later
```

后续 change 建议顺序：

1. `define-quant-domain-contracts`：标的、行情、信号、策略、组合、交易计划、风控、订单、成交和持仓。
2. `build-historical-data-and-backtest`：A 股 CSV/Parquet 导入、标准化、DuckDB 查询、Python 策略插件和可复现回测。
3. `add-realtime-a-share-market-data`：自选股与策略股票池的快照、tick、1 分钟线、断线补齐和 WebSocket 推送。
4. `add-knowledge-and-skill-registry`：导入 SKILL.md、Markdown/PDF/DOCX/TXT/HTML，默认不可信、只读启用和权限审批。
5. `evaluate-local-rag-store`：对比 SQLite FTS5 + Qdrant Local 与 LanceDB Embedded，按中文检索、更新删除、Windows 打包和重建能力定案。
6. `build-ai-research-chat`：OpenAI/火山方舟显式选择，结合只读工具与 RAG 分析持仓、行情、策略和新闻，可生成待审核交易计划但不可下单。
7. `add-market-briefing`：国内/国际切换；应用会话首次打开刷新、手动刷新；已发生 24 小时、未来 7 天默认窗口；官方源优先、新闻补充、RAG 只做背景。
8. `add-mock-paper-trading-and-risk`：Mock 账户、订单和成交，默认拒绝的确定性风控、审计和紧急停止。
9. `integrate-qmt-simulation`：获得 Windows QMT/MiniQMT 与仿真账户后实现 Adapter、状态恢复、幂等、部分成交和断线重连。
10. 实盘交易必须另建独立 change，不得由仿真 change 顺带开启。

### 9. 已确认的后续安全边界

- AI 对话由用户显式触发；实时行情不得自动唤醒 AI 形成后台自主循环。
- AI 只读取持仓、行情、新闻、策略、回测和风控结果；不能修改风控或直接调用交易网关。
- Python 策略插件只产生信号；AI 生成代码先隔离并通过检查、测试、回测和人工确认。
- 确定性风控位于 AI 与 TradingGateway 之间，缺少行情、持仓或账户状态时默认拒绝。
- Skill 导入后默认不可信、只读、无 shell/文件写入/网络/账户/QMT 权限；工具权限单独审批。
- RAG 默认使用本地 Embedding；云端 Embedding 必须显式授权并最小化发送内容。
- 舆情速递区分事实、已公布日程、AI 推断和不确定性，并保留来源、发布时间和抓取时间。

## Risks / Trade-offs

- [风险] 基础 change 预留过多无实现价值的接口 → 只实现状态与配置所需最小契约，具体业务接口随对应 change 引入。
- [风险] Mac 开发通过但 Windows 路径或进程行为失败 → CI 增加 Windows 核心矩阵，并避免 Unix 专有脚本作为唯一入口。
- [风险] 前后端分离增加初始工具链 → 发布模式合并为单一本地入口，并提供统一验证命令。
- [风险] 环境变量使用方便但长期秘密管理体验有限 → 当前满足安全基线，后续增加 Windows Credential Manager/系统 Keychain Adapter。
- [风险] Provider 健康检查可能触发收费调用 → 基础健康检查只验证配置与非收费连接能力，真实调用由用户显式触发。
- [风险] 路线图被误认为当前已实现 → 总览、文档和 specs 必须明确区分 `implemented`、`unconfigured`、`mock` 与 `not-implemented`。

## Migration Plan

1. 在独立 worktree 建立前后端最小工程与锁文件。
2. 先建立后端配置、健康端点和单元测试，再建立工作台壳层。
3. 接入 SQLite 基础启动检查和 Provider 状态模型。
4. 添加本地验证入口和 GitHub Actions，确保 Windows 与 Unix 类环境通过。
5. 在 Verify 通过后合并到 `main`，再同步并归档 OpenSpec change。

回滚时删除本 change 新增的应用骨架与 CI 文件即可；当前没有业务数据迁移。若依赖安装或跨平台验证失败，保持 OpenSpec artifacts，不合并实现分支。

## Open Questions

- QMT/MiniQMT 的具体版本、Python 兼容性和仿真账户能力，等实际 Windows 环境可用后确认。
- 本地 RAG 最终采用 Qdrant Local 还是 LanceDB，由后续可重复技术验证决定。
- 国内外新闻与日程的具体 Provider 清单、授权和抓取策略，在 `add-market-briefing` change 中确认。
- 依赖的精确版本在 Apply 时依据官方受支持版本锁定，不改变本文的架构边界。

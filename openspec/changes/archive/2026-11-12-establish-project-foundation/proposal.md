# Proposal

## Why

项目目前只有 OpenSpec 与协作规则，尚无可运行的应用骨架、稳定的模块边界和自动质量门禁。需要先建立一个安全、可测试、可扩展的本地单机工作台基础，为后续行情、策略、AI、RAG、舆情和仿真交易能力提供统一承载面。

## What Changes

- 建立面向个人使用的本地 Web 工作台骨架，采用模块化单体结构，并提供前后端健康状态与基础导航。
- 建立配置与 Provider 边界，统一管理模型、行情、新闻、向量存储和交易网关等可替换集成。
- 默认使用安全的本地或 Mock 实现；没有 QMT 环境时不得依赖 QMT SDK，也不得宣称真实交易接入可用。
- 建立 Python 与前端的测试、静态检查、构建和 GitHub CI 门禁。
- 记录首期产品路线图和已确认的架构约束，但不在本 change 中实现 AI 对话、实时行情、策略回测、RAG、舆情速递或 QMT 交易功能。
- 实盘交易、多用户、远程访问、后台自主 AI 和自动切换模型 Provider 明确不在范围内。

## Capabilities

### New Capabilities

- `local-workbench-foundation`: 本地单用户 Web 工作台的启动、健康状态、基础导航和安全降级行为。
- `provider-configuration`: 可替换 Provider 的显式配置、密钥处理、状态展示与禁止静默切换规则。
- `quality-gates`: 项目的自动测试、静态检查、构建验证和主干合并门禁。

### Modified Capabilities

无。

## Impact

- 将新增前端、Python 后端、共享契约、测试和 CI 的基础目录与配置。
- 将引入 React、TypeScript、Vite、FastAPI、Pydantic 及相应质量工具；具体版本在实现时锁定并记录。
- 将为 SQLite、DuckDB/Parquet、OpenAI、火山方舟、新闻源、向量存储和 Trading Gateway 预留接口边界，但本 change 不接入真实外部账户或交易环境。
- 主要风险是过早搭建过多空接口、Windows 与 Mac 开发差异以及依赖版本不兼容；通过最小骨架、契约测试和 Windows 验证任务控制风险。

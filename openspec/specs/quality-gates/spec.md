# quality-gates Specification

## Purpose

为 AI 与人工提交提供可重复执行的自动验证和合并阻断机制，使每次变更都以测试、静态检查、构建和规格校验结果作为完成证据。

## Requirements

### Requirement: 本地等价验证
项目 SHALL 提供文档化的本地验证入口，覆盖 Python、前端、构建和 OpenSpec 校验，并与 CI 使用相同的核心检查。

#### Scenario: 开发者运行完整验证
- **WHEN** 开发者在受支持的环境运行完整验证入口
- **THEN** 系统 SHALL 依次报告所有检查的成功或失败，并以非零状态表示任一检查失败

#### Scenario: 单独验证子项目
- **WHEN** 开发者只修改 Python 或前端子项目
- **THEN** 项目 SHALL 允许单独运行对应测试、静态检查和构建验证

### Requirement: 自动 CI 检查
仓库 SHALL 在 Pull Request 和主干变更上自动运行后端测试与静态检查、前端测试与构建以及 OpenSpec 严格校验。

#### Scenario: Pull Request 提交变更
- **WHEN** Pull Request 创建或更新
- **THEN** CI SHALL 自动运行规定检查并发布每项检查结果

#### Scenario: 主干收到提交
- **WHEN** 变更进入 `main`
- **THEN** CI SHALL 再次运行规定检查以验证主干状态

### Requirement: 失败阻断
任何必需检查失败时，变更 MUST 不满足合并条件，且失败信息 SHALL 能定位到具体检查和日志。

#### Scenario: 测试失败
- **WHEN** 一个必需测试、静态检查、构建或规格校验失败
- **THEN** Pull Request SHALL 显示失败状态并不得被视为可合并

#### Scenario: 修复后重新验证
- **WHEN** 开发者提交针对失败的修复
- **THEN** CI SHALL 重新运行检查，并仅在全部必需检查通过后报告成功

### Requirement: 无秘密的确定性测试
自动测试 MUST 不依赖真实账户、QMT、付费 API 或开发者本机秘密信息，并 SHALL 使用 Mock 或隔离测试资源。

#### Scenario: CI 无外部凭据
- **WHEN** CI 在没有模型、新闻、行情或交易凭据的环境运行
- **THEN** 所有基础检查 SHALL 能完成，外部能力测试 SHALL 使用 Mock

#### Scenario: 外部服务不可达
- **WHEN** 测试环境无法访问外部服务
- **THEN** 基础测试结果 SHALL 不受影响，且不得尝试真实下单或收费调用

### Requirement: 跨平台基础验证
项目 SHALL 至少在 Windows 和一个 Unix 类 CI 环境验证核心 Python 契约、配置加载和应用启动检查。

#### Scenario: Windows 验证
- **WHEN** CI 在 Windows 环境执行核心验证
- **THEN** 系统 SHALL 验证路径、配置和启动行为不依赖 Unix 专有语义

#### Scenario: Unix 类环境验证
- **WHEN** CI 在 Unix 类环境执行核心验证
- **THEN** 系统 SHALL 验证开发和测试流程可以在非 Windows 环境完成

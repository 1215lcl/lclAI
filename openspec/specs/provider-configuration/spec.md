# provider-configuration Specification

## Purpose

为模型、行情、新闻、向量存储和交易等外部能力提供一致、可审计且安全的配置行为，确保用户明确知道当前选择和可用状态。

## Requirements

### Requirement: 显式 Provider 选择
系统 SHALL 要求用户或任务配置明确选择 Provider，不得根据不可见规则自动选择外部服务。

#### Scenario: 选择模型 Provider
- **WHEN** 用户为任务选择 OpenAI 或火山方舟 Provider
- **THEN** 系统 SHALL 使用该 Provider，并在任务状态和结果中显示 Provider 与模型标识

#### Scenario: 未选择 Provider
- **WHEN** 某项需要外部能力的操作没有有效 Provider 配置
- **THEN** 系统 SHALL 拒绝启动该操作并说明缺失配置

### Requirement: 禁止静默切换
系统 MUST 不得在 Provider 请求失败时静默切换到另一个 Provider。

#### Scenario: 已选模型调用失败
- **WHEN** 已选择的模型 Provider 返回错误或超时
- **THEN** 系统 SHALL 保留失败结果并让用户决定重试或更换 Provider

#### Scenario: 备用 Provider 已配置
- **WHEN** 主 Provider 失败且系统中存在另一个可用 Provider
- **THEN** 系统 MUST 不自动向备用 Provider 发送原请求

### Requirement: 凭据安全
系统 MUST 从环境变量或本机安全凭据存储读取秘密信息，并不得把明文秘密写入版本库、普通配置文件、日志或界面响应。

#### Scenario: 显示 Provider 配置
- **WHEN** 用户查看已配置 Provider
- **THEN** 系统 SHALL 仅显示凭据是否存在，不得返回完整凭据内容

#### Scenario: 记录调用错误
- **WHEN** Provider 调用失败并写入日志
- **THEN** 系统 MUST 对 API Key、Token 和其他秘密信息进行移除或遮蔽

### Requirement: Provider 状态可见
系统 SHALL 区分未配置、可用、不可用和 Mock 状态，并提供不包含秘密信息的诊断说明。

#### Scenario: 未配置外部集成
- **WHEN** 用户打开系统总览或设置
- **THEN** 系统 SHALL 显示每类 Provider 的当前状态及必要的配置提示

#### Scenario: Provider 健康检查失败
- **WHEN** Provider 健康检查失败
- **THEN** 系统 SHALL 显示失败时间和可安全公开的原因，同时保持无关核心功能可用

### Requirement: 配置变更可追踪
系统 SHALL 记录 Provider 类型、非敏感配置摘要、变更时间和变更结果，不得在审计记录中保存秘密值。

#### Scenario: 更新模型配置
- **WHEN** 用户更改 Provider、模型标识、超时或重试设置
- **THEN** 系统 SHALL 记录变更后的非敏感摘要并使后续任务使用新配置

#### Scenario: 无效配置
- **WHEN** 用户保存缺少必要字段或格式无效的 Provider 配置
- **THEN** 系统 SHALL 拒绝保存并返回可定位字段的校验错误

# Spec Delta

## Purpose

为个人量化工作台提供可安全启动、仅限本机访问、能够展示自身健康状态并在外部集成缺失时保持可诊断的基础运行能力。

## ADDED Requirements

### Requirement: 本地单用户访问
系统 SHALL 默认仅监听本机回环地址，并为单个本地用户提供 Web 工作台入口。

#### Scenario: 默认启动工作台
- **WHEN** 用户使用默认配置启动应用
- **THEN** Web 工作台仅能从运行应用的本机访问

#### Scenario: 外部设备尝试连接
- **WHEN** 其他设备尝试通过局域网地址访问默认启动的应用
- **THEN** 系统 MUST 不对该地址提供服务

### Requirement: 基础健康状态
系统 SHALL 提供可供界面和自动检查读取的健康状态，区分应用存活、核心存储就绪和可选 Provider 状态。

#### Scenario: 核心组件正常
- **WHEN** 前端、后端和核心本地存储均可用
- **THEN** 系统 SHALL 报告核心服务就绪

#### Scenario: 可选 Provider 不可用
- **WHEN** 一个模型、行情、新闻、向量存储或交易 Provider 未配置或连接失败
- **THEN** 系统 SHALL 标记该 Provider 不可用，并保持核心工作台可访问

### Requirement: 安全降级启动
系统 MUST 在缺少外部 API Key、QMT SDK 或真实交易环境时使用禁用状态或明确的本地 Mock 边界，不得伪装外部能力已经可用。

#### Scenario: 未配置模型凭据
- **WHEN** 用户在没有模型 API Key 的情况下启动应用
- **THEN** 系统 SHALL 正常启动并明确显示模型能力未配置

#### Scenario: 没有 QMT 环境
- **WHEN** 应用运行环境中不存在 QMT SDK 或可用账户
- **THEN** 系统 SHALL 保持交易集成为不可用或 Mock 状态，且不得发送任何真实订单

### Requirement: 基础功能导航
系统 SHALL 提供稳定的工作台壳层，使用户能够访问总览和设置，并识别后续能力的可用、未配置或尚未实现状态。

#### Scenario: 打开总览
- **WHEN** 用户打开工作台
- **THEN** 系统 SHALL 展示核心服务状态、Provider 状态和当前安全模式

#### Scenario: 访问未实现能力
- **WHEN** 用户选择尚未由后续 change 实现的功能区
- **THEN** 系统 SHALL 明确显示尚未实现，不得展示伪造数据或可执行操作

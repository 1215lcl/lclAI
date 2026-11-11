# lclAI 后端

后端采用 FastAPI、Pydantic Settings 与 SQLite，默认不依赖任何外部模型、新闻、行情、向量库或 QMT 凭据即可启动。

## 配置方式

配置从环境变量读取，变量统一使用 `LCLAI_` 前缀。开发时可以复制 `.env.example` 为 `.env`；`.env` 已被 Git 忽略，禁止提交真实 API Key、Token 或 Authorization 值。

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `LCLAI_HOST` | `127.0.0.1` | 后端监听地址，只允许 IPv4/IPv6 回环地址 |
| `LCLAI_PORT` | `8000` | 后端端口 |
| `LCLAI_DATA_DIR` | `data` | SQLite 等本机运行状态目录 |
| `LCLAI_OPENAI_API_KEY` | 空 | OpenAI 凭据，仅从环境变量读取 |
| `LCLAI_OPENAI_MODEL_ID` | 空 | 用户显式配置的 OpenAI 模型标识 |
| `LCLAI_OPENAI_BASE_URL` | 官方 API 地址 | OpenAI-compatible 数据面地址 |
| `LCLAI_ARK_API_KEY` | 空 | 火山方舟凭据，仅从环境变量读取 |
| `LCLAI_ARK_MODEL_ID` | 空 | 用户显式配置的方舟 Endpoint/模型标识 |
| `LCLAI_ARK_BASE_URL` | 方舟 API 地址 | 火山方舟 OpenAI-compatible 数据面地址 |
| `LCLAI_MODEL_TIMEOUT_SECONDS` | `60` | 模型调用超时基线，本阶段不发起调用 |
| `LCLAI_MODEL_MAX_RETRIES` | `2` | 所选 Provider 自身重试次数，不代表切换 Provider |

## Provider 状态

- `unconfigured`：缺少必要配置，不会尝试外部连接。
- `available`：配置和非收费健康检查通过。
- `unavailable`：已配置但当前不可用；不会阻塞无关核心功能。
- `mock`：明确的模拟实现，不会伪装成真实服务。

模型任务必须显式选择 OpenAI 或火山方舟。所选 Provider 失败时系统保留失败结果，不会把原请求静默发送给另一个 Provider。

## 安全限制

- 服务默认且强制绑定本机回环地址。
- API Key 不写入普通配置、SQLite、日志或界面响应。
- 日志和响应通过统一脱敏工具遮蔽 API Key、Token 与 Authorization。
- 配置审计只保存 Provider、模型标识、地址、超时、重试和凭据是否存在等非敏感摘要。
- 本阶段不连接实盘 QMT、不发送真实订单，也不实现真实模型调用。

启动、测试、检查和构建统一使用仓库根目录的 `scripts/project.py`，具体命令见根目录 `README.md`。

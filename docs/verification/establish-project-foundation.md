# establish-project-foundation 验证记录

日期：2026-11-12

## 本地完整验证

命令：

```bash
python3 scripts/project.py verify
```

结果：

- Ruff：通过
- mypy 严格模式：通过
- pytest：26 项通过
- 前端 oxlint：通过
- TypeScript 严格类型检查：通过
- Vitest：15 项通过
- Vite 生产构建：通过
- `openspec validate --all --strict --no-interactive`：通过

失败传播验证：使用仅返回退出码 `23` 的临时 `uv` 桩执行同一入口，根命令立即停止并返回 `23`。

## 无凭据启动冒烟

在移除 OpenAI、火山方舟等环境凭据且不安装 QMT SDK 的环境中启动后端：

- `/` 返回生产工作台 HTML。
- `/api/v1/health/ready` 返回 `200`，核心配置与 SQLite 均为 `ready`。
- OpenAI、火山方舟、行情、新闻、向量存储和 QMT 均报告 `unconfigured`。
- 未发起真实模型、新闻、行情、QMT 或交易调用。

## 敏感信息与生成文件检查

- Git 忽略规则覆盖 `.env`、运行数据、SQLite、缓存、虚拟环境、`node_modules` 和构建产物。
- 秘密格式扫描只命中脱敏单元测试中的虚构值。
- 已删除未引用的 Vite 示例图片与图标。
- `.env.example` 中的凭据字段为空，并由测试执行配置校验。

## GitHub 验证（待完成）

以下证据必须在分支推送并创建 Pull Request 后补充：

- `Backend Quality`
- `Frontend Quality`
- `OpenSpec Quality`
- `Platform Contracts (ubuntu-latest)`
- `Platform Contracts (windows-latest)`
- `main` required checks 读取验证

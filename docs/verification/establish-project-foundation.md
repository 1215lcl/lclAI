# establish-project-foundation 验证记录

日期：2026-11-12

## 本地完整验证

命令：

```bash
env PATH=/Users/lcl0229/.nvm/versions/node/v22.23.2/bin:/Users/lcl0229/.local/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin python3 scripts/project.py verify
```

执行环境：Node.js `22.23.2`（项目要求 Node.js 22 或更高版本）、Python `3.12.14`。

结果：

- Ruff：通过
- mypy 严格模式：通过
- pytest：28 项通过
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

## GitHub 验证

Pull Request：[1215lcl/lclAI#1](https://github.com/1215lcl/lclAI/pull/1)

GitHub Actions 运行：[Quality Gates #43131304733](https://github.com/1215lcl/lclAI/actions/runs/43131304733)

- `Backend Quality`：通过
- `Frontend Quality`：通过
- `OpenSpec Quality`：通过
- `Platform Contracts (ubuntu-latest)`：通过
- `Platform Contracts (windows-latest)`：通过

通过 GitHub Branch Protection 读取接口回读确认：

- `main.required_status_checks.strict` 为 `true`。
- 上述五个检查均登记为 required checks，并绑定 GitHub Actions App。
- `allow_force_pushes` 与 `allow_deletions` 均为 `false`。
- 因此 required check 缺失或失败时，GitHub 不允许通过受保护分支规则完成合并。
- 五项检查成功后，PR #1 的 `mergeStateStatus` 为 `CLEAN`、`mergeable` 为 `MERGEABLE`。

## 最终变更扫描

- `git diff --check main...HEAD`：通过。
- 已跟踪文件扫描只发现预期的 `backend/.env.example`，未发现 `.env`、SQLite、运行数据库、`node_modules`、`dist`、虚拟环境或缓存被提交。
- 变更不包含真实模型、新闻、行情、QMT 或交易调用；测试使用虚构或脱敏凭据。
- 未发现临时调试代码或未解释的生成文件。

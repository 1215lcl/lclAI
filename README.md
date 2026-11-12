# lclAI

lclAI 是一个仅供个人本机使用的 A 股 AI 量化工作台。本阶段只建立安全、可验证的工程基础，不连接实盘 QMT，不发送真实订单，也不调用真实模型、新闻或行情服务。

## 环境要求

- Python 3.12 或 3.13
- [uv](https://docs.astral.sh/uv/)
- Node.js 22 或更高版本
- OpenSpec CLI

所有根命令由 `scripts/project.py` 统一调度。macOS/Linux 使用 `python3`，Windows 使用 `py`；其余参数完全一致。

## 初始化

```bash
python3 scripts/project.py setup
```

Windows：

```powershell
py scripts/project.py setup
```

## 本地启动

分别打开两个终端：

```bash
python3 scripts/project.py dev-backend
python3 scripts/project.py dev-frontend
```

后端默认监听 `http://127.0.0.1:8000`，前端地址由 Vite 输出。服务只绑定本机回环地址。

## 测试、检查与构建

```bash
python3 scripts/project.py test
python3 scripts/project.py check
python3 scripts/project.py verify
python3 scripts/project.py build
```

- `test`：运行后端测试和前端组件测试。
- `check`：运行 Python lint/类型检查、前端 lint/类型检查和 OpenSpec 严格校验。
- `verify`：运行后端与前端的全部 lint、类型检查、测试、前端生产构建和 OpenSpec 严格校验；提交前与 CI 使用此入口。
- `build`：构建 Python wheel/sdist 和前端生产包。

项目命令使用仓库内 `.cache/` 保存工具缓存；运行数据、构建产物和秘密文件不会提交到 Git。

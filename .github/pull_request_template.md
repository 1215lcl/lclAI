## OpenSpec change

<!-- 填写 change 名称和 proposal/spec/design/tasks 链接。 -->

- Change：

## 变更范围

<!-- 说明本 PR 实际完成的内容，并与 tasks 勾选项对应。 -->

## 验证命令与结果

```text
python3 scripts/project.py verify
```

<!-- 粘贴结果摘要；不得只写“已测试”。 -->

## 明确未改动范围

<!-- 说明刻意没有实现、没有重构或没有连接的能力。 -->

## 风险与回滚

<!-- 包括配置、数据、凭据、外部调用、QMT/交易、兼容性和回滚方式。 -->

## 安全检查

- [ ] 没有提交真实 API Key、Token、Authorization 或本地秘密文件
- [ ] 没有未经批准连接实盘 QMT 或发送真实订单
- [ ] 外部 Provider 失败不会静默切换或阻塞无关核心功能
- [ ] OpenSpec tasks 已与实际实现同步
- [ ] Verify 证据已记录

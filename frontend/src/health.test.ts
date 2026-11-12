import { describe, expect, it } from 'vitest'

import { mapHealthSummary, providerStatusLabel } from './health'


describe('健康状态映射', () => {
  it('将核心就绪和本机安全模式映射为明确文案', () => {
    const summary = mapHealthSummary({
      status: 'ready',
      core: { configuration: 'ready', storage: 'ready' },
      safe_mode: 'local_only',
      detail: '核心本地服务已就绪',
    })

    expect(summary.coreLabel).toBe('核心服务就绪')
    expect(summary.storageLabel).toBe('SQLite 已就绪')
    expect(summary.safeModeLabel).toBe('本机安全模式')
  })

  it('区分核心未就绪与四种 Provider 状态', () => {
    const summary = mapHealthSummary({
      status: 'not_ready',
      core: { configuration: 'ready', storage: 'not_ready' },
      safe_mode: 'local_only',
      detail: 'storage_initialization_failed',
    })

    expect(summary.coreLabel).toBe('核心服务未就绪')
    expect(summary.storageLabel).toBe('SQLite 未就绪')
    expect(providerStatusLabel.unconfigured).toBe('未配置')
    expect(providerStatusLabel.available).toBe('可用')
    expect(providerStatusLabel.unavailable).toBe('不可用')
    expect(providerStatusLabel.mock).toBe('Mock')
  })
})

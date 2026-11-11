import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { AppRoutes } from './App'


describe('工作台主导航', () => {
  it('支持鼠标从总览进入设置', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppRoutes />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: '工作台总览' })).toBeInTheDocument()
    await user.click(screen.getByRole('link', { name: '设置' }))

    expect(screen.getByRole('heading', { name: '设置' })).toBeInTheDocument()
  })

  it('支持键盘聚焦并打开设置', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppRoutes />
      </MemoryRouter>,
    )

    await user.tab()
    await user.tab()
    expect(screen.getByRole('link', { name: '设置' })).toHaveFocus()
    await user.keyboard('{Enter}')

    expect(screen.getByRole('heading', { name: '设置' })).toBeInTheDocument()
  })

  it('展示与健康 API 一致的核心、安全和 Provider 状态', async () => {
    vi.stubGlobal('fetch', vi.fn(async (input: string | URL | Request) => {
      const path = String(input)
      const body = path.endsWith('/health/ready')
        ? {
            status: 'ready',
            core: { configuration: 'ready', storage: 'ready' },
            safe_mode: 'local_only',
            detail: '核心本地服务已就绪',
          }
        : {
            providers: [
              {
                provider_id: 'openai',
                kind: 'model',
                display_name: 'OpenAI',
                configured: true,
                available: false,
                mock: false,
                diagnostic: '连接检查失败',
                last_checked_at: '2026-11-12T08:30:00Z',
                status: 'unavailable',
              },
            ],
          }
      return { status: 200, json: async () => body }
    }))

    render(
      <MemoryRouter initialEntries={['/']}>
        <AppRoutes />
      </MemoryRouter>,
    )

    expect(await screen.findByText('核心服务就绪')).toBeInTheDocument()
    expect(screen.getByText('SQLite 已就绪')).toBeInTheDocument()
    expect(screen.getAllByText('本机安全模式')).toHaveLength(2)
    expect(screen.getByText('OpenAI')).toBeInTheDocument()
    expect(screen.getByText('不可用')).toBeInTheDocument()
    expect(screen.getByText('最近检查：2026-11-12 08:30:00 UTC')).toBeInTheDocument()
  })

  it('设置页不渲染秘密并提示不完整配置', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => ({
      status: 200,
      json: async () => ({
        providers: [
          {
            provider_id: 'openai',
            display_name: 'OpenAI',
            model_id: null,
            base_url: 'https://api.openai.com/v1',
            timeout_seconds: 60,
            max_retries: 2,
            credential_present: true,
          },
          {
            provider_id: 'ark',
            display_name: '火山方舟',
            model_id: null,
            base_url: 'https://ark.example.test/api/v3',
            timeout_seconds: 60,
            max_retries: 2,
            credential_present: false,
          },
        ],
      }),
    })))

    render(
      <MemoryRouter initialEntries={['/settings']}>
        <AppRoutes />
      </MemoryRouter>,
    )

    expect(await screen.findByText('配置不完整：缺少模型标识')).toBeInTheDocument()
    expect(screen.getByText('未配置凭据')).toBeInTheDocument()
    expect(screen.queryByText(/secret|sk-/i)).not.toBeInTheDocument()
  })
})

describe('后续能力占位入口', () => {
  const futureFeatures = [
    ['/ai-chat', 'AI 对话'],
    ['/market', '行情'],
    ['/watchlist', '自选'],
    ['/strategies', '策略'],
    ['/backtests', '回测'],
    ['/portfolio', '组合持仓'],
    ['/orders', '订单成交'],
    ['/knowledge', '知识 Skill'],
    ['/briefing', '舆情速递'],
  ] as const

  it.each(futureFeatures)('%s 明确显示尚未实现且没有操作按钮', (path, title) => {
    render(
      <MemoryRouter initialEntries={[path]}>
        <AppRoutes />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: title })).toBeInTheDocument()
    expect(screen.getByText('尚未实现')).toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})

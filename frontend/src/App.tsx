import { useEffect, useState } from 'react'
import { BrowserRouter, NavLink, Navigate, Outlet, Route, Routes } from 'react-router-dom'

import './App.css'
import { formatProviderCheckedAt, loadHealthSnapshot, mapHealthSummary, providerStatusLabel, type HealthSnapshot } from './health'
import { loadModelProviderSettings, providerConfigurationLabel, type ModelProviderSetting } from './providerSettings'

const primaryNavigation = [
  { label: '总览', to: '/' },
  { label: '设置', to: '/settings' },
]

const futureFeatures = [
  { label: 'AI 对话', to: '/ai-chat', description: '持仓、行情与新闻分析将在独立 change 中实现。' },
  { label: '行情', to: '/market', description: 'A 股实时与本地行情接入尚未实现。' },
  { label: '自选', to: '/watchlist', description: '自选分组与关注列表尚未实现。' },
  { label: '策略', to: '/strategies', description: 'Python 策略插件管理尚未实现。' },
  { label: '回测', to: '/backtests', description: '可复现回测与指标分析尚未实现。' },
  { label: '组合持仓', to: '/portfolio', description: '本地组合、持仓与风险视图尚未实现。' },
  { label: '订单成交', to: '/orders', description: 'Mock 订单与成交将在风控能力完成后实现。' },
  { label: '知识 Skill', to: '/knowledge', description: 'SKILL.md 与设计文档导入、解析和检索尚未实现。' },
  { label: '舆情速递', to: '/briefing', description: '国内外重要事件与数据速递尚未实现。' },
]

function AppShell() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand" aria-label="lclAI 本地量化工作台">
          <span className="brand-mark" aria-hidden="true">L</span>
          <span>
            <strong>lclAI</strong>
            <small>本地量化工作台</small>
          </span>
        </div>
        <nav className="primary-nav" aria-label="主导航">
          {primaryNavigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-dot" aria-hidden="true" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="nav-section-label">规划能力</div>
        <nav className="future-nav" aria-label="规划能力">
          {futureFeatures.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => isActive ? 'future-link active' : 'future-link'}
            >
              {item.label}
              <span>待实现</span>
            </NavLink>
          ))}
        </nav>
        <div className="safety-note">
          <span className="status-dot" aria-hidden="true" />
          <span>
            <strong>本机安全模式</strong>
            <small>实盘交易未启用</small>
          </span>
        </div>
      </aside>
      <main className="workspace">
        <Outlet />
      </main>
    </div>
  )
}

function OverviewPage() {
  const [snapshot, setSnapshot] = useState<HealthSnapshot | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    loadHealthSnapshot()
      .then((result) => {
        if (active) setSnapshot(result)
      })
      .catch((error: unknown) => {
        if (active) setLoadError(error instanceof Error ? error.message : '健康检查失败')
      })
    return () => {
      active = false
    }
  }, [])

  const summary = snapshot ? mapHealthSummary(snapshot.readiness) : null

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">LOCAL WORKBENCH</p>
          <h1>工作台总览</h1>
          <p className="page-description">查看本地核心服务与外部能力的可用边界。</p>
        </div>
        <span className="mode-badge">仅本机访问</span>
      </header>
      <section className="status-grid" aria-label="基础状态">
        <article className="status-card">
          <span className="card-label">核心服务</span>
          <strong>{summary?.coreLabel ?? (loadError ? '健康检查不可用' : '等待健康检查')}</strong>
          <p>{summary?.storageLabel ?? loadError ?? '正在读取后端核心状态。'}</p>
        </article>
        <article className="status-card">
          <span className="card-label">外部 Provider</span>
          <strong>{snapshot ? `${snapshot.providers.length} 项已读取` : '等待状态'}</strong>
          <p>每项外部能力独立降级，不使用虚构数据。</p>
        </article>
        <article className="status-card safe">
          <span className="card-label">交易安全</span>
          <strong>{summary?.safeModeLabel ?? '本机安全模式'}</strong>
          <p>当前基础阶段不会发送任何真实订单。</p>
        </article>
      </section>

      {snapshot && (
        <section className="provider-panel" aria-labelledby="provider-title">
          <div className="section-heading">
            <div>
              <span className="card-label">INTEGRATIONS</span>
              <h2 id="provider-title">Provider 状态</h2>
            </div>
            <span className="outline-badge">独立降级</span>
          </div>
          <div className="provider-list">
            {snapshot.providers.map((provider) => (
              <article className="provider-row" key={provider.provider_id}>
                <div>
                  <strong>{provider.display_name}</strong>
                  <p>{provider.diagnostic ?? '暂无诊断信息'}</p>
                  {provider.last_checked_at && (
                    <p>
                      <time dateTime={provider.last_checked_at}>
                        最近检查：{formatProviderCheckedAt(provider.last_checked_at)}
                      </time>
                    </p>
                  )}
                </div>
                <span className={`provider-status ${provider.status}`}>
                  {providerStatusLabel[provider.status]}
                </span>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

function SettingsPage() {
  const [providers, setProviders] = useState<ModelProviderSetting[]>([])
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    loadModelProviderSettings()
      .then((result) => {
        if (active) setProviders(result)
      })
      .catch((error: unknown) => {
        if (active) setLoadError(error instanceof Error ? error.message : '设置读取失败')
      })
    return () => {
      active = false
    }
  }, [])

  return (
    <div className="page narrow-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">LOCAL CONFIGURATION</p>
          <h1>设置</h1>
          <p className="page-description">这里只展示非敏感配置摘要，绝不回显完整凭据。</p>
        </div>
      </header>
      <section className="settings-panel">
        <div>
          <span className="card-label">配置入口</span>
          <h2>环境变量</h2>
          <p>OpenAI 与火山方舟凭据从本机环境读取，当前界面不提供明文编辑。</p>
        </div>
        <span className="outline-badge">安全只读</span>
      </section>
      {loadError && <p className="inline-error" role="alert">{loadError}</p>}
      {providers.length > 0 && (
        <section className="configuration-list" aria-label="模型 Provider 配置">
          {providers.map((provider) => (
            <article className="configuration-card" key={provider.provider_id}>
              <div className="configuration-title">
                <h2>{provider.display_name}</h2>
                <span className={provider.model_id && provider.credential_present ? 'config-state ready' : 'config-state'}>
                  {providerConfigurationLabel(provider)}
                </span>
              </div>
              <dl>
                <div><dt>模型标识</dt><dd>{provider.model_id ?? '未选择'}</dd></div>
                <div><dt>数据面地址</dt><dd>{provider.base_url}</dd></div>
                <div><dt>超时 / 重试</dt><dd>{provider.timeout_seconds}s / {provider.max_retries}</dd></div>
                <div><dt>凭据</dt><dd>{provider.credential_present ? '已安全读取，不显示内容' : '未配置'}</dd></div>
              </dl>
            </article>
          ))}
        </section>
      )}
    </div>
  )
}

function PlaceholderPage({ title, description }: { title: string; description: string }) {
  return (
    <div className="page narrow-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">PLANNED CAPABILITY</p>
          <h1>{title}</h1>
          <p className="page-description">{description}</p>
        </div>
        <span className="outline-badge">规划中</span>
      </header>
      <section className="placeholder-panel">
        <span className="placeholder-mark" aria-hidden="true">—</span>
        <h2>尚未实现</h2>
        <p>这里不会展示伪造数据，也不会提供任何可执行交易操作。</p>
      </section>
    </div>
  )
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<OverviewPage />} />
        <Route path="settings" element={<SettingsPage />} />
        {futureFeatures.map((feature) => (
          <Route
            key={feature.to}
            path={feature.to.slice(1)}
            element={<PlaceholderPage title={feature.label} description={feature.description} />}
          />
        ))}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  )
}

export default App

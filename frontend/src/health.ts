export type CoreState = 'ready' | 'not_ready'
export type ProviderStatus = 'unconfigured' | 'available' | 'unavailable' | 'mock'

export interface ReadinessResponse {
  status: CoreState
  core: {
    configuration: CoreState
    storage: CoreState
  }
  safe_mode: 'local_only'
  detail: string
}

export interface ProviderSummary {
  provider_id: string
  kind: 'model' | 'market_data' | 'news' | 'vector_store' | 'trading'
  display_name: string
  configured: boolean
  available: boolean
  mock: boolean
  diagnostic: string | null
  last_checked_at: string | null
  status: ProviderStatus
}

export interface ProvidersResponse {
  providers: ProviderSummary[]
}

export interface HealthSnapshot {
  readiness: ReadinessResponse
  providers: ProviderSummary[]
}

export const providerStatusLabel: Record<ProviderStatus, string> = {
  unconfigured: '未配置',
  available: '可用',
  unavailable: '不可用',
  mock: 'Mock',
}

export function mapHealthSummary(readiness: ReadinessResponse) {
  return {
    coreLabel: readiness.status === 'ready' ? '核心服务就绪' : '核心服务未就绪',
    storageLabel: readiness.core.storage === 'ready' ? 'SQLite 已就绪' : 'SQLite 未就绪',
    safeModeLabel: readiness.safe_mode === 'local_only' ? '本机安全模式' : '未知安全模式',
  }
}

export function formatProviderCheckedAt(value: string): string {
  return value.replace('T', ' ').replace(/Z$/, ' UTC')
}

async function requestJson<T>(path: string, acceptedStatuses: number[] = [200]): Promise<T> {
  const response = await fetch(path, { headers: { Accept: 'application/json' } })
  if (!acceptedStatuses.includes(response.status)) {
    throw new Error(`健康接口请求失败：HTTP ${response.status}`)
  }
  return response.json() as Promise<T>
}

export async function loadHealthSnapshot(): Promise<HealthSnapshot> {
  const [readiness, providersResponse] = await Promise.all([
    requestJson<ReadinessResponse>('/api/v1/health/ready', [200, 503]),
    requestJson<ProvidersResponse>('/api/v1/providers'),
  ])
  return { readiness, providers: providersResponse.providers }
}

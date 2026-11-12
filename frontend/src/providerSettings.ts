export interface ModelProviderSetting {
  provider_id: string
  display_name: string
  model_id: string | null
  base_url: string
  timeout_seconds: number
  max_retries: number
  credential_present: boolean
}

interface ModelProviderSettingsResponse {
  providers: ModelProviderSetting[]
}

export async function loadModelProviderSettings(): Promise<ModelProviderSetting[]> {
  const response = await fetch('/api/v1/settings/providers', {
    headers: { Accept: 'application/json' },
  })
  if (response.status !== 200) {
    throw new Error(`设置接口请求失败：HTTP ${response.status}`)
  }
  const payload = await response.json() as ModelProviderSettingsResponse
  return payload.providers
}

export function providerConfigurationLabel(provider: ModelProviderSetting): string {
  if (!provider.credential_present) return '未配置凭据'
  if (!provider.model_id) return '配置不完整：缺少模型标识'
  return '已配置'
}

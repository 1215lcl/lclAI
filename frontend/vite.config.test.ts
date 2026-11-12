import { describe, expect, it } from 'vitest'

import config from './vite.config'


describe('Vite 开发服务器', () => {
  it('将 API 请求代理到本机 FastAPI 后端', () => {
    expect(config).toMatchObject({
      server: {
        proxy: {
          '/api': {
            target: 'http://127.0.0.1:8000',
          },
        },
      },
    })
  })
})

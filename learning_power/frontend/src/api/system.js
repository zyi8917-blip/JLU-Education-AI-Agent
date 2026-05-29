import request from '@/utils/request'

// 获取系统配置
export function getConfig() {
  return request({
    url: '/system/config',
    method: 'get'
  })
}

// 更新系统配置
export function updateConfig(data) {
  return request({
    url: '/system/config',
    method: 'put',
    data
  })
}

// 获取统计数据
export function getStatistics() {
  return request({
    url: '/system/statistics',
    method: 'get'
  })
}

// 健康检查
export function healthCheck() {
  return request({
    url: '/system/health',
    method: 'get'
  })
}


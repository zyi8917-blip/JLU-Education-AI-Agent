import request from '@/utils/request'

// 获取单次测评分析
export function getAssessmentAnalysis(assessmentId) {
  return request({
    url: `/analysis/assessment/${assessmentId}`,
    method: 'get'
  })
}

// 获取趋势分析
export function getTrendAnalysis(studentId, params) {
  return request({
    url: `/analysis/trend/${studentId}`,
    method: 'get',
    params
  })
}

// 获取雷达图数据
export function getRadarData(assessmentId) {
  return request({
    url: `/analysis/radar/${assessmentId}`,
    method: 'get'
  })
}

// 对比分析
export function compareAssessments(params) {
  return request({
    url: '/analysis/compare',
    method: 'get',
    params
  })
}

// 获取测评列表
export function getAnalysisList(params) {
  return request({
    url: '/analysis/list',
    method: 'get',
    params
  })
}

/**
 * 获取全体测评分析
 * @param {string} studentId - 学生ID
 * @returns {Promise} 包含评级统计和评语汇总的Promise
 */
export function getOverallAnalysis(studentId) {
  return request({
    url: `/analysis/overall/${studentId}`,
    method: 'get'
  })
}

/**
 * 删除测评记录
 * @param {string} assessmentId - 测评ID
 * @returns {Promise} 删除结果
 */
export function deleteAssessment(assessmentId) {
  return request({
    url: `/assessments/${assessmentId}`,
    method: 'delete'
  })
}


import request from '@/utils/request'

// 创建测评会话
export function createSession(data) {
  return request({
    url: '/assessments/sessions',
    method: 'post',
    data
  })
}

// 获取题目列表
export function getQuestions(sessionId) {
  return request({
    url: `/assessments/sessions/${sessionId}/questions`,
    method: 'get',
    timeout: 60000  // 60 秒超时（AI 个性化改写需要时间）
  })
}

// 获取单个题目
export function getQuestion(sessionId, questionIndex) {
  return request({
    url: `/assessments/sessions/${sessionId}/questions/${questionIndex}`,
    method: 'get'
  })
}

// 提交答案
export function submitAnswer(sessionId, data) {
  return request({
    url: `/assessments/sessions/${sessionId}/answers`,
    method: 'post',
    data
  })
}

// 获取评分
export function getScore(sessionId) {
  return request({
    url: `/assessments/sessions/${sessionId}/score`,
    method: 'get'
  })
}

// 完成测评
export function completeSession(sessionId) {
  return request({
    url: `/assessments/sessions/${sessionId}/complete`,
    method: 'post',
    timeout: 120000  // 120 秒超时（AI 评分需要时间，3道题并行处理）
  })
}

// 获取测评历史
export function getHistory(studentId) {
  return request({
    url: `/assessments/history/${studentId}`,
    method: 'get'
  })
}


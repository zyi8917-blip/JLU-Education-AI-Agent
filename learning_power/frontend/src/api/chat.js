import request from '@/utils/request'

/**
 * 与学习力画像智能助手对话
 * @param {Object} data - 对话数据
 * @param {string} data.student_id - 学生ID
 * @param {string} data.student_name - 学生姓名
 * @param {string} data.message - 用户消息
 * @param {Object} data.portrait_data - 学习力画像数据
 * @param {Array} data.chat_history - 对话历史
 * @returns {Promise}
 */
export function chatWithPortrait(data) {
  return request({
    url: '/chat/portrait',
    method: 'post',
    data,
    timeout: 30000  // 30秒超时
  })
}


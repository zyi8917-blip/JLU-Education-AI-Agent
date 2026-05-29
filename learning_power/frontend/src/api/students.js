import request from '@/utils/request'

// 获取学生列表
export function getStudents(params) {
  return request({
    url: '/students',
    method: 'get',
    params
  })
}

// 创建学生
export function createStudent(data) {
  return request({
    url: '/students',
    method: 'post',
    data
  })
}

// 获取学生详情
export function getStudent(id) {
  return request({
    url: `/students/${id}`,
    method: 'get'
  })
}

// 更新学生
export function updateStudent(id, data) {
  return request({
    url: `/students/${id}`,
    method: 'put',
    data
  })
}

// 删除学生
export function deleteStudent(id) {
  return request({
    url: `/students/${id}`,
    method: 'delete'
  })
}

// 验证学生是否存在
export function verifyStudent(data) {
  return request({
    url: '/students/verify',
    method: 'post',
    data
  })
}

// 获取学生信息选项（年级、性别等）
export function getStudentOptions() {
  return request({
    url: '/students/options',
    method: 'get'
  })
}

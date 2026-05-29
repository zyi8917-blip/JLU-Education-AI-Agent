import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    redirect: '/home',
    children: [
      {
        path: '/home',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: '/students',
        name: 'Students',
        component: () => import('@/views/Students.vue'),
        meta: { title: '学生管理' }
      },
      {
        path: '/assessment',
        name: 'Assessment',
        component: () => import('@/views/Assessment.vue'),
        meta: { title: '开始测评' }
      },
      {
        path: '/analysis',
        name: 'Analysis',
        component: () => import('@/views/Analysis.vue'),
        meta: { title: '结果分析' }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置' }
      },
      {
        path: '/persona',
        name: 'Persona',
        component: () => import('@/views/Persona.vue'),
        meta: { title: '学生画像' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 学生创造力测评系统` : '学生创造力测评系统'
  next()
})

export default router


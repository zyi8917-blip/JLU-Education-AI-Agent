<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <!-- Logo区域 -->
      <div class="logo">
        <div class="logo-icon">
          <div class="ai-core">
            <div class="core-inner"></div>
          </div>
        </div>
        <div class="logo-text">
          <span class="text-gradient">AI学习力测评</span>
        </div>
      </div>

      <!-- 自定义菜单 -->
      <div class="menu-container">
        <div
          v-for="item in menuItems"
          :key="item.path"
          class="menu-item"
          :class="{ 'is-active': activeMenu === item.path }"
          @click="navigateTo(item.path)"
        >
          <div class="menu-item-content">
            <el-icon class="menu-icon">
              <component :is="item.icon" />
            </el-icon>
            <span class="menu-text">{{ item.title }}</span>
          </div>
          <div class="menu-glow"></div>
          <div class="menu-indicator"></div>
        </div>
      </div>

      <!-- 底部状态 -->
      <div class="sidebar-footer">
        <div class="status-indicator">
          <div class="status-dot"></div>
          <span class="status-text">AI在线</span>
        </div>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <h1 class="page-title">
            <span class="title-text">{{ pageTitle }}</span>
            <div class="title-underline"></div>
          </h1>
        </div>
        <div class="header-right">
          <div class="header-icon-wrapper">
            <el-icon class="header-icon"><Bell /></el-icon>
            <span class="notification-badge">3</span>
          </div>
          <div class="header-icon-wrapper">
            <el-icon class="header-icon"><User /></el-icon>
          </div>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <transition name="page-fade" mode="out-in">
          <router-view />
        </transition>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeFilled, User, Edit, DataAnalysis, Setting, Bell, Avatar } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || '首页')

// 菜单项配置
const menuItems = [
  { path: '/home', title: '首页', icon: HomeFilled },
  { path: '/students', title: '学生管理', icon: User },
  { path: '/assessment', title: '开始测评', icon: Edit },
  { path: '/analysis', title: '结果分析', icon: DataAnalysis },
  { path: '/persona', title: '学生画像', icon: Avatar },
  { path: '/settings', title: '系统设置', icon: Setting }
]

const navigateTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}

/* ========== 侧边栏样式 ========== */
.sidebar {
  background: rgba(255, 255, 255, 0.95);
  /* 移除backdrop-filter以提升性能 */
  border-right: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.04);
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* Logo区域 */
.logo {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  position: relative;
}

.logo-icon {
  position: relative;
  flex-shrink: 0;
}

.ai-core {
  width: 18px;
  height: 18px;
  background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-purple) 100%);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(41, 151, 255, 0.2);
  position: relative;
}

/* 简化发光效果 */
.ai-core::before {
  content: '';
  position: absolute;
  inset: -1px;
  background: linear-gradient(135deg, var(--primary-blue), var(--primary-purple));
  border-radius: 5px;
  opacity: 0.1;
  filter: blur(2px);
  z-index: -1;
}

.core-inner {
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 1px;
}

.logo-text {
  display: flex;
  align-items: center;
  margin: 0;
  line-height: 1;
  flex: 1;
  min-width: 0;
}

.text-gradient {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-purple) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* 菜单容器 */
.menu-container {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 菜单项 */
.menu-item {
  position: relative;
  padding: 12px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  background: transparent;
}

.menu-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 60%;
  background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-purple) 100%);
  border-radius: 0 4px 4px 0;
  transition: width 0.3s;
}

.menu-item:hover {
  background: rgba(41, 151, 255, 0.08);
  transform: translateX(4px);
}

.menu-item:hover::before {
  width: 4px;
}

.menu-item.is-active {
  background: linear-gradient(135deg, rgba(41, 151, 255, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
  box-shadow: 0 4px 12px rgba(41, 151, 255, 0.2);
}

.menu-item.is-active::before {
  width: 4px;
}

.menu-item-content {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  z-index: 1;
}

.menu-icon {
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.3s;
  flex-shrink: 0;
}

.menu-item:hover .menu-icon,
.menu-item.is-active .menu-icon {
  color: var(--primary-blue);
  transform: scale(1.05);
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  transition: all 0.3s;
}

.menu-item.is-active .menu-text {
  font-weight: 600;
  color: var(--primary-blue);
}

.menu-glow {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(41, 151, 255, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s;
  border-radius: 12px;
}

.menu-item:hover .menu-glow {
  opacity: 1;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 14px 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 8px;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: var(--accent-green);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
}

.status-text {
  font-size: 11px;
  font-weight: 500;
  color: var(--accent-green);
}



/* ========== 顶部导航样式 ========== */
.header {
  background: rgba(255, 255, 255, 0.95);
  /* 移除backdrop-filter以提升性能 */
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: relative;
}

.header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary-blue), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.header:hover::after {
  opacity: 0.5;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0;
  position: relative;
  display: inline-block;
}

.title-text {
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--primary-blue) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-underline {
  height: 3px;
  background: linear-gradient(90deg, var(--primary-blue) 0%, var(--primary-purple) 100%);
  border-radius: 2px;
  margin-top: 4px;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s;
}

.page-title:hover .title-underline {
  transform: scaleX(1);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon-wrapper {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(241, 245, 249, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.header-icon-wrapper:hover {
  background: rgba(41, 151, 255, 0.1);
  border-color: var(--primary-blue);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(41, 151, 255, 0.2);
}

.header-icon {
  font-size: 20px;
  color: var(--text-secondary);
  transition: all 0.3s;
}

.header-icon-wrapper:hover .header-icon {
  color: var(--primary-blue);
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  font-size: 11px;
  font-weight: 600;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
  animation: pulse 2s ease-in-out infinite;
}

/* ========== 主内容区样式 ========== */
.main-content {
  background: transparent;
  padding: 24px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}

/* 页面切换动画 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.3s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>


<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
// 主应用组件
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* CSS变量 - 科技风主题色 */
:root {
  /* 主色调 */
  --primary-blue: #2997ff;
  --primary-purple: #8b5cf6;
  --accent-cyan: #06b6d4;
  --accent-green: #10b981;
  --accent-orange: #f59e0b;

  /* 背景色 */
  --bg-primary: #f8fafc;
  --bg-secondary: #f1f5f9;
  --bg-tertiary: #e0f2fe;

  /* 文字颜色 */
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-tertiary: #94a3b8;

  /* 边框颜色 */
  --border-light: rgba(148, 163, 184, 0.2);
  --border-medium: rgba(148, 163, 184, 0.4);

  /* 阴影 */
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.12);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.16);
  --shadow-glow: 0 0 20px rgba(41, 151, 255, 0.3);

  /* Element Plus主题覆盖 */
  --el-color-primary: #2997ff;
  --el-color-success: #10b981;
  --el-color-warning: #f59e0b;
  --el-color-danger: #ef4444;
  --el-border-radius-base: 12px;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-primary);
  min-height: 100vh;

  /* 纯白背景 */
  background: #f5f3f3;
  position: relative;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(241, 245, 249, 0.5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-purple) 100%);
  border-radius: 4px;
  transition: all 0.3s;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, var(--primary-purple) 0%, var(--primary-blue) 100%);
  box-shadow: 0 0 8px rgba(41, 151, 255, 0.5);
}

/* 全局动画关键帧 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(41, 151, 255, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(41, 151, 255, 0.6);
  }
}

@keyframes shimmer {
  0% {
    background-position: -200% center;
  }
  100% {
    background-position: 200% center;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Element Plus组件样式覆盖 */
.el-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-light);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.el-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-medium);
}

.el-button--primary {
  background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-purple) 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(41, 151, 255, 0.3);
  transition: all 0.3s;
}

.el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(41, 151, 255, 0.4);
}

.el-button--success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
}

.el-button--info {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  border: none;
}

.el-input__wrapper {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  transition: all 0.3s;
}

.el-input__wrapper:hover,
.el-input__wrapper.is-focus {
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(41, 151, 255, 0.1);
}

.el-table {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
}

.el-table th.el-table__cell {
  background: linear-gradient(135deg, rgba(41, 151, 255, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  color: var(--text-primary);
  font-weight: 600;
}

.el-table tr:hover > td {
  background: rgba(41, 151, 255, 0.05) !important;
}
</style>


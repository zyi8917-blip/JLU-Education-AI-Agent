<template>
  <div class="home">
    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stats-row">
      <el-col :span="6" v-for="(stat, index) in statsCards" :key="index">
        <div class="stat-card" :style="{ animationDelay: `${index * 0.1}s` }">
          <div class="stat-background" :style="{ background: stat.gradient }"></div>

          <div class="stat-icon-wrapper">
            <component :is="stat.icon" class="stat-icon" />
            <div class="icon-glow" :style="{ background: stat.glowColor }"></div>
          </div>

          <div class="stat-content">
            <div class="stat-value">
              <span class="number">{{ stat.value }}</span>
              <span v-if="stat.unit" class="unit">{{ stat.unit }}</span>
            </div>
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-trend" v-if="stat.trend">
              <span class="trend-value" :class="stat.trend > 0 ? 'up' : 'down'">
                {{ stat.trend > 0 ? '↑' : '↓' }} {{ Math.abs(stat.trend) }}%
              </span>
              <span class="trend-text">较昨日</span>
            </div>
          </div>

          <div class="stat-particles">
            <div class="particle" v-for="i in 5" :key="i"></div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <div class="section-header">
        <h2 class="section-title">
          <span class="title-icon">⚡</span>
          <span>快速操作</span>
        </h2>
        <div class="title-line"></div>
      </div>

      <div class="action-grid">
        <div
          v-for="(action, index) in quickActions"
          :key="index"
          class="action-card"
          :style="{ animationDelay: `${0.2 + index * 0.1}s` }"
          @click="action.handler"
        >
          <div class="action-glow"></div>
          <div class="action-icon-wrapper">
            <component :is="action.icon" class="action-icon" />
          </div>
          <div class="action-content">
            <h3 class="action-title">{{ action.title }}</h3>
            <p class="action-desc">{{ action.desc }}</p>
          </div>
          <div class="action-arrow">→</div>
        </div>
      </div>
    </div>

    <!-- 系统信息和使用说明 -->
    <el-row :gutter="24" class="info-row">
      <el-col :span="12">
        <div class="info-card">
          <div class="card-header">
            <h2 class="card-title">
              <span>🔧</span>
              <span>系统信息</span>
            </h2>
          </div>
          <div class="system-info">
            <div class="info-item" v-for="(info, index) in systemInfo" :key="index">
              <div class="info-icon">{{ info.icon }}</div>
              <div class="info-content">
                <div class="info-label">{{ info.label }}</div>
                <div class="info-value">{{ info.value }}</div>
              </div>
              <span v-if="info.badge" class="info-badge">{{ info.badge }}</span>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="info-card">
          <div class="card-header">
            <h2 class="card-title">
              <span>📖</span>
              <span>使用说明</span>
            </h2>
          </div>
          <div class="instructions">
            <div class="instruction-item" v-for="(instruction, index) in instructions" :key="index">
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-content">
                <p class="step-text">{{ instruction }}</p>
              </div>
              <div v-if="index < instructions.length - 1" class="step-line"></div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Document, Calendar, TrendCharts, Edit, DataAnalysis, Avatar } from '@element-plus/icons-vue'
import { getStatistics } from '@/api/system'
import { getConfig } from '@/api/system'
import { useSystemStore } from '@/store'

const router = useRouter()
const systemStore = useSystemStore()

const statistics = ref({
  total_students: 0,
  total_assessments: 0,
  assessments_today: 0,
  average_score: 0
})

const config = ref({
  model_name: 'DeepSeek-V3',
  max_questions: 10,
  time_limit_minutes: 30
})

// 统计卡片数据
const statsCards = computed(() => [
  {
    label: '学生总数',
    value: statistics.value.total_students || 0,
    icon: User,
    gradient: 'linear-gradient(135deg, rgba(41, 151, 255, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%)',
    glowColor: 'rgba(41, 151, 255, 0.4)',
    trend: 12
  },
  {
    label: '测评总数',
    value: statistics.value.total_assessments || 0,
    icon: Document,
    gradient: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%)',
    glowColor: 'rgba(139, 92, 246, 0.4)',
    trend: 8
  },
  {
    label: '今日测评',
    value: statistics.value.assessments_today || 0,
    icon: Calendar,
    gradient: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(251, 146, 60, 0.15) 100%)',
    glowColor: 'rgba(245, 158, 11, 0.4)',
    trend: -3
  },
  {
    label: '平均分数',
    value: statistics.value.average_score || 0,
    icon: TrendCharts,
    gradient: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%)',
    glowColor: 'rgba(16, 185, 129, 0.4)',
    trend: 5
  }
])

// 快速操作
const quickActions = [
  {
    title: '开始测评',
    desc: '创建新的学习力测评任务',
    icon: Edit,
    handler: () => router.push('/assessment')
  },
  {
    title: '学生管理',
    desc: '管理学生档案和信息',
    icon: User,
    handler: () => router.push('/students')
  },
  {
    title: '结果分析',
    desc: '查看测评数据和分析报告',
    icon: DataAnalysis,
    handler: () => router.push('/analysis')
  },
  {
    title: '学生画像',
    desc: 'AI智能生成学生能力画像',
    icon: Avatar,
    handler: () => router.push('/persona')
  }
]

// 系统信息
const systemInfo = computed(() => [
  {
    icon: '🔖',
    label: '系统版本',
    value: 'v1.0.0',
    badge: 'Latest'
  },
  {
    icon: '🤖',
    label: 'AI模型',
    value: config.value.model_name || 'DeepSeek-V3',
    badge: 'Active'
  },
  {
    icon: '📝',
    label: '题目数量',
    value: `${config.value.max_questions || 10} 题`
  },
  {
    icon: '⏱️',
    label: '时间限制',
    value: `${config.value.time_limit_minutes || 30} 分钟`
  }
])

// 使用说明
const instructions = [
  '在"学生管理"中添加学生档案信息',
  '点击"开始测评"选择学生进行AI测评',
  '学生完成测评后，系统自动智能评分',
  '在"结果分析"中查看详细的分析报告'
]

const loadData = async () => {
  try {
    const statsRes = await getStatistics()
    statistics.value = statsRes.data

    const configRes = await getConfig()
    config.value = configRes.data
    systemStore.setConfig(configRes.data)
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.home {
  padding: 0;
  animation: fadeIn 0.5s ease-out;
}

/* ========== 统计卡片区域 ========== */
.stats-row {
  margin-bottom: 32px;
}

.stat-card {
  position: relative;
  height: 185px;
  background: rgba(255, 255, 255, 0.9);
  /* 移除backdrop-filter以提升性能 */
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 20px;
  padding: 24px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeInUp 0.6s ease-out backwards;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: rgba(41, 151, 255, 0.4);
  box-shadow: 0 8px 24px rgba(41, 151, 255, 0.15);
}

.stat-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0.6;
  transition: opacity 0.4s;
  border-radius: 20px;
}

.stat-card:hover .stat-background {
  opacity: 0.8;
}

.stat-icon-wrapper {
  position: relative;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  margin-bottom: 14px;
  transition: all 0.4s;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.08) rotate(3deg);
  border-color: rgba(41, 151, 255, 0.4);
}

.stat-icon {
  font-size: 22px;
  color: var(--primary-blue);
  transition: all 0.4s;
}

.stat-card:hover .stat-icon {
  color: var(--primary-purple);
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  border-radius: 16px;
  opacity: 0;
  filter: blur(12px);
  transition: opacity 0.4s;
}

.stat-card:hover .icon-glow {
  opacity: 0.4;
}

.stat-content {
  position: relative;
  z-index: 1;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 10px;
}

.stat-value .number {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--primary-blue) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.stat-value .unit {
  font-size: 14px;
  color: var(--text-tertiary);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  letter-spacing: 0.5px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  flex-wrap: wrap;
}

.trend-value {
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
}

.trend-value.up {
  color: var(--accent-green);
  background: rgba(16, 185, 129, 0.1);
}

.trend-value.down {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.trend-text {
  color: var(--text-tertiary);
}

/* 粒子效果 - 已禁用以提升性能 */
.stat-particles {
  display: none; /* 禁用粒子动画以提升性能 */
}

/* ========== 快速操作区域 ========== */
.quick-actions {
  margin-bottom: 32px;
  animation: fadeInUp 0.6s ease-out 0.2s backwards;
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.title-icon {
  font-size: 24px;
}

.title-line {
  height: 2px;
  background: linear-gradient(90deg, rgba(41, 151, 255, 0.5) 0%, transparent 100%);
  margin-top: 12px;
  border-radius: 2px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.action-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  /* 移除backdrop-filter以提升性能 */
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeInUp 0.6s ease-out backwards;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.action-card:hover {
  transform: translateY(-4px);
  border-color: rgba(41, 151, 255, 0.4);
  box-shadow: 0 12px 32px rgba(41, 151, 255, 0.15);
}

.action-icon-wrapper {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(41, 151, 255, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
  border: 1px solid rgba(41, 151, 255, 0.2);
  border-radius: 10px;
  margin-bottom: 12px;
  transition: all 0.4s;
}

.action-card:hover .action-icon-wrapper {
  transform: scale(1.08) rotate(-3deg);
  box-shadow: 0 6px 12px rgba(41, 151, 255, 0.2);
}

.action-icon {
  font-size: 20px;
  color: var(--primary-blue);
}

.action-content {
  margin-bottom: 12px;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.action-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.action-arrow {
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-size: 18px;
  color: var(--primary-blue);
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.4s;
}

.action-card:hover .action-arrow {
  opacity: 1;
  transform: translateX(0);
}

.action-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(41, 151, 255, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
  opacity: 0;
  transition: opacity 0.4s;
}

.action-card:hover .action-glow {
  opacity: 1;
}

/* ========== 信息卡片区域 ========== */
.info-row {
  animation: fadeInUp 0.6s ease-out 0.3s backwards;
}

.info-card {
  background: rgba(255, 255, 255, 0.95);
  /* 移除backdrop-filter以提升性能 */
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 16px;
  padding: 24px;
  height: 100%;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.info-card:hover {
  border-color: rgba(41, 151, 255, 0.3);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.card-header {
  margin-bottom: 24px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 系统信息 */
.system-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(248, 250, 252, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 12px;
  transition: all 0.3s;
}

.info-item:hover {
  background: rgba(41, 151, 255, 0.05);
  border-color: rgba(41, 151, 255, 0.3);
  transform: translateX(4px);
}

.info-icon {
  font-size: 20px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(41, 151, 255, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
  border-radius: 8px;
}

.info-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.info-badge {
  padding: 4px 12px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-green);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 使用说明 */
.instructions {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.instruction-item {
  position: relative;
  display: flex;
  gap: 16px;
  padding-left: 8px;
}

.step-number {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-purple) 100%);
  border-radius: 50%;
  font-size: 13px;
  font-weight: 700;
  color: white;
  box-shadow: 0 3px 8px rgba(41, 151, 255, 0.3);
}

.step-content {
  flex: 1;
  padding-top: 4px;
}

.step-text {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.step-line {
  position: absolute;
  left: 21px;
  top: 36px;
  width: 2px;
  height: calc(100% + 12px);
  background: linear-gradient(180deg, rgba(41, 151, 255, 0.5) 0%, transparent 100%);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .action-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .action-grid {
    grid-template-columns: 1fr;
  }
}
</style>


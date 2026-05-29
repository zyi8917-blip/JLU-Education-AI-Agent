<template>
  <div class="analysis">
    <!-- 历史记录列表 -->
    <div v-if="!selectedAssessmentId" class="history-list">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>测评历史记录</span>
            <el-button type="primary" @click="goToAssessment">开始新测评</el-button>
          </div>
        </template>

        <div v-loading="loading">
          <el-empty v-if="assessmentList.length === 0" description="暂无测评记录" />

          <el-table v-else :data="assessmentList" stripe style="width: 100%">
            <el-table-column prop="assessment_id" label="测评ID" width="180" />
            <el-table-column prop="student_name" label="学生姓名" width="120" />
            <el-table-column prop="evaluation_type" label="测评类型" width="120">
              <template #default="{ row }">
                {{ getEvaluationTypeName(row.evaluation_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="end_time" label="完成时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.end_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="total_score" label="总分" width="100">
              <template #default="{ row }">
                <el-tag :type="getScoreType(row.total_score)">{{ row.total_score }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="各维度分数">
              <template #default="{ row }">
                <div class="scores-mini">
                  <span v-for="(score, key) in row.final_scores" :key="key">
                    {{ getDimensionName(key, row.evaluation_type) }}: {{ score }}
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button type="primary" link @click="viewDetail(row.assessment_id)">
                  查看详情
                </el-button>
                <el-button type="danger" link @click="handleDelete(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-if="total > pageSize"
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="loadList"
            style="margin-top: 20px; justify-content: center;"
          />
        </div>
      </el-card>
    </div>

    <!-- 详细分析 -->
    <div v-else-if="selectedAssessmentId && analysisData" class="detail-view">
      <el-button @click="backToList" style="margin-bottom: 20px;">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>

      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>测评结果详情</span>
            <el-button type="danger" @click="handleDeleteCurrent">
              <el-icon><Delete /></el-icon>
              删除此记录
            </el-button>
          </div>
        </template>

        <!-- 基本信息 -->
        <div class="basic-info">
          <div class="info-item">
            <span class="label">学生姓名：</span>
            <span class="value">{{ analysisData.student_name }}</span>
          </div>
          <div class="info-item">
            <span class="label">测评ID：</span>
            <span class="value">{{ analysisData.assessment_id }}</span>
          </div>
          <div class="info-item">
            <span class="label">测评类型：</span>
            <span class="value">{{ getEvaluationTypeName(analysisData.evaluation_type) }}</span>
          </div>
          <div class="info-item">
            <span class="label">完成时间：</span>
            <span class="value">{{ formatTime(analysisData.end_time) }}</span>
          </div>
          <div class="info-item">
            <span class="label">总分：</span>
            <span class="value score">{{ analysisData.total_score }}</span>
          </div>
          <div class="info-item">
            <span class="label">等级：</span>
            <el-tag :type="getLevelType(analysisData.level)">{{ analysisData.level }}</el-tag>
          </div>
        </div>
      </el-card>

      <!-- 各维度的分数卡片 -->
      <div class="scores-grid">
        <el-card class="score-card" v-for="(score, key) in (analysisData.scores || analysisData.final_scores)" :key="key">
          <div class="score-item">
            <div class="score-label">{{ getDimensionName(key) }}</div>
            <div class="score-value">{{ score }}</div>
            <el-progress :percentage="score" :stroke-width="8" />
            <div class="score-level">{{ getScoreLevel(score) }}</div>
          </div>
        </el-card>
      </div>

      <!-- 能力雷达图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>能力雷达图</span>
          </div>
        </template>
        <div ref="radarChart" style="width: 100%; height: 400px;"></div>
      </el-card>

      <!-- 总体反馈 -->
      <el-card class="overall-feedback-card" v-if="analysisData.overall_feedback">
        <template #header>
          <div class="card-header">
            <el-icon style="margin-right: 8px; color: #409eff;"><Document /></el-icon>
            <span>总体评价</span>
          </div>
        </template>
        <div class="overall-feedback-content">
          <div class="feedback-text">{{ analysisData.overall_feedback }}</div>
        </div>
      </el-card>

      <!-- 详细分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <el-icon style="margin-right: 8px; color: #67c23a;"><List /></el-icon>
            <span>各维度详细分析</span>
          </div>
        </template>

        <el-collapse>
          <el-collapse-item
            v-for="(analysis, key) in analysisData.dimension_analysis"
            :key="key"
            :title="getDimensionName(key)"
          >
            <div class="dimension-detail">
              <div class="detail-section">
                <div class="section-title">表现评价</div>
                <div class="section-content">{{ analysis }}</div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Delete, Document, List } from '@element-plus/icons-vue'
import { getAssessmentAnalysis, getAnalysisList, deleteAssessment } from '@/api/analysis'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const selectedAssessmentId = ref('')
const analysisData = ref(null)
const radarChart = ref(null)

// 列表相关
const assessmentList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 加载列表
const loadList = async () => {
  loading.value = true
  try {
    const response = await getAnalysisList({
      page: currentPage.value,
      page_size: pageSize.value
    })
    assessmentList.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('Failed to load list:', error)
    ElMessage.error('加载列表失败')
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = async (assessmentId) => {
  selectedAssessmentId.value = assessmentId
  await loadAnalysis(assessmentId)
}

// 返回列表
const backToList = () => {
  selectedAssessmentId.value = ''
  analysisData.value = null
  loadList()
}

// 加载分析数据
const loadAnalysis = async (assessmentId) => {
  loading.value = true
  try {
    const response = await getAssessmentAnalysis(assessmentId)

    // 处理数据结构兼容性，确保数据格式统一
    const data = response.data

    // 确保有evaluation_type字段
    if (!data.evaluation_type) {
      // 如果没有明确的测评类型，默认使用cognitive
      data.evaluation_type = 'cognitive_strategy'
    }

    // 确保分数数据存在且格式一致
    if (!data.scores && data.final_scores) {
      // 如果没有scores但有final_scores，将final_scores赋值给scores
      data.scores = data.final_scores
    }

    // 确保有level字段，如果没有则根据总分计算
    if (!data.level) {
      const totalScore = data.total_score || 0
      if (totalScore >= 85) data.level = '优秀'
      else if (totalScore >= 75) data.level = '良好'
      else if (totalScore >= 65) data.level = '中等'
      else if (totalScore >= 60) data.level = '及格'
      else data.level = '需提高'
    }

    // 确保有维度分析数据，如果没有则生成默认的
    if (!data.dimension_analysis) {
      const scores = data.scores || data.final_scores || {}
      data.dimension_analysis = {}

      for (const [key, score] of Object.entries(scores)) {
        data.dimension_analysis[key] = `建议加强${getDimensionName(key, data.evaluation_type)}方面的训练和提高`
      }
    }

    // 提取总体反馈（overall_feedback）
    // 注意：overall_feedback 可能在不同位置，需要兼容处理
    if (!data.overall_feedback) {
      // 尝试从其他可能的位置获取
      if (data.feedback && typeof data.feedback === 'object') {
        data.overall_feedback = data.feedback.overall_feedback || ''
      }
    }

    analysisData.value = data
    await nextTick()
    initRadarChart()
  } catch (error) {
    console.error('Failed to load analysis:', error)
    ElMessage.error('加载详情失败')
  } finally {
    loading.value = false
  }
}

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChart.value || !analysisData.value) return

  const chart = echarts.init(radarChart.value)
  const scores = analysisData.value.scores || analysisData.value.final_scores
  const evaluationType = analysisData.value.evaluation_type || ''

  // 根据测评类型生成雷达图指标
  const indicators = []
  const values = []
  
  for (const [key, value] of Object.entries(scores)) {
    indicators.push({ name: getDimensionName(key, evaluationType), max: 100 })
    values.push(value)
  }

  const option = {
    radar: {
      indicator: indicators
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: `${getEvaluationTypeName(evaluationType)}评分`
      }]
    }]
  }

  chart.setOption(option)
  
  // 添加窗口大小变化时重新调整图表大小
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 辅助函数
const getEvaluationTypeName = (type) => {
  const typeMap = {
    'cognitive_strategy': '认知能力',
    'metacognition': '元认知能力',
    'critical_thinking': '批判性思维',
    'learning_motivation': '学习动机',
    'social_emotional': '社会情感能力',
    'total': '总评'
  }
  return typeMap[type] || type
}

const getDimensionName = (key, evaluationType = '') => {
  // 基础维度名称映射
  let names = {
    fluency: '流畅性',
    flexibility: '灵活性',
    originality: '独创性',
    elaboration: '精致性'
  }

  // 根据不同的测评类型返回不同的维度名称
  if (evaluationType === 'cognitive_strategy' || (analysisData.value && analysisData.value.evaluation_type === 'cognitive_strategy')) {
    names = {
      ...names,
      // 认知能力的特定维度
      rehearsal: "复述策略",
      elaboration: "精加工策略",
      organization: "组织策略",
      resource_management: "资源管理策略"
    }
  } else if (evaluationType === 'metacognition' || (analysisData.value && analysisData.value.evaluation_type === 'metacognition')) {
    names = {
      ...names,
      // 元认知能力的特定维度
      monitoring: "自我监控能力",
      integration: "自我整合能力",
      differentiation: "分化能力",
      decentralization: "去中心化能力"
    }
  } else if (evaluationType === 'critical_thinking' || (analysisData.value && analysisData.value.evaluation_type === 'critical_thinking')) {
    names = {
      ...names,
      // 批判性思维的特定维度
      open_mindedness: "开放思维",
      analytical_logical_skills: "分析逻辑能力",
      systematic_planning: "系统规划能力",
      intellectual_curiosity: "求知欲与探索精神",
      cognitive_maturity: "认知成熟度"
    }
  } else if (evaluationType === 'learning_motivation' || (analysisData.value && analysisData.value.evaluation_type === 'learning_motivation')) {
    names = {
      ...names,
      // 学习动机的特定维度
      autonomy: "自主性",
      competence: "胜任感",
      relatedness: "归属感"
    }
  } else if (evaluationType === 'social_emotional' || (analysisData.value && analysisData.value.evaluation_type === 'social_emotional')) {
    names = {
      ...names,
      // 社会情感能力的特定维度
      responsible_decision_making: "负责任的决策",
      social_awareness: "社会知觉",
      self_management: "自我管理",
      relationship_skills: "人际关系"
    }
  }

  return names[key] || key
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const getScoreType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 70) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

const getLevelType = (level) => {
  const types = {
    '优秀': 'success',
    '良好': 'success',
    '中等': 'warning',
    '及格': 'warning',
    '需提高': 'danger'
  }
  return types[level] || ''
}

const getScoreLevel = (score) => {
  if (score >= 9) return '优秀'
  if (score >= 8) return '良好'
  if (score >= 7) return '中等'
  if (score >= 6) return '及格'
  return '需提高'
}

const goToAssessment = () => {
  router.push('/assessment')
}

// 删除测评记录（从列表）
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测评记录 "${row.assessment_id}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteAssessment(row.assessment_id)
    ElMessage.success('删除成功')
    loadList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete assessment:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 删除当前查看的测评记录
const handleDeleteCurrent = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除当前测评记录吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteAssessment(selectedAssessmentId.value)
    ElMessage.success('删除成功')
    backToList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete assessment:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 组件挂载
onMounted(() => {
  // 如果有 assessmentId 参数，直接查看详情
  const assessmentId = route.query.assessmentId
  if (assessmentId) {
    viewDetail(assessmentId)
  } else {
    loadList()
  }
})

// 组件卸载时清理事件监听器
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 处理窗口大小变化
const handleResize = () => {
  if (radarChart.value) {
    const chart = echarts.getInstanceByDom(radarChart.value)
    if (chart) {
      chart.resize()
    }
  }
}
</script>

<style scoped>
.analysis {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.scores-mini {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 13px;
}

.scores-mini span {
  color: #606266;
}

.info-card {
  margin-bottom: 20px;
}

.basic-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  padding: 10px 0;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item .label {
  font-weight: bold;
  color: #606266;
  margin-right: 8px;
}

.info-item .value {
  color: #303133;
}

.info-item .value.score {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.score-card {
  text-align: center;
}

.score-item {
  padding: 10px;
}

.score-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.score-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 12px;
}

.score-level {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.chart-card {
  margin-bottom: 20px;
}

.overall-feedback-card {
  margin-bottom: 20px;
  border-left: 4px solid #409eff;
}

.overall-feedback-content {
  padding: 10px 0;
}

.feedback-text {
  font-size: 15px;
  color: #303133;
  line-height: 1.8;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8f4ff 100%);
  border-radius: 8px;
  border-left: 3px solid #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.analysis-card {
  margin-bottom: 20px;
}

.dimension-detail {
  padding: 10px 0;
}

.detail-section {
  margin-bottom: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.section-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>

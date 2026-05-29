<template>
  <div class="persona-container">
    <!-- 学生信息输入区域 -->
    <div v-if="!studentValidated" class="info-input-section">
      <el-card class="input-card">
        <template #header>
          <div class="card-header">
            <span>请输入学生信息</span>
          </div>
        </template>
        <el-form :model="studentForm" :rules="rules" ref="studentFormRef" label-width="100px">
          <el-form-item label="学生姓名" prop="name">
            <el-input v-model="studentForm.name" placeholder="请输入学生姓名"></el-input>
          </el-form-item>
          <el-form-item label="学号" prop="id">
            <el-input v-model="studentForm.id" placeholder="请输入学号"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="validateStudent" :loading="validating">验证信息</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 查看画像区域 -->
    <div v-else>
      <!-- 返回按钮 -->
      <el-row class="mb-20">
        <el-col>
          <el-button @click="resetValidation">← 返回重新输入</el-button>
        </el-col>
      </el-row>

      <!-- 学生信息展示 -->
      <el-card class="student-info-card mb-20">
        <div class="student-info">
          <el-avatar :size="60" icon="User" />
          <div class="info-details">
            <h3>{{ studentInfo.name }}</h3>
            <p>学号: {{ studentInfo.id }}</p>
          </div>
        </div>
      </el-card>

      <!-- 测评卡片展示区域 -->
      <div class="assessment-cards-container mb-20">
        <h3>测评完成情况</h3>
        <div class="assessment-cards">
          <el-card 
            v-for="assessmentType in assessmentTypes" 
            :key="assessmentType.value" 
            class="assessment-card"
            :class="{ 'completed': isAssessmentCompleted(assessmentType.value), 'pending': !isAssessmentCompleted(assessmentType.value) }"
            @click="handleAssessmentCardClick(assessmentType.value)"
          >
            <div class="card-content">
              <div class="card-header">
                <span class="assessment-name">{{ assessmentType.label }}</span>
                <el-icon v-if="isAssessmentCompleted(assessmentType.value)" class="status-icon completed-icon">
                  <Check />
                </el-icon>
                <el-icon v-else class="status-icon pending-icon">
                  <Close />
                </el-icon>
              </div>
              <div class="card-status">
                <el-tag :type="isAssessmentCompleted(assessmentType.value) ? 'success' : 'danger'">
                  {{ isAssessmentCompleted(assessmentType.value) ? '已完成' : '未完成' }}
                </el-tag>
              </div>
              <div class="card-description">
                {{ assessmentType.description }}
              </div>
            </div>
          </el-card>
        </div>
      </div>
  
       <!-- 未完成提示 -->
      <el-alert 
        v-if="assessments.length > 0 && !allAssessmentsCompleted" 
        title="请完成所有测评题目后再生成学习力画像" 
        type="warning" 
        show-icon 
        class="completion-prompt"
      ></el-alert>
       
       <!-- 生成画像按钮 -->
        <div v-if="assessments.length > 0" class="generate-report-section mb-20">
        <el-button 
          type="primary" 
          size="large" 
          @click="generateLearningPortrait"
          :disabled="!allAssessmentsCompleted"
        >
          生成学习力画像
        </el-button>
      </div>

      <!-- 学习力画像报告 - 参考专业评估报告风格 -->
      <div v-if="showLearningPortrait" class="portrait-report">

        <!-- 报告标题 -->
        <div class="report-title">用户自主学习力深度评估画像</div>

        <!-- 左右分栏布局 -->
        <div class="report-layout">

          <!-- 左侧区域 -->
          <div class="report-left">

            <!-- 基本信息与总体评价 -->
            <div class="info-card">
              <div class="info-header">
                <div class="info-text">
                  <div class="info-title">基本信息与总体评价</div>
                  <div class="info-row">用户昵称：<span class="info-value">{{ studentInfo.name }}</span></div>
                  <div class="info-row">测评日期：<span class="info-value">{{ getCurrentDate() }}</span></div>
                  <div class="info-row">
                    总体等级：
                    <span class="overall-level-badge" :class="getOverallLevelClass()">
                      ● {{ getOverallLevelText() }}
                    </span>
                    <span class="level-score">(Level {{ getOverallLevelScore() }}/5)</span>
                  </div>
                </div>
                <div class="overall-badge" :class="getOverallLevelClass()">
                  <span class="badge-label">总体等级:</span>
                  <span class="badge-text">{{ getOverallLevelText() }}</span>
                </div>
              </div>
              <div class="core-summary">
                <span class="summary-label">核心简述：</span>
                {{ generateCoreSummary() }}
              </div>
            </div>

            <!-- 核心动力系统 -->
            <div class="module-card">
              <div class="module-header">
                <div class="module-icon">❤️</div>
                <div class="module-title">核心动力系统</div>
                <div class="module-subtitle">(Core Motivation System)</div>
                <div class="scale-legend">
                  <span v-for="n in 5" :key="n" class="scale-dot" :class="{ 'active': n <= 3 }">{{ n }}</span>
                </div>
              </div>
              <div class="motivation-items">
                <div class="motivation-item" v-if="overallAnalysisData?.dimension_scores_dict?.learning_motivation">
                  <div class="item-header">
                    <span class="item-icon">🔥</span>
                    <span class="item-label">学习动机</span>
                    <span class="item-score">● {{ getScoreFor5Scale('learning_motivation') }}</span>
                    <span class="item-level">({{ getLevelDescription(getScoreFor5Scale('learning_motivation')) }})</span>
                  </div>
                  <div class="scale-bar-container">
                    <div class="scale-bar">
                      <div class="scale-fill" :style="{ width: getScoreFor5Scale('learning_motivation') * 20 + '%' }"></div>
                    </div>
                    <div class="scale-dots">
                      <span v-for="n in 5" :key="n" class="dot" :class="{ 'filled': n <= Math.round(getScoreFor5Scale('learning_motivation')) }"></span>
                    </div>
                  </div>
                </div>

                <div v-for="(score, subKey) in overallAnalysisData?.dimension_scores_dict?.learning_motivation" :key="subKey" class="sub-motivation-item">
                  <div class="sub-item-row">
                    <span class="sub-icon">{{ getSubIcon(subKey) }}</span>
                    <span class="sub-label">{{ getSubDimensionName(subKey, 'learning_motivation') }}</span>
                    <span class="sub-score">● {{ convertTo5Scale(score) }}</span>
                    <span class="sub-level">({{ getLevelDescription(convertTo5Scale(score)) }})</span>
                  </div>
                  <div class="sub-bar-container">
                    <div class="sub-bar">
                      <div class="sub-fill" :style="{ width: convertTo5Scale(score) * 20 + '%' }"></div>
                    </div>
                    <span class="bar-dashes">- - - - - - - - -</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 学习策略中枢 -->
            <div class="module-card strategy-module">
              <div class="module-header">
                <div class="module-icon">📊</div>
                <div class="module-title">学习策略中枢</div>
                <div class="module-subtitle">(Strategy Core)</div>
                <div class="focus-tag" v-if="isFocusArea('cognitive_strategy') || isFocusArea('metacognition')">
                  <span class="star">★</span> 重点区域
                </div>
              </div>

              <!-- 元认知与批判性思维 -->
              <div class="strategy-group">
                <div class="group-header">
                  <span class="group-title">元认知与批判性思维</span>
                  <span class="group-score">● {{ getAverageScore(['metacognition', 'critical_thinking']) }}</span>
                </div>
                <div class="strategy-items-grid">
                  <div v-for="(score, subKey) in overallAnalysisData?.dimension_scores_dict?.metacognition" :key="'meta-' + subKey" class="strategy-item">
                    <span class="s-label">{{ getSubDimensionName(subKey, 'metacognition') }}</span>
                    <div class="s-bar"><div class="s-fill" :style="{ width: convertTo5Scale(score) * 20 + '%' }"></div></div>
                    <span class="s-score">{{ convertTo5Scale(score) }}</span>
                  </div>
                  <div v-for="(score, subKey) in overallAnalysisData?.dimension_scores_dict?.critical_thinking" :key="'ct-' + subKey" class="strategy-item">
                    <span class="s-label">{{ getSubDimensionName(subKey, 'critical_thinking') }}</span>
                    <div class="s-bar"><div class="s-fill" :style="{ width: convertTo5Scale(score) * 20 + '%' }"></div></div>
                    <span class="s-score">{{ convertTo5Scale(score) }}</span>
                  </div>
                </div>
              </div>

              <!-- 基础认知与资源管理 -->
              <div class="strategy-group">
                <div class="group-header">
                  <span class="group-title">基础认知与资源管理</span>
                  <span class="group-score">● {{ getScoreFor5Scale('cognitive_strategy') }}</span>
                </div>
                <div class="strategy-items-grid">
                  <div v-for="(score, subKey) in overallAnalysisData?.dimension_scores_dict?.cognitive_strategy" :key="'cog-' + subKey" class="strategy-item">
                    <span class="s-label">{{ getSubDimensionName(subKey, 'cognitive_strategy') }}</span>
                    <div class="s-bar"><div class="s-fill" :style="{ width: convertTo5Scale(score) * 20 + '%' }"></div></div>
                    <span class="s-score">{{ convertTo5Scale(score) }}</span>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <!-- 右侧区域 -->
          <div class="report-right">

            <!-- 宏观能力地形图 -->
            <div class="module-card radar-module">
              <div class="module-header">
                <div class="module-title">宏观能力地形图</div>
              </div>
              <div class="radar-chart-container">
                <div ref="radarChartRef" class="radar-chart"></div>
              </div>
            </div>

            <!-- 高阶能力与表现 -->
            <div class="module-card">
              <div class="module-header">
                <div class="module-title">高阶能力与表现</div>
                <div class="module-subtitle">(Higher-Order Outcome)</div>
                <div class="scale-legend small">
                  <span v-for="n in 5" :key="n" class="scale-dot">{{ n }}</span>
                </div>
              </div>
              <div class="higher-order-items">
                <div class="ho-item" v-for="(score, subKey) in overallAnalysisData?.dimension_scores_dict?.social_emotional" :key="'se-' + subKey">
                  <div class="ho-header">
                    <span class="ho-icon">{{ getSubIcon(subKey) }}</span>
                    <span class="ho-label">{{ getSubDimensionName(subKey, 'social_emotional') }}</span>
                    <span class="ho-score">● {{ convertTo5Scale(score) }}</span>
                    <span class="ho-level">({{ getLevelDescription(convertTo5Scale(score)) }})</span>
                  </div>
                  <div class="ho-bar-container">
                    <div class="ho-bar">
                      <div class="ho-fill" :style="{ width: convertTo5Scale(score) * 20 + '%', background: getBarGradient(convertTo5Scale(score)) }"></div>
                    </div>
                    <div class="ho-dots">
                      <span v-for="n in 5" :key="n" class="dot"></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 挑战与体验 -->
            <div class="module-card challenges-module">
              <div class="module-header">
                <div class="module-title">挑战与体验</div>
                <div class="module-subtitle">(Challenges & Experience)</div>
                <div class="attention-tag" v-if="hasAttentionArea()">
                  <span class="star">★</span> 关注区域
                </div>
              </div>
              <div class="challenge-items">
                <div class="challenge-item" :class="{ 'attention': isLowScore('cognitive_strategy') }">
                  <span class="c-icon">🧠</span>
                  <span class="c-label">认知策略</span>
                  <span class="c-score">● {{ getScoreFor5Scale('cognitive_strategy') }}</span>
                  <span class="c-level">({{ getLevelDescription(getScoreFor5Scale('cognitive_strategy')) }})</span>
                  <div class="c-bar"><div class="c-fill" :style="{ width: getScoreFor5Scale('cognitive_strategy') * 20 + '%' }"></div></div>
                </div>
                <div class="challenge-item" :class="{ 'attention': isLowScore('metacognition') }">
                  <span class="c-icon">🎯</span>
                  <span class="c-label">元认知能力</span>
                  <span class="c-score">● {{ getScoreFor5Scale('metacognition') }}</span>
                  <span class="c-level">({{ getLevelDescription(getScoreFor5Scale('metacognition')) }})</span>
                  <div class="c-bar"><div class="c-fill" :style="{ width: getScoreFor5Scale('metacognition') * 20 + '%' }"></div></div>
                </div>
                <div class="challenge-item" :class="{ 'attention': isLowScore('social_emotional') }">
                  <span class="c-icon">💬</span>
                  <span class="c-label">社情能力</span>
                  <span class="c-score">● {{ getScoreFor5Scale('social_emotional') }}</span>
                  <span class="c-level">({{ getLevelDescription(getScoreFor5Scale('social_emotional')) }})</span>
                  <div class="c-bar"><div class="c-fill" :style="{ width: getScoreFor5Scale('social_emotional') * 20 + '%' }"></div></div>
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- 维度详情弹窗（保留原有功能） -->
        <div class="dimension-detail-section" v-if="expandedDimension && overallAnalysisData">
          <div class="detail-panel">
            <div class="detail-header">
              <div class="detail-title">
                <span class="detail-icon">{{ getDimensionIcon(expandedDimension) }}</span>
                <span>{{ getDimensionName(expandedDimension) }} - 详细分析</span>
              </div>
              <el-button type="info" text @click="expandedDimension = null">
                <el-icon><Close /></el-icon>
                收起
              </el-button>
            </div>

            <div class="detail-feedback" v-if="overallAnalysisData.feedback_dict[expandedDimension]">
              <p>{{ overallAnalysisData.feedback_dict[expandedDimension] }}</p>
            </div>

            <div class="sub-feedback-toggle" v-if="overallAnalysisData.dimension_feedback_dict && overallAnalysisData.dimension_feedback_dict[expandedDimension]">
              <el-button type="primary" text @click="showSubFeedback = !showSubFeedback">
                {{ showSubFeedback ? '收起详细反馈' : '查看详细反馈' }}
                <el-icon class="toggle-icon" :class="{ 'rotated': showSubFeedback }"><ArrowDown /></el-icon>
              </el-button>

              <div v-if="showSubFeedback" class="sub-feedback-content">
                <div v-for="(feedback, subKey) in overallAnalysisData.dimension_feedback_dict[expandedDimension]" :key="subKey" class="sub-feedback-item">
                  <div class="sub-feedback-name">{{ getSubDimensionName(subKey, expandedDimension) }}</div>
                  <div class="sub-feedback-text">{{ feedback }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- 智能对话助手 -->
      <PortraitChat
        v-if="showLearningPortrait && showChat"
        :student-info="studentInfo"
        :portrait-data="overallAnalysisData"
        @close="showChat = false"
      />

      <!-- 浮动触发按钮 -->
      <el-button
        v-if="showLearningPortrait && !showChat"
        class="chat-trigger-btn"
        type="primary"
        size="large"
        circle
        @click="showChat = true"
      >
        <el-icon :size="24"><ChatDotSquare /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, Close, ChatDotSquare, Document, ChatDotRound, List, ArrowDown, ArrowRight, TrendCharts, DataAnalysis } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getHistory } from '@/api/assessments.js'
import PortraitChat from '@/components/PortraitChat.vue'

// 路由
const router = useRouter()

// 数据状态
const studentValidated = ref(false)
const validating = ref(false)
const showLearningPortrait = ref(false)
const showChat = ref(false)  // 控制对话框显示
const activeFeedbackNames = ref(['fluency', 'flexibility', 'originality', 'elaboration'])
const radarChartData = ref(null)
// 新增响应式数据：全体测评分析数据
const overallAnalysisData = ref(null)
// 仪表盘展开状态
const expandedDimension = ref(null)
const showSubFeedback = ref(false)

// 学生表单
const studentForm = reactive({
  name: '',
  id: ''
})

// 学生信息
const studentInfo = reactive({
  name: '',
  id: ''
})

// 测评数据
const assessments = ref([])

// 测评类型定义
const assessmentTypes = ref([
  { 
    label: '认知能力', 
    value: 'cognitive_strategy',
    description: '评估学生的认知策略运用能力，包括复述、精加工和组织策略等'
  },
  { 
    label: '元认知能力', 
    value: 'metacognition',
    description: '评估学生的元认知能力，包括自我监控、自我整合等能力'
  },
  { 
    label: '批判性思维', 
    value: 'critical_thinking',
    description: '评估学生的批判性思维能力，包括分析逻辑、系统规划等'
  },
  { 
    label: '学习动机', 
    value: 'learning_motivation',
    description: '评估学生的学习动机水平，包括自主性、胜任感和归属感'
  },
  { 
    label: '社会情感能力', 
    value: 'social_emotional',
    description: '评估学生的社会情感能力，包括自我管理、人际关系等'
  }
])

// 反馈数据
const feedbackData = ref({})

// 雷达图引用
const radarChartRef = ref(null)
let radarChart = null

// 维度顺序定义
const dimensionOrder = [
  'cognitive_strategy',
  'metacognition',
  'critical_thinking',
  'learning_motivation',
  'social_emotional'
]

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入学生姓名', trigger: 'blur' }
  ],
  id: [
    { required: true, message: '请输入学号', trigger: 'blur' }
  ]
}

// 表单引用
const studentFormRef = ref(null)

// 验证学生信息
const validateStudent = async () => {
  if (!studentFormRef.value) return
  
  await studentFormRef.value.validate(async (valid) => {
    if (valid) {
      validating.value = true
      try {
        // 导入验证学生API
        const { verifyStudent } = await import('@/api/students.js')
        
        // 调用后端API验证学生信息
        const res = await verifyStudent({
          name: studentForm.name,
          student_id: studentForm.id
        })
        
        if (res.code === 200) {
          // 验证通过，保存学生信息
          studentInfo.name = studentForm.name
          studentInfo.id = studentForm.id
          studentValidated.value = true
          
          // 获取测评历史
          await fetchAssessmentHistory()
          
          ElMessage.success('学生信息验证成功')
        } else {
          ElMessage.error(res.message || '学生信息验证失败')
        }
      } catch (error) {
        console.error('验证失败:', error)
        ElMessage.error(error.message || '学生信息验证失败')
      } finally {
        validating.value = false
      }
    }
  })
}

// 重置验证状态
const resetValidation = () => {
  studentValidated.value = false
  studentForm.name = ''
  studentForm.id = ''
  assessments.value = []
  showLearningPortrait.value = false
  feedbackData.value = {}
}

// 获取测评历史
const fetchAssessmentHistory = async () => {
  try {
    const res = await getHistory(studentInfo.id)
    assessments.value = res.data.assessments || []
    console.log('获取到的测评历史:', assessments.value)
  } catch (error) {
    console.error('获取测评历史失败:', error)
    assessments.value = []
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  return dateString.split('T')[0]
}

// 获取等级标签类型
const getGradeTagType = (grade) => {
  const typeMap = {
    'A': 'success',
    'B': 'warning',
    'C': 'info',
    'D': 'danger'
  }
  return typeMap[grade] || 'info'
}

// 获取水平标签类型
const getLevelTagType = (level) => {
  const levelMap = {
    '优秀': 'success',
    '良好': 'warning',
    '一般': 'info',
    '需改进': 'danger'
  }
  return levelMap[level] || 'info'
}

// 前往测评
const goToAssessment = () => {
  router.push('/assessment')
}

// 查看测评详情
const viewAssessmentDetail = (assessment) => {
  // 跳转到分析页面查看具体测评详情
  router.push(`/analysis?assessmentId=${assessment.assessment_id}`)
}

// 生成学习力画像
const generateLearningPortrait = async () => {
  showLearningPortrait.value = true
  
  // 如果有测评数据，使用全体测评分析API
  if (assessments.value.length > 0) {
    // 导入分析API，包括新增的全体测评分析接口
    const { getOverallAnalysis } = await import('@/api/analysis.js')
    
    try {
      // 获取全体测评分析数据
      const overallRes = await getOverallAnalysis(studentInfo.id)
      if (overallRes.code === 200) {
        // 保存全体测评分析数据
        overallAnalysisData.value = overallRes.data
        console.log('获取到的全体测评分析数据:', overallRes.data)
      }
    } catch (error) {
      console.error('获取全体测评分析数据失败:', error)
      ElMessage.error('获取分析数据失败')
    }
  }
  
  // 等待DOM更新后初始化图表
  await nextTick()
  initRadarChart()
}

// 初始化雷达图（宏观能力地形图）
const initRadarChart = async () => {
  if (!radarChartRef.value) return

  // 销毁之前的图表实例
  if (radarChart) {
    radarChart.dispose()
  }

  // 初始化图表
  radarChart = echarts.init(radarChartRef.value)

  // 准备数据
  const totalDict = overallAnalysisData.value?.total_dict || {}

  // 雷达图指标（8个维度，扩展显示）
  const radarIndicators = [
    { name: '学习动机', key: 'learning_motivation' },
    { name: '成就目标', key: 'learning_motivation' },  // 复用
    { name: '自觉能感', key: 'learning_motivation' },  // 复用
    { name: '学习风格', key: 'metacognition' },
    { name: '学习策略(综合)', key: 'cognitive_strategy' },
    { name: '创造力', key: 'critical_thinking' },
    { name: '问题解决', key: 'critical_thinking' },
    { name: '学业延迟满足', key: 'social_emotional' },
    { name: '学习体验', key: 'social_emotional' }
  ]

  // 转换为5分制数据
  const radarData = radarIndicators.map(ind => {
    const score = totalDict[ind.key] || 0
    return convertTo5Scale(score)
  })

  const option = {
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: radarIndicators.map(ind => ({
        name: ind.name,
        max: 5
      })),
      center: ['50%', '50%'],
      radius: '65%',
      startAngle: 90,
      splitNumber: 4,
      shape: 'polygon',
      axisName: {
        color: '#333',
        fontSize: 11,
        fontWeight: 500
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(64, 158, 255, 0.05)', 'rgba(64, 158, 255, 0.1)',
                  'rgba(64, 158, 255, 0.15)', 'rgba(64, 158, 255, 0.2)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(64, 158, 255, 0.3)'
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(64, 158, 255, 0.3)'
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: radarData,
        name: '能力值',
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#409eff',
          width: 2
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.6)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ])
        },
        itemStyle: {
          color: '#409eff',
          borderColor: '#fff',
          borderWidth: 2
        }
      }]
    }]
  }

  radarChart.setOption(option)

  // 监听窗口大小变化
  const handleResize = () => {
    if (radarChart) {
      radarChart.resize()
    }
  }
  window.addEventListener('resize', handleResize)
  resizeHandlerRef = handleResize
}

// 窗口大小变化处理器引用
let resizeHandlerRef = null

// ========== 新增：专业报告风格辅助函数 ==========

// 获取当前日期
const getCurrentDate = () => {
  const now = new Date()
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
}

// 将100分制转换为5分制
const convertTo5Scale = (score) => {
  const s = Number(score) || 0
  return (s / 20).toFixed(1)
}

// 获取维度的5分制分数
const getScoreFor5Scale = (key) => {
  if (!overallAnalysisData.value || !overallAnalysisData.value.total_dict) return 0
  const score = overallAnalysisData.value.total_dict[key] || 0
  return convertTo5Scale(score)
}

// 获取等级描述
const getLevelDescription = (score) => {
  const s = Number(score)
  if (s >= 4.5) return '非常好'
  if (s >= 3.5) return '较好'
  if (s >= 2.5) return '一般'
  if (s >= 1.5) return '较差'
  return '需改进'
}

// 获取总体等级文字
const getOverallLevelText = () => {
  const avgScore = getOverallLevelScore()
  return getLevelDescription(avgScore)
}

// 获取总体等级分数（5分制）
const getOverallLevelScore = () => {
  if (!overallAnalysisData.value || !overallAnalysisData.value.total_dict) return 0
  const scores = Object.values(overallAnalysisData.value.total_dict)
  const avg = scores.reduce((sum, s) => sum + Number(s), 0) / scores.length
  return convertTo5Scale(avg)
}

// 获取总体等级CSS类
const getOverallLevelClass = () => {
  const score = Number(getOverallLevelScore())
  if (score >= 4.5) return 'level-excellent'
  if (score >= 3.5) return 'level-good'
  if (score >= 2.5) return 'level-average'
  return 'level-poor'
}

// 生成核心简述
const generateCoreSummary = () => {
  if (!overallAnalysisData.value || !overallAnalysisData.value.total_dict) {
    return '完成所有测评后将生成您的核心能力简述。'
  }

  const totalDict = overallAnalysisData.value.total_dict
  let maxKey = null, minKey = null
  let maxScore = -1, minScore = 101

  Object.keys(totalDict).forEach(key => {
    const score = Number(totalDict[key])
    if (score > maxScore) { maxScore = score; maxKey = key }
    if (score < minScore) { minScore = score; minKey = key }
  })

  const maxName = getDimensionName(maxKey)
  const minName = getDimensionName(minKey)

  return `您具备卓越的自主学习能力。您的${maxName}非常强，且擅长运用高级的元认知策略。当前的小短板在于"${minName}"的日常使用上。`
}

// 获取多维度平均分
const getAverageScore = (keys) => {
  if (!overallAnalysisData.value || !overallAnalysisData.value.total_dict) return 0
  let sum = 0, count = 0
  keys.forEach(key => {
    if (overallAnalysisData.value.total_dict[key]) {
      sum += Number(overallAnalysisData.value.total_dict[key])
      count++
    }
  })
  return count > 0 ? convertTo5Scale(sum / count) : 0
}

// 获取子维度图标
const getSubIcon = (subKey) => {
  const iconMap = {
    'autonomy': '🎯', 'competence': '💪', 'relatedness': '🤝',
    'rehearsal': '📝', 'elaboration': '🔍', 'organization': '📊', 'resource_management': '📚',
    'monitoring': '👁️', 'integration': '🔗', 'differentiation': '🎭', 'decentration': '🌐',
    'open_mindedness': '💭', 'analytical_logical_skills': '🧮', 'systematic_planning': '📋',
    'intellectual_curiosity': '🔬', 'cognitive_maturity': '🎓',
    'responsible_decision_making': '⚖️', 'social_awareness': '👥',
    'self_management': '🎛️', 'relationship_skills': '💬'
  }
  return iconMap[subKey] || '•'
}

// 判断是否为重点区域（高分）
const isFocusArea = (key) => {
  const score = Number(getScoreFor5Scale(key))
  return score >= 4.0
}

// 判断是否有关注区域（低分）
const hasAttentionArea = () => {
  if (!overallAnalysisData.value || !overallAnalysisData.value.total_dict) return false
  return Object.values(overallAnalysisData.value.total_dict).some(s => Number(s) < 60)
}

// 判断是否为低分项
const isLowScore = (key) => {
  const score = Number(getScoreFor5Scale(key))
  return score < 3.0
}

// 获取进度条渐变色
const getBarGradient = (score) => {
  const s = Number(score)
  if (s >= 4.0) return 'linear-gradient(90deg, #67c23a, #85ce61)'
  if (s >= 3.0) return 'linear-gradient(90deg, #e6a23c, #f0c78a)'
  if (s >= 2.0) return 'linear-gradient(90deg, #909399, #a6a9ad)'
  return 'linear-gradient(90deg, #f56c6c, #f89898)'
}

// ========== 原有辅助函数 ==========

// 获取维度名称
const getDimensionName = (key) => {
  const nameMap = {
    'fluency': '流畅性',
    'flexibility': '灵活性',
    'originality': '独创性',
    'elaboration': '精细性',
    'cognitive_strategy': '认知能力',
    'metacognition': '元认知能力',
    'critical_thinking': '批判性思维',
    'learning_motivation': '学习动机',
    'social_emotional': '社会情感能力',
    'overall': '总体评价'
  }
  return nameMap[key] || key
}

// 获取子维度名称
const getSubDimensionName = (subKey, parentKey) => {
  const subDimensionMap = {
    // 认知策略的子维度
    'cognitive_strategy': {
      'rehearsal': '复述策略',
      'elaboration': '精加工策略',
      'organization': '组织策略',
      'resource_management': '资源管理策略'
    },
    // 元认知能力的子维度
    'metacognition': {
      'monitoring': '自我监测',
      'integration': '自我整合',
      'differentiation': '他人分化',
      'decentration': '他人去中心化'
    },
    // 批判性思维的子维度
    'critical_thinking': {
      'open_mindedness': '思维的开放性',
      'analytical_logical_skills': '分析性与逻辑性',
      'systematic_planning': '系统性与规划性',
      'intellectual_curiosity': '求知欲与探索精神',
      'cognitive_maturity': '认知成熟度'
    },
    // 学习动机的子维度
    'learning_motivation': {
      'autonomy': '自主性',
      'competence': '胜任感',
      'relatedness': '关系需求'
    },
    // 社会情感能力的子维度
    'social_emotional': {
      'responsible_decision_making': '负责任的决策',
      'social_awareness': '社会知觉',
      'self_management': '自我管理',
      'relationship_skills': '同伴关系'
    }
  }

  if (subDimensionMap[parentKey] && subDimensionMap[parentKey][subKey]) {
    return subDimensionMap[parentKey][subKey]
  }
  return subKey
}

// 获取子维度分数
const getSubDimensionScore = (parentKey, subKey) => {
  if (overallAnalysisData.value &&
      overallAnalysisData.value.dimension_scores_dict &&
      overallAnalysisData.value.dimension_scores_dict[parentKey]) {
    const score = overallAnalysisData.value.dimension_scores_dict[parentKey][subKey]
    return score !== undefined ? Number(score).toFixed(2) : 'N/A'
  }
  return 'N/A'
}

// 获取维度描述
const getDimensionDescription = (key) => {
  const descriptionMap = {
    'fluency': '指思维的流畅程度，即在限定时间内产生观念的数量',
    'flexibility': '指思维的灵活程度，即产生不同类别观念的能力',
    'originality': '指思维的独特程度，即产生新颖、独特观念的能力',
    'elaboration': '指思维的精细程度，即对观念进行详细阐述的能力',
    'cognitive_strategy': '认知策略运用能力，包括复述、精加工和组织策略等',
    'metacognition': '元认知能力，包括自我监控、自我整合等能力',
    'critical_thinking': '批判性思维能力，包括分析逻辑、系统规划等',
    'learning_motivation': '学习动机水平，包括自主性、胜任感和归属感',
    'social_emotional': '社会情感能力，包括自我管理、人际关系等'
  }
  return descriptionMap[key] || '能力维度'
}

// 获取评级卡片对应的CSS类名
const getRatingCardClass = (level) => {
  const levelClassMap = {
    'A': 'rating-excellent',
    'B': 'rating-good',
    'C': 'rating-average',
    'D': 'rating-poor'
  }
  return levelClassMap[level] || 'rating-default'
}

// 获取维度图标
const getDimensionIcon = (key) => {
  const iconMap = {
    'cognitive_strategy': '🧠',
    'metacognition': '🎯',
    'critical_thinking': '💡',
    'learning_motivation': '🔥',
    'social_emotional': '💬'
  }
  return iconMap[key] || '📊'
}

// 根据key获取分数
const getScoreByKey = (key) => {
  if (overallAnalysisData.value && overallAnalysisData.value.total_dict) {
    const score = overallAnalysisData.value.total_dict[key]
    return score !== undefined ? Number(score).toFixed(0) : 'N/A'
  }
  return 'N/A'
}

// 获取综合等级
const getOverallGrade = () => {
  if (!overallAnalysisData.value || !overallAnalysisData.value.level_dict) return '-'
  const levels = Object.values(overallAnalysisData.value.level_dict)
  const gradeScore = { 'A': 4, 'B': 3, 'C': 2, 'D': 1 }
  const avgScore = levels.reduce((sum, l) => sum + (gradeScore[l] || 0), 0) / levels.length
  if (avgScore >= 3.5) return 'A'
  if (avgScore >= 2.5) return 'B'
  if (avgScore >= 1.5) return 'C'
  return 'D'
}

// 获取综合等级CSS类
const getOverallGradeClass = () => {
  const grade = getOverallGrade()
  return getRatingCardClass(grade)
}

// 切换展开维度
const toggleDimension = (key) => {
  if (expandedDimension.value === key) {
    expandedDimension.value = null
  } else {
    expandedDimension.value = key
    showSubFeedback.value = false
  }
}

// 获取进度条颜色
const getProgressColor = (score) => {
  const s = Number(score)
  if (s >= 85) return '#67c23a'
  if (s >= 70) return '#e6a23c'
  if (s >= 60) return '#909399'
  return '#f56c6c'
}

// 截断反馈文字
const truncateFeedback = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// 关键发现（计算属性）
const keyFindings = computed(() => {
  if (!overallAnalysisData.value || !overallAnalysisData.value.level_dict || !overallAnalysisData.value.total_dict) {
    return {
      strength: '完成所有测评后将显示您的优势领域',
      improvement: '完成所有测评后将显示待提升领域',
      suggestion: '完成所有测评后将获得个性化建议'
    }
  }

  const levelDict = overallAnalysisData.value.level_dict
  const totalDict = overallAnalysisData.value.total_dict
  const feedbackDict = overallAnalysisData.value.feedback_dict || {}

  // 找出最高分和最低分的维度
  let maxKey = null, minKey = null
  let maxScore = -1, minScore = 101

  Object.keys(totalDict).forEach(key => {
    const score = Number(totalDict[key])
    if (score > maxScore) {
      maxScore = score
      maxKey = key
    }
    if (score < minScore) {
      minScore = score
      minKey = key
    }
  })

  // 生成关键发现
  const strengthName = getDimensionName(maxKey)
  const improveName = getDimensionName(minKey)

  return {
    strength: `${strengthName}表现突出（${levelDict[maxKey]}级，${maxScore.toFixed(0)}分）`,
    improvement: `${improveName}有提升空间（${levelDict[minKey]}级，${minScore.toFixed(0)}分）`,
    suggestion: generateSuggestion(minKey, feedbackDict[minKey])
  }
})

// 生成建议
const generateSuggestion = (key, feedback) => {
  const suggestionMap = {
    'cognitive_strategy': '建议多练习知识整理和归纳，使用思维导图等工具',
    'metacognition': '建议在学习过程中加强自我反思和监控',
    'critical_thinking': '建议多参与讨论和辩论，培养批判性分析习惯',
    'learning_motivation': '建议设定明确的学习目标，增强学习的内在动力',
    'social_emotional': '建议多参与团队活动，提升人际沟通能力'
  }
  return suggestionMap[key] || '建议针对薄弱领域进行专项提升'
}

// 表格数据
const scoreTableData = computed(() => {
  // 优先使用全体测评分析数据
  if (overallAnalysisData.value && overallAnalysisData.value.level_dict && overallAnalysisData.value.total_dict) {
    const levelDict = overallAnalysisData.value.level_dict
    const totalDict = overallAnalysisData.value.total_dict
    
    return Object.keys(levelDict).map(key => ({
      dimension: getDimensionName(key),
      score: totalDict[key] || 0,
      level: levelDict[key] || 'N/A',
      description: getDimensionDescription(key)
    }))
  }
  // 备用方案：使用最新测评数据
  else if (assessments.value.length > 0) {
    const latestScores = assessments.value[0].final_scores || {}
    const scoreDescriptions = {
      'fluency': '指思维的流畅程度，即在限定时间内产生观念的数量',
      'flexibility': '指思维的灵活程度，即产生不同类别观念的能力',
      'originality': '指思维的独特程度，即产生新颖、独特观念的能力',
      'elaboration': '指思维的精细程度，即对观念进行详细阐述的能力'
    }
    
    return [
      {
        dimension: '流畅性',
        score: latestScores.fluency || 0,
        level: getScoreLevel(latestScores.fluency || 0),
        description: scoreDescriptions.fluency
      },
      {
        dimension: '灵活性',
        score: latestScores.flexibility || 0,
        level: getScoreLevel(latestScores.flexibility || 0),
        description: scoreDescriptions.flexibility
      },
      {
        dimension: '独创性',
        score: latestScores.originality || 0,
        level: getScoreLevel(latestScores.originality || 0),
        description: scoreDescriptions.originality
      },
      {
        dimension: '精细性',
        score: latestScores.elaboration || 0,
        level: getScoreLevel(latestScores.elaboration || 0),
        description: scoreDescriptions.elaboration
      }
    ]
  }
  
  return []
})

// 判断是否有任何测评完成
const hasAnyAssessmentCompleted = computed(() => {
  return assessments.value.length > 0
})

// 判断是否所有测评类型都已完成
const allAssessmentsCompleted = computed(() => {
  // 检查每种测评类型是否都有对应的完成记录
  return assessmentTypes.value.every(assessmentType => {
    return isAssessmentCompleted(assessmentType.value)
  })
})

// 判断指定类型的测评是否已完成
const isAssessmentCompleted = (assessmentType) => {
  // 遍历已有的测评记录，检查是否有匹配的测评类型
  return assessments.value.some(assessment => {
    // 从测评记录中提取测评类型信息
    // 注意：这里假设后端返回的数据中包含evaluation_type字段
    return assessment.evaluation_type === assessmentType
  })
}

// 处理测评卡片点击事件
const handleAssessmentCardClick = (assessmentType) => {
  // 如果该类型测评已完成，查看测评记录
  if (isAssessmentCompleted(assessmentType)) {
    // 找到对应的测评记录
    const completedAssessment = assessments.value.find(assessment => 
      assessment.evaluation_type === assessmentType
    )
    if (completedAssessment) {
      viewAssessmentDetail(completedAssessment)
    }
  } else {
    // 如果未完成，前往测评页面并预选该类型
    router.push({
      path: '/assessment',
      query: { type: assessmentType }
    })
  }
}

// 根据得分获取等级
const getScoreLevel = (score) => {
  if (score >= 8.5) return '优秀'
  if (score >= 7.0) return '良好'
  if (score >= 6.0) return '一般'
  return '需改进'
}

// 导出报告
const exportReport = () => {
  ElMessage.success('报告导出功能将在后续版本中实现')
}

// 组件卸载时的清理工作
onUnmounted(() => {
  // 销毁图表实例
  if (radarChart) {
    radarChart.dispose()
    radarChart = null
  }

  // 移除窗口大小变化监听
  if (resizeHandlerRef) {
    window.removeEventListener('resize', resizeHandlerRef)
    resizeHandlerRef = null
  }
})
</script>

<style scoped>
.persona-container {
  max-width: 1200px;
  margin: 0 auto;
}

.mb-10 {
  margin-bottom: 10px;
}

.mb-20 {
  margin-bottom: 20px;
}

.mb-30 {
  margin-bottom: 30px;
}

.mt-30 {
  margin-top: 30px;
}

.input-card {
  max-width: 500px;
  margin: 50px auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.student-info-card {
  text-align: center;
}

.student-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.info-details h3 {
  margin: 0 0 10px 0;
}

.info-details p {
  margin: 0;
  color: #666;
}

.no-assessment {
  text-align: center;
  padding: 40px 0;
}

.generate-report-section {
  text-align: center;
}

.student-basic-info {
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

.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.chart-card {
  margin-bottom: 20px;
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

.feedback-list {
  padding: 10px 0;
}

.feedback-item {
  display: flex;
  margin-bottom: 16px;
}

.feedback-label {
  font-weight: bold;
  color: #303133;
  min-width: 100px;
}

.feedback-content {
  color: #606266;
  line-height: 1.6;
}

.learning-portrait-card {
  margin-bottom: 30px;
}

/* 测评卡片样式 */
.assessment-cards-container {
  width: 100%;
}

.assessment-cards-container h3 {
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: bold;
}

.assessment-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.assessment-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
}

.assessment-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.assessment-card.completed {
  border-color: #67c23a;
}

.assessment-card.pending {
  border-color: #f56c6c;
}

.card-content {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.assessment-name {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.status-icon {
  font-size: 20px;
}

.completed-icon {
  color: #67c23a;
}

.pending-icon {
  color: #f56c6c;
}

.card-status {
  margin-bottom: 15px;
}

.card-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.no-assessment-prompt {
  text-align: center;
  padding: 40px 0;
}

.no-assessment-prompt {
  margin-top: 20px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.completion-prompt {
  margin-top: 20px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

/* ========== 专业报告风格样式 ========== */

/* 报告容器 */
.portrait-report {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 30px;
}

/* 报告标题 */
.report-title {
  text-align: center;
  font-size: 22px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e4e7ed;
}

/* 左右分栏布局 */
.report-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 1024px) {
  .report-layout {
    grid-template-columns: 1fr;
  }
}

.report-left, .report-right {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 基本信息卡片 */
.info-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.info-text {
  flex: 1;
}

.info-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12px;
}

.info-row {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
}

.info-value {
  color: #303133;
  font-weight: 500;
}

.overall-level-badge {
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 4px;
}

.overall-level-badge.level-excellent { color: #67c23a; background: #f0f9eb; }
.overall-level-badge.level-good { color: #e6a23c; background: #fdf6ec; }
.overall-level-badge.level-average { color: #909399; background: #f5f5f5; }
.overall-level-badge.level-poor { color: #f56c6c; background: #fef0f0; }

.level-score {
  font-size: 12px;
  color: #909399;
  margin-left: 4px;
}

/* 渐变圆形徽章 */
.overall-badge {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f7971e 0%, #67c23a 50%, #409eff 100%);
  color: white;
  text-align: center;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.3);
}

.overall-badge .badge-label {
  font-size: 10px;
  opacity: 0.9;
}

.overall-badge .badge-text {
  font-size: 16px;
  font-weight: bold;
}

.core-summary {
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.summary-label {
  font-weight: bold;
  color: #303133;
}

/* 模块卡片通用样式 */
.module-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.module-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.module-icon {
  font-size: 20px;
}

.module-title {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
}

.module-subtitle {
  font-size: 11px;
  color: #909399;
}

.scale-legend {
  display: flex;
  gap: 6px;
  margin-left: auto;
  font-size: 10px;
}

.scale-legend.small {
  font-size: 9px;
}

.scale-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.scale-dot.active {
  background: #409eff;
  color: white;
}

.focus-tag, .attention-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  margin-left: auto;
}

.focus-tag {
  background: #fef0f0;
  color: #f56c6c;
}

.attention-tag {
  background: #fdf6ec;
  color: #e6a23c;
}

.star {
  color: #f56c6c;
}

/* 动机项目样式 */
.motivation-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.motivation-item {
  padding-bottom: 12px;
  border-bottom: 1px dashed #e4e7ed;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 14px;
}

.item-icon {
  font-size: 16px;
}

.item-label {
  font-weight: 600;
  color: #303133;
}

.item-score {
  color: #409eff;
  font-weight: bold;
}

.item-level {
  font-size: 12px;
  color: #67c23a;
}

/* 刻度进度条 */
.scale-bar-container {
  position: relative;
}

.scale-bar {
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.scale-fill {
  height: 100%;
  background: linear-gradient(90deg, #f56c6c, #e6a23c, #67c23a);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.scale-dots {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 8px;
  display: flex;
  justify-content: space-between;
  padding: 0 2px;
}

.scale-dots .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255,255,255,0.8);
  margin-top: 1px;
}

.scale-dots .dot.filled {
  background: white;
}

/* 子动机项目 */
.sub-motivation-item {
  padding-left: 24px;
}

.sub-item-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  margin-bottom: 4px;
}

.sub-icon {
  font-size: 14px;
}

.sub-label {
  color: #606266;
}

.sub-score {
  color: #409eff;
  font-weight: 500;
}

.sub-level {
  font-size: 11px;
  color: #909399;
}

.sub-bar-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sub-bar {
  flex: 1;
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.sub-fill {
  height: 100%;
  background: linear-gradient(90deg, #f56c6c, #e6a23c, #67c23a);
  border-radius: 3px;
}

.bar-dashes {
  font-size: 10px;
  color: #c0c4cc;
  letter-spacing: 2px;
}

/* 策略模块 */
.strategy-group {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.strategy-group:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.group-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.group-score {
  font-size: 13px;
  color: #409eff;
  font-weight: bold;
}

.strategy-items-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.strategy-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.s-label {
  flex: 0 0 80px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.s-bar {
  flex: 1;
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
  min-width: 40px;
}

.s-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 3px;
}

.s-score {
  flex: 0 0 24px;
  text-align: right;
  color: #303133;
  font-weight: 500;
}

/* 雷达图模块 */
.radar-module {
  min-height: 320px;
}

.radar-chart-container {
  width: 100%;
  height: 280px;
}

.radar-chart {
  width: 100%;
  height: 100%;
}

/* 高阶能力项目 */
.higher-order-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ho-item {
  padding-bottom: 10px;
  border-bottom: 1px dashed #e4e7ed;
}

.ho-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.ho-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 13px;
}

.ho-icon {
  font-size: 14px;
}

.ho-label {
  font-weight: 500;
  color: #303133;
}

.ho-score {
  color: #409eff;
  font-weight: bold;
}

.ho-level {
  font-size: 11px;
  color: #67c23a;
}

.ho-bar-container {
  position: relative;
}

.ho-bar {
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.ho-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.ho-dots {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 8px;
  display: flex;
  justify-content: space-between;
  padding: 0 4px;
}

.ho-dots .dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: rgba(255,255,255,0.6);
  margin-top: 2px;
}

/* 挑战模块 */
.challenge-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.challenge-item {
  display: grid;
  grid-template-columns: 20px 80px auto 60px 1fr;
  gap: 6px;
  align-items: center;
  font-size: 12px;
  padding: 8px;
  border-radius: 6px;
  transition: background 0.3s;
}

.challenge-item.attention {
  background: #fef0f0;
}

.c-icon {
  font-size: 14px;
}

.c-label {
  color: #303133;
  font-weight: 500;
}

.c-score {
  color: #409eff;
  font-weight: bold;
}

.c-level {
  font-size: 11px;
  color: #909399;
}

.c-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.c-fill {
  height: 100%;
  background: linear-gradient(90deg, #f56c6c, #e6a23c, #67c23a);
  border-radius: 3px;
}

/* 维度详情面板 */
.dimension-detail-section {
  margin-bottom: 24px;
}

.detail-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e4e7ed;
}

.detail-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.detail-icon {
  font-size: 24px;
}

.detail-feedback {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #409eff;
}

.detail-feedback p {
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
}

/* 子维度进度条 */
.sub-dimensions-bars {
  margin-bottom: 20px;
}

.sub-title {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 16px;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sub-name {
  font-size: 14px;
  color: #303133;
}

.sub-score {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

/* 子维度反馈折叠 */
.sub-feedback-toggle {
  margin-top: 16px;
}

.toggle-icon {
  margin-left: 4px;
  transition: transform 0.3s ease;
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

.sub-feedback-content {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.sub-feedback-item {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.sub-feedback-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.sub-feedback-text {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

/* 所有维度概览 */
.all-dimensions-overview {
  margin-bottom: 24px;
}

.overview-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.overview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.overview-item:hover {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  transform: translateX(4px);
}

.overview-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.overview-icon {
  font-size: 20px;
}

.overview-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.overview-right {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #909399;
}

.overview-feedback {
  font-size: 13px;
  color: #909399;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .overview-feedback {
    display: none;
  }
}

/* 智能对话助手浮动按钮 */
.chat-trigger-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
  z-index: 1999;
  transition: all 0.3s ease;
}

.chat-trigger-btn:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5);
}

.chat-trigger-btn:active {
  transform: translateY(-2px) scale(1.02);
}
</style>
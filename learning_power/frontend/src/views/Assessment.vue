<template>
  <div class="assessment">
    <!-- 开始测评表单 -->
    <el-card v-if="!showEvaluationTypeSelection && !sessionStarted && !assessmentCompleted">
      <template #header>
        <div class="card-header">
          <span>开始测评</span>
        </div>
      </template>

      <el-form :model="startForm" label-width="100px" style="max-width: 500px">
        <el-form-item label="学生姓名">
          <el-input v-model="startForm.student_name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="学号">
          <el-input v-model="startForm.student_id" placeholder="请输入学号" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="startAssessment" :loading="loading">
            开始测评
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 测评指标选择 -->
    <el-card v-else-if="showEvaluationTypeSelection && !sessionStarted && !assessmentCompleted"
             v-loading="loading"
             :element-loading-text="loadingMessage"
             element-loading-background="rgba(255, 255, 255, 0.9)">
      <template #header>
        <div class="card-header">
          <span>选择测评指标</span>
        </div>
      </template>

      <div class="evaluation-types">
        <div v-for="(type, index) in evaluationTypes" :key="type.value" class="type-card"
          @click="selectEvaluationType(type.value)">
          <div class="type-icon">
            <el-icon>
              <ChatDotSquare />
            </el-icon>
          </div>
          <div class="type-label">{{ type.label }}</div>
        </div>
      </div>

      <div class="back-button">
        <el-button @click="backToStart">
          <el-icon>
            <ArrowLeft />
          </el-icon>
          返回
        </el-button>
      </div>
    </el-card>

    <!-- 测评进行中 -->
    <div v-else-if="sessionStarted && !assessmentCompleted" class="chat-container">
      <!-- 顶部字幕按钮 -->
      <div class="subtitle-toggle">
        <el-button
          :type="showSubtitle ? 'primary' : 'default'"
          @click="showSubtitle = !showSubtitle"
          class="subtitle-btn"
          circle
        >
          <el-icon><ChatLineSquare /></el-icon>
        </el-button>
      </div>

      <!-- 右上角退出按钮 -->
      <div class="exit-button-wrapper">
        <el-button
          type="danger"
          @click="showExitConfirm"
          class="exit-assessment-btn"
        >
          <el-icon><Close /></el-icon>
          <span>退出测评</span>
        </el-button>
      </div>

      <!-- 字幕展开区域 -->
      <transition name="subtitle-slide">
        <div v-if="showSubtitle" class="subtitle-panel">
          <div class="subtitle-content">
            {{ currentAIText || '等待AI提问...' }}
          </div>
        </div>
      </transition>

      <!-- 中间AI头像区域 -->
      <div class="ai-avatar-container">
        <!-- AI头像和声波的容器 -->
        <div class="avatar-with-waves">
          <!-- 声波扩散动画 -->
          <div v-if="isAISpeaking" class="sound-waves">
            <div class="wave wave-1"></div>
            <div class="wave wave-2"></div>
            <div class="wave wave-3"></div>
          </div>

          <!-- AI头像 -->
          <div class="ai-avatar-circle">
            <div class="avatar-image">
              <!-- 动态视频头像：AI 说话时播放说话视频，不说话时播放待机视频 -->
              <video
                v-if="avatarVideoEnabled"
                :src="isAISpeaking ? avatarTalkingUrl : avatarIdleUrl"
                :key="isAISpeaking ? 'talking' : 'idle'"
                autoplay
                loop
                muted
                playsinline
                class="avatar-video"
              ></video>
              <!-- 备用：CSS 绘制的卡通头像 -->
              <div v-else class="cute-avatar">
                <!-- 头部背景 -->
                <div class="head-bg"></div>

                <!-- 头发层 -->
                <div class="hair-layer">
                  <!-- 后发 -->
                  <div class="hair-back-left"></div>
                  <div class="hair-back-right"></div>

                  <!-- 双马尾 -->
                  <div class="ponytail ponytail-left">
                    <div class="ponytail-strand"></div>
                    <div class="ponytail-strand"></div>
                  </div>
                  <div class="ponytail ponytail-right">
                    <div class="ponytail-strand"></div>
                    <div class="ponytail-strand"></div>
                  </div>
                </div>

                <!-- 脸部 -->
                <div class="face-cute">
                  <!-- 大眼睛 -->
                  <div class="big-eyes">
                    <div class="big-eye left-eye">
                      <div class="eye-white"></div>
                      <div class="eye-iris"></div>
                      <div class="eye-pupil"></div>
                      <div class="eye-highlight highlight-1"></div>
                      <div class="eye-highlight highlight-2"></div>
                      <div class="eyelash eyelash-1"></div>
                      <div class="eyelash eyelash-2"></div>
                      <div class="eyelash eyelash-3"></div>
                    </div>
                    <div class="big-eye right-eye">
                      <div class="eye-white"></div>
                      <div class="eye-iris"></div>
                      <div class="eye-pupil"></div>
                      <div class="eye-highlight highlight-1"></div>
                      <div class="eye-highlight highlight-2"></div>
                      <div class="eyelash eyelash-1"></div>
                      <div class="eyelash eyelash-2"></div>
                      <div class="eyelash eyelash-3"></div>
                    </div>
                  </div>

                  <!-- 可爱的眉毛 -->
                  <div class="cute-eyebrow left-brow"></div>
                  <div class="cute-eyebrow right-brow"></div>

                  <!-- 小鼻子 -->
                  <div class="tiny-nose"></div>

                  <!-- 可爱的嘴巴 -->
                  <div class="cute-mouth" :class="{ 'talking': isAISpeaking }">
                    <div class="mouth-shape"></div>
                    <div class="mouth-tongue"></div>
                  </div>

                  <!-- 腮红 -->
                  <div class="cheek-blush left-blush"></div>
                  <div class="cheek-blush right-blush"></div>
                </div>

                <!-- 前刘海装饰 -->
                <div class="front-bangs">
                  <div class="bang-piece bang-1"></div>
                  <div class="bang-piece bang-2"></div>
                  <div class="bang-piece bang-3"></div>
                  <div class="bang-piece bang-4"></div>
                  <div class="bang-piece bang-5"></div>
                </div>

                <!-- 发饰 -->
                <div class="hair-accessory left-bow">
                  <div class="bow-left"></div>
                  <div class="bow-right"></div>
                  <div class="bow-center"></div>
                </div>
                <div class="hair-accessory right-bow">
                  <div class="bow-left"></div>
                  <div class="bow-right"></div>
                  <div class="bow-center"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 进度提示 -->
        <div class="progress-hint">
          <span class="question-count">{{ currentQuestionIndex + 1 }} / {{ totalQuestions }}</span>
          <span class="evaluation-type">{{ getEvaluationTypeName(currentEvaluationType) }}</span>
        </div>

        <!-- 隐藏的语音播放器（自动播放最新AI消息） -->
        <div style="display: none;">
          <VoicePlayer
            v-if="currentAIText"
            :text="currentAIText"
            :auto-play="true"
            @start="handleVoicePlayStart"
            @end="handleVoicePlayEnd"
            @error="handleVoicePlayError"
          />
        </div>
      </div>

      <!-- 底部用户输入区 -->
      <div class="user-input-area">
        <!-- 文本输入框 -->
        <div class="text-input-wrapper">
          <el-input
            v-model="answer"
            type="textarea"
            :rows="3"
            placeholder="请输入您的答案..."
            @keydown.ctrl.enter="submitAnswer"
            resize="none"
            class="answer-textarea"
          />
        </div>

        <!-- 操作按钮组 -->
        <div class="action-icons">
          <!-- 麦克风 -->
          <div class="icon-wrapper">
            <VoiceInput
              v-model="answer"
              :disabled="submitting"
              @start="handleVoiceStart"
              @end="handleVoiceEnd"
              @error="handleVoiceError"
            />
          </div>

          <!-- 上传文件 -->
          <div class="icon-wrapper">
            <el-button circle class="action-icon-btn" disabled>
              <el-icon><Upload /></el-icon>
            </el-button>
          </div>

          <!-- 摄像头 -->
          <div class="icon-wrapper">
            <el-button circle class="action-icon-btn" disabled>
              <el-icon><Camera /></el-icon>
            </el-button>
          </div>

          <!-- 发送 -->
          <div class="icon-wrapper">
            <el-button
              circle
              type="primary"
              class="action-icon-btn send-icon"
              :loading="submitting"
              :disabled="!answer.trim()"
              @click="submitAnswer"
            >
              <el-icon v-if="!submitting"><Promotion /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 测评完成 - 显示结果 -->
    <div v-else-if="assessmentCompleted" class="result-container">
      <el-card class="result-card">
        <template #header>
          <div class="card-header">
            <span>🎉 测评完成</span>
          </div>
        </template>

        <el-result icon="success" title="恭喜完成测评！" sub-title="以下是您的测评结果">
          <template #extra>
            <div class="result-summary">
              <div class="summary-item">
                <div class="label">学生姓名</div>
                <div class="value">{{ assessmentResult.student_name }}</div>
              </div>
              <div class="summary-item">
                <div class="label">学号</div>
                <div class="value">{{ assessmentResult.student_id }}</div>
              </div>
              <div class="summary-item">
                <div class="label">总分</div>
                <div class="value score">{{ assessmentResult.total_score }}</div>
              </div>
            </div>
          </template>
        </el-result>

        <!-- n个维度的分数 -->
        <div class="scores-grid">
          <el-card class="score-card" v-for="(score, key) in assessmentResult.final_scores" :key="key">
            <div class="score-item">
              <div class="score-label">{{ getDimensionName(key) }}</div>
              <div class="score-value">{{ score }}</div>
              <el-progress :percentage="score" :stroke-width="8" />
            </div>
          </el-card>
        </div>

        <!-- 详细评分 -->
        <el-divider>详细评分</el-divider>
        <el-collapse v-if="assessmentResult.answer_details && assessmentResult.answer_details.length > 0">
          <el-collapse-item v-for="(detail, index) in assessmentResult.answer_details" :key="index"
            :title="`第 ${index + 1} 题`">
            <div class="answer-detail">
              <div class="detail-section">
                <div class="section-title">题目</div>
                <div class="section-content">{{ detail.question_content }}</div>
              </div>
              <div class="detail-section">
                <div class="section-title">您的答案</div>
                <div class="section-content">{{ detail.answer_content }}</div>
              </div>
              <div class="detail-section">
                <div class="section-title">评分</div>
                <div class="scores-row">
                  <div class="mini-score">
                    <span class="mini-value">{{ detail.scores }}</span>
                  </div>
                </div>
              </div>
              <div class="detail-section" v-if="detail.comments">
                <div class="section-title">评价</div>
                <div class="section-content">{{ detail.comments }}</div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>

        <!-- 操作按钮 -->
        <div class="result-actions">
          <el-button type="primary" @click="viewHistory">查看历史记录</el-button>
          <el-button @click="restartAssessment">再次测评</el-button>
          <el-button @click="goHome">返回首页</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, ChatDotSquare, Close, ChatLineSquare, Upload, Camera, Promotion } from '@element-plus/icons-vue'
import { createSession, getQuestions, submitAnswer as submitAnswerApi, completeSession } from '@/api/assessments'
import { verifyStudent } from '@/api/students'
import { useAssessmentStore } from '@/store'
import VoiceInput from '@/components/VoiceInput.vue'
import VoicePlayer from '@/components/VoicePlayer.vue'

const router = useRouter()
const assessmentStore = useAssessmentStore()

const loading = ref(false)
const loadingMessage = ref('加载中...')
const submitting = ref(false)
const sessionStarted = ref(false)
const assessmentCompleted = ref(false)
const showEvaluationTypeSelection = ref(false)
const currentEvaluationType = ref('')
const startForm = ref({
  student_name: '',
  student_id: ''
})

// 测评指标列表
const evaluationTypes = ref([
  { label: '认知能力', value: 'cognitive_strategy' },
  { label: '元认知能力', value: 'metacognition' },
  { label: '批判性思维', value: 'critical_thinking' },
  { label: '学习动机', value: 'learning_motivation' },
  { label: '社会情感能力', value: 'social_emotional' }
])

const currentQuestionIndex = ref(0)
const totalQuestions = ref(0)
const questions = ref([])
const answer = ref('')
const sessionId = ref('')
const assessmentResult = ref({
  assessment_id: '',
  student_name: '',
  student_id: '',
  total_score: 0,
  final_scores: {},
  answer_details: []
})

const currentQuestion = computed(() => questions.value[currentQuestionIndex.value])
const isLastQuestion = computed(() => currentQuestionIndex.value === totalQuestions.value - 1)

// 对话交互记录
const chatMessages = ref(null)
const chatHistory = ref([])

// 新增：字幕和AI状态
const showSubtitle = ref(false)
const isAISpeaking = ref(false)
const currentAIText = computed(() => {
  // 获取最后一条AI消息
  const lastAIMessage = chatHistory.value.filter(item => item.type === 'question').pop()
  return lastAIMessage ? lastAIMessage.content : ''
})

// AI 头像视频配置
// 将您的视频文件放在 public/avatars/ 目录下
// 支持 MP4、WebM 等格式，推荐使用 MP4（兼容性好）或 WebM（支持透明背景）
const avatarIdleUrl = ref('/avatars/ai-idle.mp4')      // 待机状态视频
const avatarTalkingUrl = ref('/avatars/ai-talking.mp4') // 说话状态视频（动嘴巴）
const avatarVideoEnabled = ref(true) // 设置为 true 启用视频头像，false 使用 CSS 绘制头像

// LocalStorage 键名
const STORAGE_KEY = 'assessment_progress'

// 保存测评进度到 localStorage
const saveProgress = () => {
  if (!sessionStarted.value || assessmentCompleted.value) {
    return
  }

  const progress = {
    sessionId: sessionId.value,
    studentName: startForm.value.student_name,
    studentId: startForm.value.student_id,
    evaluationType: currentEvaluationType.value,
    currentQuestionIndex: currentQuestionIndex.value,
    totalQuestions: totalQuestions.value,
    questions: questions.value,
    chatHistory: chatHistory.value,
    timestamp: Date.now()
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(progress))
  console.log('Progress saved:', progress)
}

// 从 localStorage 恢复测评进度
const restoreProgress = () => {
  const savedProgress = localStorage.getItem(STORAGE_KEY)
  if (!savedProgress) {
    return false
  }

  try {
    const progress = JSON.parse(savedProgress)

    // 检查是否过期（24小时）
    const now = Date.now()
    const elapsed = now - progress.timestamp
    const EXPIRY_TIME = 24 * 60 * 60 * 1000 // 24小时

    if (elapsed > EXPIRY_TIME) {
      localStorage.removeItem(STORAGE_KEY)
      return false
    }

    // 恢复状态
    sessionId.value = progress.sessionId
    startForm.value.student_name = progress.studentName
    startForm.value.student_id = progress.studentId
    currentEvaluationType.value = progress.evaluationType
    currentQuestionIndex.value = progress.currentQuestionIndex
    totalQuestions.value = progress.totalQuestions
    questions.value = progress.questions
    chatHistory.value = progress.chatHistory
    sessionStarted.value = true
    showEvaluationTypeSelection.value = false

    ElMessage.success('已恢复上次未完成的测评')
    console.log('Progress restored:', progress)
    return true
  } catch (error) {
    console.error('Failed to restore progress:', error)
    localStorage.removeItem(STORAGE_KEY)
    return false
  }
}

// 清除保存的进度
const clearProgress = () => {
  localStorage.removeItem(STORAGE_KEY)
  console.log('Progress cleared')
}

// 监听聊天历史变化，自动滚动到最新消息并保存进度
watch(chatHistory, () => {
  nextTick(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight
    }
  })
  saveProgress() // 每次对话更新时保存进度
}, { deep: true })

// 监听当前问题索引变化，保存进度
watch(currentQuestionIndex, () => {
  saveProgress()
})

// 页面加载时尝试恢复进度
const checkAndRestoreProgress = () => {
  const savedProgress = localStorage.getItem(STORAGE_KEY)
  if (savedProgress) {
    ElMessageBox.confirm(
      '检测到您有未完成的测评，是否继续上次的测评？',
      '恢复测评进度',
      {
        confirmButtonText: '继续测评',
        cancelButtonText: '重新开始',
        type: 'info',
      }
    )
      .then(() => {
        restoreProgress()
      })
      .catch(() => {
        clearProgress()
        ElMessage.info('已清除上次的测评进度')
      })
  }
}

// 浏览器关闭/刷新时保存进度
const handleBeforeUnload = (e) => {
  if (sessionStarted.value && !assessmentCompleted.value) {
    saveProgress()
    console.log('Browser unload: Progress saved automatically')
  }
}

// 组件挂载时检查是否有未完成的测评
onMounted(() => {
  checkAndRestoreProgress()
  // 监听浏览器关闭/刷新事件
  window.addEventListener('beforeunload', handleBeforeUnload)
})

// 组件卸载时移除事件监听
onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

// 路由离开守卫 - 切换页面时自动保存进度
onBeforeRouteLeave((to, from, next) => {
  // 如果正在进行测评（未完成），自动保存进度
  if (sessionStarted.value && !assessmentCompleted.value) {
    saveProgress()
    console.log('Route leaving: Progress saved automatically')
  }
  next()
})

const startAssessment = async () => {
  if (!startForm.value.student_name || !startForm.value.student_id) {
    ElMessage.warning('请填写学生姓名和学号')
    return
  }

  loading.value = true
  try {
    // 先验证学生是否存在
    console.log('Verifying student:', startForm.value)
    await verifyStudent({
      name: startForm.value.student_name,
      student_id: startForm.value.student_id
    })

    // 验证通过，显示测评指标选择界面
    showEvaluationTypeSelection.value = true
    ElMessage.success('学生验证成功，请选择测评指标')
  } catch (error) {
    console.error('Failed to start assessment:', error)
    // 显示错误信息
    const errorMsg = error.response?.data?.message || '启动测评失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 选择测评指标并开始测评
const selectEvaluationType = async (type) => {
  loading.value = true
  loadingMessage.value = '正在创建测评会话...'

  try {
    currentEvaluationType.value = type
    console.log(`Selected evaluation type: ${type}`)

    // 创建测评会话，传递测评类型
    const sessionData = {
      ...startForm.value,
      evaluationType: type
    }

    const sessionRes = await createSession(sessionData)
    sessionId.value = sessionRes.data.session_id

    // 更新加载提示为个性化问卷生成中
    loadingMessage.value = '🎯 个性化问卷正在生成中，请稍候...'

    const questionsRes = await getQuestions(sessionId.value)
    questions.value = questionsRes.data.questions
    totalQuestions.value = questionsRes.data.total

    // 初始化聊天历史，添加第一个问题
    chatHistory.value = [{
      type: 'question',
      content: questions.value[0].content || '请描述一个回形针的多种用途'
    }]

    showEvaluationTypeSelection.value = false
    sessionStarted.value = true
    ElMessage.success(`已开始${getEvaluationTypeName(type)}测评`)
  } catch (error) {
    console.error('Failed to create session with selected type:', error)
    const errorMsg = error.response?.data?.message || '创建测评会话失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
    loadingMessage.value = '加载中...'
  }
}

// 获取测评指标的中文名称
const getEvaluationTypeName = (type) => {
  const typeMap = {
    'cognitive_strategy': '认知能力',
    'metacognition': '元认知能力',
    'critical_thinking': '批判性思维',
    'learning_motivation': '学习动机',
    'social_emotional': '社会情感能力'
  }
  return typeMap[type] || type
}

// 返回开始页面
const backToStart = () => {
  showEvaluationTypeSelection.value = false
}

// 返回指标选择界面（等待实现）
const returnToTypeSelection = () => {
  sessionStarted.value = false
  showEvaluationTypeSelection.value = true
  // 清空相关数据
  questions.value = []
  chatHistory.value = []
  answer.value = ''
  currentQuestionIndex.value = 0
  sessionId.value = ''
}

const submitAnswer = async () => {
  if (!answer.value.trim()) {
    ElMessage.warning('请输入答案')
    return
  }

  // 添加答案到聊天历史
  chatHistory.value.push({
    type: 'answer',
    content: answer.value
  })

  const currentAnswer = answer.value
  answer.value = '' // 清空输入框

  submitting.value = true
  try {
    await submitAnswerApi(sessionId.value, {
      question_id: currentQuestion.value.id,
      content: currentAnswer,
      time_spent: 0
    })

    if (isLastQuestion.value) {
      console.log('Completing assessment session:', sessionId.value)
      const result = await completeSession(sessionId.value)
      console.log('Complete session result:', result)

      // 保存测评结果
      assessmentResult.value = {
        assessment_id: result.data.assessment_id,
        student_name: startForm.value.student_name,
        student_id: startForm.value.student_id,
        total_score: result.data.total_score,  // 评级
        final_scores: result.data.final_scores,  // 各小项评分
        answer_details: result.data.answer_details || []  // 各题评分详情
      }

      // 显示完成状态
      sessionStarted.value = false
      assessmentCompleted.value = true

      // 清除保存的进度
      clearProgress()

      ElMessage.success('测评已完成！正在生成结果...')
    } else {
      // 添加下一题到聊天历史
      setTimeout(() => {
        currentQuestionIndex.value++
        chatHistory.value.push({
          type: 'question',
          content: questions.value[currentQuestionIndex.value].content || '请描述一个回形针的多种用途'
        })

        // 滚动到底部
        nextTick(() => {
          if (chatMessages.value) {
            chatMessages.value.scrollTop = chatMessages.value.scrollHeight
          }
        })
        answer.value = '' // 清空输入框
      }, 500)
    }
  } catch (error) {
    console.error('Failed to submit answer:', error)
    // 提交失败时移除最后一条答案
    chatHistory.value.pop()
    // 恢复答案到输入框
    answer.value = currentAnswer
    // 显示错误信息
    const errorMsg = error.response?.data?.message || error.message || '提交答案失败，请重试'
    ElMessage.error(errorMsg)
  } finally {
    submitting.value = false
  }
}

// 语音输入事件处理
const handleVoiceStart = () => {
  console.log('开始语音录音')
}

const handleVoiceEnd = (text) => {
  console.log('语音识别完成:', text)
  if (text) {
    ElMessage.success('语音识别成功')
  }
}

const handleVoiceError = (error) => {
  console.error('语音识别错误:', error)
}

// 语音播放事件处理
const handleVoicePlayStart = () => {
  console.log('开始播放AI问题')
  isAISpeaking.value = true
}

const handleVoicePlayEnd = () => {
  console.log('AI问题播放完成')
  isAISpeaking.value = false
}

const handleVoicePlayError = (error) => {
  console.error('语音播放错误:', error)
}

// 维度名称映射 - 根据测评类型返回不同的维度名称
const getDimensionName = (key) => {
  // 基础维度名称映射
  let names = {
    fluency: '流畅性',
    flexibility: '灵活性',
    originality: '独创性',
    elaboration: '精致性'
  }

  // 根据不同的测评类型返回不同的维度名称
  if (currentEvaluationType.value === 'cognitive_strategy') {
    names = {
      ...names,
      rehearsal: "复述策略",
      elaboration: "精加工策略",
      organization: "组织策略",
      resource_management: "资源管理策略"
    }
  } else if (currentEvaluationType.value === 'metacognition') {
    names = {
      ...names,
      // 指标B的特定维度可以在这里定义
      monitoring: "自我监控能力",
      integration: "自我整合能力",
      differentiation: "分化能力",
      decentralization: "去中心化能力"
    }
  } else if (currentEvaluationType.value === 'critical_thinking') {
    names = {
      ...names,
      open_mindedness: "开放思维",
      analytical_logical_skills: "分析逻辑能力",
      systematic_planning: "系统规划能力",
      intellectual_curiosity: "求知欲与探索精神",
      cognitive_maturity: "认知成熟度"
    }
  } else if (currentEvaluationType.value === 'learning_motivation') { 
    names = {
      ...names,
      autonomy: "自主性",
      competence: "胜任感",
      relatedness: "归属感"
    }
  } else if (currentEvaluationType.value === 'social_emotional') {
    names = {
      ...names,
      responsible_decision_making: "负责任的决策",
      social_awareness: "社会知觉",
      self_management: "自我管理",
      relationship_skills: "人际关系"
    }
  }

  return names[key] || key
}

// 查看历史记录
const viewHistory = () => {
  router.push('/analysis')
}

// 退出问卷确认对话框
const showExitConfirm = () => {
  ElMessageBox.confirm(
    '是否退出测评，已作答的内容将不被保存',
    '退出测评',
    {
      confirmButtonText: '确定退出',
      cancelButtonText: '继续答题',
      type: 'warning',
    }
  )
    .then(() => {
      // 清除保存的进度（不保存）
      clearProgress()

      // 重置状态回到问卷选择界面
      sessionStarted.value = false
      showEvaluationTypeSelection.value = true
      currentEvaluationType.value = ''
      currentQuestionIndex.value = 0
      answer.value = ''
      questions.value = []
      chatHistory.value = []

      ElMessage.info('已退出测评')
    })
    .catch(() => {
      // 用户取消，继续答题
    })
}

// 重新开始测评
const restartAssessment = () => {
  // 清除保存的进度
  clearProgress()

  assessmentCompleted.value = false
  sessionStarted.value = false
  showEvaluationTypeSelection.value = false
  currentEvaluationType.value = ''
  currentQuestionIndex.value = 0
  answer.value = ''
  questions.value = []
  chatHistory.value = []
  assessmentResult.value = {
    assessment_id: '',
    student_name: '',
    student_id: '',
    total_score: 0,
    final_scores: {},
    answer_details: []
  }
}

// 返回首页
const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.assessment {
  height: 88vh;
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 结果显示样式 */
.result-container {
  max-width: 1000px;
  margin: 0 auto;
}

.result-card {
  margin-bottom: 20px;
}

.result-summary {
  width: 100%;
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin: 20px 0;
  padding: 30px 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.summary-item {
  text-align: center;
  min-width: 150px;
  padding: 0 15px;
}

.summary-item .label {
  font-size: 16px;
  color: #909399;
  margin-bottom: 12px;
}

.summary-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.summary-item .value.score {
  font-size: 36px;
  color: #409eff;
}

.summary-item {
  text-align: center;
}

.summary-item .label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-item .value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.summary-item .value.score {
  font-size: 32px;
  color: #409eff;
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 20px 0;
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

.answer-detail {
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

.scores-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.mini-score {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.mini-value {
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
}

.result-actions {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* ========== 测评聊天界面 ========== */
.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #fce7f3 0%, #dbeafe 50%, #fce7f3 100%);
  background-attachment: fixed;
  padding: 40px 20px;
  position: relative;
}

/* 顶部字幕按钮 */
.subtitle-toggle {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.subtitle-btn {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.subtitle-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
}

/* 右上角退出按钮 */
.exit-button-wrapper {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
}

.exit-assessment-btn {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  font-weight: 500;
  transition: all 0.3s;
  border-radius: 10px;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.exit-assessment-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.exit-assessment-btn .el-icon {
  font-size: 16px;
}

/* 字幕面板 */
.subtitle-panel {
  position: absolute;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  max-width: 600px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px 30px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  z-index: 9;
}

.subtitle-content {
  font-size: 16px;
  line-height: 1.8;
  color: #1f2937;
  text-align: center;
}

/* 字幕滑动动画 */
.subtitle-slide-enter-active,
.subtitle-slide-leave-active {
  transition: all 0.3s ease;
}

.subtitle-slide-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.subtitle-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

/* AI头像容器 */
.ai-avatar-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  min-height: 300px;
}

/* 头像和声波的容器 */
.avatar-with-waves {
  position: relative;
  width: 300px;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 声波扩散动画 */
.sound-waves {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.wave {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px solid rgba(59, 130, 246, 0.4);
  animation: wave-expand 2s ease-out infinite;
}

.wave-1 {
  animation-delay: 0s;
}

.wave-2 {
  animation-delay: 0.6s;
}

.wave-3 {
  animation-delay: 1.2s;
}

@keyframes wave-expand {
  0% {
    transform: scale(0.5);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

/* AI头像圆形 */
.ai-avatar-circle {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 40px rgba(59, 130, 246, 0.3);
  position: relative;
  z-index: 2;
  transition: all 0.3s ease;
}

.ai-avatar-circle:hover {
  transform: scale(1.05);
  box-shadow: 0 15px 50px rgba(59, 130, 246, 0.4);
}

.avatar-image {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fff5f7 0%, #ffe8f0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid rgba(255, 255, 255, 0.9);
  overflow: visible;
  position: relative;
}

/* 视频头像样式 */
.avatar-video {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  transition: all 0.3s ease;
}

/* ========== 可爱卡通女孩头像 ========== */
.cute-avatar {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 头部背景 */
.head-bg {
  position: absolute;
  width: 120px;
  height: 130px;
  background: #ffe4d6;
  border-radius: 50% 50% 48% 48%;
  box-shadow: inset 0 -8px 15px rgba(255, 200, 180, 0.3);
  z-index: 1;
}

/* 头发层 */
.hair-layer {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 0;
}

/* 后发 - 左右两侧 */
.hair-back-left,
.hair-back-right {
  position: absolute;
  width: 70px;
  height: 100px;
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #ff9a9e 100%);
  border-radius: 50%;
  top: 20px;
}

.hair-back-left {
  left: 10px;
  transform: rotate(-15deg);
}

.hair-back-right {
  right: 10px;
  transform: rotate(15deg);
}

/* 双马尾 */
.ponytail {
  position: absolute;
  width: 35px;
  height: 60px;
  top: 35px;
  animation: ponytail-sway 3s ease-in-out infinite;
}

.ponytail-left {
  left: 5px;
  transform-origin: top center;
}

.ponytail-right {
  right: 5px;
  transform-origin: top center;
  animation-delay: 0.5s;
}

@keyframes ponytail-sway {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(5deg); }
}

.ponytail-strand {
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #ff9a9e 0%, #fecfef 100%);
  border-radius: 50% 50% 60% 40%;
  position: absolute;
}

.ponytail-strand:nth-child(2) {
  transform: translateX(8px) scale(0.9);
  opacity: 0.8;
}

/* 脸部 */
.face-cute {
  width: 120px;
  height: 130px;
  position: relative;
  z-index: 2;
}

/* 大眼睛容器 */
.big-eyes {
  position: absolute;
  width: 100%;
  top: 40px;
  display: flex;
  justify-content: center;
  gap: 25px;
}

/* 单个大眼睛 */
.big-eye {
  width: 32px;
  height: 36px;
  position: relative;
  animation: cute-blink 5s infinite;
}

@keyframes cute-blink {
  0%, 94%, 100% {
    transform: scaleY(1);
    opacity: 1;
  }
  95%, 97% {
    transform: scaleY(0.05);
    opacity: 0.8;
  }
}

/* 眼白 */
.eye-white {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 50% 50% 50% 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: absolute;
}

/* 虹膜 */
.eye-iris {
  width: 22px;
  height: 22px;
  background: radial-gradient(circle, #8b6f47 0%, #5d4e37 100%);
  border-radius: 50%;
  position: absolute;
  top: 7px;
  left: 5px;
}

/* 瞳孔 */
.eye-pupil {
  width: 12px;
  height: 12px;
  background: #1a1a1a;
  border-radius: 50%;
  position: absolute;
  top: 12px;
  left: 10px;
}

/* 眼睛高光 */
.eye-highlight {
  background: white;
  border-radius: 50%;
  position: absolute;
}

.highlight-1 {
  width: 8px;
  height: 8px;
  top: 10px;
  left: 12px;
  opacity: 0.95;
}

.highlight-2 {
  width: 4px;
  height: 4px;
  top: 20px;
  left: 18px;
  opacity: 0.7;
}

/* 睫毛 */
.eyelash {
  width: 2px;
  height: 8px;
  background: #4a3728;
  position: absolute;
  top: -6px;
  border-radius: 2px;
}

.eyelash-1 {
  left: 8px;
  transform: rotate(-20deg);
}

.eyelash-2 {
  left: 15px;
  transform: rotate(0deg);
  height: 10px;
  top: -8px;
}

.eyelash-3 {
  right: 8px;
  transform: rotate(20deg);
}

/* 可爱的眉毛 */
.cute-eyebrow {
  width: 20px;
  height: 3px;
  background: #8b6f47;
  border-radius: 50%;
  position: absolute;
  top: 32px;
}

.left-brow {
  left: 22px;
  transform: rotate(-10deg);
}

.right-brow {
  right: 22px;
  transform: rotate(10deg);
}

/* 小鼻子 */
.tiny-nose {
  width: 3px;
  height: 3px;
  background: rgba(255, 150, 150, 0.4);
  border-radius: 50%;
  position: absolute;
  top: 70px;
  left: 50%;
  transform: translateX(-50%);
}

/* 可爱的嘴巴 */
.cute-mouth {
  position: absolute;
  width: 28px;
  height: 16px;
  bottom: 35px;
  left: 50%;
  transform: translateX(-50%);
  transition: all 0.3s ease;
}

.mouth-shape {
  width: 100%;
  height: 100%;
  border: 2.5px solid #ff8fa3;
  border-top: none;
  border-radius: 0 0 50% 50%;
  background: transparent;
  transition: all 0.3s ease;
  position: relative;
}

.mouth-tongue {
  width: 12px;
  height: 8px;
  background: #ffb3c1;
  border-radius: 50%;
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

/* 说话动画 */
.cute-mouth.talking {
  animation: cute-talk 0.4s ease-in-out infinite;
}

.cute-mouth.talking .mouth-shape {
  background: rgba(255, 179, 193, 0.2);
}

.cute-mouth.talking .mouth-tongue {
  opacity: 0.6;
}

@keyframes cute-talk {
  0%, 100% {
    height: 16px;
  }
  50% {
    height: 22px;
  }
}

/* 腮红 */
.cheek-blush {
  width: 18px;
  height: 14px;
  background: radial-gradient(ellipse, rgba(255, 150, 180, 0.5) 0%, rgba(255, 150, 180, 0) 70%);
  border-radius: 50%;
  position: absolute;
  top: 75px;
}

.left-blush {
  left: 8px;
}

.right-blush {
  right: 8px;
}

/* 前刘海 */
.front-bangs {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 110px;
  display: flex;
  justify-content: space-between;
  z-index: 3;
}

.bang-piece {
  width: 18px;
  height: 35px;
  background: linear-gradient(180deg, #ff9a9e 0%, #fecfef 100%);
  border-radius: 0 0 50% 50%;
}

.bang-1 {
  transform: rotate(-15deg);
}

.bang-2 {
  transform: rotate(-7deg);
}

.bang-3 {
  transform: rotate(0deg);
  height: 40px;
}

.bang-4 {
  transform: rotate(7deg);
}

.bang-5 {
  transform: rotate(15deg);
}

/* 发饰蝴蝶结 */
.hair-accessory {
  position: absolute;
  width: 30px;
  height: 20px;
  top: 30px;
  z-index: 4;
}

.left-bow {
  left: 8px;
}

.right-bow {
  right: 8px;
}

.bow-left,
.bow-right {
  width: 12px;
  height: 16px;
  background: linear-gradient(135deg, #ffd93d 0%, #ffb347 100%);
  border-radius: 50% 0 50% 50%;
  position: absolute;
  top: 2px;
}

.bow-left {
  left: 0;
  transform: rotate(-10deg);
}

.bow-right {
  right: 0;
  transform: rotate(10deg) scaleX(-1);
}

.bow-center {
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #ffd93d 0%, #ffb347 100%);
  border-radius: 50%;
  position: absolute;
  top: 6px;
  left: 50%;
  transform: translateX(-50%);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* 进度提示 */
.progress-hint {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.question-count {
  font-size: 24px;
  font-weight: bold;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.evaluation-type {
  font-size: 16px;
  color: #6b7280;
  font-weight: 500;
}

/* 底部用户输入区 */
.user-input-area {
  width: 100%;
  max-width: 700px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.text-input-wrapper {
  width: 100%;
}

.answer-textarea :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  padding: 16px 20px;
  font-size: 15px;
  line-height: 1.6;
  color: #1f2937;
  transition: all 0.3s;
  resize: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.answer-textarea :deep(.el-textarea__inner):focus {
  background: white;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.answer-textarea :deep(.el-textarea__inner)::placeholder {
  color: #9ca3af;
}

/* 操作按钮组 */
.action-icons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  color: #3b82f6;
}

.action-icon-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
  border-color: #3b82f6;
}

.action-icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.action-icon-btn.send-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border: none;
  color: white;
}

.action-icon-btn.send-icon:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

/* 调整VoiceInput组件样式以匹配新设计 */
.icon-wrapper :deep(.voice-button) {
  width: 50px !important;
  height: 50px !important;
  background: rgba(255, 255, 255, 0.9) !important;
  border: 2px solid rgba(59, 130, 246, 0.3) !important;
  color: #3b82f6 !important;
}

.icon-wrapper :deep(.voice-button.status-idle) {
  background: rgba(255, 255, 255, 0.9) !important;
  border: 2px solid rgba(59, 130, 246, 0.3) !important;
  color: #3b82f6 !important;
}

.icon-wrapper :deep(.voice-button.status-idle:hover) {
  transform: translateY(-3px) !important;
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3) !important;
  border-color: #3b82f6 !important;
}

.icon-wrapper :deep(.voice-button.status-recording) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
  border: none !important;
  color: white !important;
}

.icon-wrapper :deep(.recording-tip),
.icon-wrapper :deep(.interim-result) {
  display: none;
}

/* 调整卡片样式 */
.el-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* 调整结果容器样式 */
.result-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

/* 测评类型选择样式 */
.evaluation-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  padding: 40px 0;
  max-width: 900px;
  margin: 0 auto;
}

.type-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 16px;
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8eef7;
}

.type-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(64, 158, 255, 0.2);
  border-color: #d0e3ff;
}

.type-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 32px;
  color: #409eff;
  background-color: #ecf5ff;
}

.type-label {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.back-button {
  text-align: center;
  margin-top: 30px;
  padding-bottom: 20px;
}

/* 自定义 loading 样式 */
:deep(.el-loading-text) {
  font-size: 16px;
  font-weight: 500;
  color: #409EFF;
  margin-top: 10px;
}

:deep(.el-loading-spinner) {
  top: 45%;
}

:deep(.el-loading-spinner .circular) {
  width: 50px;
  height: 50px;
}
</style>

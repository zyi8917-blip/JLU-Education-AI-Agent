<template>
  <div class="voice-input">
    <!-- 语音输入按钮 -->
    <el-button
      :class="['voice-button', statusClass]"
      :disabled="disabled || !isSupported"
      :loading="status === 'processing'"
      @click="toggleRecording"
      circle
    >
      <el-icon v-if="status === 'idle'" :size="20">
        <Microphone />
      </el-icon>
      <el-icon v-else-if="status === 'recording'" :size="20" class="recording-icon">
        <VideoCamera />
      </el-icon>
      <el-icon v-else-if="status === 'success'" :size="20">
        <Check />
      </el-icon>
      <el-icon v-else-if="status === 'error'" :size="20">
        <Close />
      </el-icon>
    </el-button>

    <!-- 录音状态提示 -->
    <transition name="fade">
      <div v-if="status === 'recording'" class="recording-tip">
        <div class="wave-animation">
          <span class="wave-dot"></span>
          <span class="wave-dot"></span>
          <span class="wave-dot"></span>
        </div>
        <span class="tip-text">正在录音，请说话...</span>
        <span v-if="remainingTime > 0" class="countdown">{{ remainingTime }}s</span>
      </div>
    </transition>

    <!-- 识别结果预览 -->
    <transition name="fade">
      <div v-if="interimText && status === 'recording'" class="interim-result">
        {{ interimText }}
      </div>
    </transition>

    <!-- 不支持提示 -->
    <el-tooltip
      v-if="!isSupported"
      content="您的浏览器不支持语音识别，请使用 Chrome 或 Edge 浏览器"
      placement="top"
    >
      <el-icon class="unsupported-icon">
        <WarningFilled />
      </el-icon>
    </el-tooltip>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Microphone, VideoCamera, Check, Close, WarningFilled } from '@element-plus/icons-vue'
import { SpeechRecognizer } from '@/utils/speech'

// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: '点击麦克风开始录音'
  },
  maxDuration: {
    type: Number,
    default: 60 // 最大录音时长（秒）
  },
  continuous: {
    type: Boolean,
    default: true // 改为 true，支持连续识别
  },
  lang: {
    type: String,
    default: 'zh-CN'
  },
  autoSubmit: {
    type: Boolean,
    default: false // 识别完成后是否自动提交
  },
  appendMode: {
    type: Boolean,
    default: true // 是否追加模式（不清空已有内容）
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'start', 'end', 'error', 'submit'])

// 状态
const status = ref('idle') // idle, recording, processing, success, error
const interimText = ref('') // 临时识别结果
const currentSegmentText = ref('') // 当前段落的最终识别结果
const baseText = ref('') // 录音开始时输入框中已有的文本
const isSupported = ref(false)
const recognizer = ref(null)
const recordingTimer = ref(null)
const recordingStartTime = ref(0) // 录音开始时间
const remainingTime = ref(0) // 剩余时间（秒）
const shouldContinue = ref(false) // 是否应该继续录音（用于手动控制）

// 计算状态类名
const statusClass = computed(() => {
  return `status-${status.value}`
})

// 初始化
onMounted(() => {
  // 检查浏览器支持
  isSupported.value = SpeechRecognizer.isSupported()
  
  if (!isSupported.value) {
    console.warn('浏览器不支持语音识别')
    return
  }
  
  try {
    // 创建识别器
    recognizer.value = new SpeechRecognizer({
      lang: props.lang,
      continuous: props.continuous,
      interimResults: true
    })
    
    // 监听事件
    recognizer.value.on('start', handleStart)
    recognizer.value.on('result', handleResult)
    recognizer.value.on('end', handleEnd)
    recognizer.value.on('error', handleError)
  } catch (error) {
    console.error('初始化语音识别失败:', error)
    isSupported.value = false
  }
})

// 清理
onBeforeUnmount(() => {
  if (recognizer.value) {
    recognizer.value.stop()
  }
  if (recordingTimer.value) {
    clearTimeout(recordingTimer.value)
  }
})

// 切换录音状态
const toggleRecording = async () => {
  if (status.value === 'recording') {
    stopRecording()
  } else {
    startRecording()
  }
}

// 开始录音
const startRecording = async () => {
  if (!recognizer.value) {
    ElMessage.error('语音识别未初始化')
    return
  }

  try {
    // 保存录音开始时输入框中已有的文本
    baseText.value = props.modelValue || ''

    // 清空当前段落的识别结果
    interimText.value = ''
    currentSegmentText.value = ''

    // 设置继续录音标志
    shouldContinue.value = true

    // 记录开始时间
    recordingStartTime.value = Date.now()
    remainingTime.value = props.maxDuration

    // 开始识别
    await recognizer.value.start()

    // 设置最大录音时长倒计时
    if (props.maxDuration > 0) {
      const updateTimer = () => {
        const elapsed = Math.floor((Date.now() - recordingStartTime.value) / 1000)
        remainingTime.value = Math.max(0, props.maxDuration - elapsed)

        if (remainingTime.value > 0 && shouldContinue.value) {
          recordingTimer.value = setTimeout(updateTimer, 1000)
        } else if (remainingTime.value === 0) {
          shouldContinue.value = false
          stopRecording()
          ElMessage.warning(`录音时长已达到 ${props.maxDuration} 秒，自动停止`)
        }
      }
      recordingTimer.value = setTimeout(updateTimer, 1000)
    }
  } catch (error) {
    console.error('启动录音失败:', error)
    status.value = 'error'
    shouldContinue.value = false

    // 根据错误类型显示不同提示
    if (error.message.includes('已经在录音中')) {
      ElMessage.warning('已经在录音中')
    } else {
      ElMessage.error('启动录音失败，请检查麦克风权限')
    }

    setTimeout(() => {
      status.value = 'idle'
    }, 2000)
  }
}

// 停止录音
const stopRecording = () => {
  // 设置停止标志，防止自动重启
  shouldContinue.value = false

  if (recognizer.value) {
    recognizer.value.stop()
  }

  if (recordingTimer.value) {
    clearTimeout(recordingTimer.value)
    recordingTimer.value = null
  }
}

// 处理开始事件
const handleStart = () => {
  status.value = 'recording'
  emit('start')
}

// 处理识别结果
const handleResult = (results) => {
  if (!results || results.length === 0) return

  // 分别收集最终结果和临时结果
  let finalTranscript = ''
  let interimTranscript = ''

  results.forEach(result => {
    if (result.isFinal) {
      // 最终结果：累积到当前段落
      finalTranscript += result.transcript
    } else {
      // 临时结果：只显示，不累积
      interimTranscript += result.transcript
    }
  })

  // 更新当前段落的最终文本和临时文本
  if (finalTranscript) {
    // 有最终结果：累积到 currentSegmentText
    currentSegmentText.value += finalTranscript
    interimText.value = ''  // 清空临时结果
  } else {
    // 只有临时结果：直接替换（不累积）
    interimText.value = interimTranscript
  }

  // 构建完整文本：基础文本 + 当前段落最终文本 + 临时文本
  let newText = ''

  if (props.appendMode) {
    // 追加模式：基础文本（录音开始时的内容）+ 当前录音内容
    const currentRecordingText = currentSegmentText.value + interimText.value

    if (baseText.value && currentRecordingText) {
      // 添加空格分隔
      newText = baseText.value + ' ' + currentRecordingText
    } else {
      newText = baseText.value + currentRecordingText
    }
  } else {
    // 替换模式：只显示当前识别的内容
    newText = currentSegmentText.value + interimText.value
  }

  // 更新 v-model
  emit('update:modelValue', newText)
}

// 处理结束事件
const handleEnd = () => {
  // 如果应该继续录音（用户没有手动停止），则自动重启
  if (shouldContinue.value && remainingTime.value > 0) {
    // 自动重启识别，实现连续录音
    setTimeout(() => {
      if (shouldContinue.value && recognizer.value) {
        try {
          recognizer.value.start()
        } catch (error) {
          console.error('重启识别失败:', error)
          shouldContinue.value = false
          status.value = 'idle'
        }
      }
    }, 100)
    return
  }

  // 用户手动停止或超时，处理结束逻辑
  status.value = 'processing'

  // 短暂延迟后显示成功状态
  setTimeout(() => {
    const hasContent = currentSegmentText.value || interimText.value

    if (hasContent) {
      status.value = 'success'

      // 发送当前段落的最终结果
      const result = currentSegmentText.value || interimText.value
      emit('end', result)

      // 如果设置了自动提交，则触发提交事件
      if (props.autoSubmit) {
        emit('submit', props.modelValue)
      }

      // 1秒后恢复空闲状态（不清空内容，因为已经保存在 modelValue 中）
      setTimeout(() => {
        status.value = 'idle'
        interimText.value = ''
        currentSegmentText.value = ''
      }, 1000)
    } else {
      status.value = 'idle'
      interimText.value = ''
      currentSegmentText.value = ''
      // 只在有尝试录音但没有内容时提示
      if (shouldContinue.value === false) {
        ElMessage.warning('未检测到语音，请重试')
      }
    }
  }, 300)
}

// 处理错误事件
const handleError = (error) => {
  console.error('语音识别错误:', error)

  // 停止继续录音
  shouldContinue.value = false
  status.value = 'error'

  // 清除定时器
  if (recordingTimer.value) {
    clearTimeout(recordingTimer.value)
    recordingTimer.value = null
  }

  // 显示错误提示
  ElMessage.error(error.message || '语音识别失败')

  emit('error', error)

  // 2秒后恢复空闲状态
  setTimeout(() => {
    status.value = 'idle'
    interimText.value = ''
    currentSegmentText.value = ''
  }, 2000)
}
</script>

<style scoped>
.voice-input {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  position: relative;
}

.voice-button {
  width: 48px;
  height: 48px;
  transition: all 0.3s ease;
}

/* 空闲状态 */
.voice-button.status-idle {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
}

.voice-button.status-idle:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 录音状态 */
.voice-button.status-recording {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border: none;
  color: white;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(245, 87, 108, 0.7);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 10px rgba(245, 87, 108, 0);
  }
}

.recording-icon {
  animation: blink 1s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 处理状态 */
.voice-button.status-processing {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  border: none;
  color: #333;
}

/* 成功状态 */
.voice-button.status-success {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  border: none;
  color: #10b981;
}

/* 错误状态 */
.voice-button.status-error {
  background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
  border: none;
  color: #ef4444;
}

/* 录音提示 */
.recording-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(245, 87, 108, 0.1);
  border-radius: 20px;
  border: 1px solid rgba(245, 87, 108, 0.3);
}

.wave-animation {
  display: flex;
  gap: 4px;
  align-items: center;
}

.wave-dot {
  width: 6px;
  height: 6px;
  background: #f5576c;
  border-radius: 50%;
  animation: wave 1.2s ease-in-out infinite;
}

.wave-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.wave-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes wave {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.5);
    opacity: 1;
  }
}

.tip-text {
  font-size: 14px;
  color: #f5576c;
  font-weight: 500;
}

.countdown {
  font-size: 13px;
  color: #f5576c;
  font-weight: 600;
  padding: 2px 8px;
  background: rgba(245, 87, 108, 0.15);
  border-radius: 12px;
  margin-left: 8px;
  min-width: 36px;
  text-align: center;
  display: inline-block;
}

/* 临时结果 */
.interim-result {
  position: absolute;
  top: -40px;
  left: 0;
  padding: 8px 12px;
  background: rgba(102, 126, 234, 0.9);
  color: white;
  border-radius: 8px;
  font-size: 14px;
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.interim-result::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 20px;
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid rgba(102, 126, 234, 0.9);
}

/* 不支持图标 */
.unsupported-icon {
  color: #f59e0b;
  font-size: 20px;
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>


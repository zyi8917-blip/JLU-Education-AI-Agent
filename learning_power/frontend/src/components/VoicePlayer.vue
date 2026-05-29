<template>
  <div class="voice-player">
    <!-- 播放按钮 -->
    <el-button
      :class="['play-button', statusClass]"
      :disabled="!isSupported || disabled"
      @click="togglePlay"
      circle
      size="small"
    >
      <el-icon v-if="status === 'idle'">
        <VideoPlay />
      </el-icon>
      <el-icon v-else-if="status === 'playing'">
        <VideoPause />
      </el-icon>
      <el-icon v-else-if="status === 'loading'">
        <Loading />
      </el-icon>
      <el-icon v-else-if="status === 'error'">
        <WarningFilled />
      </el-icon>
    </el-button>

    <!-- 不支持提示 -->
    <el-tooltip v-if="!isSupported" content="您的浏览器不支持语音合成" placement="top">
      <el-icon class="warning-icon">
        <WarningFilled />
      </el-icon>
    </el-tooltip>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, VideoPause, Loading, WarningFilled } from '@element-plus/icons-vue'
import { SpeechSynthesizer } from '@/utils/speech.js'

// Props
const props = defineProps({
  // 要播放的文本
  text: {
    type: String,
    required: true
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 是否自动播放
  autoPlay: {
    type: Boolean,
    default: false
  },
  // 语言
  lang: {
    type: String,
    default: 'zh-CN'
  },
  // 语速 (0.1 - 10)
  rate: {
    type: Number,
    default: 1.0
  },
  // 音调 (0 - 2)
  pitch: {
    type: Number,
    default: 1.0
  },
  // 音量 (0 - 1)
  volume: {
    type: Number,
    default: 1.0
  },
  // 使用后端 TTS 服务（Edge TTS，音质更好）
  useBackendTTS: {
    type: Boolean,
    default: true
  },
  // 音色 ID (xiaoxiao, yunxi, xiaoyi, yunjian, xiaoxuan, yunyang)
  voice: {
    type: String,
    default: 'xiaoxiao'
  }
})

// Emits
const emit = defineEmits(['start', 'end', 'pause', 'resume', 'error'])

// 状态
const status = ref('idle') // idle, loading, playing, paused, error
const isSupported = ref(false)
const synthesizer = ref(null)
const audioElement = ref(null) // 用于播放后端 TTS 音频

// 计算状态类名
const statusClass = computed(() => {
  return `status-${status.value}`
})

// 初始化
onMounted(() => {
  // 检查浏览器支持
  isSupported.value = SpeechSynthesizer.isSupported()
  
  if (!isSupported.value) {
    console.warn('浏览器不支持语音合成')
    return
  }
  
  // 创建语音合成器
  synthesizer.value = new SpeechSynthesizer({
    lang: props.lang,
    rate: props.rate,
    pitch: props.pitch,
    volume: props.volume
  })
  
  // 监听事件
  synthesizer.value.on('start', handleStart)
  synthesizer.value.on('end', handleEnd)
  synthesizer.value.on('pause', handlePause)
  synthesizer.value.on('resume', handleResume)
  synthesizer.value.on('error', handleError)
  
  // 自动播放
  if (props.autoPlay && props.text) {
    play()
  }
})

// 清理
onUnmounted(() => {
  if (synthesizer.value) {
    synthesizer.value.cancel()
  }
})

// 监听文本变化（用于自动播放）
watch(() => props.text, (newText) => {
  if (props.autoPlay && newText && status.value === 'idle') {
    play()
  }
})

// 播放
const play = async () => {
  if (!props.text) {
    return
  }

  try {
    status.value = 'loading'

    if (props.useBackendTTS) {
      // 使用后端 TTS 服务（Edge TTS）
      try {
        await playWithBackendTTS()
      } catch (backendError) {
        // 后端 TTS 失败，自动回退到浏览器 TTS
        console.warn('后端 TTS 失败，回退到浏览器 TTS:', backendError)
        ElMessage.warning('Edge TTS 服务不可用，使用浏览器语音')

        // 使用浏览器 TTS
        if (!synthesizer.value) {
          throw new Error('语音合成器未初始化')
        }
        await synthesizer.value.speak(props.text, {
          lang: props.lang,
          rate: props.rate,
          pitch: props.pitch,
          volume: props.volume
        })
      }
    } else {
      // 使用浏览器原生 TTS
      if (!synthesizer.value) {
        throw new Error('语音合成器未初始化')
      }
      await synthesizer.value.speak(props.text, {
        lang: props.lang,
        rate: props.rate,
        pitch: props.pitch,
        volume: props.volume
      })
    }
  } catch (error) {
    console.error('播放失败:', error)
    status.value = 'error'
    ElMessage.error('语音播放失败')
  }
}

// 使用后端 TTS 服务播放
const playWithBackendTTS = async () => {
  try {
    // 转换参数格式
    const ratePercent = Math.round((props.rate - 1) * 100)
    const pitchHz = Math.round((props.pitch - 1) * 50)
    const volumePercent = Math.round((props.volume - 1) * 100)

    // 调用后端 API（使用相对路径，通过 Vite 代理）
    const response = await fetch('/api/v1/tts/synthesize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: props.text,
        voice: props.voice,
        rate: `${ratePercent >= 0 ? '+' : ''}${ratePercent}%`,
        pitch: `${pitchHz >= 0 ? '+' : ''}${pitchHz}Hz`,
        volume: `${volumePercent >= 0 ? '+' : ''}${volumePercent}%`
      })
    })

    if (!response.ok) {
      throw new Error(`TTS 服务错误: ${response.status}`)
    }

    // 获取音频数据
    const audioBlob = await response.blob()
    const audioUrl = URL.createObjectURL(audioBlob)

    // 创建音频元素并播放
    if (audioElement.value) {
      audioElement.value.pause()
      audioElement.value = null
    }

    audioElement.value = new Audio(audioUrl)

    // 监听播放事件
    audioElement.value.onplay = () => {
      status.value = 'playing'
      emit('start')
    }

    audioElement.value.onended = () => {
      status.value = 'idle'
      emit('end')
      URL.revokeObjectURL(audioUrl)
    }

    audioElement.value.onerror = (error) => {
      status.value = 'error'
      emit('error', error)
      URL.revokeObjectURL(audioUrl)
    }

    // 开始播放
    await audioElement.value.play()

  } catch (error) {
    console.error('后端 TTS 播放失败:', error)
    throw error
  }
}

// 停止
const stop = () => {
  if (props.useBackendTTS && audioElement.value) {
    audioElement.value.pause()
    audioElement.value.currentTime = 0
    status.value = 'idle'
  } else if (synthesizer.value) {
    synthesizer.value.cancel()
    status.value = 'idle'
  }
}

// 暂停
const pause = () => {
  if (synthesizer.value) {
    synthesizer.value.pause()
  }
}

// 继续
const resume = () => {
  if (synthesizer.value) {
    synthesizer.value.resume()
  }
}

// 切换播放/暂停
const togglePlay = () => {
  if (status.value === 'idle' || status.value === 'error') {
    play()
  } else if (status.value === 'playing') {
    stop()
  }
}

// 事件处理
const handleStart = () => {
  status.value = 'playing'
  emit('start')
}

const handleEnd = () => {
  status.value = 'idle'
  emit('end')
}

const handlePause = () => {
  status.value = 'paused'
  emit('pause')
}

const handleResume = () => {
  status.value = 'playing'
  emit('resume')
}

const handleError = (error) => {
  status.value = 'error'
  emit('error', error)
}

// 暴露方法
defineExpose({
  play,
  stop,
  pause,
  resume
})
</script>

<script>
import { computed } from 'vue'
</script>

<style scoped>
.voice-player {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.play-button {
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 空闲状态 */
.play-button.status-idle {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.play-button.status-idle:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 播放中状态 */
.play-button.status-playing {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  animation: pulse 2s ease-in-out infinite;
}

.play-button.status-playing:hover {
  transform: scale(1.1);
}

/* 加载状态 */
.play-button.status-loading {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: #ff6b6b;
}

.play-button.status-loading .el-icon {
  animation: spin 1s linear infinite;
}

/* 错误状态 */
.play-button.status-error {
  background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
  color: #d63031;
}

/* 禁用状态 */
.play-button:disabled {
  background: #e0e0e0;
  color: #9e9e9e;
  cursor: not-allowed;
  opacity: 0.6;
}

/* 警告图标 */
.warning-icon {
  color: #f5576c;
  font-size: 18px;
}

/* 脉冲动画 */
@keyframes pulse {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(245, 87, 108, 0.3);
  }
  50% {
    box-shadow: 0 4px 16px rgba(245, 87, 108, 0.6);
  }
}

/* 旋转动画 */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>


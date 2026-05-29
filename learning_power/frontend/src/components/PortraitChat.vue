<template>
  <div class="portrait-chat-container" :class="{ 'minimized': isMinimized }">
    <!-- 对话框头部 -->
    <div class="chat-header" @click="isMinimized && toggleMinimize()">
      <div class="header-left">
        <el-icon class="chat-icon"><ChatDotSquare /></el-icon>
        <span class="header-title">💬 智能学习助手</span>
      </div>
      <div class="header-actions" v-if="!isMinimized">
        <el-button 
          size="small" 
          text 
          @click.stop="toggleMinimize"
          class="action-btn"
        >
          <el-icon><Minus /></el-icon>
        </el-button>
        <el-button 
          size="small" 
          text 
          @click.stop="handleClose"
          class="action-btn"
        >
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 对话内容区域 -->
    <div class="chat-content" v-show="!isMinimized">
      <!-- 欢迎消息 -->
      <div class="welcome-message" v-if="messages.length === 0">
        <div class="welcome-icon">🎓</div>
        <h3>你好，{{ studentInfo.name }}！</h3>
        <p>我是你的学习力分析助手，可以帮你：</p>
        <ul>
          <li>📊 解读你的测评结果</li>
          <li>💡 分析你的优势和潜力</li>
          <li>🎯 提供个性化学习建议</li>
          <li>❓ 回答关于学习力的问题</li>
        </ul>
        <p class="welcome-hint">试试下面的快捷问题，或者直接输入你的问题吧！</p>
      </div>

      <!-- 对话消息列表 -->
      <div class="chat-messages" ref="messagesContainer" v-else>
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          :class="['message-item', msg.role]"
        >
          <div class="message-avatar">
            <el-icon v-if="msg.role === 'assistant'">
              <Avatar />
            </el-icon>
            <el-icon v-else>
              <User />
            </el-icon>
          </div>
          <div class="message-bubble">
            <div class="message-content" v-html="formatMessage(msg.content)"></div>
            <div class="message-time">{{ msg.time }}</div>
          </div>
        </div>
        
        <!-- 加载中提示 -->
        <div v-if="isLoading" class="message-item assistant">
          <div class="message-avatar">
            <el-icon><Avatar /></el-icon>
          </div>
          <div class="message-bubble loading">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷问题 -->
      <div class="quick-questions" v-if="!isLoading">
        <div class="quick-title">💡 快捷问题：</div>
        <div class="quick-buttons">
          <el-button 
            v-for="(question, index) in quickQuestions" 
            :key="index"
            size="small"
            @click="sendQuickQuestion(question)"
            class="quick-btn"
          >
            {{ question }}
          </el-button>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input">
        <el-input
          v-model="userInput"
          placeholder="输入你的问题..."
          @keyup.enter="sendMessage"
          :disabled="isLoading"
          class="input-field"
        >
          <template #suffix>
            <el-button 
              type="primary" 
              @click="sendMessage"
              :disabled="!userInput.trim() || isLoading"
              :loading="isLoading"
              class="send-btn"
            >
              发送
            </el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotSquare, Close, Minus, Avatar, User } from '@element-plus/icons-vue'
import { chatWithPortrait } from '@/api/chat'

// Props
const props = defineProps({
  studentInfo: {
    type: Object,
    required: true
  },
  portraitData: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['close'])

// 状态
const isMinimized = ref(false)
const isLoading = ref(false)
const userInput = ref('')
const messages = ref([])
const messagesContainer = ref(null)

// 快捷问题
const quickQuestions = ref([
  '我的优势是什么？',
  '如何提升我的弱项？',
  '各项指标是什么意思？',
  '我适合什么学习方法？',
  '与同龄人相比如何？'
])

// 切换最小化
const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
}

// 关闭对话框
const handleClose = () => {
  emit('close')
}

// 发送快捷问题
const sendQuickQuestion = (question) => {
  userInput.value = question
  sendMessage()
}

// 发送消息
const sendMessage = async () => {
  const message = userInput.value.trim()
  if (!message || isLoading.value) return

  // 添加用户消息
  const userMessage = {
    role: 'user',
    content: message,
    time: formatTime(new Date())
  }
  messages.value.push(userMessage)
  userInput.value = ''

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // 调用API
  isLoading.value = true
  
  try {
    // 构建对话历史（只发送role和content）
    const chatHistory = messages.value.map(msg => ({
      role: msg.role,
      content: msg.content
    }))

    const response = await chatWithPortrait({
      student_id: props.studentInfo.id,
      student_name: props.studentInfo.name,
      message: message,
      portrait_data: props.portraitData,
      chat_history: chatHistory.slice(0, -1)  // 不包含刚发送的消息
    })

    // 添加助手回复
    const assistantMessage = {
      role: 'assistant',
      content: response.data.reply,
      time: formatTime(new Date())
    }
    messages.value.push(assistantMessage)

    // 滚动到底部
    await nextTick()
    scrollToBottom()

  } catch (error) {
    console.error('Chat error:', error)
    ElMessage.error('对话失败，请稍后重试')
    
    // 添加错误提示消息
    const errorMessage = {
      role: 'assistant',
      content: '抱歉，我暂时无法回答你的问题，请稍后再试。',
      time: formatTime(new Date())
    }
    messages.value.push(errorMessage)
  } finally {
    isLoading.value = false
  }
}

// 格式化消息内容（支持简单的Markdown）
const formatMessage = (content) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // 粗体
    .replace(/\n/g, '<br>')  // 换行
    .replace(/【(.*?)】/g, '<div class="section-title">【$1】</div>')  // 章节标题
    .replace(/(\d+)\.\s/g, '<br>$1. ')  // 列表项
}

// 格式化时间
const formatTime = (date) => {
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 监听消息变化，自动滚动
watch(() => messages.value.length, () => {
  nextTick(() => {
    scrollToBottom()
  })
})
</script>

<style scoped>
.portrait-chat-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 420px;
  height: 650px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  z-index: 2000;
  transition: all 0.3s ease;
  overflow: hidden;
}

.portrait-chat-container.minimized {
  height: 60px;
  cursor: pointer;
}

/* 头部样式 */
.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-icon {
  font-size: 20px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  color: white !important;
  padding: 4px !important;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2) !important;
}

/* 内容区域 */
.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 欢迎消息 */
.welcome-message {
  padding: 30px 24px;
  text-align: center;
  color: #606266;
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome-message h3 {
  font-size: 20px;
  color: #303133;
  margin-bottom: 12px;
}

.welcome-message p {
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.6;
}

.welcome-message ul {
  text-align: left;
  max-width: 300px;
  margin: 0 auto 16px;
  padding-left: 20px;
}

.welcome-message li {
  margin-bottom: 8px;
  font-size: 14px;
}

.welcome-hint {
  font-size: 13px;
  color: #909399;
  font-style: italic;
}

/* 消息列表 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
}

.message-item {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.message-item.user .message-avatar {
  background: linear-gradient(135deg, #42b983 0%, #33a06f 100%);
}

.message-bubble {
  max-width: 70%;
  margin: 0 12px;
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

.message-item.assistant .message-content {
  background: white;
  color: #303133;
  border: 1px solid #e4e7ed;
}

.message-item.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  padding: 0 4px;
}

/* 加载动画 */
.message-bubble.loading {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #909399;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* 快捷问题 */
.quick-questions {
  padding: 12px 16px;
  background: white;
  border-top: 1px solid #e4e7ed;
}

.quick-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.quick-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-btn {
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 16px;
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  color: #606266;
  transition: all 0.3s;
}

.quick-btn:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  transform: translateY(-2px);
}

/* 输入区域 */
.chat-input {
  padding: 16px;
  background: white;
  border-top: 1px solid #e4e7ed;
}

.input-field {
  width: 100%;
}

.input-field :deep(.el-input__wrapper) {
  border-radius: 20px;
  padding-right: 80px;
}

.send-btn {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  border-radius: 16px;
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

/* 消息内容格式化样式 */
.message-content :deep(.section-title) {
  font-weight: bold;
  color: #409eff;
  margin: 8px 0 4px;
}

.message-content :deep(strong) {
  font-weight: 600;
  color: #303133;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>


/**
 * 语音识别和合成工具类
 * 基于 Web Speech API
 */

/**
 * 语音识别器
 * 用于将语音转换为文字
 */
export class SpeechRecognizer {
  constructor(options = {}) {
    // 检查浏览器支持
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      throw new Error('浏览器不支持语音识别')
    }
    
    // 创建识别器实例
    this.recognition = new SpeechRecognition()
    
    // 配置参数
    this.recognition.lang = options.lang || 'zh-CN'
    this.recognition.continuous = options.continuous || false
    this.recognition.interimResults = options.interimResults !== false
    this.recognition.maxAlternatives = options.maxAlternatives || 1
    
    // 状态
    this.isRecording = false
    
    // 事件监听器
    this.listeners = {
      start: [],
      result: [],
      end: [],
      error: []
    }
    
    // 绑定事件
    this._bindEvents()
  }
  
  /**
   * 检查浏览器支持
   */
  static isSupported() {
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition)
  }
  
  /**
   * 开始识别
   */
  start() {
    return new Promise((resolve, reject) => {
      if (this.isRecording) {
        reject(new Error('已经在录音中'))
        return
      }
      
      try {
        this.recognition.start()
        this.isRecording = true
        resolve()
      } catch (error) {
        reject(error)
      }
    })
  }
  
  /**
   * 停止识别
   */
  stop() {
    if (this.isRecording) {
      this.recognition.stop()
      this.isRecording = false
    }
  }
  
  /**
   * 取消识别
   */
  abort() {
    if (this.isRecording) {
      this.recognition.abort()
      this.isRecording = false
    }
  }
  
  /**
   * 监听事件
   */
  on(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event].push(callback)
    }
  }
  
  /**
   * 移除监听
   */
  off(event, callback) {
    if (this.listeners[event]) {
      const index = this.listeners[event].indexOf(callback)
      if (index > -1) {
        this.listeners[event].splice(index, 1)
      }
    }
  }
  
  /**
   * 触发事件
   */
  _emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data))
    }
  }
  
  /**
   * 绑定原生事件
   */
  _bindEvents() {
    // 开始录音
    this.recognition.onstart = () => {
      this._emit('start')
    }
    
    // 识别结果
    this.recognition.onresult = (event) => {
      const results = []
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        const transcript = result[0].transcript
        const confidence = result[0].confidence
        const isFinal = result.isFinal
        
        results.push({
          transcript,
          confidence,
          isFinal
        })
      }
      
      this._emit('result', results)
    }
    
    // 识别结束
    this.recognition.onend = () => {
      this.isRecording = false
      this._emit('end')
    }
    
    // 识别错误
    this.recognition.onerror = (event) => {
      this.isRecording = false
      this._emit('error', {
        error: event.error,
        message: this._getErrorMessage(event.error)
      })
    }
  }
  
  /**
   * 获取错误消息
   */
  _getErrorMessage(error) {
    const messages = {
      'no-speech': '未检测到语音，请重试',
      'audio-capture': '无法访问麦克风，请检查权限',
      'not-allowed': '麦克风权限被拒绝',
      'network': '网络错误，请检查网络连接',
      'aborted': '识别已取消',
      'service-not-allowed': '语音识别服务不可用'
    }
    
    return messages[error] || '语音识别失败，请重试'
  }
}

/**
 * 语音合成器
 * 用于将文字转换为语音
 */
export class SpeechSynthesizer {
  constructor(options = {}) {
    // 检查浏览器支持
    if (!('speechSynthesis' in window)) {
      throw new Error('浏览器不支持语音合成')
    }
    
    this.synthesis = window.speechSynthesis
    
    // 配置参数
    this.options = {
      lang: options.lang || 'zh-CN',
      rate: options.rate || 1.0,
      pitch: options.pitch || 1.0,
      volume: options.volume || 1.0,
      voice: options.voice || null
    }
    
    // 状态
    this.isSpeaking = false
    this.isPaused = false
    this.currentUtterance = null
    
    // 事件监听器
    this.listeners = {
      start: [],
      end: [],
      pause: [],
      resume: [],
      error: []
    }
  }
  
  /**
   * 检查浏览器支持
   */
  static isSupported() {
    return 'speechSynthesis' in window
  }
  
  /**
   * 播放文本
   */
  speak(text, options = {}) {
    return new Promise((resolve, reject) => {
      // 停止当前播放
      this.cancel()
      
      // 创建语音对象
      const utterance = new SpeechSynthesisUtterance(text)
      
      // 设置参数
      utterance.lang = options.lang || this.options.lang
      utterance.rate = options.rate || this.options.rate
      utterance.pitch = options.pitch || this.options.pitch
      utterance.volume = options.volume || this.options.volume
      
      // 设置语音
      if (options.voice || this.options.voice) {
        utterance.voice = options.voice || this.options.voice
      }
      
      // 绑定事件
      utterance.onstart = () => {
        this.isSpeaking = true
        this._emit('start')
      }
      
      utterance.onend = () => {
        this.isSpeaking = false
        this.currentUtterance = null
        this._emit('end')
        resolve()
      }
      
      utterance.onerror = (event) => {
        this.isSpeaking = false
        this.currentUtterance = null
        this._emit('error', event)
        reject(event)
      }
      
      utterance.onpause = () => {
        this.isPaused = true
        this._emit('pause')
      }
      
      utterance.onresume = () => {
        this.isPaused = false
        this._emit('resume')
      }
      
      // 保存当前语音对象
      this.currentUtterance = utterance
      
      // 开始播放
      this.synthesis.speak(utterance)
    })
  }
  
  /**
   * 暂停播放
   */
  pause() {
    if (this.isSpeaking && !this.isPaused) {
      this.synthesis.pause()
    }
  }
  
  /**
   * 继续播放
   */
  resume() {
    if (this.isSpeaking && this.isPaused) {
      this.synthesis.resume()
    }
  }
  
  /**
   * 停止播放
   */
  cancel() {
    if (this.isSpeaking) {
      this.synthesis.cancel()
      this.isSpeaking = false
      this.isPaused = false
      this.currentUtterance = null
    }
  }
  
  /**
   * 获取可用语音列表
   */
  getVoices() {
    return new Promise((resolve) => {
      let voices = this.synthesis.getVoices()
      
      if (voices.length > 0) {
        resolve(voices)
      } else {
        // 某些浏览器需要等待 voiceschanged 事件
        this.synthesis.onvoiceschanged = () => {
          voices = this.synthesis.getVoices()
          resolve(voices)
        }
      }
    })
  }
  
  /**
   * 监听事件
   */
  on(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event].push(callback)
    }
  }
  
  /**
   * 移除监听
   */
  off(event, callback) {
    if (this.listeners[event]) {
      const index = this.listeners[event].indexOf(callback)
      if (index > -1) {
        this.listeners[event].splice(index, 1)
      }
    }
  }
  
  /**
   * 触发事件
   */
  _emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data))
    }
  }
}

/**
 * 检查语音功能支持
 */
export function checkSpeechSupport() {
  return {
    recognition: SpeechRecognizer.isSupported(),
    synthesis: SpeechSynthesizer.isSupported()
  }
}


import { defineStore } from 'pinia'

// 学生管理Store
export const useStudentStore = defineStore('student', {
  state: () => ({
    students: [],
    currentStudent: null,
    total: 0
  }),
  
  actions: {
    setStudents(students) {
      this.students = students
    },
    
    setCurrentStudent(student) {
      this.currentStudent = student
    },
    
    setTotal(total) {
      this.total = total
    }
  }
})

// 测评Store
export const useAssessmentStore = defineStore('assessment', {
  state: () => ({
    currentSession: null,
    questions: [],
    currentQuestionIndex: 0,
    answers: [],
    scores: null
  }),
  
  getters: {
    currentQuestion: (state) => {
      return state.questions[state.currentQuestionIndex] || null
    },
    
    progress: (state) => {
      if (state.questions.length === 0) return 0
      return Math.round((state.currentQuestionIndex / state.questions.length) * 100)
    }
  },
  
  actions: {
    setSession(session) {
      this.currentSession = session
    },
    
    setQuestions(questions) {
      this.questions = questions
    },
    
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++
      }
    },
    
    prevQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
      }
    },
    
    addAnswer(answer) {
      this.answers.push(answer)
    },
    
    setScores(scores) {
      this.scores = scores
    },
    
    reset() {
      this.currentSession = null
      this.questions = []
      this.currentQuestionIndex = 0
      this.answers = []
      this.scores = null
    }
  }
})

// 系统Store
export const useSystemStore = defineStore('system', {
  state: () => ({
    config: {
      max_questions: 10,
      time_limit_minutes: 30,
      model_name: 'DeepSeek-V3',
      debug: false
    },
    statistics: null
  }),
  
  actions: {
    setConfig(config) {
      this.config = config
    },
    
    setStatistics(statistics) {
      this.statistics = statistics
    }
  }
})


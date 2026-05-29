<template>
  <div class="settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>
      
      <el-form :model="config" label-width="150px" style="max-width: 600px">
        <el-form-item label="最大题目数量">
          <el-input-number v-model="config.max_questions" :min="1" :max="50" />
        </el-form-item>
        <el-form-item label="时间限制(分钟)">
          <el-input-number v-model="config.time_limit_minutes" :min="1" :max="120" />
        </el-form-item>
        <el-form-item label="AI模型">
          <el-input v-model="config.model_name" disabled />
        </el-form-item>
        <el-form-item label="调试模式">
          <el-switch v-model="config.debug" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig" :loading="loading">
            保存设置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getConfig, updateConfig } from '@/api/system'

const loading = ref(false)
const config = ref({
  max_questions: 10,
  time_limit_minutes: 30,
  model_name: 'DeepSeek-V3',
  debug: false
})

const loadConfig = async () => {
  try {
    const res = await getConfig()
    config.value = res.data
  } catch (error) {
    console.error('Failed to load config:', error)
  }
}

const saveConfig = async () => {
  loading.value = true
  try {
    await updateConfig(config.value)
    ElMessage.success('设置已保存')
  } catch (error) {
    console.error('Failed to save config:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.settings {
  padding: 0;
}

.card-header {
  font-weight: 500;
  font-size: 16px;
}
</style>


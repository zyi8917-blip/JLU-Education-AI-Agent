<template>
  <div class="students">
    <el-card>
      <!-- 搜索和操作栏 -->
      <div class="toolbar">
        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索学生姓名"
            clearable
            style="width: 300px"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="searchGrade"
            placeholder="选择年级"
            clearable
            style="width: 150px; margin-left: 10px"
            @change="handleSearch"
          >
            <el-option
              v-for="grade in gradeOptions"
              :key="grade"
              :label="grade"
              :value="grade"
            />
          </el-select>
          <el-button type="primary" @click="handleSearch" style="margin-left: 10px">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </div>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加学生
        </el-button>
      </div>

      <!-- 学生列表 -->
      <el-table
        :data="students"
        style="width: 100%; margin-top: 20px"
        v-loading="loading"
      >
        <el-table-column prop="student_id" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="grade" label="年级" width="100" />
        <el-table-column prop="college" label="学院" width="180" />
        <el-table-column prop="school" label="学校" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="学号" prop="student_id">
          <el-input
            v-model="form.student_id"
            placeholder="请输入学号"
            :disabled="dialogTitle === '编辑学生'"
          />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%">
            <el-option
              v-for="gender in genderOptions"
              :key="gender"
              :label="gender"
              :value="gender"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="form.age" :min="16" :max="100" />
        </el-form-item>
        <el-form-item label="年级" prop="grade">
          <el-select v-model="form.grade" placeholder="请选择年级" style="width: 100%">
            <el-option
              v-for="grade in gradeOptions"
              :key="grade"
              :label="grade"
              :value="grade"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学院" prop="college">
          <el-input v-model="form.college" placeholder="请输入学院名称" />
        </el-form-item>
        <el-form-item label="学校" prop="school">
          <el-input v-model="form.school" placeholder="请输入学校名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getStudents, createStudent, updateStudent, deleteStudent, getStudentOptions } from '@/api/students'
import { useStudentStore } from '@/store'

const studentStore = useStudentStore()

const loading = ref(false)
const students = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const searchGrade = ref('')

// 选项数据
const gradeOptions = ref([])
const genderOptions = ref([])
const defaultSchool = ref('吉林大学')

const dialogVisible = ref(false)
const dialogTitle = ref('添加学生')
const formRef = ref(null)
const form = reactive({
  name: '',
  student_id: '',
  gender: '',
  age: 18,
  grade: '',
  college: '',
  school: '吉林大学'
})

const rules = {
  name: [{ required: true, message: '请输入学生姓名', trigger: 'blur' }],
  student_id: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }],
  college: [{ required: true, message: '请输入学院', trigger: 'blur' }]
}

// 加载选项数据
const loadOptions = async () => {
  try {
    const res = await getStudentOptions()
    gradeOptions.value = res.data.grades
    genderOptions.value = res.data.genders
    defaultSchool.value = res.data.default_school
    form.school = res.data.default_school
  } catch (error) {
    console.error('Failed to load options:', error)
  }
}

const loadStudents = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      keyword: searchKeyword.value,
      grade: searchGrade.value
    }
    const res = await getStudents(params)
    students.value = res.data.students
    total.value = res.data.total
    studentStore.setStudents(res.data.students)
    studentStore.setTotal(res.data.total)
  } catch (error) {
    console.error('Failed to load students:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadStudents()
}

const handleAdd = () => {
  dialogTitle.value = '添加学生'
  Object.assign(form, {
    name: '',
    student_id: '',
    gender: '',
    age: 18,
    grade: '',
    college: '',
    school: defaultSchool.value
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑学生'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该学生吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteStudent(row.student_id)
    ElMessage.success('删除成功')
    loadStudents()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete student:', error)
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    if (dialogTitle.value === '编辑学生') {
      await updateStudent(form.student_id, form)
      ElMessage.success('更新成功')
    } else {
      await createStudent(form)
      ElMessage.success('添加成功')
    }

    dialogVisible.value = false
    loadStudents()
  } catch (error) {
    console.error('Failed to submit:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const handleSizeChange = () => {
  loadStudents()
}

const handlePageChange = () => {
  loadStudents()
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadOptions()
  loadStudents()
})
</script>

<style scoped>
.students {
  padding: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>


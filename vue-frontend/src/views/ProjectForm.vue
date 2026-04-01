<template>
  <div class="project-form">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑项目' : '新建项目' }}</span>
        </div>
      </template>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入项目名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目代码" prop="code">
              <el-input v-model="form.code" placeholder="请输入项目代码" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="项目描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入项目描述" 
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目负责人" prop="manager_id">
              <el-select v-model="form.manager_id" placeholder="请选择项目负责人" filterable>
                <el-option 
                  v-for="user in users" 
                  :key="user.id" 
                  :label="user.username" 
                  :value="user.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目类型" prop="project_type">
              <el-select v-model="form.project_type" placeholder="请选择项目类型">
                <el-option label="内部项目" value="internal" />
                <el-option label="客户项目" value="client" />
                <el-option label="研发项目" value="rd" />
                <el-option label="维护项目" value="maintenance" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker 
                v-model="form.start_date" 
                type="date" 
                placeholder="选择开始日期" 
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker 
                v-model="form.end_date" 
                type="date" 
                placeholder="选择结束日期" 
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择项目状态">
                <el-option label="活跃" value="active" />
                <el-option label="已完成" value="completed" />
                <el-option label="已关闭" value="closed" />
                <el-option label="已归档" value="archived" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" placeholder="请选择优先级">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="紧急" value="urgent" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预算" prop="budget">
              <el-input-number v-model="form.budget" :min="0" :step="1000" placeholder="请输入预算金额" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际成本" prop="actual_cost">
              <el-input-number v-model="form.actual_cost" :min="0" :step="1000" placeholder="请输入实际成本" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同金额" prop="contract_value">
              <el-input-number v-model="form.contract_value" :min="0" :step="1000" placeholder="请输入合同金额" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预估工时" prop="estimated_hours">
              <el-input-number v-model="form.estimated_hours" :min="0" :step="8" placeholder="请输入预估工时" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="实际工时" prop="actual_hours">
              <el-input-number v-model="form.actual_hours" :min="0" :step="8" placeholder="请输入实际工时" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="团队规模" prop="team_size">
              <el-input-number v-model="form.team_size" :min="0" :step="1" placeholder="请输入团队人数" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户名称" prop="client_name">
              <el-input v-model="form.client_name" placeholder="请输入客户名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户联系方式" prop="client_contact">
              <el-input v-model="form.client_contact" placeholder="请输入客户联系方式" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="技术栈" prop="technology_stack">
          <el-input 
            v-model="form.technology_stack" 
            type="textarea" 
            :rows="2" 
            placeholder="请输入项目使用的技术栈" 
          />
        </el-form-item>
        
        <el-form-item label="标签" prop="tags">
          <el-input v-model="form.tags" placeholder="请输入项目标签，多个标签用逗号分隔" />
        </el-form-item>
        
        <el-form-item label="里程碑" prop="milestones">
          <el-input 
            v-model="form.milestones" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入项目里程碑，每个里程碑用换行分隔" 
          />
        </el-form-item>
        
        <!-- 版本管理 -->
        <el-form-item label="项目版本" prop="versions">
          <div class="version-management">
            <div v-for="(version, index) in versions" :key="index" class="version-item">
              <el-input 
                v-model="version.name" 
                placeholder="版本名称，如 v1.0"
                style="width: 30%"
              />
              <el-input 
                v-model="version.description" 
                placeholder="版本描述"
                style="width: 45%"
              />
              <el-date-picker
                v-model="version.release_date"
                type="date"
                placeholder="发布日期"
                value-format="YYYY-MM-DD"
                style="width: 20%"
              />
              <el-button 
                type="danger" 
                :icon="Delete" 
                circle 
                @click="removeVersion(index)"
              />
            </div>
            <el-button type="primary" plain @click="addVersion">
              <el-icon><Plus /></el-icon>
              添加版本
            </el-button>
          </div>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="当前阶段" prop="current_stage">
              <el-input v-model="form.current_stage" placeholder="请输入当前阶段" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="进度" prop="progress">
              <el-slider v-model="form.progress" :min="0" :max="100" :show-tooltip="true" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="质量" prop="quality">
              <el-select v-model="form.quality" placeholder="选择质量等级">
                <el-option label="优秀" value="Excellent" />
                <el-option label="良好" value="Good" />
                <el-option label="一般" value="Fair" />
                <el-option label="差" value="Poor" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="风险" prop="risk">
              <el-select v-model="form.risk" placeholder="选择风险等级">
                <el-option label="低" value="Low" />
                <el-option label="中" value="Medium" />
                <el-option label="高" value="High" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            {{ isEdit ? '更新项目' : '创建项目' }}
          </el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete, Plus } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)
const users = ref([])

const isEdit = ref(false)
const projectId = ref(null)

const form = reactive({
  name: '',
  code: '',
  description: '',
  manager_id: '',
  start_date: '',
  end_date: '',
  status: 'active',
  priority: 'medium',
  project_type: '',
  budget: 0,
  actual_cost: 0,
  contract_value: 0,
  estimated_hours: 0,
  actual_hours: 0,
  team_size: 0,
  client_name: '',
  client_contact: '',
  technology_stack: '',
  tags: '',
  milestones: '',
  current_stage: '',
  progress: 0,
  quality: 'Fair',
  risk: 'Medium'
})

const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入项目代码', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入项目描述', trigger: 'blur' },
    { min: 10, max: 500, message: '长度在 10 到 500 个字符', trigger: 'blur' }
  ],
  manager_id: [
    { required: true, message: '请选择项目负责人', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择项目状态', trigger: 'change' }
  ]
}

const versions = ref([])

const addVersion = () => {
  versions.value.push({
    name: '',
    description: '',
    release_date: ''
  })
}

const removeVersion = (index) => {
  versions.value.splice(index, 1)
}

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await apiService.users.getList()
    users.value = response.users || response || []
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  }
}

// 加载项目详情（编辑模式）
const loadProject = async () => {
  if (!projectId.value) return
  
  try {
    const response = await apiService.projects.getById(projectId.value)
    const projectData = response.project || response || {}
    Object.assign(form, projectData)
    
    // 解析versions字段
    if (projectData.versions) {
      try {
        versions.value = typeof projectData.versions === 'string' 
          ? JSON.parse(projectData.versions) 
          : projectData.versions
      } catch (e) {
        console.error('解析versions失败:', e)
        versions.value = []
      }
    }
  } catch (error) {
    console.error('加载项目详情失败:', error)
    ElMessage.error('加载项目详情失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    loading.value = true
    
    // 格式化日期字段为ISO字符串
    const submitData = {
      ...form,
      start_date: form.start_date ? new Date(form.start_date).toISOString() : null,
      end_date: form.end_date ? new Date(form.end_date).toISOString() : null,
      versions: JSON.stringify(versions.value)
    }
    
    if (isEdit.value) {
      // 编辑项目
      await apiService.projects.update(projectId.value, submitData)
      ElMessage.success('项目更新成功')
    } else {
      // 新建项目
      await apiService.projects.create(submitData)
      ElMessage.success('项目创建成功')
    }
    
    router.push('/projects/list')
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    loading.value = false
  }
}

// 取消操作
const handleCancel = () => {
  router.push('/projects/list')
}

onMounted(() => {
  // 检查是否是编辑模式
  if (route.params.id) {
    isEdit.value = true
    projectId.value = route.params.id
    loadProject()
  }
  
  loadUsers()
})
</script>

<style scoped>
.project-form {
  padding: 20px;
}

.form-card {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.version-management {
  width: 100%;
}

.version-item {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .project-form {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page-header h2 {
    font-size: 18px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 12px;
    padding: 8px 12px;
  }

  .project-form-card {
    margin-bottom: 16px;
  }

  .el-form-item {
    margin-bottom: 16px;
  }

  .el-form-item__label {
    font-size: 13px;
  }

  .el-input__inner,
  .el-textarea__inner {
    font-size: 14px;
  }

  .el-select,
  .el-input,
  .el-textarea {
    width: 100% !important;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .project-form {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .el-form-item__label {
    font-size: 12px;
  }
}
</style>
<template>
  <div class="test-case-manage">
    <a-card title="用例管理">
      <a-row :gutter="16" style="margin-bottom: 16px;">
        <a-col :span="8">
          <a-form-item label="选择项目">
            <a-select
              v-model:value="selectedProjectId"
              placeholder="请选择项目"
              @change="onProjectChange"
            >
              <a-select-option
                v-for="project in projects"
                :key="project.id"
                :value="project.id"
              >
                {{ project.name }}
              </a-select-option>
            </a-select>
          </a-form-item>
        </a-col>
        <a-col :span="4">
          <a-button
            type="primary"
            @click="showModal()"
            :disabled="!selectedProjectId"
          >
            创建用例
          </a-button>
        </a-col>
      </a-row>

      <a-table
        :dataSource="testCases"
        :columns="columns"
        :loading="loading"
        rowKey="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'action'">
            <a-space>
              <a-button type="link" @click="showModal(record)">编辑</a-button>
              <a-popconfirm
                title="确定要删除这个用例吗？"
                @confirm="handleDelete(record.id)"
              >
                <a-button type="link" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 用例编辑/创建模态框 -->
    <a-modal
      v-model:visible="visible"
      :title="editingTestCase ? '编辑用例' : '创建用例'"
      :footer="null"
      @cancel="handleCancel"
      width="60%"
    >
      <a-form :model="form" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="用例名称" name="name" :rules="[{ required: true, message: '请输入用例名称' }]">
              <a-input v-model:value="form.name" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="请求方法" name="method" :rules="[{ required: true, message: '请选择请求方法' }]">
              <a-select v-model:value="form.method">
                <a-select-option value="GET">GET</a-select-option>
                <a-select-option value="POST">POST</a-select-option>
                <a-select-option value="PUT">PUT</a-select-option>
                <a-select-option value="DELETE">DELETE</a-select-option>
                <a-select-option value="PATCH">PATCH</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="Base URL" name="baseUrl" :rules="[{ required: true, message: '请输入Base URL' }]">
          <a-input v-model:value="baseUrl" placeholder="https://api.example.com" />
        </a-form-item>

        <a-form-item label="接口路径" name="path" :rules="[{ required: true, message: '请输入接口路径' }]">
          <a-input v-model:value="form.path" placeholder="/api/users" />
        </a-form-item>

        <a-tabs v-model:activeKey="activeTab">
          <a-tab-pane key="headers" tab="Headers">
            <a-form-item>
              <a-textarea
                v-model:value="headersJson"
                :rows="6"
                placeholder='{"Content-Type": "application/json"}'
              />
            </a-form-item>
          </a-tab-pane>
          <a-tab-pane key="body" tab="Body">
            <a-form-item>
              <a-textarea
                v-model:value="bodyJson"
                :rows="6"
                placeholder='{"name": "test", "age": 18}'
              />
            </a-form-item>
          </a-tab-pane>
          <a-tab-pane key="config" tab="配置元件">
            <a-form-item>
              <a-textarea
                v-model:value="configElementsJson"
                :rows="6"
                placeholder='[{"type": "extractor", "key": "token", "expression": "$.data.token"}]'
              />
            </a-form-item>
          </a-tab-pane>
        </a-tabs>
        
        <div style="text-align: right; margin-top: 20px;">
          <a-button @click="handleCancel" style="margin-right: 8px;">取消</a-button>
          <a-button @click="handleDebug" type="primary" :loading="debugLoading" style="margin-right: 8px;">发送调试</a-button>
          <a-button @click="handleOk" type="primary">保存用例</a-button>
        </div>
      </a-form>
      
      <!-- 调试结果展示区 -->
      <div v-if="debugResult" style="margin-top: 20px;">
        <a-alert 
          :type="debugResult.overall_pass ? 'success' : 'error'" 
          :message="`调试${debugResult.overall_pass ? '通过' : '失败'}`"
          :show-icon="true"
        >
          <template #description>
            <p>状态码: {{ debugResult.response_info.status_code }}</p>
            <p>耗时: {{ debugResult.response_info.elapsed_time }} ms</p>
          </template>
        </a-alert>
        
        <a-descriptions title="请求信息" bordered size="small" style="margin-top: 20px;">
          <a-descriptions-item label="方法">{{ debugResult.request_info.method }}</a-descriptions-item>
          <a-descriptions-item label="URL">{{ debugResult.request_info.url }}</a-descriptions-item>
        </a-descriptions>
        
        <a-collapse style="margin-top: 20px;">
          <a-collapse-panel key="1" header="断言详情">
            <a-table 
              :dataSource="debugResult.assertion_results" 
              :columns="assertionColumns" 
              :pagination="false"
              size="small"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.dataIndex === 'passed'">
                  <span :style="{ color: record.passed ? 'green' : 'red' }">
                    {{ record.passed ? '通过' : '失败' }}
                  </span>
                </template>
              </template>
            </a-table>
          </a-collapse-panel>
          
          <a-collapse-panel key="2" header="响应体">
            <pre>{{ JSON.stringify(debugResult.response_info.response_body, null, 2) }}</pre>
          </a-collapse-panel>
        </a-collapse>
      </div>
    </a-modal>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { message } from 'ant-design-vue'

export default {
  name: 'TestCaseView',
  setup() {
    const projects = ref([])
    const testCases = ref([])
    const loading = ref(false)
    const visible = ref(false)
    const editingTestCase = ref(null)
    const selectedProjectId = ref(null)
    const activeTab = ref('headers')
    // 新增状态变量
    const debugResult = ref(null)
    const debugLoading = ref(false)
    const baseUrl = ref('')

    const form = reactive({
      name: '',
      method: 'GET',
      path: ''
    })

    const headersJson = ref('')
    const bodyJson = ref('')
    const configElementsJson = ref('')

    const columns = [
      {
        title: '用例名称',
        dataIndex: 'name',
        key: 'name'
      },
      {
        title: '请求方法',
        dataIndex: 'method',
        key: 'method'
      },
      {
        title: '接口路径',
        dataIndex: 'path',
        key: 'path'
      },
      {
        title: '所属项目',
        dataIndex: 'project_name',
        key: 'project_name'
      },
      {
        title: '创建者',
        dataIndex: 'creator_name',
        key: 'creator_name'
      },
      {
        title: '操作',
        dataIndex: 'action',
        key: 'action'
      }
    ]
    
    // 断言结果表格列定义
    const assertionColumns = [
      {
        title: '断言类型',
        dataIndex: 'check_type',
        key: 'check_type'
      },
      {
        title: '期望值',
        dataIndex: 'expected',
        key: 'expected'
      },
      {
        title: '实际值',
        dataIndex: 'actual',
        key: 'actual'
      },
      {
        title: '结果',
        dataIndex: 'passed',
        key: 'passed'
      },
      {
        title: '信息',
        dataIndex: 'message',
        key: 'message'
      }
    ]

    // 获取项目列表
    const fetchProjects = async () => {
      try {
        const response = await axios.get('/api/projects/')
        projects.value = response.data
      } catch (error) {
        console.error('获取项目列表失败:', error)
        message.error('获取项目列表失败')
      }
    }

    // 获取用例列表
    const fetchTestCases = async (projectId) => {
      if (!projectId) return

      loading.value = true
      try {
        const response = await axios.get(`/api/testcases/?project_id=${projectId}`)
        testCases.value = response.data
      } catch (error) {
        console.error('获取用例列表失败:', error)
        message.error('获取用例列表失败')
      } finally {
        loading.value = false
      }
    }

    // 项目选择变更
    const onProjectChange = (projectId) => {
      selectedProjectId.value = projectId
      fetchTestCases(projectId)
    }

    // 显示模态框
    const showModal = (testCase = null) => {
      editingTestCase.value = testCase
      if (testCase) {
        form.name = testCase.name
        form.method = testCase.method
        form.path = testCase.path
        baseUrl.value = testCase.base_url || ''

        // JSON 转换：将后端 JSON 对象转换为格式化字符串
        headersJson.value = JSON.stringify(testCase.headers || {}, null, 2)
        bodyJson.value = JSON.stringify(testCase.body || {}, null, 2)
        configElementsJson.value = JSON.stringify(testCase.config_elements || [], null, 2)
      } else {
        form.name = ''
        form.method = 'GET'
        form.path = ''
        baseUrl.value = ''
        headersJson.value = '{}'
        bodyJson.value = '{}'
        configElementsJson.value = '[]'
      }
      visible.value = true
      debugResult.value = null // 清空之前的调试结果
    }

    // 处理确认
    const handleOk = async () => {
      try {
        // JSON 校验与转换
        let headersObj = {}
        let bodyObj = {}
        let configElementsArr = []

        try {
          headersObj = headersJson.value ? JSON.parse(headersJson.value) : {}
          bodyObj = bodyJson.value ? JSON.parse(bodyJson.value) : {}
          configElementsArr = configElementsJson.value ? JSON.parse(configElementsJson.value) : []
        } catch (parseError) {
          message.error('JSON格式错误，请检查输入内容')
          return
        }

        const requestData = {
          project: selectedProjectId.value,
          name: form.name,
          method: form.method,
          path: form.path,
          headers: headersObj,
          body: bodyObj,
          config_elements: configElementsArr
        }

        if (editingTestCase.value) {
          // 更新用例
          await axios.put(`/api/testcases/${editingTestCase.value.id}/`, requestData)
          message.success('用例更新成功')
        } else {
          // 创建用例
          await axios.post('/api/testcases/', requestData)
          message.success('用例创建成功')
        }

        visible.value = false
        fetchTestCases(selectedProjectId.value) // 刷新列表
      } catch (error) {
        console.error('保存用例失败:', error)
        message.error('保存用例失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    // 处理取消
    const handleCancel = () => {
      visible.value = false
      editingTestCase.value = null
    }

    // 删除用例
    const handleDelete = async (id) => {
      try {
        await axios.delete(`/api/testcases/${id}/`)
        message.success('用例删除成功')
        fetchTestCases(selectedProjectId.value) // 刷新列表
      } catch (error) {
        console.error('删除用例失败:', error)
        message.error('删除用例失败')
      }
    }
    
    // 处理调试
    const handleDebug = async () => {
      debugLoading.value = true
      debugResult.value = null
      
      try {
        // 数据校验
        if (!baseUrl.value) {
          message.error('请输入Base URL')
          debugLoading.value = false
          return
        }
        
        // JSON 校验与转换
        let headersObj = {}
        let bodyObj = {}
        let configElementsArr = []

        try {
          headersObj = headersJson.value ? JSON.parse(headersJson.value) : {}
          bodyObj = bodyJson.value ? JSON.parse(bodyJson.value) : {}
          configElementsArr = configElementsJson.value ? JSON.parse(configElementsJson.value) : []
        } catch (parseError) {
          message.error('JSON格式错误，请检查输入内容')
          debugLoading.value = false
          return
        }

        // 构造请求数据
        const debugData = {
          method: form.method,
          path: form.path,
          headers: headersObj,
          body: bodyObj,
          config_elements: configElementsArr,
          base_url: baseUrl.value
        }

        // 发送调试请求
        const response = await axios.post('/api/run_testcase/', debugData)
        debugResult.value = response.data
      } catch (error) {
        console.error('调试失败:', error)
        message.error('调试失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        debugLoading.value = false
      }
    }

    // 组件挂载时获取项目列表
    onMounted(() => {
      fetchProjects()
    })

    return {
      projects,
      testCases,
      loading,
      visible,
      editingTestCase,
      selectedProjectId,
      activeTab,
      form,
      headersJson,
      bodyJson,
      configElementsJson,
      columns,
      assertionColumns,
      // 新增的返回变量
      debugResult,
      debugLoading,
      baseUrl,
      fetchProjects,
      fetchTestCases,
      onProjectChange,
      showModal,
      handleOk,
      handleCancel,
      handleDelete,
      handleDebug
    }
  }
}
</script>

<style scoped>
.test-case-manage {
  padding: 20px;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}
</style>
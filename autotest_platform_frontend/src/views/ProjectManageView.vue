/**
 * 项目管理功能模块
 *
 * 该模块提供项目数据的完整管理功能，包括数据获取、创建、编辑、删除等操作，
 * 并使用Ant Design Vue组件库构建用户界面。
 *
 * 主要功能：
 * - 数据获取：通过fetchProjects方法从后端API获取项目列表数据
 * - 创建/编辑：通过showModal和handleOk方法处理项目的创建和更新操作
 * - 删除功能：通过handleDelete方法实现项目数据的删除
 * - UI渲染：使用a-table、a-modal、a-form等Ant Design Vue组件构建界面
 * - 状态管理：通过editingProject变量区分当前处于创建或编辑模式
 */



<template>
  <div class="project-manage">
    <a-card title="项目管理">
      <template #extra>
        <a-button type="primary" @click="showModal()">创建项目</a-button>
      </template>

      <a-table
        :dataSource="projects"
        :columns="columns"
        :loading="loading"
        rowKey="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'action'">
            <a-space>
              <a-button type="link" @click="showModal(record)">编辑</a-button>
              <a-popconfirm
                title="确定要删除这个项目吗？"
                @confirm="handleDelete(record.id)"
              >
                <a-button type="link" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 项目编辑/创建模态框 -->
    <a-modal
      v-model:visible="visible"
      :title="editingProject ? '编辑项目' : '创建项目'"
      @ok="handleOk"
      @cancel="handleCancel"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="项目名称" name="name" :rules="[{ required: true, message: '请输入项目名称' }]">
          <a-input v-model:value="form.name" />
        </a-form-item>
        <a-form-item label="项目描述" name="description">
          <a-textarea v-model:value="form.description" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import axios from 'axios'

export default {
  name: 'ProjectManageView',
  setup() {
    const projects = ref([])
    const loading = ref(false)
    const visible = ref(false)
    const editingProject = ref(null)

    const form = reactive({
      name: '',
      description: ''
    })

    const columns = [
      {
        title: '项目名称',
        dataIndex: 'name',
        key: 'name'
      },
      {
        title: '项目描述',
        dataIndex: 'description',
        key: 'description'
      },
      {
        title: '创建者',
        dataIndex: 'creator_name',
        key: 'creator_name'
      },
      {
        title: '创建时间',
        dataIndex: 'created_at',
        key: 'created_at'
      },
      {
        title: '操作',
        dataIndex: 'action',
        key: 'action'
      }
    ]

    // 获取项目列表
    const fetchProjects = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/projects/')
        projects.value = response.data
      } catch (error) {
        console.error('获取项目列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 显示模态框
    const showModal = (project = null) => {
      editingProject.value = project
      if (project) {
        form.name = project.name
        form.description = project.description
      } else {
        form.name = ''
        form.description = ''
      }
      visible.value = true
    }

    // 处理确认
    const handleOk = async () => {
      try {
        if (editingProject.value) {
          // 更新项目
          await axios.put(`/api/projects/${editingProject.value.id}/`, form)
        } else {
          // 创建项目
          await axios.post('/api/projects/', form)
        }
        visible.value = false
        fetchProjects() // 刷新列表
      } catch (error) {
        console.error('保存项目失败:', error)
      }
    }

    // 处理取消
    const handleCancel = () => {
      visible.value = false
      editingProject.value = null
    }

    // 删除项目
    const handleDelete = async (id) => {
      try {
        await axios.delete(`/api/projects/${id}/`)
        fetchProjects() // 刷新列表
      } catch (error) {
        console.error('删除项目失败:', error)
      }
    }

    // 组件挂载时获取数据
    fetchProjects()

    return {
      projects,
      loading,
      visible,
      editingProject,
      form,
      columns,
      fetchProjects,
      showModal,
      handleOk,
      handleCancel,
      handleDelete
    }
  }
}
</script>

<style scoped>
.project-manage {
  padding: 20px;
}
</style>

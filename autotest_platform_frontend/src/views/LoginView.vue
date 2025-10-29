<!-- src/views/LoginView.vue -->
<template>
  <div class="login-container">
    <div class="login-form">
      <h2>用户登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名:</label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label for="password">密码:</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            placeholder="请输入密码"
          />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button type="submit" class="login-button">登录</button>
      </form>
      <div class="register-link">
        还没有账号？ <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      error: ''
    };
  },
  methods: {
    async handleLogin() {
      this.error = '';
      try {
        // 通过代理访问后端 /api/login/
        const response = await axios.post('/api/login/', {
          username: this.username,
          password: this.password
        });
        if (response.status === 200) {
          localStorage.setItem('username', response.data.username);
          this.$router.push('/'); // 跳转到首页
        }
      } catch (err) {
        if (err.response && err.response.status === 401) {
          this.error = '用户名或密码错误，请重试。';
        } else {
          this.error = '登录请求失败，请检查网络或后端服务。';
        }
        console.error('登录失败:', err);
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.login-button {
  width: 100%;
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.login-button:hover {
  background-color: #0056b3;
}

.error-message {
  color: #dc3545;
  margin-bottom: 1rem;
}

.register-link {
  text-align: center;
  margin-top: 1rem;
}
</style>

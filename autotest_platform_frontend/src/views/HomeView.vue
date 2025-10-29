<template>
  <div class="home-container">
    <div class="background-animation"></div>
    <div class="content-wrapper">
      <a-card class="welcome-card">
        <div class="card-header">
          <h1 class="welcome-title">🚀 Miaoyi接口自动化测试平台</h1>
          <p class="welcome-subtitle">高效、稳定、易用的接口自动化测试解决方案</p>
        </div>
        
        <div class="feature-grid">
          <div class="feature-item" @click="goTo('/project')">
            <div class="feature-icon project-icon">
              <span>📁</span>
            </div>
            <h3>项目管理</h3>
            <p>统一管理您的测试项目</p>
          </div>
          
          <div class="feature-item" @click="goTo('/testcase')">
            <div class="feature-icon testcase-icon">
              <span>📝</span>
            </div>
            <h3>用例管理</h3>
            <p>创建和维护测试用例</p>
          </div>
          
          <div class="feature-item coming-soon">
            <div class="feature-icon reports-icon">
              <span>📊</span>
            </div>
            <h3>测试报告</h3>
            <p>可视化测试结果报告</p>
            <div class="coming-soon-badge">敬请期待</div>
          </div>
          
          <div class="feature-item coming-soon">
            <div class="feature-icon scheduler-icon">
              <span>⏰</span>
            </div>
            <h3>定时任务</h3>
            <p>定时执行测试任务</p>
            <div class="coming-soon-badge">敬请期待</div>
          </div>
        </div>
        
        <div class="platform-stats">
          <div class="stat-item">
            <div class="stat-number">100+</div>
            <div class="stat-label">项目接入</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">10k+</div>
            <div class="stat-label">用例执行</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">99.9%</div>
            <div class="stat-label">系统稳定</div>
          </div>
        </div>
      </a-card>
    </div>
    
    <div class="floating-elements">
      <div class="floating-element" style="top: 10%; left: 5%;"></div>
      <div class="floating-element" style="top: 70%; left: 8%;"></div>
      <div class="floating-element" style="top: 30%; left: 90%;"></div>
      <div class="floating-element" style="top: 80%; left: 85%;"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  methods: {
    /**
     * 路由跳转方法
     * @param {string} path - 目标路由路径
     */
    goTo(path) {
      this.$router.push(path);
    }
  }
}
</script>

<style scoped>
.home-container {
  position: relative;
  display: flex;
  justify-content: flex-end; /* 改为靠右对齐 */
  align-items: center;
  min-height: 100vh; /* 铺满整个视口高度 */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden; /* 隐藏滚动条 */
  padding: 0; /* 移除padding */
}

.background-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, rgba(255,255,255,0.1) 25%, transparent 25%, transparent 75%, rgba(255,255,255,0.1) 75%),
              linear-gradient(45deg, rgba(255,255,255,0.1) 25%, transparent 25%, transparent 75%, rgba(255,255,255,0.1) 75%);
  background-size: 60px 60px;
  animation: moveBackground 10s linear infinite;
  z-index: 0;
}

@keyframes moveBackground {
  0% { background-position: 0 0; }
  100% { background-position: 60px 60px; }
}

.content-wrapper {
  display: flex;
  justify-content: flex-end;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.welcome-card {
  position: relative;
  width: 100%;
  max-width: 900px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  z-index: 1;
  margin: 0; /* 移除默认的margin */
}

.card-header {
  text-align: center;
  padding: 30px 20px 20px;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 30px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 25px;
  padding: 20px 40px 40px;
}

.feature-item {
  position: relative;
  text-align: center;
  padding: 25px 15px;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.feature-item:hover:not(.coming-soon) {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 0.9);
}

.feature-item.coming-soon {
  opacity: 0.7;
  cursor: not-allowed;
}

.feature-icon {
  width: 70px;
  height: 70px;
  margin: 0 auto 15px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  transition: all 0.3s ease;
}

.project-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.testcase-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.reports-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.scheduler-icon {
  background: linear-gradient(135deg, #a6c0fe 0%, #f68084 100%);
}

.feature-item:hover:not(.coming-soon) .feature-icon {
  transform: scale(1.1);
}

.feature-item h3 {
  font-size: 1.2rem;
  margin: 0 0 8px 0;
  color: #333;
}

.feature-item p {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

.coming-soon-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  color: white;
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 10px;
  font-weight: bold;
}

.platform-stats {
  display: flex;
  justify-content: space-around;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 25px;
  border-radius: 15px;
  margin: 20px 40px 40px;
  color: white;
  text-align: center;
}

.stat-item .stat-number {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-item .stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.floating-element {
  position: absolute;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.floating-element:nth-child(1) {
  width: 40px;
  height: 40px;
  animation-delay: 0s;
}

.floating-element:nth-child(2) {
  width: 25px;
  height: 25px;
  animation-delay: 1s;
}

.floating-element:nth-child(3) {
  width: 50px;
  height: 50px;
  animation-delay: 2s;
}

.floating-element:nth-child(4) {
  width: 30px;
  height: 30px;
  animation-delay: 3s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(10px, 15px);
  }
}

@media (max-width: 768px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    padding: 20px;
  }
  
  .welcome-title {
    font-size: 2rem;
  }
  
  .platform-stats {
    flex-direction: column;
    gap: 15px;
    margin: 20px;
  }
  
  .welcome-card {
    margin: 10px;
  }
  
  .content-wrapper {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
  
  .welcome-title {
    font-size: 1.5rem;
  }
  
  .welcome-subtitle {
    font-size: 1rem;
  }
}
</style>
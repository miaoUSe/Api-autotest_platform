<template>
  <div class="app-container">
    <nav class="main-nav">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">
          <span class="brand-icon">🚀</span>
          <span class="brand-text">Miaoyi</span>
        </router-link>
      </div>
      
      <div class="nav-links">
        <router-link to="/" class="nav-link">
          <span class="link-text">首页</span>
        </router-link>
        <router-link to="/about" class="nav-link">
          <span class="link-text">关于</span>
        </router-link>
      </div>
    </nav>
    
    <div class="content-wrapper">
      <router-view/>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.main-nav {
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 1.2rem;
  color: #333;
}

.brand-icon {
  font-size: 1.5rem;
  color: #667eea;
}

.brand-text {
  color: #333;
}

.nav-links {
  display: flex;
  gap: 30px;
  margin-left: auto;
}

.nav-link {
  text-decoration: none;
  color: #666;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  padding: 5px 0;
}

.nav-link:hover {
  color: #333;
  transform: translateY(-2px);
}

.nav-link.router-link-exact-active {
  color: #667eea;
  font-weight: 600;
}

.nav-link.router-link-exact-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 1px;
}

.content-wrapper {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .main-nav {
    padding: 10px 15px;
  }
  
  .nav-links {
    gap: 20px;
  }
  
  .nav-brand {
    font-size: 1.1rem;
  }
  
  .brand-icon {
    font-size: 1.3rem;
  }
}
</style>
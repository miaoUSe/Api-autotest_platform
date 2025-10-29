<template>
  <div class="about-container">
    <a-card class="about-card" :bordered="false">
      <!-- 平台名称 -->
      <h1 class="platform-title">渺逸</h1>
      <p class="platform-subtitle">接口自动化测试平台</p>

      <a-divider />

      <!-- 座右铭 -->
      <div class="motto-section">
        <a-typography-title :level="4" class="motto-title">我的座右铭</a-typography-title>
        <a-blockquote class="motto-text">
          始于业务、精于代码、成于架构
        </a-blockquote>
      </div>

      <a-divider />

      <!-- 关于平台 -->
      <div class="platform-description">
        <a-typography-title :level="5">关于平台</a-typography-title>
        <a-typography-paragraph>
          “渺逸”平台致力于提供一个高效、可靠且易于使用的接口自动化测试解决方案。它诞生于对测试工作提效的深度思考，通过将繁琐的手动测试流程转化为自动化脚本，将复杂的业务逻辑抽象为结构化的测试用例，最终构建一个稳定、可扩展的测试服务架构。
        </a-typography-paragraph>
        <a-typography-paragraph>
          希望这个平台能帮助您从重复的回归测试中解放出来，更专注于业务逻辑的深度验证和质量保障体系的建设。
        </a-typography-paragraph>
      </div>
    </a-card>
  </div>
</template>

<script>
export default {
  name: 'AboutView'
}
</script>

<style scoped>
.about-container {
  display: flex;
  justify-content: center;
  align-items: flex-start; /* 顶部对齐 */
  padding: 40px 20px;
  min-height: calc(100vh - 100px); /* 视口高度减去可能的导航栏高度 */
  background-color: #f0f2f5;
}

.about-card {
  width: 100%;
  max-width: 800px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.platform-title {
  font-size: 48px;
  font-weight: 600;
  text-align: center;
  color: #1890ff; /* 主题蓝色 */
  margin-bottom: 0;
  font-family: 'KaiTi', 'STKaiti', '楷体', serif; /* 使用楷体以增加艺术感 */
}

.platform-subtitle {
  font-size: 16px;
  text-align: center;
  color: #888;
  margin-bottom: 24px;
}

.motto-section {
  text-align: center;
  margin: 24px 0;
}

.motto-title {
  color: #555;
  margin-bottom: 16px;
}

.motto-text {
  font-size: 20px;
  font-weight: 500;
  color: #333;
  font-style: italic;
}

.platform-description {
  margin-top: 24px;
  text-align: left;
}

.ant-typography-paragraph {
  text-indent: 2em; /* 段落首行缩进 */
  line-height: 1.8;
}
</style>

// autotest_platform_frontend/vue.config.js
module.exports = {
  // *** 关键修改：设置 publicPath 为相对路径 './' ***
  publicPath: './',

  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8020', // 后端 Django 服务器地址
        changeOrigin: true,
//        pathRewrite: {
//          '^/api': '' // 移除 /api 前缀
//        }
      }
    }
  }
}
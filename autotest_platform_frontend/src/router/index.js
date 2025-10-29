// src/router/index.js

//import { createRouter, createWebHistory } from 'vue-router'
// 修改为：
import { createRouter, createWebHashHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ProjectManageView from '../views/ProjectManageView.vue'
import TestCaseView from '../views/TestCaseView.vue'
import AboutView from '../views/AboutView.vue'
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true } // 首页需要登录
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/project',
    name: 'project',
    component: ProjectManageView,
    meta: { requiresAuth: true }
  },
  {
    path: '/testcase',
    name: 'testcase',
    component: TestCaseView,
    meta: { requiresAuth: true }
  },
  {
    path: '/register',
    name: 'register',
    component: LoginView // 暂时指向 LoginView
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView,
    meta: { requiresAuth: true }
  }
]

//const router = createRouter({
//  history: createWebHistory(process.env.BASE_URL),
//  routes
//})

// 修改为：
const router = createRouter({
  history: createWebHashHistory(), // 使用 Hash 模式
  routes,
})


// 全局路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('username');

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login'); // 未登录访问受保护页面，跳转到登录页
  } else if ((to.name === 'login' || to.name === 'register') && isAuthenticated) {
    next('/'); // 已登录访问登录/注册页，跳转到首页
  } else {
    next();
  }
});

export default router
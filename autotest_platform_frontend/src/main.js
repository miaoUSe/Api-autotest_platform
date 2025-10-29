import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/antd.css';

import axios from 'axios';

// 1. 全局设置所有请求都携带 Cookie
axios.defaults.withCredentials = true;

// 2. 核心解决步骤：从 Cookie 中读取 CSRF Token 并设置到请求头
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
if (csrftoken) {
    // 只有在获取到 token 时才设置请求头
    axios.defaults.headers.common['X-CSRFToken'] = csrftoken;
}

// -------------------------------------------------------------------
// 确保 createApp 在所有配置之后
createApp(App).use(store).use(router).use(Antd).mount('#app')


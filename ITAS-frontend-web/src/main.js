import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
const app = createApp(App)
// 使用插件
app.use(router)

// 挂载应用
app.mount('#app')
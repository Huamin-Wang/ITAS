import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
const app = createApp(App)
// 使用插件
app.use(router)
app.use(ElementPlus)
// 挂载应用
app.mount('#app')
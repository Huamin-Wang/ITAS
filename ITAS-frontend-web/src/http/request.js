import axios from "axios";

// 生产环境使用相对路径
const baseURL = import.meta.env.PROD ? '/api' : 'http://127.0.0.1:5000';

const service = axios.create({
    baseURL: baseURL,
    timeout: 5000,
    withCredentials: true  // 重要：允许携带Cookie
})

// 请求拦截器 - 移除手动添加token的逻辑，因为现在使用HttpOnly Cookie
service.interceptors.request.use(
    config => {
        // 不再手动设置Authorization头部，token将通过Cookie自动发送
        return config;
    },
    error => {
        console.log('Request Error:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    response => {
        return response.data
    },
    error => {
        if (error.response) {
            return Promise.resolve(error.response.data)
        } else if (error.request) {
            return Promise.resolve({
                success: false,
                message: '网络错误，请检查网络连接',
                code: 0
            })
        } else {
            return Promise.resolve({
                success: false,
                message: '请求配置错误',
                code: 0
            })
        }
    }
)

export default service
import axios from "axios";

const service = axios.create({
    baseURL: 'http://127.0.0.1:5000',
    timeout: 5000
})

// 请求拦截器
service.interceptors.request.use(
    config => {
        const token = sessionStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;

    },
    error => {
        // 请求错误处理
        console.log('Request Error:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    response => {

        if (response.status === 200) {
            return Promise.resolve(response.data);
        } else {
            return Promise.reject(response);
        }
    },
    error => {
        console.log('Response Error:', error);
        return Promise.reject(error);
    }
);

export default service
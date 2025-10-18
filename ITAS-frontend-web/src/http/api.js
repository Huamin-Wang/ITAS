import request from './request'

// 登录
export function login(data) {
   return request({
        url: '/login',
        method: 'post',
        data: data
    })
}

// 注册
export function register(data) {
   return request({
        url: '/register',
        method: 'post',
        data: data
    })
}

//登出
export function logout() {
   return request({
        url: '/logout',
        method: 'post',
    })
}

//获取教师对应课程
export function teacher_course(data) {
   return request({
        url: `/teacher_course?teacher_id=${data.teacher_id}`,
        method: 'get',
    })
}

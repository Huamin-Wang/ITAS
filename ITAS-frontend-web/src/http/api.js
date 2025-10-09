import request from './request'
export function apiTest() {
    return request({
        url: '/test',
        method: 'get',
    })
}
export function getStudents() {
   return request({
        url: '/getStudents',
        method: 'get',
    })
}
export function login(data) {
   return request({
        url: '/login',
        method: 'post',
        data: data
    })
}
export function register(data) {
   return request({
        url: '/register',
        method: 'post',
        data: data
    })
}

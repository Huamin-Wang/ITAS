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

//获取课程信息
export function get_course_by_id(course_id) {
    return request({
        url: `/course_by_id?course_id=${course_id}`,
        method: 'get',
    })
}

//更新学生注册信息
export function update_registration_status(course_id) {
    return request({
        url: `/update_registration_status?course_id=${course_id}`,
        method: 'get',
    })
}

//创建课程
export function create_course(data) {
    return request({
        url: '/create_course',
        method: 'post',
        data: data
    })
}

//编辑课程信息
export function update_course(data) {
    return request({
        url: '/update_course',
        method: 'post',
        data: data
    })
}

//获取课程学生数
export function course_student_count(course_id) {
    return request({
        url: `/course_student_count?course_id=${course_id}`,
        method: 'get',
    })
}

//获取课程学生名单
export function course_students(course_id) {
    return request({
        url: `/course_students?course_id=${course_id}`,
        method: 'get',
    })
}

//获取课程作业列表
export function get_assignments(course_id) {
    return request({
        url: `/get_assignments?course_id=${course_id}`,
        method: 'get',
    })
}

//获取作业
export function get_assignment_by_id(assignment_id) {
    return request({
        url: `/get_assignment_by_id?assignment_id=${assignment_id}`,
        method: 'get',
    })
}

//创建作业
export function assignments(data) {
    return request({
        url: '/assignments',
        method: 'post',
        data: data
    })
}

//编辑作业
export function update_assignment(data) {
    return request({
        url: '/update_assignment',
        method: 'post',
        data: data
    })
}

//更新学生分数
export function update_score(data) {
    return request({
        url: '/update_score',
        method: 'post',
        data: data
    })
}

//获取学生排行
export function ranking(course_id) {
    return request({
        url: `/ranking?course_id=${course_id}`,
        method: 'get',
    })
}
import request from './request'

// 登录
export function login(data) {
    return request({
        url: '/login',
        method: 'post',
        data: data
    })
}

//心跳检测
export function heartbeat() {
    return request({
        url: '/heartbeat',
        method: 'post',
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

// // 生成作业标签
// export function generate_tags(data) {
//     return request({
//         url: '/generate_tags',
//         method: 'post',
//         data: data
//     })
// }

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

//获取随机选择学生列表
export function random_select_list(course_id) {
    return request({
        url: `/random_select_list?course_id=${course_id}`,
        method: 'get',
    })
}

//ai问答
export function chat_handle(data) {
    return request({
        url: '/chat_handle',
        method: 'post',
        data: data
    })
}

//获取课堂小测列表
export function get_quizzes(course_id) {
    return request({
        url: `/get_quizzes?course_id=${course_id}`,
        method: 'get',
    })
}

//创建课堂小测(总表)
export function create_quiz(data) {
    return request({
        url: '/create_quiz',
        method: 'post',
        data: data
    })
}

//添加课堂小测题目
export function add_quiz_questions(data) {
    return request({
        url: '/add_quiz_questions',
        method: 'post',
        data: data
    })
}

//获取小测题目
export function get_quiz_questions(quiz_id) {
    return request({
        url: `/get_quiz_questions?quiz_id=${quiz_id}`,
        method: 'get'
    })
}

//编辑小测
export function update_quiz(data) {
    return request({
        url: '/update_quiz',
        method: 'post',
        data: data
    })
}

//发布小测
export function publish_quiz(data) {
    return request({
        url: '/publish_quiz',
        method: 'post',
        data: data
    })
}

//删除小测
export function delete_quiz(data) {
    return request({
        url: '/delete_quiz',
        method: 'post',
        data: data
    })
}

//获取班级学生学号
export function get_student_numbers(course_id) {
    return request({
        url: `/get_student_numbers?course_id=${course_id}`,
        method: 'get'
    })
}

//学生小测提交情况
export function has_submitted_quiz(data) {
    return request({
        url: '/has_submitted_quiz',
        method: 'post',
        data: data
    })
}

//学生小测提交详情
export function get_quiz_response(data) {
    return request({
        url: '/get_quiz_response',
        method: 'post',
        data: data
    })
}

//创建备注
export function create_record(data) {
    return request({
        url: '/create_record',
        method: 'post',
        data: data
    })
}

//获取备注
export function get_records(course_id) {
    return request({
        url: `/get_records?course_id=${course_id}`,
        method: 'get'
    })
}

//修改备注
export function update_record(data) {
    return request({
        url: '/update_record',
        method: 'post',
        data: data
    })
}

//获取教学资源
export function get_resources(course_id) {
    return request({
        url: `/get_resources?course_id=${course_id}`,
        method: 'get'
    })
}

//创建教学资源
export function create_resource(data) {
    return request({
        url: '/create_resource',
        method: 'post',
        data: data
    })
}

//删除教学资源分享
export function delete_resource(data) {
    return request({
        url: `/delete_resource`,
        method: 'post',
        data: data
    })
}

//ai自动批改
export function batch_score_assignments(data) {
    return request({
        url: '/batch_score_assignments',
        method: 'post',
        data: data
    })
}

//存储批改结果
export function add_grading_results(data) {
    return request({
        url: '/add_grading_results',
        method: 'post',
        data: data
    })
}

//获取批改结果
export function get_grading_results(data) {
    return request({
        url: '/get_grading_results',
        method: 'post',
        data: data
    })
}

//获取错题分析结果
export function analyze_student_knowledge(data) {
    return request({
        url: '/analyze_student_knowledge',
        method: 'post',
        data: data
    })
}

//生成习题
export function generate_exercises(data) {
    return request({
        url: '/generate_exercises',
        method: 'post',
        data: data
    })
}

//获取生成习题详情
export function get_exercise_questions(exercise_id) {
    return request({
        url: `/get_exercise_questions?exercise_id=${exercise_id}`,
        method: 'get'
    })
}

//更新习题状态(包括发布)
export function update_exercise(data) {
    return request({
        url: '/update_exercise',
        method: 'post',
        data: data
    })
}

//习题提交并自动批改
export function submit_exercise(data) {
    return request({
        url: '/submit_exercise',
        method: 'post',
        data: data
    })
}

//获取习题批改详情
export function get_grading_results_e(data) {
    return request({
        url: '/get_grading_results_e',
        method: 'post',
        data: data
    })
}

//获取学生习题提交详情
export function get_exercise_response(data) {
    return request({
        url: '/get_exercise_response',
        method: 'post',
        data: data
    })
}

//学生端 -- 获取当前用户信息
export function getCurrentStudent(user_id) {
    return request({
        url: `/course_student_info?user_id=${user_id}`,
        method: 'get'
    })
}

//学生端 -- 获取当前用户课程id
export function getCurrentStudentCourseId(user_id) {
    return request({
        url: `/student_course_info?user_id=${user_id}`,
        method: 'get'
    })
}

//学生端 -- 获取所有课程信息
export function getCourses() {
    return request({
        url: '/getCourses',
        method: 'get',
    })
}

//学生端 -- 根据课程id获取学生对应课程信息
export function getStudentCourses(course_id) {
    return request({
        url: `/get_student_course?course_id=${course_id}`,
        method: 'get',
    })
}


//学生端 -- 根据课程ID进入对应课程
export function getCourseDetail(course_id) {
    return request({
        url: `/course_detail?course_id=${course_id}`,
        method: 'get',
    })
}

//学生端 -- 获取所有作业列表
export function getAllAssignments() {
    return request({
        url: '/get_all_assignments',
        method: 'get',
    })
}

//学生端 -- 根据课程ID获取作业列表
export function getAssignments(course_id) {
    return request({
        url: `/get_assignments?course_id=${course_id}`,
        method: 'get',
    })
}

//学生端 -- 根据作业ID获取作业详情
export function getAssignmentDetail(assignment_id) {
    return request({
        url: `/assignment_detail?assignment_id=${assignment_id}`,
        method: 'get',
    })
}

//学生端 -- 获取小测列表
export function getQuizzesStudent(data) {
    return request({
        url: '/get_quizzes_student',
        method: 'post',
        data: data
    })
}

//学生端 -- 提交小测
export function submit_quiz(data) {
    return request({
        url: '/submit_quiz',
        method: 'post',
        data: data
    })
}

//学生端 -- 错题分析
export function analyze_student_knowledge_s(data) {
    return request({
        url: '/analyze_student_knowledge_s',
        method: 'post',
        data: data
    })
}

//学生端 -- 获取生成习题列表
export function get_exercises_student(data) {
    return request({
        url: '/get_exercises_student',
        method: 'post',
        data: data
    })
}
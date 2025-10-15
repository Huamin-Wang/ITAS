import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/home.vue'
import Login from '../views/login.vue'
import Register from '../views/register.vue'
import TeacherProfile from '../views/students/teacher_profile.vue';
// student

import student_profile from '../views/students/student_profile.vue';  //学生中心
import submission_detail from '../views/students/submission_detail.vue'; //提交作业详情
import assignments from '../views/students/assignments.vue'; //作业列表
import course_detail from '../views/students/course_detail.vue'; //课程详情


import student_profile from '../views/students/student_profile.vue';


const routes = [
  {
    path: '/',
    name: 'Home',
    component:Home,
    meta:{
      title: '基于大模型的智能教学辅助系统'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component:Login,
  },
  {
    path: '/register',
    name: 'Register',
    component:Register,
  },
  {
    path: '/teacher_profile',
    name: 'TeacherProfile',
    component:TeacherProfile,
    meta:{
      title: '教师中心 - 基于大模型的智能教学辅助系统'
    }
  },
  {
    path: '/student_profile',
    name: 'Student_profile',
    component:student_profile
  },
  {
    path: '/submission_detail',
    name: 'Submission_detail',
    component:submission_detail
  },
  {
    path: '/assignments',
    name: 'Assignments',
    component:assignments
  },
  {
    path:'/course_detail',
    name:'Course_detail',
    component:course_detail
  }
];
const router = createRouter({
  history: createWebHistory(),
  routes,
})
// 在这里添加路由的导航守卫
router.beforeEach((to, from, next) => {
  console.log('Navigating to:', to.path);
    if (to.meta.title) {
    document.title = to.meta.title;
  } else {
    document.title = '我的网站'; // 默认标题
  }
  next();
}); 
export default router
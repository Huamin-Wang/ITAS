import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/home.vue'
import Login from '../views/login.vue'
import Register from '../views/register.vue'
import PersonInfo from '../views/personInfo.vue';

// students
import student_profile from '../views/students/student_profile.vue';  //学生中心
import submission_detail from '../views/students/submission_detail.vue'; //提交作业详情
import assignments from '../views/students/assignments.vue'; //作业列表
import course_detail from '../views/students/course_detail.vue'; //课程详情

//teachers
import TeacherProfile from '../views/teachers/teacher_profile.vue'; //教师中心
import assignment_detail from '../views/teachers/assignment_detail.vue'; // 编辑作业
import attendance_manager from '../views/teachers/attendance_manager.vue'; // 课程考勤管理系统
import attendance from '../views/teachers/attendance.vue'; // 课程签到
import course_analysis from '../views/teachers/course_analysis.vue'; // 学习状况分析
import course_students from '../views/teachers/course_students.vue'; // 课程学生名单
import courseManager from '../views/teachers/courseManager.vue'; // 课程管理



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
    path: '/personInfo',
    name: 'PersonInfo',
    component:PersonInfo
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
    component:student_profile,
    meta:{
      title: '学生中心 - 基于大模型的智能教学辅助系统'
    }
  },
  {
    path: '/submission_detail',
    name: 'Submission_detail',
    component:submission_detail,
    meta:{
      title: '学生端-提交详情'
    }
  },
  {
    path: '/assignments',
    name: 'Assignments',
    component:assignments,
    meta:{
      title: '学生端-课程作业列表'
    }
  },
  {
    path:'/course_detail',
    name:'Course_detail',
    component:course_detail,
    meta:{
      title: '学生端-课程详情'
    }
  },
  {
    path:'/assignment_detail',
    name:'Assignment_detail',
    component:assignment_detail,
    meta:{
      title: '教师端-编辑作业'
    }
  },
  {
    path:'/attendance_manager',
    name:'Attendance_manager',
    component:attendance_manager,
    meta:{
      title: '教师端-课程考勤管理系统'
    }
  },
  {
    path:'/attendance',
    name:'Attendance',
    component:attendance,
    meta:{
      title: '教师端-课程签到'
    }
  },
  {
    path:'/course_analysis',
    name:'Course_analysis',
    component:course_analysis,
    meta:{
      title: '教师端-学习状况分析'
    }
  },
  {
    path:'/course_students',
    name:'Course_students',
    component:course_students,
    meta:{
      title: ''
    }
  },
  {
    path:'/courseManager',
    name:'CourseManager',
    component:courseManager,
    meta:{
      title:''
    }
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
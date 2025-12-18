import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/home.vue'
import Login from '../views/login.vue'
import Register from '../views/register.vue'
import PersonInfo from '../views/personInfo.vue';
import chat from '../views/chat.vue' //ai问答小助手


// students
import student_profile from '../views/students/student_profile.vue';  //学生中心
import submission_detail from '../views/students/submission_detail.vue'; //提交作业详情
import submissions from '../views/students/submissions.vue'; //提交作业
import course_detail from '../views/students/course_detail.vue'; //课程详情
import student_quiz from '../views/students/student_quiz.vue'; //学生小测

//teachers
import TeacherProfile from '../views/teachers/teacher_profile.vue'; //教师中心
import assignments from '../views/teachers/assignments.vue'; //课程作业列表
import assignment_detail from '../views/teachers/assignment_detail.vue'; // 编辑作业
import attendance_manager from '../views/teachers/attendance_manager.vue'; // 课程考勤管理系统
import attendance from '../views/teachers/attendance.vue'; // 课程签到
import course_analysis from '../views/teachers/course_analysis.vue'; // 学习状况分析
import course_students from '../views/teachers/course_students.vue'; // 课程学生名单
import courseManager from '../views/teachers/course_manager.vue'; // 课程管理
import update_course from '../views/teachers/update_course.vue'; // 编辑课程
import create_course from '../views/teachers/create_course.vue'; // 创建课程
import add_score from '../views/teachers/add_score.vue'; //成绩管理
import ranking from '../views/teachers/ranking.vue'; //排名
import random_select from '../views/teachers/random_select.vue'; //随机选择
import course_quiz from '../views/teachers/course_quiz.vue'; //课堂测试
import course_resource from '../views/teachers/course_resource.vue'; //资源分享
import quiz_grading from '../views/teachers/quiz_grading.vue'; //测试批改
import detail_grading from '../views/teachers/detail_grading.vue'; //测试批改-查看详情



const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '基于大模型的智能教学辅助系统'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: '登录'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      title: '用户注册'
    }
  },
  {
    path: '/personInfo',
    name: 'PersonInfo',
    component: PersonInfo,
    meta: {
      title: '个人信息修改提示'
    }
  },
  {
    path: '/teacher_profile',
    name: 'TeacherProfile',
    component: TeacherProfile,
    meta: {
      title: '教师中心 - 基于大模型的智能教学辅助系统'
    }
  },
  {
    path: '/student_profile',
    name: 'Student_profile',
    component: student_profile,
    meta: {
      title: '学生中心 - 基于大模型的智能教学辅助系统'
    }
  },
  {
    path: '/submission_detail/:assignmentId?',
    name: 'Submission_detail',
    component: submission_detail,
    meta: {
      title: '学生端-提交详情'
    }
  },
  {
    path: '/submissions',
    name: 'Submissions',
    component: submissions,
    meta: {
      title: '学生端-提交作业'
    }
  },
  {
    path: '/course_detail/:courseId?',
    name: 'Course_detail',
    component: course_detail,
    meta: {
      title: '学生端-课程详情'
    }
  },
  {
    path: '/student_quiz/:quizId?',
    name: 'student_quiz',
    component: student_quiz,
    meta: {
      title: '学生端-小测详情'
    }
  },
  {
    path: '/assignments/:courseId?',
    name: 'Assignments',
    component: assignments,
    meta: {
      title: '课程作业列表'
    }
  },
  {
    path: '/assignment_detail/:assignmentId?',
    name: 'Assignment_detail',
    component: assignment_detail,
    meta: {
      title: '编辑作业'
    }
  },
  {
    path: '/attendance_manager',
    name: 'Attendance_manager',
    component: attendance_manager,
    meta: {
      title: '教师端-课程考勤管理系统'
    }
  },
  {
    path: '/attendance/:courseId?',
    name: 'Attendance',
    component: attendance,
    meta: {
      title: '课程签到二维码'
    }
  },
  {
    path: '/course_analysis',
    name: 'Course_analysis',
    component: course_analysis,
    meta: {
      title: '教师端-学习状况分析'
    }
  },
  {
    path: '/course_students/:courseId?',
    name: 'Course_students',
    component: course_students,
  },
  {
    path: '/course_manager/:courseId?',
    name: 'Course_manager',
    component: courseManager,
  },
  {
    path: '/create_course/:teacherId?',
    name: 'create_course',
    component: create_course,
    meta: {
      title: '创建新课程'
    }
  },
  {
    path: '/update_course/:courseId?',
    name: 'update_course',
    component: update_course,
    meta: {
      title: '更新课程'
    }
  },
  {
    path: '/add_score/:courseId?',
    name: 'add_score',
    component: add_score,
    meta: {
      title: '课程成绩管理系统'
    }
  },
  {
    path: '/ranking/:courseId?',
    name: 'ranking',
    component: ranking,
    meta: {
      title: '学生排名'
    }
  },
  {
    path: '/random_select/:courseId?',
    name: 'random_select',
    component: random_select,
    meta: {
      title: '随机选择'
    }
  },
  {
    path: '/chat/:courseId?',
    name: 'chat',
    component: chat,
    meta: {
      title: 'AI问答小助手'
    }
  },
  {
    path: '/course_quiz/:courseId?',
    name: 'course_quiz',
    component: course_quiz,
    meta: {
      title: '课堂测试'
    }
  },
  {
    path: '/quiz_grading/:courseId?/:quizId?',
    name: 'quiz_grading',
    component: quiz_grading,
    meta: {
      title: '小测批改'
    }
  },
  {
    path: '/detail_grading/:courseId?/:quizId?/:studentNumber?',
    name: 'detail_grading',
    component: detail_grading,
    meta: {
      title: '小测批改'
    }
  },
  {
    path: '/course_resource/:courseId?',
    name: 'course_resource',
    component: course_resource,
    meta: {
      title: '资源分享'
    }
  },
];
const router = createRouter({
  history: createWebHistory(),
  routes,
})
// 在这里添加路由的导航守卫
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title;
  } else {
    document.title = '我的网站'; // 默认标题
  }
  next();
});
export default router
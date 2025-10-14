import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/home.vue'
import Login from '../views/login.vue'
import Register from '../views/register.vue'
import TeacherProfile from '../views/teacher_profile.vue'
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
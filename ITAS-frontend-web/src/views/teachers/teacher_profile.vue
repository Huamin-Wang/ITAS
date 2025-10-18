<template>
<div class="teacher-profile">
        
<header>
        <div class="alert alert-{{ category }}">            
        </div>
    <h1>基于大模型的智能教学辅助系统</h1>
    <p>教师中心 - 提升教学效率，优化教学管理</p>
    <div class="login-status">
        <span class="edit_profile" @click="edit_profile">欢迎,{{ userInfo.name }}老师!</span>
        <span class="logout" @click="logout()">退出</span>
    </div>
</header>

<div class="container">
    <div class="welcome-section">
         <h2>欢迎, <a href="/edit_profile" style="color: #1890ff; text-decoration: underline;">{{ userInfo.name }}</a>老师!</h2>
        <p>以下是您教授的课程列表，点击课程进入管理页面。</p>
    </div>

    <div class="create-course">
        <button onclick="location.href='/create_course'">创建新课程</button>
    </div>

    

        <div class="semester-section" v-for=" semesterCourses in this.couresList">
            <h4 class="semester-heading"><b>{{ semesterCourses.semester }}</b></h4>
            <div class="course-grid" v-for=" course in semesterCourses.courses">
               
                <div class="course-card">
                    <div class="course-header">
                        <h3>{{ course.name }}</h3>
                        <span class="course-code">{{ course.code }}</span>
                    </div>
                    <div class="course-info">
                        <p>学生人数：{{ course.student_count }}</p>
                    </div>
                    <button>进入课程管理</button>
                </div>
                
            </div>
        </div>
</div>

<footer>
    <p>&copy; 2025 基于大模型的智能教学辅助系统. All Rights Reserved.</p>
</footer>
    </div>
</template>
<script>
import { teacher_course,logout } from '@/http/api.js';
export default {
    data() {
        return {
            userInfo: {},
            couresList: {},
        }
    },
    mounted() {
        this.userInfo = JSON.parse(sessionStorage.getItem('userInfo'));
        teacher_course({ teacher_id: this.userInfo.user_id }).then(response => {
            this.couresList = response.data;
            console.log(this.couresList);
        }).catch(error => {
            console.error("获取课程信息失败:", error);
        });    
    },
    methods: {
        async logout() {
            const confirmLogout = await this.$confirm('确定要退出登录吗？', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).catch(() => {
                return false;
            });
            if (!confirmLogout) return;
            try {
                const response = await logout();
                
                if (response.code === 200) {
                    // 显示成功消息
                    this.$message.success('登出成功');
                    // 延迟跳转，让用户看到成功消息
                    setTimeout(() => {
                        sessionStorage.removeItem('userInfo');
                        localStorage.removeItem('access_token'); // 确保清除token
                        localStorage.removeItem('user_info'); // 确保清除用户信息
                        this.$router.push("/");
                    }, 500);
                } else {
                    this.$message.error('登出失败');
                }
            } catch (error) {
                console.error("退出登录失败:", error);
                // 即使后端登出失败，也要清除前端存储
                this.$message.error('网络错误，已清除本地登录状态');
                
                setTimeout(() => {
                    sessionStorage.removeItem('userInfo');
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('user_info');
                    this.$router.push("/");
                }, 1500);
            }
        },
    },
}
</script>
<style scoped>
 .teacher-profile {
            font-family: 'Microsoft YaHei', sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        header {
            background: linear-gradient(135deg, #1890ff, #096dd9);
            color: white;
            text-align: center;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            position: relative;
        }

        header h1 {
            margin: 0;
            font-size: 2em;
            font-weight: bold;
        }

        header p {
            margin: 10px 0;
            font-size: 1.1em;
            opacity: 0.9;
        }

        .login-status {
            margin-top: 20px;
        }

        .login-status span {
            color: white;
            padding: 8px 20px;
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            margin: 5px;
            display: inline-block;
        }

        .login-status a {
            color: #fff;
            text-decoration: none;
            transition: color 0.3s;
        }

        .login-status a:hover {
            color: #ffcc00;
        }

        .back-to-home {
            position: absolute;
            top: 20px;
            left: 20px;
            color: white;
            text-decoration: none;
            font-size: 1em;
        }

        .container {
            flex: 1;
            width: 90%;
            max-width: 1200px;
            margin: 30px auto;
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            position: relative;
        }

        .welcome-section {
            text-align: center;
            margin-bottom: 30px;
        }

        .welcome-section h2 {
            color: #1890ff;
            font-size: 1.8em;
            margin-bottom: 10px;
        }

        .welcome-section p {
            color: #666;
            font-size: 1.1em;
        }

        .semester-section {
            margin-bottom: 40px;
        }

        .semester-heading {
            color: #333;
            border-bottom: 2px solid #1890ff;
            padding-bottom: 10px;
            margin-top: 30px;
            margin-bottom: 20px;
        }

        .course-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .course-card {
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e8e8e8;
            transition: all 0.3s ease;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 180px;
        }

        .course-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }

        .course-header {
            margin-bottom: 15px;
        }

        .course-header h3 {
            color: #1890ff;
            margin-bottom: 5px;
            font-size: 1.3em;
        }

        .course-code {
            display: inline-block;
            background-color: #f0f2f5;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            color: #666;
        }

        .course-info {
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }

        .course-card button {
            background: #1890ff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .course-card button:hover {
            background: #096dd9;
        }

        .create-course {
            text-align: center;
            margin: 30px 0;
        }

        .create-course button {
            background: #52c41a;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1.05em;
            font-weight: 500;
        }

        .create-course button:hover {
            background: #389e0d;
            transform: scale(1.05);
        }

        footer {
            background-color: #001529;
            color: rgba(255, 255, 255, 0.8);
            text-align: center;
            padding: 20px 0;
            margin-top: 30px;
        }

        /* 通用消息样式 */
        .alert {
            padding: 15px;
            margin: 15px auto;
            border: 1px solid transparent;
            border-radius: 4px;
            max-width: 80%;
            text-align: center;
            animation: fadeOut 10s forwards;
        }

        /* 成功消息样式 */
        .alert-success {
            color: #3c763d;
            background-color: #dff0d8;
            border-color: #d6e9c6;
        }

        /* 错误消息样式 */
        .alert-registerError {
            color: #721c24;
            background-color: #f8d7da;
            border-color: #f5c6cb;
        }

        @keyframes fadeOut {
            0% { opacity: 1; }
            70% { opacity: 1; }
            100% { opacity: 0; }
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 1.6em;
            }

            .container {
                width: 95%;
                margin: 15px auto;
                padding: 15px;
            }

            .course-grid {
                grid-template-columns: 1fr;
            }

            .course-card {
                margin-bottom: 15px;
                height: auto;
                min-height: 160px;
            }
        }
        .logout{
            cursor: pointer;
        }
        .edit_profile{
            cursor: pointer;
        }
</style>
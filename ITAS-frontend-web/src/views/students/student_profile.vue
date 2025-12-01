<template>
  <div class="student-profile-page">
    <header>
      <div class="alert alert-{{ category }}"></div>

      <h1>基于大模型的智能教学辅助系统</h1>
      <p>学生中心 - 提升学习效率，增强学习体验</p>
      <div class="login-status">
        <span>欢迎,
          <a href="/edit_profile">
            {{ student_name }} </a>同学!</span>

        <span class="logout" @click="logout()">退出</span>
      </div>
    </header>

    <div class="container">
      <div class="welcome-section">
        <h2>
          欢迎,
          <a href="/edit_profile" style="color: #1890ff; text-decoration: underline">
            {{ student_name }} </a>同学!
        </h2>
        <div style="text-align: center">
          <h3>关注微信公众号，进入AI教学助手，体验更完整功能！</h3>
          <img src="../../static/weixinQR.jpg" alt="微信公众号二维码" style="
              width: 50px;
              height: 50px;
              border: 1px solid #ddd;
              border-radius: 10px;
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            " />
        </div>
        <p>
          以下是您的学习数据和相关功能，如未显示课程，请联系教师上传名单或检查注册信息是否与学校教务系统一致
        </p>
      </div>
      <!-- {#将后端传递的所有课程展示#} -->
      <div class="course-grid">
        <div v-for="course in courses" :key="course.id" class="dashboard-card">
          <h3>{{ course.name }}</h3>
          <p>课程代码：{{ course.id }}</p>
          <p>教师：</p>

          <router-link :to="`/course_detail/${course.id}`">
            <button>进入课程</button>
          </router-link>
        </div>
      </div>

      <div class="dashboard-card">
        <h3>待完成作业</h3>
        <ul v-if="assignments && assignments.length">
          <li v-for="assignment in assignments" :key="assignment.id">
            <a :href="`/submission_detail/${assignment.id}`">
              {{ assignment.course_name }} -
              {{ assignment.title }} （截止日期：）{{ assignment.due_date }}
            </a>
          </li>
        </ul>

        <p v-else>你真棒，作业都做完了！</p>
      </div>
    </div>

    <footer>
      <p>&copy; 2025 基于大模型的智能教学辅助系统. All Rights Reserved.</p>
    </footer>
  </div>
</template>

<script>
import {
  getAssignments,
  getStudentCourses,
  getCurrentStudent,
  logout,
} from "@/http/api";

export default {
  data() {
    return {
      student_name: "",
      userInfo: {},
      courses: [],
      assignments: [],
    };
  },
  methods: {
    async loaduserInfo() {
      try {
        const userInfo = JSON.parse(localStorage.getItem("userInfo"));
        console.log(userInfo);
        const userId = userInfo.user_id;
        //使用接口获取用户信息而不是从localStorage获取
        const response = await getCurrentStudent(userId);
        if ((response.code = 200)) {
          this.userInfo = response.data;
          this.student_name = response.data.student_name;
        } else {
          console.log("获取用户信息失败");
        }
      } catch (error) {
        console.log("获取用户信息失败:", error);
        this.$router.push("/login");
      }
    },

    async fetchCourses() {
      try {
        // 先获取用户信息，从中获取 course_id
        const userInfo = JSON.parse(localStorage.getItem("userInfo"));
        const userId = userInfo.user_id;

        // 获取学生课程信息
        const studentResponse = await getCurrentStudent(userId);
        if (studentResponse.code === 200) {
          // 从学生信息中获取 course_id
          const courseId = studentResponse.data.course_id;

          if (courseId) {
            // 使用 course_id 获取课程详情
            const response = await getStudentCourses(courseId);
            console.log("获取课程响应:", response);
            if (response.code === 200) {
              this.courses = [response.data]; // 包装成数组，因为可能只有一个课程
            } else {
              console.log("获取课程失败:", response.message);
            }
          } else {
            console.log("学生信息中未找到课程ID");
          }
        } else {
          console.log("获取学生信息失败");
        }
      } catch (error) {
        console.log("获取课程信息失败:", error);
      }
    },

    async fetchAssignments() {
      try {
        // 先获取用户信息，从中获取 course_id
        const userInfo = JSON.parse(localStorage.getItem("userInfo"));
        const userId = userInfo.user_id;

        // 获取学生课程信息
        const studentResponse = await getCurrentStudent(userId);
        if (studentResponse.code === 200) {
          // 从学生信息中获取 course_id
          const courseId = studentResponse.data.course_id ;

          if (courseId) {
            // 使用 course_id 获取课程详情
            const response = await getAssignments(courseId);
            console.log("获取课程响应:", response);
            if (response.code === 200) {
              this.assignments = response.data; // 包装成数组，因为可能只有一个课程
            } else {
              console.log("获取课程失败:", response.message);
            }
          } else {
            console.log("学生信息中未找到课程ID");
          }
        } else {
          console.log("获取学生信息失败");
        }
      } catch (error) {
        console.log("获取课程信息失败:", error);
      }
    },

    async logout() {
      const confirmLogout = await this.$confirm("确定要退出登录吗？", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }).catch(() => {
        return false;
      });
      if (!confirmLogout) return;
      try {
        const response = await logout();

        if (response.code === 200) {
          // 显示成功消息
          this.$message.success("登出成功");
          // 延迟跳转，让用户看到成功消息
          setTimeout(() => {
            localStorage.removeItem("userInfo"); // 确保清除用户信息
            this.$router.push("/");
          }, 500);
        } else {
          this.$message.error("登出失败");
        }
      } catch (error) {
        console.error("退出登录失败:", error);
        // 即使后端登出失败，也要清除前端存储
        this.$message.error("网络错误，已清除本地登录状态");

        setTimeout(() => {
          sessionStorage.removeItem("userInfo");
          localStorage.removeItem("access_token");
          localStorage.removeItem("userInfo");
          this.$router.push("/");
        }, 1500);
      }
    }
  },
  mounted() {
    this.loaduserInfo();
    this.fetchCourses();
    this.fetchAssignments();
  },
};
</script>

<style scoped>
.student-profile-page {
  font-family: "Microsoft YaHei", sans-serif;
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

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.dashboard-card {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  border: 1px solid #e8e8e8;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.dashboard-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.dashboard-card h3 {
  color: #1890ff;
  margin-bottom: 10px;
}

.dashboard-card p {
  color: #666;
  line-height: 1.6;
}

.dashboard-card button {
  background: #1890ff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dashboard-card button:hover {
  background: #096dd9;
}

footer {
  background-color: #001529;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 20px 0;
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

  .dashboard-card {
    margin-bottom: 15px;
  }
}

/* 通用消息样式 */
.alert {
  padding: 15px;
  margin-bottom: 20px;
  border: 1px solid transparent;
  border-radius: 4px;
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

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.logout {
  cursor: pointer;
}
</style>
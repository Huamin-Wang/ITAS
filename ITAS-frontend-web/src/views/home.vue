<template>
  <div class="home-page">
    <div class="home-page">
      <header>
        <h1>基于大模型的智能教学辅助系统</h1>
        <p>提升课堂教学效率，增强学生学习体验</p>

        <div class="login-status">
          <div v-if="user.user_id">
            <span v-if="user.role === 'student'"
              >欢迎, {{ user.name }}同学!</span
            >
            <span v-else-if="user.role === 'teacher'"
              >欢迎, {{ user.name }}老师!</span
            >
            <a href="#" @click.prevent="logout()" style="font-size: 0.5em"
              >登出</a
            >
            <div class="profile">
              <a v-if="user.role === 'student'" href="/student_profile"
                >学生中心</a
              >
              <a v-else-if="user.role === 'teacher'" href="/teacher_profile"
                >查看课程</a
              >
            </div>
          </div>
          <div v-else>
            <p class="motivation-text">当下的努力，换来的是明天更好的自己！</p>
          </div>
        </div>

        <!-- <div class="header-links">
        <router-link to="/forum">论坛</router-link>
        <router-link to="/chat">智能聊天</router-link>
      </div> -->
      </header>

      <div class="container">
        <div v-if="!user.user_id" class="login-prompt">
          <h2>欢迎！您尚未登录</h2>
          <p>为了更好的使用智能教学辅助系统，请登录或注册。</p>
          <router-link to="/login" class="auth-link">登录</router-link>
          <router-link to="/register" class="auth-link">注册</router-link>
        </div>

        <div class="welcome-section">
          <h2>欢迎使用智能教学辅助系统</h2>
          <p>让学习变得更智能、更高效、更有趣</p>
        </div>

        <div class="feature-grid">
          <div
            v-for="feature in features"
            :key="feature.title"
            class="feature-card"
          >
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>

      <footer>
        <p>&copy; 2025 基于大模型的智能教学辅助系统. All Rights Reserved.</p>
        <p>
          备案号：<a href="https://beian.miit.gov.cn/" target="_blank"
            >闽ICP备2025085215号</a
          >
        </p>
      </footer>
    </div>
  </div>
</template>

<script>
import { logout } from "@/http/api.js";
export default {
  name: "Home",
  data() {
    return {
      user: {
        id: null, // 登录状态管理
        name: "",
        role: "", // 'student' 或 'teacher'
      },
      features: [
        {
          title: "智能答疑",
          description:
            "基于大模型的实时问答系统，为学生提供24小时学习支持，快速解答各类学习疑问。",
        },
        {
          title: "个性化学习",
          description:
            "根据学生的学习进度和掌握情况，提供定制化的学习建议和资源推荐。",
        },
        {
          title: "课程管理",
          description:
            "教师可以轻松创建和管理课程内容，学生可以便捷地访问学习资料。",
        },
        {
          title: "学习分析",
          description:
            "通过数据分析，了解学习效果，帮助教师优化教学策略，提升教学质量。",
        },
        {
          title: "互动讨论",
          description:
            "支持师生在线交流，营造良好的学习氛围，促进知识的共享与创新。",
        },
        {
          title: "作业批改",
          description:
            "智能辅助批改作业，提供详细的反馈，帮助学生更好地理解和改进。",
        },
      ],
      testNote: "",
      studentsList: [],
    };
  },
  mounted() {
    document.body.classList.add("home-page");
    this.checkLoginStatus();
  },
  beforeUnmount() {
    document.body.classList.remove("home-page");
  },
  methods: {
    checkLoginStatus() {
      this.user = JSON.parse(localStorage.getItem("userInfo"));
      if (this.user) {
        return;
      } else {
        this.user = {
          id: null,
          name: "",
          role: "",
        };
      }
    },

    // 退出登录
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
          this.$message.success("登出成功");
          localStorage.removeItem("userInfo");
          // 跳转到首页，后端会清除 Cookie
          this.$router.push("/");
          // 刷新页面以确保状态更新
          location.reload();
        } else {
          this.$message.error("登出失败");
        }
      } catch (error) {
        console.error("退出登录失败:", error);
        this.$message.error("网络错误，已清除本地登录状态");

        // 即使后端登出失败，也要清除前端存储
        localStorage.removeItem("userInfo");
        this.$router.push("/");
        location.reload();
      }
    },
  },
};
</script>

<style scoped>
.home-page {
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
  background: linear-gradient(135deg, #54fc25, #096dd9);
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

.login-status a {
  color: white;
  text-decoration: none;
  padding: 8px 20px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  margin: 5px;
  transition: all 0.3s ease;
  display: inline-block;
}

.login-status a:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.motivation-text {
  font-family: "Microsoft YaHei", sans-serif;
  color: gainsboro;
  font-size: 0.5em;
}

.header-links {
  position: absolute;
  bottom: 10px;
  right: 20px;
  display: flex;
  gap: 15px;
}

.header-links a {
  color: white;
  text-decoration: none;
  padding: 8px 15px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  transition: all 0.3s ease;
}

.header-links a:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
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

.login-prompt {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  padding: 15px 30px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: 0 3px 15px rgba(0, 0, 0, 0.15);
  z-index: 2;
}

.login-prompt h2 {
  margin: 0;
  color: #1890ff;
  font-size: 1.5em;
}

.login-prompt p {
  margin: 10px 0;
  color: #666;
  font-size: 1em;
}

.auth-link {
  text-decoration: none;
  color: white;
  background: #1890ff;
  padding: 10px 20px;
  border-radius: 5px;
  transition: all 0.3s ease;
  margin: 0 5px;
  display: inline-block;
}

.auth-link:hover {
  background: #096dd9;
}

.welcome-section {
  text-align: center;
  margin-bottom: 30px;
}

.welcome-section h2 {
  color: #1890ff;
  margin-bottom: 10px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.feature-card {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  border: 1px solid #e8e8e8;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.feature-card h3 {
  color: #1890ff;
  margin-bottom: 10px;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

footer {
  background-color: #001529;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 20px 0;
  margin-top: auto;
}

footer a {
  color: rgba(255, 255, 255, 0.8);
}

/* 响应式设计 */
@media (max-width: 768px) {
  header h1 {
    font-size: 1.6em;
  }

  .header-links {
    position: static;
    justify-content: center;
    margin-top: 15px;
  }

  .container {
    width: 95%;
    margin: 15px auto;
    padding: 15px;
  }

  .login-prompt {
    width: 90%;
    max-width: 300px;
    padding: 10px 20px;
    font-size: 14px;
  }

  .feature-card {
    margin-bottom: 15px;
  }
}
</style>
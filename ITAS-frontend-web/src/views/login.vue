<template>
  <div class="login-page">
    <div class="container">
      <div class="card">
        <h2>登录</h2>
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="identifier">学号/教工号</label>
            <input
              type="text"
              id="identifier"
              name="identifier"
              placeholder="请输入学号/教工号"
              required
              v-model="identifier"
            />
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input
              type="password"
              id="password"
              name="password"
              placeholder="请输入密码"
              required
              v-model="password"
            />
          </div>
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? "登录中..." : "登录" }}
          </button>
        </form>
        <div class="text-center mt-3">
          <a href="/register">没有账号？注册</a>
        </div>
        <div class="text-center mt-3">
          <a href="/" class="btn-primary">返回首页</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { login } from "../http/api.js";
import heartbeat from "@/utils/heartbeat";
export default {
  data() {
    return {
      identifier: "",
      password: "",
      loading: false,
      errorMessage: "",
    };
  },
  methods: {
    async login() {
      // 重置错误信息
      this.errorMessage = "";
      this.loading = true;

      try {
        const data = {
          identifier: this.identifier,
          password: this.password,
        };

        const response = await login(data);

        if (response.code == 200) {
          const userInfo = {
            user_id: response.data.user_id,
            name: response.data.name,
            identifier: response.data.identifier,
            role: response.data.role,
            email: response.data.email,
          };

          localStorage.setItem("userInfo", JSON.stringify(userInfo));
          // 启动心跳服务
          heartbeat.init();
          this.$message.success("登陆成功");
          // 跳转到首页或其他页面
          if (userInfo.role == "teacher") {
            setTimeout(() => {
              this.$router.push("/teacher_profile").catch((err) => {
                console.log("路由跳转错误:", err);
              });
            }, 1000);
          } else if (userInfo.role == "student") {
            setTimeout(() => {
              this.$router.push("/student_profile").catch((err) => {
                console.log("路由跳转错误:", err);
              });
            }, 1000);
          } else {
            setTimeout(() => {
              this.$router.push("/").catch((err) => {
                console.log("路由跳转错误:", err);
              });
            }, 1000);
          }
        } else {
          this.errorMessage = response.message || "登录失败，请重试";
        }
      } catch (error) {
        console.error("登录错误:", error);
        this.errorMessage = "网络错误，请检查网络连接后重试";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style>
/* 全局样式 - 登录页面专用 */
</style>

<style scoped>
.login-page {
  margin: 0;
  padding: 0;
  background: linear-gradient(135deg, #6a11cb, #2575fc);
  font-family: "Poppins", sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  color: #333;
}

/* 容器样式 */
.container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

/* 卡片样式 */
.card {
  background: rgba(255, 255, 255, 0.9);
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 标题样式 */
h2 {
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
  color: #333;
}

/* 表单组样式 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-group input:focus {
  border-color: #6a11cb;
  box-shadow: 0 0 8px rgba(106, 17, 203, 0.3);
  outline: none;
}

/* 错误消息样式 */
.error-message {
  color: #ff4757;
  background-color: #ffe6e6;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 15px;
  text-align: center;
  border: 1px solid #ff4757;
}

/* 按钮样式 */
.btn-primary {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #6a11cb, #2575fc);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2575fc, #6a11cb);
  transform: translateY(-2px);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
}

/* 注册链接样式 */
.text-center {
  text-align: center;
  margin-top: 20px;
}

.text-center a {
  color: #2acb11;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.text-center a:hover {
  color: #54fc25;
  text-decoration: underline;
}
</style>
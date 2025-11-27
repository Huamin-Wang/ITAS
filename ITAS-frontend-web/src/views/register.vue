<template>
  <div class="register-page">
    <div class="register-form">
      <h3><b>用户注册</b></h3>

      <form @submit.prevent="register">
        <div class="form-group">
          <label for="identifier">学号/教工号</label>
          <input type="text" id="identifier" required v-model="identifier" />
        </div>

        <div class="form-group">
          <label for="role">身份</label>
          <select id="role" required v-model="role">
            <option value="student">学生</option>
            <option value="teacher">教师</option>
          </select>
        </div>

        <div class="form-group">
          <label for="name">姓名</label>
          <input type="text" id="name" v-model="name" />
        </div>

        <div class="form-group">
          <label for="gender">性别</label>
          <select id="gender" v-model="gender">
            <option value="男">男</option>
            <option value="女">女</option>
          </select>
        </div>

        <div class="form-group">
          <label for="email">邮箱</label>
          <input type="text" id="email" v-model="email" />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input type="password" id="password" required v-model="password" />
        </div>

        <div class="form-group">
          <label for="confirm_password">确认密码</label>
          <input
            type="password"
            id="confirm_password"
            required
            v-model="confirm_password"
          />
        </div>

        <!-- 🔥 错误提示区域（和登录页完全一样） -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? "注册中..." : "注册" }}
        </button>
      </form>

      <div class="text-center mt-3">
        <a href="/" class="btn-primary">返回首页</a>
      </div>
    </div>
  </div>
</template>

<script>
import { register } from "../http/api.js";
import heartbeat from "@/utils/heartbeat.js";

export default {
  data() {
    return {
      identifier: "",
      role: "student",
      name: "",
      gender: "男",
      email: "",
      password: "",
      confirm_password: "",
      loading: false,
      errorMessage: "",
    };
  },

  methods: {
    async register() {
      this.errorMessage = "";
      this.loading = true;

      const data = {
        identifier: this.identifier,
        role: this.role,
        name: this.name,
        gender: this.gender,
        email: this.email,
        password: this.password,
        confirm_password: this.confirm_password,
      };

      try {
        const res = await register(data);

        if (res.code !== 201 && res.code !== 200) {
          // ⚠ 后端错误（邮箱存在、密码不一致等）
          this.errorMessage = res.message || "注册失败，请检查输入信息";
          this.loading = false;
          return;
        }

        // 保存用户信息
        const userInfo = {
          user_id: res.data.user_id,
          name: res.data.name,
          identifier: res.data.identifier,
          role: res.data.role,
          email: res.data.email,
        };
        localStorage.setItem("userInfo", JSON.stringify(userInfo));

        heartbeat.init();

        this.$message.success("注册成功！");

        // 注册成功跳转
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
        }
      } catch (err) {
        console.error(err);
        this.errorMessage = "网络错误，请稍后再试";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.register-page {
  font-family: Arial, sans-serif;
  background-color: #f8f9fa;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  margin: 0;
}
.register-form {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 100%;
}
.form-group {
  margin-bottom: 15px;
}
label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
input,
select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

button {
  background-color: #4caf50;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* 🔥 从你的登录页面复用的错误提示样式 */
.error-message {
  color: #ff4757;
  background-color: #ffe6e6;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 15px;
  text-align: center;
  border: 1px solid #ff4757;
}
</style>

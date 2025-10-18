<template>
  <div class="register-page">
    <div class="register-form">
      <h3><b>用户注册</b></h3>
      <form>
        <div class="form-group">
          <label for="identifier">学号/教工号</label>
          <input
            type="text"
            id="identifier"
            name="identifier"
            required
            v-model="identifier"
          />
        </div>

        <div class="form-group">
          <label for="role">身份</label>
          <select id="role" name="role" required v-model="role">
            <option value="student">学生</option>
            <option value="teacher">教师</option>
          </select>
        </div>

        <div class="form-group">
          <label for="name">姓名</label>
          <input type="text" id="name" name="name" v-model="name" />
        </div>
        <div class="form-group">
          <label for="gender">性别</label>
          <select id="gender" name="gender" v-model="gender">
            <option value="男">男</option>
            <option value="女">女</option>
          </select>
        </div>

        <div class="form-group">
          <label for="email">邮箱</label>
          <input type="text" id="email" name="email" v-model="email" />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            name="password"
            required
            v-model="password"
          />
        </div>

        <div class="form-group">
          <label for="confirm_password">确认密码</label>
          <input
            type="password"
            id="confirm_password"
            name="confirm_password"
            required
            v-model="confirm_password"
          />
        </div>

        <button type="button" @click="register()">注册</button>
      </form>
      <div class="text-center mt-3">
        <a href="/" class="btn-primary">返回首页</a>
      </div>
    </div>
  </div>
</template>
<script>
import { register } from "../http/api.js";
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
    };
  },

  methods: {
    register() {
      // 构建与后端一致的请求体
      const data = {
        identifier: this.identifier,
        role: this.role,
        name: this.name,
        gender: this.gender,
        email: this.email,
        password: this.password,
        confirm_password: this.confirm_password,
      };
      register(data)
        .then((res) => {
          if (res) {
            if (res.access_token) {
              sessionStorage.setItem("token", res.access_token);
            }
            if (res.name) {
              sessionStorage.setItem("user_name", res.name);
            }
          }
          console.log("注册成功，返回：", res);
        })
        .catch((err) => {
          console.error(err);
        });
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

button:hover {
  background-color: #45a049;
}

.flash-messages {
  margin-bottom: 20px;
}

.flash-message {
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
  background-color: #ffebee;
  color: #c62828;
}
</style>
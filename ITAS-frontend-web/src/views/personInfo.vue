<template>
  <div class="personInfo-page">
    <span @click="back_profile()" class="back-home">返回</span>
    <header>
      <h1>基于大模型的智能教学辅助系统</h1>
    </header>

    <div class="container">
      <h2>个人信息修改提示</h2>

      <div class="info-card">
        <p>
          尊敬的用户，为了提供更好的用户体验和安全性，个人信息修改（包括密码修改）功能已迁移至微信小程序。
        </p>

        <div class="qr-section">
          <h3>请扫描下方二维码，进入小程序</h3>
          <img src="../assets/weixinQR.jpg" alt="微信小程序二维码" />
        </div>

        <div class="info-steps">
          <h3>在小程序中修改个人信息的步骤：</h3>
          <div class="step">
            打开小程序，点击顶部菜单中的<span class="highlight">【姓名】</span>
          </div>
          <div class="step">在个人信息页面中，您可以修改各项个人信息</div>
          <div class="step">按照提示完成身份验证并设置新密码</div>
        </div>
      </div>
    </div>

    <footer>
      <p>&copy; 2025 基于大模型的智能教学辅助系统. All Rights Reserved.</p>
    </footer>
  </div>
</template>

<script>
export default {
  data() {
    return {};
  },
  methods: {
    back_profile() {
      const userInfo = JSON.parse(localStorage.getItem("userInfo"));
      if (userInfo.role == "teacher") {
        this.$router.push("/teacher_profile");
      } else {
        this.$router.push("/student_profile");
      }
    },
  },
  mounted() {},
};
</script>

<style scoped>
.personInfo-page {
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  background-color: #f5f5f5;
  margin: 0;
  padding: 0;
  color: #333;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

header {
  background-color: #001529;
  color: white;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

header h1 {
  margin: 0;
  font-size: 1.8em;
}

.container {
  flex: 1;
  width: 90%;
  max-width: 800px;
  margin: 30px auto;
  padding: 25px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.info-card {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  background-color: #f9f9f9;
}

.qr-section {
  margin: 30px 0;
}

.qr-section img {
  width: 180px;
  height: 180px;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.info-steps {
  text-align: left;
  max-width: 500px;
  margin: 0 auto;
}

.step {
  margin-bottom: 15px;
  padding-left: 20px;
  position: relative;
}

.step:before {
  content: "•";
  position: absolute;
  left: 0;
  color: #1890ff;
  font-weight: bold;
}

.highlight {
  color: #1890ff;
  font-weight: bold;
}

.btn-back {
  display: inline-block;
  background: #1890ff;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 5px;
  cursor: pointer;
  text-decoration: none;
  font-size: 16px;
  margin-top: 20px;
  transition: background-color 0.3s;
}

.btn-back:hover {
  background: #096dd9;
}

footer {
  background-color: #001529;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 15px 0;
  margin-top: auto;
}

@media (max-width: 768px) {
  .container {
    width: 95%;
    padding: 15px;
  }
}

.back-home {
  position: fixed;
  top: 10px;
  left: 10px;
  padding: 0.4rem 1rem;
  background-color: #4299e1;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 200;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(66, 153, 225, 0.1);
  z-index: 1000;
  cursor: pointer;
}

.back-home:hover {
  background-color: #2acb11;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(66, 153, 225, 0.2);
}
</style>
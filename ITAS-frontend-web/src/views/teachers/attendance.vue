<template>
  <div class="attendance-page">
    <div class="nav-container">
      <span @click="go_to_course_manager(this.course.id)" class="back-home"
        >返回课程</span
      >
    </div>

    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8">
          <div class="card">
            <div class="card-header text-center">
              <h3>课堂签到二维码</h3>
            </div>
            <div class="card-body">
              <div class="course-info">
                <h4>{{ course.name }}</h4>
                <p class="mb-0">{{ course.description }}</p>
              </div>

              <div class="qr-container">
                <img
                  src="@/assets/qrcode_sign_id=abc123.png"
                  alt="签到二维码"
                  class="qr-code"
                />
              </div>

              <div class="instructions">
                <div class="alert alert-info">
                  <h5>签到说明：</h5>
                  <ol>
                    <li>请使用微信小程序扫描上方二维码</li>
                    <li>在小程序中完成签到</li>
                    <li>签到有效时间为发起后15分钟内</li>
                  </ol>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { get_course_by_id } from "@/http/api.js";
export default {
  name: "attendance",
  data() {
    return {
      course: {},
    };
  },
  mounted() {
    this.init_course();
  },
  methods: {
    //初始化课程信息
    init_course() {
      const courseId = this.$route.params.courseId;
      if (courseId) {
        get_course_by_id(courseId)
          .then((response) => {
            this.course = response.data;
            const courseName = this.course.name;
            document.title = `课程管理 - ${courseName}`;
          })
          .catch((error) => {
            console.error("获取课程信息失败:", error);
            this.$message.error("获取课程信息失败");
          });
      } else {
        this.$message.error("未提供课程ID");
      }
    },

    // 跳转课程管理
    go_to_course_manager(id) {
      this.$router.push(`/course_manager/${id}`);
    },
  },
};
</script>

<style scoped>
.attendance-page {
  font-family: "Microsoft YaHei", -apple-system, BlinkMacSystemFont, sans-serif;
  background-color: #f8f9fa;
  min-height: 100vh;
  /* 修改顶部内边距以适应返回按钮 */
  padding: 5rem 1rem 2rem 1rem;
  background: linear-gradient(135deg, #f6f8ff 0%, #f1f4ff 100%);
}

.card {
  border: none;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  background: white;
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
}

.card-header {
  background: #4361ee;
  color: white;
  border-radius: 20px 20px 0 0 !important;
  padding: 1.5rem;
  border: none;
  background: linear-gradient(45deg, #4361ee, #4895ef);
}

.card-header h3 {
  margin: 0;
  font-weight: 600;
  font-size: 1.5rem;
}

.qr-container {
  display: flex;
  justify-content: center;
  margin: 2rem 0;
  padding: 1rem;
}

.qr-code {
  width: 280px;
  height: 280px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 10px;
  background: white;
  transition: transform 0.3s ease;
}

.qr-code:hover {
  transform: scale(1.02);
}

.course-info {
  padding: 1.5rem;
  background: rgba(67, 97, 238, 0.05);
  border-radius: 15px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #4361ee;
}

.course-info h4 {
  color: #4361ee;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.course-info p {
  color: #4a5568;
  line-height: 1.6;
}

.instructions {
  color: #2d3748;
}

.alert-info {
  background-color: rgba(72, 149, 239, 0.1);
  border: none;
  border-radius: 15px;
  padding: 1.5rem;
}

.alert-info h5 {
  color: #4361ee;
  margin-bottom: 1rem;
  font-weight: 600;
}

.alert-info ol {
  padding-left: 1.2rem;
}

.alert-info li {
  margin-bottom: 0.5rem;
  color: #4a5568;
}

/* 修改返回按钮样式，确保不被遮挡 */
.nav-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.back-home {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  background: #4361ee;
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(67, 97, 238, 0.2);
}

.back-home:hover {
  background: #3f37c9;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(67, 97, 238, 0.3);
}

@media (max-width: 768px) {
  body {
    padding-top: 4rem;
  }

  .container {
    padding: 0;
  }

  .card {
    margin: 0;
    border-radius: 15px;
  }

  .nav-container {
    padding: 0.5rem;
  }

  .back-home {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }
}
</style>
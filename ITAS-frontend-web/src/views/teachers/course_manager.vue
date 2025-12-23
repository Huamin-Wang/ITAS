<template>
  <div class="courseManager-page">
    <header>
      <!-- <div class="alert alert-{{ category }}">

            </div> -->

      <a href="/teacher_profile" class="back-to-home">返回课程列表</a>
      <div
        style="
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 20px;
          margin-bottom: 10px;
        "
      >
        <h1 style="margin: 0">
          <span style="color: white; cursor: pointer">{{ course.name }}</span>
        </h1>
        <span
          @click="go_to_update_course(this.course.id)"
          style="
            background: #1890ff;
            color: #fff;
            padding: 8px 18px;
            border-radius: 5px;
            text-decoration: none;
            font-size: 1em;
            margin-left: 10px;
            transition: background 0.3s;
            cursor: pointer;
          "
          >更新课程信息</span
        >
      </div>
      <p>课程代码：{{ course.code }}</p>
      <p>
        课程简介：{{ course.description ? course.description : "暂无课程简介" }}
      </p>

      <div class="course-stats">
        <span
          @click="go_to_course_students(this.course.id)"
          class="stat-item"
          style="
            display: block;
            text-decoration: none;
            color: inherit;
            cursor: pointer;
          "
        >
          应修学生：<strong style="text-decoration: underline">{{
            student_count.total_count
          }}</strong>
          人
        </span>
        <span
          @click="go_to_course_students(this.course.id)"
          class="stat-item"
          style="
            display: block;
            text-decoration: none;
            color: inherit;
            cursor: pointer;
          "
        >
          已加入学生：<strong style="text-decoration: underline">{{
            student_count.enrolled_count
          }}</strong>
          人
        </span>
      </div>

      <div class="login-status">
        <span style="color: #2acb11; font-size: 30px"
          >欢迎{{ userInfo.name }}老师！</span
        >
      </div>
    </header>

    <div class="container">
      <div class="welcome-section">
        <h2><b>课程管理中心</b></h2>
        <button
          @click="go_to_attendance(this.course.id)"
          class="attendance-btn"
        >
          考勤管理
        </button>
        <p>使用下方功能管理您的课程教学活动</p>
      </div>

      <div class="dashboard-grid">
        <div class="dashboard-card">
          <h3>随机选择</h3>
          <p>随机选中一个学生回答问题，增强课堂互动性</p>
          <button @click="go_to_random_select(this.course.id)">
            进入随机选择管理
          </button>
        </div>

        <div class="dashboard-card">
          <h3>课堂抢答</h3>
          <p>发布课堂抢答活动，激发学生学习积极性</p>
          <button disabled style="cursor: not-allowed; opacity: 0.6">
            功能开发中
          </button>
          <!--<button onclick="location.href='/course/quiz/{{ course.id }}'">进入抢答管理</button>-->
        </div>

        <div class="dashboard-card">
          <h3>作业管理</h3>
          <p>发布、批改和管理课程作业</p>
          <button @click="go_to_course_assignments(this.course.id)">
            进入作业管理
          </button>
        </div>

        <div class="dashboard-card">
          <h3>成绩管理</h3>
          <p>录入和查看学生平时成绩</p>
          <button @click="go_to_add_score(this.course.id)">进入成绩管理</button>
        </div>

        <div class="dashboard-card">
          <h3>学生管理</h3>
          <p>查看和管理课程学生名单</p>
          <button @click="go_to_course_students(this.course.id)">
            进入学生管理
          </button>
        </div>

        <div class="dashboard-card">
          <h3>教学资源</h3>
          <p>分享和管理课程学习资源</p>
          <button @click="go_to_course_resource(this.course.id)">
            进入资源管理
          </button>
        </div>

        <div class="dashboard-card">
          <h3>学习状况分析</h3>
          <p>智能分析学生薄弱知识点，优化教学重点</p>
          <button @click="go_to_analysis_selection(this.course.id)">
            进入分析管理
          </button>
        </div>

        <div class="dashboard-card">
          <h3>课堂测试</h3>
          <p>发布、批改和管理课程小测</p>
          <button @click="go_to_course_quiz(this.course.id)">
            进入课堂测试
          </button>
        </div>
      </div>
      <!-- <div style="text-align: center; margin-top: 40px">
        <span
          @click="go_to_chat(this.course.id)"
          style="
            display: inline-block;
            background: #1890ff;
            color: #fff;
            padding: 14px 32px;
            border-radius: 6px;
            font-size: 1.15em;
            text-decoration: none;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: background 0.3s;
            cursor: pointer;
          "
        >
          跳转到AI问答
        </span>
      </div> -->
    </div>

    <footer>
      <p>&copy; 2025 基于大模型的智能教学辅助系统. All Rights Reserved.</p>
    </footer>
  </div>
</template>

<script>
import {
  get_course_by_id,
  update_registration_status,
  course_student_count,
} from "@/http/api.js";
export default {
  name: "",
  data() {
    return {
      course: {},
      userInfo: {},
      student_count: {},
    };
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

    //初始化用户信息
    init_userInfo() {
      this.userInfo = JSON.parse(localStorage.getItem("userInfo"));
    },

    //更新学生注册信息
    update_registration_status(course_id) {
      update_registration_status(course_id)
        .then((response) => {
          console.log("更新学生注册信息成功");
        })
        .catch((error) => {
          console.error("更新学生注册信息失败:", error);
        });
    },

    //获取课程学生数
    get_course_student_count(course_id) {
      course_student_count(course_id)
        .then((response) => {
          this.student_count = response.data;
        })
        .catch((error) => {
          console.error("获取课程学生数失败:", error);
        });
    },

    //转跳到课程学生名单
    go_to_course_students(course_id) {
      this.$router.push(`/course_students/${course_id}`);
    },

    //转跳到更新课程信息
    go_to_update_course(course_id) {
      this.$router.push(`/update_course/${course_id}`);
    },

    //转跳到考勤页面
    go_to_attendance(course_id) {
      this.$router.push(`/attendance/${course_id}`);
    },

    //转跳到课程作业页面
    go_to_course_assignments(course_id) {
      this.$router.push(`/assignments/${course_id}`);
    },

    //跳转成绩管理页面
    go_to_add_score(course_id) {
      this.$router.push(`/add_score/${course_id}`);
    },

    //跳转随机选择页面
    go_to_random_select(course_id) {
      this.$router.push(`/random_select/${course_id}`);
    },

    //跳转课堂测试页面
    go_to_course_quiz(course_id) {
      this.$router.push(`/course_quiz/${course_id}`);
    },

    //跳转资源分享页面
    go_to_course_resource(course_id) {
      this.$router.push(`/course_resource/${course_id}`);
    },

    //跳转学习状况分析选择页面
    go_to_analysis_selection(course_id) {
      this.$router.push(`/analysis_selection/${course_id}`);
    },
    //跳转ai小问答
    // go_to_chat(course_id) {
    //   this.$router.push(`/chat/${course_id}`);
    // },
  },
  mounted() {
    this.init_course();
    this.init_userInfo();
    this.update_registration_status(this.$route.params.courseId);
    this.get_course_student_count(this.$route.params.courseId);
  },
};
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.courseManager-page {
  font-family: "Microsoft YaHei", sans-serif;
  background-color: #f0f2f5;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: #333;
  line-height: 1.6;
}

header {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  text-align: center;
  padding: 30px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: relative;
}

header h1 {
  margin: 0;
  font-size: 2.2em;
  font-weight: bold;
  margin-bottom: 10px;
}

header p {
  margin: 8px 0;
  font-size: 1.1em;
  opacity: 0.9;
}

.back-to-home {
  position: absolute;
  top: 20px;
  left: 20px;
  color: #fff;
  text-decoration: none;
  font-size: 1em;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.back-to-home:before {
  content: "←";
  margin-right: 5px;
}

.back-to-home:hover {
  transform: translateX(-5px);
}

.login-status {
  margin-top: 15px;
}

.container {
  flex: 1;
  width: 90%;
  max-width: 1200px;
  margin: 30px auto;
  padding: 30px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.welcome-section h2 {
  color: #1890ff;
  font-size: 2em;
  margin-bottom: 20px;
  position: relative;
  display: inline-block;
}

.welcome-section h2:after {
  content: "";
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background-color: #1890ff;
}

.welcome-section p {
  color: #666;
  font-size: 1.1em;
  margin: 15px 0;
}

.attendance-btn {
  margin: 20px 10px;
  padding: 12px 24px;
  background-color: #1890ff;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1.1em;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.attendance-btn:hover {
  background-color: #096dd9;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

.dashboard-card {
  background: #fff;
  padding: 25px;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 200px;
}

.dashboard-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.dashboard-card h3 {
  color: #1890ff;
  font-size: 1.4em;
  margin-bottom: 15px;
}

.dashboard-card p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.dashboard-card button {
  background: #1890ff;
  color: #fff;
  border: none;
  padding: 12px 20px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  width: 100%;
  margin-top: auto;
}

.dashboard-card button:hover {
  background: #096dd9;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

footer {
  background-color: #001529;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 20px 0;
  margin-top: 30px;
}

.course-stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin: 15px 0;
}

.stat-item {
  background: rgba(255, 255, 255, 0.2);
  padding: 10px 20px;
  border-radius: 8px;
}

.stat-item a {
  color: #fff;
  text-decoration: none;
}

.alert {
  padding: 15px;
  margin-bottom: 20px;
  border: 1px solid transparent;
  border-radius: 4px;
}

.alert-success {
  color: #3c763d;
  background-color: #dff0d8;
  border-color: #d6e9c6;
}

.alert-registerError {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

@media (max-width: 768px) {
  header h1 {
    font-size: 1.8em;
  }

  .container {
    width: 95%;
    margin: 15px auto;
    padding: 20px;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .course-stats {
    flex-direction: column;
    gap: 10px;
    align-items: center;
  }
}
</style>
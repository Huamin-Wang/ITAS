<template>
  <div class="course_detail-page">
    <a href="/student_profile" class="back-home">返回</a>

    <div class="header">
      <!-- 课程名 course.name -->
      <h1>{{ course.name }}</h1>
      <p>课程代码：{{ course.code }}</p>
      <p>教师：</p>
      <p>学期：{{ course.semester }}</p>
    </div>

    <div class="container">
      <div class="main-content">
        <div class="content">
          <!-- 课程概览 -->
          <div class="section">
            <h3><span class="section-icon">📊</span>课程概览</h3>
            <div class="course-overview">
              <div class="overview-card">
                <h4>总作业数</h4>
                <div class="overview-number">
                  {{ assignments.length }}
                </div>
              </div>
            </div>
          </div>

          <!-- 小测列表 -->
          <div class="section">
            <h3><span class="section-icon">📋</span>课程小测</h3>
            <!-- 使用小测组件 -->
            <QuizList
              v-if="course.id"
              :course-ids="[course.id]"
              :student_number="student_number"
            />
          </div>

          <!-- 作业列表 -->
          <div class="section">
            <h3><span class="section-icon">📝</span>作业列表</h3>
            <div v-if="assignments.length">
              <div
                class="homework-card"
                v-for="assignment in assignments"
                :key="assignment.id"
                :class="{ hidden: index >= 5 && !showAllAssignments }"
              >
                <h4>
                  <a :href="`/submission_detail/${assignment.id}`">{{
                    assignment.title
                  }}</a>
                </h4>
                <div class="homework-date">
                  截止日期：{{ assignment.due_date }}
                </div>
              </div>

              <button
                class="btn"
                v-if="assignments.length > 5 && !showAllAssignments"
                @click="showAllAssignments = true"
              >
                显示更多作业
              </button>
            </div>
            <p style="color: #666; text-align: center; padding: 2rem" v-else>
              暂无作业
            </p>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <button
              class="btn btn-secondary coming-soon"
              onclick="showComingSoon('课程视频')"
            >
              🎥 课程视频
            </button>
            <button
              class="btn btn-info coming-soon"
              onclick="showComingSoon('在线讨论')"
            >
              💬 在线讨论
            </button>
          </div>
        </div>
      </div>

      <div class="sidebar">
        <div class="content">
          <!-- 课程简介 -->
          <div class="section">
            <h3><span class="section-icon">📖</span>课程简介</h3>
            <p>
              本课程旨在帮助学生掌握相关知识和技能，通过理论学习和实践操作相结合的方式，培养学生的综合能力。
            </p>
          </div>

          <!-- 快速操作 -->
          <div class="section">
            <h3><span class="section-icon">⚡</span>快速操作</h3>
            <div
              class="action-buttons"
              style="flex-direction: column; gap: 0.5rem"
            >
              <button class="btn" @click="showComingSoon('练习题库')">
                📒 练习题库
              </button>
              <button class="btn" @click="showComingSoon('错题分析')">
                ❌ 错题分析
              </button>
              <button
                class="btn coming-soon"
                onclick="showComingSoon('学习计划')"
              >
                📅 学习计划
              </button>
            </div>
          </div>

          <!-- 通知公告 -->
          <div class="section">
            <h3><span class="section-icon">📢</span>通知公告</h3>
            <div class="notification-item">
              <div class="notification-title">期末考试安排</div>
              <div class="notification-date">2024-12-20</div>
            </div>
            <div class="notification-item">
              <div class="notification-title">作业提交提醒</div>
              <div class="notification-date">2024-12-15</div>
            </div>
            <button
              class="btn coming-soon"
              style="width: 100%"
              onclick="showComingSoon('更多公告')"
            >
              查看更多公告
            </button>
          </div>

          <!-- 推荐学习资源 -->
          <div class="section">
            <h3><span class="section-icon">🔗</span>学习资源</h3>
            <ul class="resource-list">
              <li>
                <a href="https://www.icourse163.org/" target="_blank"
                  >慕课平台提升</a
                >
              </li>
              <li><a href="/chat" target="_blank">智能问答助手</a></li>
              <li>
                <a
                  href="#"
                  class="coming-soon"
                  onclick="showComingSoon('电子教材'); return false;"
                  >电子教材</a
                >
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getCourseDetail, getAssignments } from "@/http/api";
import QuizList from "@/components/QuizList.vue"; // 导入小测组件

export default {
  name: "CourseDetail",
  components: {
    QuizList,
  },
  data() {
    return {
      course: {},
      error: "",
      loading: true,
      assignments: {},
      course_id: null,
      student_number: null,
      showAllAssignments: false,
    };
  },
  methods: {
    init_student_number() {
      try {
        const userInfo = JSON.parse(localStorage.getItem("userInfo"));
        this.student_number = userInfo.identifier;
      } catch (error) {
        console.error("获取用户信息失败:", error);
        return null;
      }
    },
    async loadCourseDetail() {
      const courseId = this.$route.params.courseId;
      try {
        const response = await getCourseDetail(courseId);
        if (response.code === 200) {
          this.course = response.data;
        } else {
          console.error("获取课程详情失败:", response.message);
          this.$router.push("/student_profile");
        }
      } catch (error) {
        console.error("获取课程详情失败:", error);
        this.$router.push("/student_profile");
      }
    },

    //获取课程作业列表
    async fetchAssignments() {
      const courseId = this.$route.params.courseId;
      if (courseId) {
        getAssignments(courseId)
          .then((response) => {
            this.assignments = response.data;
          })
          .catch((error) => {
            console.error("获取课程作业列表失败:", error);
            this.$message.error("获取课程作业列表失败");
          });
      } else {
        this.$message.error("未提供课程ID");
      }
    },

    //页面转跳
    showComingSoon(name) {
      switch (name) {
        case "错题分析":
          this.$router.push(`/wrong_questions/${this.course_id}`);
          break;
        case "练习题库":
          this.$router.push(`/student_exercise/${this.course_id}`);
          break;
        default:
          break;
      }
    },
  },
  mounted() {
    this.init_student_number();
    this.loadCourseDetail();
    this.fetchAssignments();
    this.course_id = this.$route.params.courseId;
  },
};
</script>

<style scoped>
:root {
  --primary-color: #1890ff;
  --primary-dark: #0056b3;
  --gray-light: #f4f4f4;
  --gray-medium: #eee;
  --text-dark: #333;
  --success: #52c41a;
  --white: #fff;
  --shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  --header-text-align: center;
  --warning: #fa8c16;
  --info: #13c2c2;
}
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.course_detail-page {
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f4f4f4;
  color: #333;
  line-height: 1.6;
}

.container {
  width: 90%;
  max-width: 1200px;
  margin: 2rem auto;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.main-content,
.sidebar {
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  overflow: hidden;
}

.header {
  background-color: #1890ff;
  color: #fff;
  padding: 2rem;
  grid-column: 1 / -1;
  border-radius: 12px;
  margin-bottom: 1rem;
  text-align: center;
}

.header h1 {
  font-size: 2.2rem;
}

.content {
  padding: 2rem;
}

.section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
  background-color: rgba(24, 144, 255, 0.05);
}

.section h3 {
  margin-bottom: 1rem;
  color: #1890ff;
  display: flex;
  align-items: center;
}

.section a {
  text-decoration: none;
}

.section-icon {
  margin-right: 0.5rem;
  font-size: 1.2em;
}

.course-overview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.overview-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
}

.overview-card h4 {
  color: #1890ff;
  margin-bottom: 0.5rem;
}

.overview-number {
  font-size: 1.8rem;
  font-weight: bold;
  color: #0056b3;
}

.homework-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.homework-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.homework-status {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
  margin-left: 1rem;
  font-weight: 500;
}

.status-pending {
  background-color: #ffd666;
  color: #874d00;
}

.status-submitted {
  background-color: #b7eb8f;
  color: #135200;
}

.status-overdue {
  background-color: #ffccc7;
  color: #820014;
}

.homework-date {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
}

.homework-date::before {
  content: "📅";
  margin-right: 0.5rem;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin: 1.5rem 0;
}

.btn {
  padding: 0.8rem 1.2rem;
  background-color: #1890ff;
  color: #fff;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  min-width: 120px;
  transition: 0.3s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: #fa8c16;
}

.btn-secondary:hover {
  background-color: #d48806;
}

.btn-info {
  background-color: #13c2c2;
}

.btn-info:hover {
  background-color: #08979c;
}

.notification-item {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  border-left: 4px solid #fa8c16;
}

.notification-title {
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #333;
}

.notification-date {
  color: #666;
  font-size: 0.9rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #eee;
  border-radius: 4px;
  margin-top: 0.5rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #52c41a, #73d13d);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #333;
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
}

.back-home:hover {
  background-color: #2acb11;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(66, 153, 225, 0.2);
}

.hidden {
  display: none;
}

.coming-soon {
  opacity: 0.7;
  cursor: not-allowed;
}

.resource-list {
  list-style: none;
}

.resource-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.resource-list li:last-child {
  border-bottom: none;
}

.resource-list a {
  color: #1890ff;
  text-decoration: none;
  display: flex;
  align-items: center;
}

.resource-list a:hover {
  color: #0056b3;
}

.resource-list a::before {
  content: "📎";
  margin-right: 0.5rem;
}

@media screen and (max-width: 1024px) {
  .container {
    grid-template-columns: 1fr;
    width: 95%;
  }

  .course-overview {
    grid-template-columns: 1fr;
  }
}

@media screen and (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .content {
    padding: 1rem;
  }

  .course-overview {
    grid-template-columns: 1fr;
  }
}

:deep(.dashboard-card) {
  padding: 1rem;
  margin-top: 0;
  border-radius: 8px;
  border: none;
  transition: none;
  box-shadow: none;
}

/* 移除小测卡片的hover效果，使其与页面其他卡片保持一致 */
:deep(.dashboard-card:hover) {
  transform: none;
  box-shadow: none;
}
</style>
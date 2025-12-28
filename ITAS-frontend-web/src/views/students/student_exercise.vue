<template>
  <div class="student_exercise-page">
    <span @click="goBack()" class="back-home">返回</span>

    <div class="header">
      <h1>习题练习</h1>
      <p>课程：{{ course.name }} ({{ course.code }})</p>
      <p>通过练习巩固所学知识，提升学习效果</p>
    </div>

    <div class="container">
      <div class="main-content">
        <div class="content">
          <!-- 统计概览 -->
          <div class="section">
            <h3><span class="section-icon">📊</span>练习统计</h3>
            <div class="course-overview">
              <div class="overview-card">
                <h4>习题合集</h4>
                <div class="overview-number">
                  {{ exercises.length }}
                </div>
              </div>
              <div class="overview-card">
                <h4>已提交习题</h4>
                <div class="overview-number">
                  {{ submittedExercisesCount }}
                </div>
              </div>
            </div>
          </div>

          <!-- 习题合集列表 -->
          <div class="section">
            <h3><span class="section-icon">📚</span>习题合集</h3>
            <div v-if="exercises.length">
              <div
                class="exercise-card"
                v-for="exercise in exercises"
                :key="exercise.id"
                @click="goToExerciseDetail(exercise.id)"
              >
                <div class="exercise-header">
                  <h4>{{ exercise.title }}</h4>
                  <span
                    class="exercise-status"
                    :class="getStatusClass(exercise)"
                  >
                    {{ getStatusText(exercise) }}
                  </span>
                </div>
                <p class="exercise-description">{{ exercise.description }}</p>
                <div class="exercise-footer">
                  <div class="exercise-meta">
                    <span class="meta-item">
                      <span class="meta-icon">📅</span>
                      {{ formatDate(exercise.create_time) }}
                    </span>
                  </div>
                  <div class="exercise-progress" v-if="exercise.is_submitted">
                    <div class="progress-bar">
                      <div class="progress-fill" style="width: 100%"></div>
                    </div>
                    <div class="progress-text">已提交</div>
                  </div>
                </div>
              </div>
            </div>
            <p style="color: #666; text-align: center; padding: 2rem" v-else>
              暂无习题合集
            </p>
          </div>
        </div>
      </div>

      <!-- 操作提示 -->
      <div class="sidebar">
        <div class="content">
          <div class="section">
            <h3><span class="section-icon">💡</span>练习提示</h3>
            <div class="tip-box">
              <div class="tip-item">
                <span class="tip-icon">✅</span>
                <div class="tip-content">
                  <strong>建议顺序练习</strong>
                  <p>按照章节顺序完成练习，有助于知识体系的构建</p>
                </div>
              </div>
              <div class="tip-item">
                <span class="tip-icon">📈</span>
                <div class="tip-content">
                  <strong>错题回顾</strong>
                  <p>定期复习错题，巩固薄弱知识点</p>
                </div>
              </div>
              <div class="tip-item">
                <span class="tip-icon">🎯</span>
                <div class="tip-content">
                  <strong>目标导向</strong>
                  <p>每次练习设定明确的目标，提高学习效率</p>
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
import { getCourseDetail, get_exercises_student } from "@/http/api.js";
export default {
  name: "StudentExercise",
  data() {
    return {
      course: {},
      exercises: [],
    };
  },
  computed: {
    submittedExercisesCount() {
      return this.exercises.filter((exercise) => exercise.is_submitted).length;
    },
  },
  methods: {
    //课程信息初始化
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

    async loadExercises() {
      try {
        const userInfo = JSON.parse(localStorage.getItem("userInfo"));
        const params = {
          course_id: this.$route.params.courseId,
          student_number: userInfo.identifier,
        };
        const res = await get_exercises_student(params);
        if (res.code === 200) {
          this.exercises = res.data;
        } else {
          console.error("获取习题列表失败:", res.message);
          this.$message.error("获取习题列表失败");
        }
      } catch (error) {
        console.error("获取习题列表失败:", error);
        this.$message.error("获取习题列表失败");
      }
    },

    goToExerciseDetail(exerciseId) {
      this.$router.push({
        name: "exercise_detail",
        params: {
          courseId: this.$route.params.courseId,
          exerciseId: exerciseId,
        },
      });
    },

    getStatusClass(exercise) {
      if (exercise.is_submitted) {
        return "status-completed";
      }
      return "status-unfinished";
    },

    getStatusText(exercise) {
      if (exercise.is_submitted) {
        return "已提交";
      }
      return "未提交";
    },

    formatDate(dateString) {
      if (!dateString) return "";
      const date = new Date(dateString);
      return date.toLocaleDateString("zh-CN");
    },

    goBack() {
      this.$router.push(`/course_detail/${this.$route.params.courseId}`);
    },
  },
  mounted() {
    this.loadCourseDetail();
    this.loadExercises();
  },
};
</script>

<style scoped>
.student_exercise-page {
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
  margin-bottom: 0.5rem;
}

.header p {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0.3rem 0;
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

.exercise-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.exercise-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border-color: #1890ff;
}

.exercise-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.exercise-header h4 {
  color: #333;
  font-size: 1.2rem;
  margin: 0;
}

.exercise-status {
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-unfinished {
  background-color: #f0f0f0;
  color: #666;
}

.status-in-progress {
  background-color: #e6f7ff;
  color: #1890ff;
}

.status-completed {
  background-color: #f6ffed;
  color: #52c41a;
}

.exercise-description {
  color: #666;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.exercise-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.exercise-meta {
  display: flex;
  gap: 1.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  color: #666;
  font-size: 0.9rem;
}

.meta-icon {
  margin-right: 0.3rem;
}

.exercise-progress {
  width: 30%;
  min-width: 150px;
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
  margin-top: 0.3rem;
  font-size: 0.85rem;
  color: #666;
  text-align: right;
}

.tip-box {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.tip-item {
  display: flex;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.tip-item:last-child {
  border-bottom: none;
}

.tip-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
  flex-shrink: 0;
}

.tip-content strong {
  display: block;
  color: #333;
  margin-bottom: 0.3rem;
}

.tip-content p {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.back-home {
  position: fixed;
  cursor: pointer;
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
  .content {
    padding: 1rem;
  }

  .exercise-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .exercise-progress {
    width: 100%;
    margin-top: 1rem;
  }

  .exercise-meta {
    flex-wrap: wrap;
    gap: 1rem;
  }
}
</style>
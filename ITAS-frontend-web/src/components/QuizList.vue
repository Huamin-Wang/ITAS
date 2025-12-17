<template>
  <div class="dashboard-card">
    <div class="quiz-header">
      <h3>小测列表</h3>
      <div>
        <button @click="refreshQuizzes" class="refresh-btn">立即刷新</button>
      </div>
    </div>

    <!-- 小测列表 -->
    <div v-if="quiz && quiz.length" class="quiz-list-container">
      <!-- 进行中的小测（未提交） -->
      <div v-if="hasPublishedQuizzes" class="quiz-section">
        <h4 class="quiz-section-title">
          待完成小测
          <span class="quiz-count-badge">{{ publishedQuizzesCount }}</span>
        </h4>
        <ul class="quiz-list">
          <li
            v-for="q in publishedQuizzes"
            :key="q.id"
            class="quiz-item quiz-item-published"
          >
            <div class="quiz-item-content">
              <div class="quiz-info">
                <span @click="go_to_student_quiz(q.id)" class="quiz-title">
                  {{ q.title }}
                </span>
                <div class="quiz-meta">
                  <span class="quiz-deadline">
                    截止日期：{{ formatDateTime(q.end_time) }}
                  </span>
                </div>
              </div>
              <div class="quiz-status">
                <span class="status-badge status-published">进行中</span>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- 已提交的小测 -->
      <div v-if="hasSubmittedQuizzes" class="quiz-section">
        <h4 class="quiz-section-title quiz-section-submitted">
          已提交小测
          <span class="quiz-count-badge">{{ submittedQuizzesCount }}</span>
        </h4>
        <ul class="quiz-list">
          <li
            v-for="q in submittedQuizzes"
            :key="q.id"
            class="quiz-item quiz-item-submitted"
          >
            <div class="quiz-item-content">
              <div class="quiz-info">
                <span
                  @click="go_to_student_quiz(q.id)"
                  class="quiz-title submitted"
                >
                  {{ q.title }}
                </span>
                <div class="quiz-meta">
                  <span class="quiz-deadline">
                    截止日期：{{ formatDateTime(q.end_time) }}
                  </span>
                  <span class="quiz-status-text">已提交</span>
                </div>
              </div>
              <div class="quiz-status">
                <span class="status-badge status-submitted">已提交</span>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- 已结束的小测（未提交） -->
      <div v-if="hasFinishedQuizzes" class="quiz-section">
        <h4 class="quiz-section-title quiz-section-finished">
          已结束小测
          <span class="quiz-count-badge">{{ finishedQuizzesCount }}</span>
        </h4>
        <ul class="quiz-list">
          <li
            v-for="q in finishedQuizzes"
            :key="q.id"
            class="quiz-item quiz-item-finished"
          >
            <div class="quiz-item-content">
              <div class="quiz-info">
                <span class="quiz-title finished">
                  {{ q.title }}
                </span>
                <div class="quiz-meta">
                  <span class="quiz-deadline">
                    截止日期：{{ formatDateTime(q.end_time) }}
                  </span>
                  <span class="quiz-status-text">已结束</span>
                </div>
              </div>
              <div class="quiz-status">
                <span class="status-badge status-finished">已结束</span>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
    <div v-else class="no-quiz-message">
      <p>你真棒，没有待完成的小测！</p>
    </div>

    <small class="last-update">最后更新：{{ lastUpdate }}</small>
  </div>
</template>

<script>
import { getQuizzesStudent } from "@/http/api";

export default {
  name: "QuizList",
  props: {
    courseIds: {
      type: Array,
      required: true,
      default: () => [],
    },
    student_number: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      quiz: [],
      lastUpdate: "尚未更新",
      previousQuizIds: new Set(),
      // SSE 相关
      sse: null,
      sseStatus: {
        active: true,
        errorCount: 0,
        maxErrors: 5,
      },
    };
  },
  computed: {
    // 根据状态过滤小测
    publishedQuizzes() {
      // 只显示进行中且未提交的小测
      return this.quiz.filter(
        (q) => q.status === "published" && !q.is_submitted
      );
    },
    submittedQuizzes() {
      // 显示所有已提交的小测（包括进行中和已结束的）
      return this.quiz.filter((q) => q.is_submitted === true);
    },
    finishedQuizzes() {
      // 只显示已结束且未提交的小测
      return this.quiz.filter(
        (q) => q.status === "finished" && !q.is_submitted
      );
    },
    publishedQuizzesCount() {
      return this.publishedQuizzes.length;
    },
    submittedQuizzesCount() {
      return this.submittedQuizzes.length;
    },
    finishedQuizzesCount() {
      return this.finishedQuizzes.length;
    },
    hasPublishedQuizzes() {
      return this.publishedQuizzes.length > 0;
    },
    hasSubmittedQuizzes() {
      return this.submittedQuizzes.length > 0;
    },
    hasFinishedQuizzes() {
      return this.finishedQuizzes.length > 0;
    },
  },
  watch: {
    courseIds: {
      immediate: true,
      handler(newCourseIds) {
        if (newCourseIds && newCourseIds.length > 0) {
          this.initSSE();
        }
      },
    },
  },
  methods: {
    // 手动刷新
    async refreshQuizzes() {
      this.$message.info("正在刷新小测数据...");
      await this.loadQuizzes();
    },

    // 传统接口获取一次（给手动刷新用）
    async loadQuizzes() {
      let newList = [];

      for (const courseId of this.courseIds) {
        const params = {
          student_number: this.student_number,
          course_id: courseId,
        };
        const r = await getQuizzesStudent(params);
        if (r.code === 200) newList.push(...r.data);
      }

      this.processQuizzes(newList);
    },

    // SSE: 开始监听
    initSSE() {
      if (this.sse) {
        this.stopSSE();
      }

      // 等待一个微任务，确保DOM已更新
      this.$nextTick(() => {
        this.startSSE();
      });
    },

    startSSE() {
      if (!this.courseIds.length) return;

      const userId = JSON.parse(localStorage.getItem("userInfo"))?.user_id;
      if (!userId) return;

      this.sse = new EventSource(
        `https://www.001ai.top/api/quiz_stream?course_ids=${this.courseIds.join(
          ","
        )}`
      );

      this.sse.onmessage = (event) => {
        const eventData = JSON.parse(event.data);
        if (eventData.type === "new_quiz") {
          console.log("sse message:", typeof event.data);
          this.loadQuizzes(); // 有新小测 → 刷新列表
          this.showNewQuizNotification();
        }
      };

      this.sse.onerror = () => {
        console.warn("SSE 连接异常");

        this.sseStatus.errorCount++;
        if (this.sseStatus.errorCount >= this.sseStatus.maxErrors) {
          this.stopSSE();
          this.$message.error("实时更新已停止（错误次数过多）");
        }
      };

      this.sseStatus.active = true;
    },

    stopSSE() {
      if (this.sse) {
        this.sse.close();
        this.sse = null;
      }
      this.sseStatus.active = false;
    },

    showNewQuizNotification() {
      if ("Notification" in window && Notification.permission === "granted") {
        new Notification("有新小测发布", {
          body: "请及时查看待完成小测",
        });
      }
      this.$notify({
        title: "新小测提醒",
        message: "您有新的小测待完成，请及时查看",
        type: "success",
      });
    },

    formatDateTime(str) {
      return str ? str.slice(0, 16).replace("T", " ") : "";
    },

    processQuizzes(newList) {
      // 按状态和截止日期排序：published的在前，然后按截止日期升序
      const sortedList = newList.sort((a, b) => {
        // 首先按状态排序：published 在前
        if (a.status === "published" && b.status !== "published") return -1;
        if (a.status !== "published" && b.status === "published") return 1;

        // 相同状态按截止日期升序排序
        const dateA = new Date(a.end_time);
        const dateB = new Date(b.end_time);
        return dateA - dateB;
      });

      this.quiz = sortedList;
      this.previousQuizIds = new Set(sortedList.map((q) => q.id));

      const now = new Date();
      this.lastUpdate =
        `${now.getHours().toString().padStart(2, "0")}:` +
        `${now.getMinutes().toString().padStart(2, "0")}:` +
        `${now.getSeconds().toString().padStart(2, "0")}`;
    },

    // 请求通知权限
    requestNotificationPermission() {
      if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission();
      }
    },

    go_to_student_quiz(quizId) {
      this.$router.push(`/student_quiz/${quizId}`);
    },
  },

  mounted() {
    this.loadQuizzes();
    this.requestNotificationPermission();
  },

  beforeDestroy() {
    this.stopSSE();
  },
};
</script>

<style scoped>
.dashboard-card {
  background: #fff;
  padding: 20px;
  margin-top: 20px;
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

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.refresh-btn {
  background-color: #1890ff;
  color: white;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.refresh-btn:hover {
  background-color: #096dd9;
}

.last-update {
  display: block;
  margin-top: 10px;
  color: #999;
  font-size: 12px;
  text-align: right;
}

/* 小测列表样式 */
.quiz-list-container {
  margin-top: 15px;
}

.quiz-section {
  margin-bottom: 25px;
}

.quiz-section:last-child {
  margin-bottom: 0;
}

.quiz-section-title {
  color: #333;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
}

.quiz-section-submitted {
  color: #1890ff;
}

.quiz-section-finished {
  color: #999;
}

.quiz-count-badge {
  background-color: #f0f0f0;
  color: #666;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  margin-left: 8px;
}

.quiz-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.quiz-item {
  padding: 12px 15px;
  margin-bottom: 8px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.quiz-item:hover {
  background-color: #fafafa;
}

.quiz-item-published {
  background-color: #f6ffed;
  border-left: 4px solid #52c41a;
}

.quiz-item-submitted {
  background-color: #f0f8ff;
  border-left: 4px solid #1890ff;
}

.quiz-item-finished {
  background-color: #fafafa;
  border-left: 4px solid #d9d9d9;
  opacity: 0.8;
}

.quiz-item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quiz-info {
  flex: 1;
}

.quiz-title {
  color: #1890ff;
  font-weight: 500;
  text-decoration: none;
  display: block;
  margin-bottom: 5px;
  transition: color 0.2s;
  cursor: pointer;
}

.quiz-title:hover {
  color: #096dd9;
  text-decoration: underline;
}

.quiz-title.submitted {
  color: #1890ff;
  cursor: pointer;
}

.quiz-title.submitted:hover {
  color: #096dd9;
  text-decoration: underline;
}

.quiz-title.finished {
  color: #999;
  cursor: default;
}

.quiz-title.finished:hover {
  text-decoration: none;
  color: #999;
}

.quiz-meta {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #666;
}

.quiz-deadline {
  margin-right: 15px;
}

.quiz-status-text {
  color: #999;
  font-size: 12px;
}

.quiz-status {
  margin-left: 15px;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  font-size: 12px;
  border-radius: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.status-published {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status-submitted {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.status-finished {
  background-color: #f5f5f5;
  color: #999;
  border: 1px solid #d9d9d9;
}

.no-quiz-message {
  text-align: center;
  padding: 30px 20px;
  color: #999;
}

.no-quiz-message p {
  font-size: 16px;
  margin: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .quiz-item-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .quiz-status {
    margin-left: 0;
    margin-top: 8px;
  }

  .quiz-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .quiz-deadline {
    margin-right: 0;
    margin-bottom: 4px;
  }
}
</style>
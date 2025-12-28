<template>
  <div class="student-wrong-questions-container">
    <!-- 头部区域 -->
    <header>
      <span @click="goBack" class="back-to-home">返回</span>
      <h1>错题分析报告</h1>
      <p>智能分析你的错题情况，提供个性化学习建议</p>
      <div class="analysis-note">注：以下分析基于你近期错题数据</div>
    </header>

    <div class="container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在分析你的错题数据...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">!</div>
        <p>{{ error }}</p>
        <button class="action-button" @click="loadWrongAnalysis">重试</button>
      </div>

      <!-- 正常显示 -->
      <div v-else>
        <!-- 学生信息卡片 -->
        <h2 class="section-title">学生基本信息</h2>
        <div class="student-info-card">
          <div class="student-avatar">
            {{ analysisData.student_name?.charAt(0) || "无" }}
          </div>
          <div class="student-details">
            <h3>{{ analysisData.student_name || "未获取到姓名" }}</h3>
            <p>
              <strong>学号:</strong> {{ analysisData.student_number || "无" }}
            </p>
            <p>
              <strong>课程:</strong>
              {{ analysisData.course_name || "未获取到课程信息" }}
            </p>
            <p>
              <strong>学习状态:</strong>
              <span
                :class="
                  getStatusClass(
                    analysisData.learning_overview?.learning_status
                  )
                "
              >
                {{ analysisData.learning_overview?.progress_level || "未知" }}
              </span>
            </p>
          </div>
        </div>

        <!-- 快速统计 -->
        <div class="quick-stats" v-if="analysisData.learning_overview">
          <div class="stat-card">
            <h4>平均得分率</h4>
            <p class="stat-value">
              {{ analysisData.learning_overview.average_score_rate }}
            </p>
            <p class="stat-note">基于错题分析</p>
          </div>
          <div class="stat-card">
            <h4>错题总数</h4>
            <p class="stat-value">
              {{ analysisData.learning_overview.wrong_question_count }}
            </p>
            <p class="stat-note">需要关注的错题</p>
          </div>
          <div class="stat-card">
            <h4>学习状态</h4>
            <p
              class="stat-value status-value"
              :class="
                getStatusClass(analysisData.learning_overview.learning_status)
              "
            >
              {{ analysisData.learning_overview.progress_level }}
            </p>
            <p class="stat-note">AI评估</p>
          </div>
        </div>

        <!-- 鼓励语 -->
        <div
          class="encouragement-section"
          v-if="analysisData.learning_overview"
        >
          <div class="encouragement-content">
            <div class="encouragement-icon">💪</div>
            <div class="encouragement-text">
              {{ analysisData.learning_overview.encouragement }}
            </div>
          </div>
        </div>

        <!-- AI学习分析 -->
        <h2 class="section-title">AI学习分析</h2>
        <div class="ai-analysis-section" v-if="analysisData.learning_analysis">
          <div class="analysis-content">
            <div class="analysis-item">
              <div class="analysis-icon">🔍</div>
              <div class="analysis-text">
                <h4 class="analysis-label">学习情况分析</h4>
                <p class="analysis-description">
                  {{ analysisData.learning_analysis.analysis_summary }}
                </p>
              </div>
            </div>

            <div class="analysis-item">
              <div class="analysis-icon">🎯</div>
              <div class="analysis-text">
                <h4 class="analysis-label">需要提升的方面</h4>
                <p class="analysis-description">
                  {{ analysisData.learning_analysis.improvement_areas }}
                </p>
              </div>
            </div>

            <div class="analysis-item">
              <div class="analysis-icon">📚</div>
              <div class="analysis-text">
                <h4 class="analysis-label">学习建议和方法</h4>
                <p class="analysis-description">
                  {{ analysisData.learning_analysis.learning_suggestions }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 错题列表 -->
        <h2 class="section-title">错题详情</h2>
        <div
          class="wrong-questions-section"
          v-if="
            analysisData.wrong_questions &&
            analysisData.wrong_questions.length > 0
          "
        >
          <div class="section-header">
            <span class="section-subtitle"
              >共{{ analysisData.wrong_questions.length }}道错题</span
            >
          </div>

          <div class="questions-container">
            <div
              class="question-item"
              v-for="(question, index) in analysisData.wrong_questions"
              :key="question.id"
            >
              <div class="question-header">
                <div class="question-info">
                  <h4 class="question-number">错题{{ index + 1 }}</h4>
                  <div class="score-display">
                    <span class="score-label">得分:</span>
                    <span class="score-value">{{ question.score.score }}</span>
                    <span class="score-divider">/</span>
                    <span class="score-max">{{
                      question.score.total_score
                    }}</span>
                    <span class="score-rate"
                      >(得分率: {{ calculateScoreRate(question) }})</span
                    >
                  </div>
                </div>
              </div>

              <!-- 问题内容 -->
              <div class="question-content">
                <p class="question-title">{{ question.title }}</p>
                <p class="question-description" v-if="question.description">
                  {{ question.description }}
                </p>

                <!-- 教师建议 -->
                <div
                  class="teacher-suggestion"
                  v-if="
                    question.suggestion && question.suggestion !== '暂无评语'
                  "
                >
                  <div class="suggestion-header">
                    <span class="suggestion-label">教师建议:</span>
                  </div>
                  <p class="suggestion-content">{{ question.suggestion }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="no-data-message">
          <p>目前没有错题记录，继续保持良好的学习状态！</p>
        </div>

        <!-- 学习建议 -->
        <h2 class="section-title">个性化学习建议</h2>
        <div
          class="recommendations-section"
          v-if="
            analysisData.self_recommendations &&
            analysisData.self_recommendations.length > 0
          "
        >
          <div class="recommendations-list">
            <div
              class="recommendation-item"
              v-for="(
                recommendation, index
              ) in analysisData.self_recommendations"
              :key="index"
            >
              <div class="recommendation-number">{{ index + 1 }}</div>
              <div class="recommendation-text">{{ recommendation }}</div>
            </div>
          </div>
        </div>
        <div v-else class="no-data-message">
          <p>暂无个性化学习建议</p>
        </div>

        <!-- 学习激励 -->
        <h2 class="section-title">学习激励</h2>
        <div class="motivation-section" v-if="analysisData.motivation">
          <div class="motivation-content">
            <div class="motivation-item">
              <div class="motivation-icon">💪</div>
              <div class="motivation-text">
                {{ analysisData.motivation.encouragement }}
              </div>
            </div>

            <div class="motivation-item">
              <div class="motivation-icon">💡</div>
              <div class="motivation-text">
                {{ analysisData.motivation.tip_of_the_day }}
              </div>
            </div>

            <div class="motivation-item">
              <div class="motivation-icon">🎯</div>
              <div class="motivation-text">
                {{ analysisData.motivation.next_goal }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <footer>
      <p>&copy; 2025 基于大模型的智能教学辅助系统. All Rights Reserved.</p>
    </footer>
  </div>
</template>

<script>
import { analyze_student_knowledge_s } from "@/http/api.js";

export default {
  name: "StudentWrongQuestions",
  data() {
    return {
      analysisData: {
        student_number: "",
        student_name: "",
        course_name: "",
        learning_overview: null,
        learning_analysis: null,
        wrong_questions: [],
        self_recommendations: [],
        motivation: null,
      },
      loading: true,
      error: null,
    };
  },
  mounted() {
    this.loadWrongAnalysis();
  },
  methods: {
    async loadWrongAnalysis() {
      this.loading = true;
      this.error = null;

      try {
        const studentNumber = JSON.parse(
          localStorage.getItem("userInfo")
        ).identifier;
        const courseId =
          this.$route.params.courseId ||
          localStorage.getItem("currentCourseId");

        if (!courseId) {
          this.$message.error("请先选择课程");
          this.goBack();
          return;
        }

        const params = {
          student_number: studentNumber,
          course_id: courseId,
        };

        const response = await analyze_student_knowledge_s(params);
        if (response.code === 200) {
          this.analysisData = response.data;
        } else {
          this.error = response.message || "加载错题分析失败";
        }
      } catch (error) {
        console.error("加载错题分析失败:", error);
        this.error = "加载错题分析失败，请重试";
      } finally {
        this.loading = false;
      }
    },

    calculateScoreRate(question) {
      try {
        const score = parseFloat(question.score.score);
        const total = parseFloat(question.score.total_score);
        if (total === 0) return "0%";
        const rate = ((score / total) * 100).toFixed(1);
        return `${rate}%`;
      } catch (error) {
        return "0%";
      }
    },

    getStatusClass(status) {
      const classMap = {
        good: "status-good",
        average: "status-normal",
        needs_improvement: "status-poor",
        excellent: "status-excellent",
      };
      return classMap[status] || "status-normal";
    },

    goBack() {
      this.$router.go(-1);
    },
  },
};
</script>

<style scoped>
/* ==================== 页面整体样式 ==================== */
.student-wrong-questions-container {
  font-family: "Arial", sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f5f5f5;
  color: #333;
}

header {
  background: linear-gradient(135deg, #001529, #003a70);
  color: white;
  padding: 20px 0;
  text-align: center;
  position: relative;
}

.back-to-home {
  position: absolute;
  cursor: pointer;
  top: 20px;
  left: 20px;
  color: white;
  text-decoration: none;
  padding: 5px 10px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  transition: all 0.3s ease;
}

.back-to-home:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

header h1 {
  margin: 0;
  padding: 0;
  font-size: 2em;
}

header p {
  margin: 10px 0 0 0;
  font-size: 1em;
  opacity: 0.9;
}

.analysis-note {
  margin-top: 10px;
  font-size: 0.85em;
  opacity: 0.7;
  font-style: italic;
}

.container {
  width: 85%;
  max-width: 1200px;
  margin: 20px auto;
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

/* ==================== 加载状态样式 ==================== */
.loading-container,
.error-container {
  text-align: center;
  padding: 40px 0;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 2s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-icon {
  background-color: #ff4d4f;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  margin: 0 auto 20px;
}

.action-button {
  background: #1890ff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.action-button:hover {
  background: #096dd9;
}

/* ==================== 通用区块样式 ==================== */
.section-title {
  color: #1890ff;
  border-bottom: 2px solid #1890ff;
  padding-bottom: 10px;
  margin-top: 30px;
  font-size: 1.5em;
}

.no-data-message {
  text-align: center;
  padding: 30px;
  color: #666;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px 0;
}

/* ==================== 学生信息卡片样式 ==================== */
.student-info-card {
  display: flex;
  align-items: center;
  background-color: #f0f8ff;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  border-left: 4px solid #1890ff;
}

.student-avatar {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5em;
  font-weight: bold;
  margin-right: 20px;
}

.student-details h3 {
  margin: 0 0 10px 0;
  color: #1890ff;
  font-size: 1.5em;
}

.student-details p {
  margin: 5px 0;
  color: #666;
}

.status-good {
  color: #52c41a;
  font-weight: bold;
}

.status-excellent {
  color: #1890ff;
  font-weight: bold;
}

.status-normal {
  color: #faad14;
  font-weight: bold;
}

.status-poor {
  color: #ff4d4f;
  font-weight: bold;
}

/* ==================== 快速统计样式 ==================== */
.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin: 25px 0;
}

.stat-card {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  border: 1px solid #e8e8e8;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

.stat-card h4 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 1em;
}

.stat-value {
  margin: 0;
  font-size: 1.8em;
  font-weight: bold;
  color: #1890ff;
}

.stat-value.status-value {
  font-size: 1.5em;
}

.stat-note {
  margin: 10px 0 0 0;
  color: #999;
  font-size: 0.85em;
}

/* ==================== 鼓励语样式 ==================== */
.encouragement-section {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 10px;
  padding: 20px;
  margin: 25px 0;
  color: white;
}

.encouragement-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.encouragement-icon {
  font-size: 3rem;
  opacity: 0.9;
}

.encouragement-text {
  flex: 1;
  font-size: 1.2rem;
  font-weight: 500;
  line-height: 1.5;
}

/* ==================== AI分析样式 ==================== */
.ai-analysis-section {
  margin: 25px 0;
  padding: 25px;
  background-color: #f8f9fa;
  border-radius: 10px;
}

.analysis-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.analysis-item {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: flex-start;
  gap: 15px;
  transition: transform 0.3s ease;
}

.analysis-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.analysis-icon {
  font-size: 1.5rem;
  min-width: 30px;
}

.analysis-text {
  flex: 1;
}

.analysis-label {
  color: #495057;
  margin: 0 0 10px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.analysis-description {
  color: #6c757d;
  line-height: 1.6;
  margin: 0;
}

/* ==================== 错题列表样式 ==================== */
.wrong-questions-section {
  margin: 25px 0;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.section-subtitle {
  color: #6c757d;
  font-size: 0.95rem;
}

.questions-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.question-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background-color: #fff;
  transition: all 0.3s ease;
  border-left: 4px solid #ff6b6b;
}

.question-item:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.question-info {
  flex: 1;
}

.question-number {
  color: #ff6b6b;
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.score-label {
  font-weight: 500;
  color: #666;
}

.score-value {
  font-weight: 700;
  color: #ff6b6b;
}

.score-divider {
  color: #999;
  margin: 0 2px;
}

.score-max {
  font-weight: 500;
  color: #666;
}

.score-rate {
  margin-left: 10px;
  padding: 2px 8px;
  background-color: #fff5f5;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #ff6b6b;
}

.question-content {
  margin-bottom: 10px;
}

.question-title {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #333;
  margin-bottom: 10px;
  font-weight: 500;
}

.question-description {
  font-size: 1rem;
  line-height: 1.6;
  color: #666;
  margin-bottom: 15px;
}

.teacher-suggestion {
  background-color: #fff9e6;
  border-left: 3px solid #ffcc00;
  padding: 12px;
  border-radius: 6px;
  margin-top: 15px;
}

.suggestion-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.suggestion-label {
  font-weight: 600;
  color: #e67e22;
}

.suggestion-content {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* ==================== 学习建议样式 ==================== */
.recommendations-section {
  margin: 25px 0;
  padding: 25px;
  background-color: #e8f5e9;
  border-radius: 10px;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  background-color: white;
  padding: 15px;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

.recommendation-item:hover {
  transform: translateX(5px);
}

.recommendation-number {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.recommendation-text {
  flex: 1;
  color: #333;
  line-height: 1.5;
  font-size: 1rem;
}

/* ==================== 学习激励样式 ==================== */
.motivation-section {
  margin: 25px 0 40px 0;
}

.motivation-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.motivation-item {
  display: flex;
  align-items: center;
  gap: 15px;
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
  transition: all 0.3s ease;
}

.motivation-item:hover {
  background-color: #f0f7ff;
  transform: translateY(-3px);
}

.motivation-icon {
  font-size: 1.8rem;
  min-width: 40px;
  text-align: center;
}

.motivation-text {
  flex: 1;
  color: #495057;
  line-height: 1.5;
  font-size: 1rem;
}

/* ==================== 页脚样式 ==================== */
footer {
  background-color: #001529;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 20px 0;
  margin-top: 30px;
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 768px) {
  .container {
    width: 95%;
    padding: 15px;
  }

  header h1 {
    font-size: 1.5em;
  }

  .student-info-card {
    flex-direction: column;
    text-align: center;
  }

  .student-avatar {
    margin-right: 0;
    margin-bottom: 15px;
  }

  .quick-stats {
    grid-template-columns: 1fr;
  }

  .analysis-content,
  .motivation-content {
    grid-template-columns: 1fr;
  }

  .encouragement-content {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }

  .encouragement-icon {
    font-size: 2.5rem;
  }

  .score-display {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }

  .score-rate {
    margin-left: 0;
  }
}
</style>
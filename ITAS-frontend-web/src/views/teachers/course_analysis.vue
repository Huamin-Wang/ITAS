<template>
  <div class="course_analysis-page">
    <header>
      <span
        @click="goBackAnalysisSelection(this.course_id)"
        class="back-to-home"
        >返回学生管理</span
      >
      <h1>学生个人学习分析</h1>
      <p>智能分析学生学习状况，助力个性化辅导</p>
      <div class="analysis-note">注：以下分析基于学生近期错题数据</div>
    </header>

    <div class="container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在分析学生近期错题数据...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">!</div>
        <p>{{ error }}</p>
        <button class="action-button" @click="fetchStudentAnalysis">
          重试
        </button>
      </div>

      <!-- 正常显示 -->
      <div v-else>
        <h2 class="section-title">学生基本信息</h2>

        <div class="student-info-card">
          <div class="student-avatar">
            {{ studentInfo.name?.charAt(0) || "无" }}
          </div>
          <div class="student-details">
            <h3>{{ studentInfo.name || "未获取到姓名" }}</h3>
            <p><strong>学号:</strong> {{ studentInfo.id || "无" }}</p>
            <p>
              <strong>班级:</strong>
              {{ studentInfo.class || "未获取到班级信息" }}
            </p>
            <p>
              <strong>学习状态:</strong>
              <span :class="statusClass">{{ getLearningStatusText }}</span>
            </p>
          </div>
        </div>

        <div class="quick-stats">
          <div class="stat-card">
            <h4>平均得分率</h4>
            <p class="stat-value">
              {{ analysisData.quick_stats?.average_score_rate || "无" }}
            </p>
            <p class="stat-note">基于近期错题分析</p>
          </div>
          <!-- <div class="stat-card">
            <h4>分析错题数</h4>
            <p class="stat-value">
              {{ analysisData.quick_stats?.wrong_question_count || 0 }}
            </p>
            <p class="stat-note">近期分析的错题数量</p>
          </div> -->
          <div class="stat-card">
            <h4>总得分</h4>
            <p class="stat-value">
              {{ getTotalScore() || "无" }}
            </p>
            <p class="stat-note">基于近期错题分析</p>
          </div>
        </div>

        <h2 class="section-title">学习概况</h2>
        <div class="summary-card">
          <p>
            {{ analysisData.summary || "暂无学习概况信息" }}
          </p>
        </div>

        <h2 class="section-title">得分分布分析</h2>
        <div class="score-distribution">
          <div class="distribution-header">
            <span>得分区间</span>
            <span>题目数</span>
            <span>占比</span>
          </div>
          <div
            class="distribution-item"
            v-if="
              analysisData.details?.score_distribution?.high_score !== undefined
            "
          >
            <div
              class="distribution-bar high-score"
              :style="{
                width: calculateWidth(
                  analysisData.details.score_distribution.high_score || 0
                ),
              }"
            ></div>
            <span>高分题 (得分率>70%)</span>
            <span class="count">{{
              analysisData.details.score_distribution.high_score || 0
            }}</span>
            <span class="percentage">{{
              calculatePercentage(
                analysisData.details.score_distribution.high_score || 0
              )
            }}</span>
          </div>
          <div
            class="distribution-item"
            v-if="
              analysisData.details?.score_distribution?.medium_score !==
              undefined
            "
          >
            <div
              class="distribution-bar medium-score"
              :style="{
                width: calculateWidth(
                  analysisData.details.score_distribution.medium_score || 0
                ),
              }"
            ></div>
            <span>中分题 (得分率40%-70%)</span>
            <span class="count">{{
              analysisData.details.score_distribution.medium_score || 0
            }}</span>
            <span class="percentage">{{
              calculatePercentage(
                analysisData.details.score_distribution.medium_score || 0
              )
            }}</span>
          </div>
          <div
            class="distribution-item"
            v-if="
              analysisData.details?.score_distribution?.low_score !== undefined
            "
          >
            <div
              class="distribution-bar low-score"
              :style="{
                width: calculateWidth(
                  analysisData.details.score_distribution.low_score || 0
                ),
              }"
            ></div>
            <span>低分题 (得分率<40%)</span>
            <span class="count">{{
              analysisData.details.score_distribution.low_score || 0
            }}</span>
            <span class="percentage">{{
              calculatePercentage(
                analysisData.details.score_distribution.low_score || 0
              )
            }}</span>
          </div>
          <div v-if="!analysisData.details?.score_distribution" class="no-data">
            暂无得分分布数据
          </div>
        </div>

        <h2 class="section-title">个性化学习分析</h2>

        <div class="grid-container">
          <div class="insight-card">
            <h3>学习问题分析</h3>
            <p>
              {{
                analysisData.analysis?.learning_problems || "暂无学习问题分析"
              }}
            </p>
            <div class="problem-tags" v-if="getFocusPoints().length > 0">
              <span
                class="tag weakness-tag"
                v-for="(focus, index) in getFocusPoints()"
                :key="index"
                >{{ focus }}</span
              >
            </div>
            <div v-else class="no-data">暂无重点知识点</div>
            <!-- <button
              class="action-button"
              @click="generateLearningMaterials"
            >
              生成专项练习
            </button> -->
            <button class="action-button" @click="generate_exercise()">
              生成专项练习
            </button>
          </div>

          <div class="insight-card">
            <h3>学习表现</h3>
            <ul class="behavior-list">
              <li>
                <span>学习状态</span>
                <span class="value" :class="statusClass">{{
                  getLearningStatusText
                }}</span>
              </li>
              <li>
                <span>平均得分率</span>
                <span class="value">{{
                  analysisData.quick_stats?.average_score_rate || "无"
                }}</span>
              </li>
              <li>
                <span>分析错题数</span>
                <span class="value">{{
                  analysisData.quick_stats?.wrong_question_count || 0
                }}</span>
              </li>
              <li>
                <span>分析题目数</span>
                <span class="value">{{ getTotalQuestions() || 0 }}</span>
              </li>
            </ul>
          </div>

          <div class="insight-card">
            <h3>重点知识点</h3>
            <p>基于错题分析需要重点关注的知识领域：</p>
            <div class="focus-points" v-if="getFocusPoints().length > 0">
              <span
                class="tag weakness-tag"
                v-for="(focus, index) in getFocusPoints()"
                :key="index"
                >{{ focus }}</span
              >
            </div>
            <div v-else class="no-data">暂无重点知识点</div>
            <!-- <button class="action-button" @click="adjustLearningPlan">
              调整学习计划
            </button> -->
          </div>
        </div>

        <h2 class="section-title">教学建议</h2>
        <div class="insight-card">
          <h3>智能教学建议</h3>
          <p>
            {{ analysisData.analysis?.teaching_suggestions || "暂无教学建议" }}
          </p>
          <ol
            v-if="
              analysisData.teacher_recommendations &&
              analysisData.teacher_recommendations.length > 0
            "
          >
            <li
              v-for="(
                recommendation, index
              ) in analysisData.teacher_recommendations"
              :key="index"
            >
              {{ recommendation }}
            </li>
          </ol>
          <div v-else class="no-data">暂无教学建议</div>
          <!-- <button class="action-button" @click="generateDetailedReport">
            生成详细报告
          </button> -->
        </div>
      </div>
      <div v-if="generatingExercise" class="global-loading-overlay">
        <div class="global-loading-container">
          <div class="global-loading-spinner"></div>
          <p>正在生成专项练习，请稍候...</p>
        </div>
      </div>
    </div>

    <!-- 新增：练习编辑弹窗 -->
    <div v-if="showExerciseDialog" class="exercise-dialog-overlay">
      <div class="exercise-dialog">
        <div class="dialog-header">
          <h3>编辑专项练习</h3>
          <button class="close-btn" @click="closeExerciseDialog">×</button>
        </div>
        <div class="dialog-body">
          <ExerciseEditor
            v-if="currentExerciseId"
            :mode="'edit'"
            :exerciseId="currentExerciseId"
            :courseId="course_id"
            @success="closeExerciseDialog"
            @cancel="closeExerciseDialog"
          />
          <div v-else class="loading-container">
            <div class="loading-spinner"></div>
            <p>正在加载练习...</p>
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
import { analyze_student_knowledge, generate_exercises } from "@/http/api.js";
import ExerciseEditor from "@/components/ExerciseEditor.vue";
export default {
  name: "student_analysis",
  components: {
    ExerciseEditor,
  },
  data() {
    return {
      loading: true,
      error: null,
      student_number: null,
      course_id: null,
      studentInfo: {
        name: "",
        id: "",
        class: "",
      },
      analysisData: {},
      showExerciseDialog: false,
      currentExerciseId: null,
      generatingExercise: false, //生成习题加载控制
    };
  },
  computed: {
    // 直接使用后端返回的学习状态
    statusClass() {
      const status =
        this.analysisData.quick_stats?.learning_status || "average";
      // 后端返回的状态是英文，我们直接映射到CSS类名
      if (status === "good" || status === "良好") return "status-good";
      if (status === "excellent" || status === "优秀")
        return "status-excellent";
      if (status === "needs_improvement" || status === "较差")
        return "status-poor";
      if (status === "average" || status === "一般") return "status-normal";
      return "status-normal";
    },
    // 获取学习状态的中文文本
    getLearningStatusText() {
      const status =
        this.analysisData.quick_stats?.learning_status || "average";
      // 将英文状态转换为中文显示
      const statusMap = {
        good: "良好",
        excellent: "优秀",
        needs_improvement: "待改进",
        average: "一般",
        良好: "良好",
        优秀: "优秀",
        较差: "待改进",
        一般: "一般",
      };
      return statusMap[status] || "一般";
    },
  },
  methods: {
    async fetchStudentAnalysis() {
      this.loading = true;
      this.error = null;

      try {
        const params = {
          student_number: this.student_number,
          course_id: this.course_id,
        };

        const result = await analyze_student_knowledge(params);
        if (result.code === 200 && result.data) {
          this.analysisData = result.data;

          // 获取学生基本信息
          this.studentInfo = {
            name: result.data.student_name || "未获取到姓名",
            id: this.student_number || "无",
            class: result.data.course_name || "未获取到班级信息",
          };
        } else {
          throw new Error(result.message || "获取数据失败");
        }
      } catch (err) {
        console.error("加载数据失败:", err);
        this.error = `加载学生分析数据失败: ${err.message}`;

        // API调用失败，清空所有数据
        this.analysisData = {};
        this.studentInfo = {
          name: "",
          id: this.student_number || "",
          class: "",
        };
      } finally {
        this.loading = false;
      }
    },

    getFocusPoints() {
      const focus = this.analysisData.analysis?.focus_areas;
      if (!focus || focus.trim() === "") return [];
      // 根据返回的数据格式进行调整
      if (focus.includes("、")) {
        return focus.split("、").map((item) => item.trim());
      } else if (focus.includes("，")) {
        return focus.split("，").map((item) => item.trim());
      } else if (focus.includes(",")) {
        return focus.split(",").map((item) => item.trim());
      } else {
        return [focus.trim()];
      }
    },

    calculateWidth(count) {
      // 计算条形图宽度，使用总分析题目数作为基准
      const totalQuestions = this.getTotalQuestions();
      if (totalQuestions === 0) return "0%";
      return `${(count / totalQuestions) * 100}%`;
    },

    calculatePercentage(count) {
      // 计算百分比
      const totalQuestions = this.getTotalQuestions();
      if (totalQuestions === 0) return "0%";
      return `${((count / totalQuestions) * 100).toFixed(1)}%`;
    },

    getTotalQuestions() {
      // 计算总分析题目数 = 低分题 + 中分题 + 高分题
      const distribution = this.analysisData.details?.score_distribution;
      if (!distribution) return 0;

      return (
        (distribution.low_score || 0) +
        (distribution.medium_score || 0) +
        (distribution.high_score || 0)
      );
    },

    getTotalScore() {
      // 从 overall_performance 中提取总得分
      const performance = this.analysisData.details?.overall_performance;
      if (!performance) return "无";

      // 解析格式：共完成10题，总分326.0，得分185.0
      const match = performance.match(/得分(\d+\.?\d*)/);
      return match ? match[1] : "无";
    },

    // 生成习题方法
    async generate_exercise() {
      // 设置生成练习的加载状态
      this.generatingExercise = true;

      try {
        const params = {
          student_number: this.student_number,
          course_id: this.course_id,
          teacher_id: JSON.parse(localStorage.getItem("userInfo")).user_id,
        };

        const response = await generate_exercises(params);

        if (response.code === 200) {
          // 获取生成的练习ID
          this.currentExerciseId = response.data.exercise_id;
          // 显示弹窗
          this.showExerciseDialog = true;
          this.$message.success("练习生成成功，请在弹窗中编辑");
        } else {
          this.$message.error("生成练习失败: " + response.message);
        }
      } catch (error) {
        console.error("生成练习失败:", error);
        this.$message.error("生成练习失败，请稍后重试");
      } finally {
        // 无论成功或失败，都结束加载状态
        this.generatingExercise = false;
      }
    },

    // generate_exercise() {
    //   this.currentExerciseId = 2;
    //   this.showExerciseDialog = true;
    // },

    // 弹窗相关方法
    closeExerciseDialog() {
      this.showExerciseDialog = false;
      this.currentExerciseId = null;
    },

    adjustLearningPlan() {
      alert("调整学习计划功能开发中...");
      // 实际实现中，这里会调整学生的学习计划
    },

    generateDetailedReport() {
      alert("生成详细报告功能开发中...");
      // 实际实现中，这里会生成详细的PDF报告
    },

    goBackAnalysisSelection(course_id) {
      this.$router.push(`/analysis_selection/${course_id}`);
    },
  },
  mounted() {
    // 从路由参数获取学生学号和课程ID
    this.student_number = this.$route.params.studentNumber || "";
    this.course_id = this.$route.params.courseId;

    // 加载学生分析数据
    this.fetchStudentAnalysis();
  },
};
</script>

<style scoped>
.course_analysis-page {
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

.container {
  width: 85%;
  margin: 20px auto;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

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

.section-title {
  color: #1890ff;
  border-bottom: 2px solid #1890ff;
  padding-bottom: 10px;
  margin-top: 25px;
}

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

.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin: 20px 0;
}

.stat-card {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  border: 1px solid #e8e8e8;
}

.stat-card h4 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 0.9em;
}

.stat-value {
  margin: 0;
  font-size: 1.5em;
  font-weight: bold;
  color: #1890ff;
}

.summary-card {
  background-color: #f0f8ff;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  border-left: 4px solid #1890ff;
}

.summary-card p {
  margin: 0;
  line-height: 1.6;
}

.score-distribution {
  margin: 20px 0;
}

.distribution-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  position: relative;
}

.distribution-bar {
  height: 30px;
  border-radius: 4px;
  margin-right: 15px;
  min-width: 20px;
}

.high-score {
  background-color: #52c41a;
}

.medium-score {
  background-color: #faad14;
}

.low-score {
  background-color: #ff4d4f;
}

.distribution-item span {
  margin-right: 10px;
}

.count {
  font-weight: bold;
  color: #1890ff;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.insight-card {
  background-color: #f9f9f9;
  border-left: 4px solid #1890ff;
  padding: 15px;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.insight-card h3 {
  margin-top: 0;
  color: #1890ff;
}

.behavior-list {
  margin-top: 15px;
  list-style-type: none;
  padding: 0;
}

.behavior-list li {
  background-color: #f0f8ff;
  margin-bottom: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
}

.behavior-list .value {
  font-weight: bold;
  color: #1890ff;
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

footer {
  background-color: #001529;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 20px 0;
  margin-top: 30px;
}

.tag {
  display: inline-block;
  padding: 3px 8px;
  background-color: #e6f7ff;
  color: #1890ff;
  border-radius: 3px;
  margin-right: 5px;
  font-size: 0.9em;
}

.weakness-tag {
  background-color: #fff2e8;
  color: #fa541c;
}

.problem-tags,
.focus-points {
  margin: 10px 0;
}

/* 弹窗样式 */
.exercise-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.exercise-dialog {
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: #001529;
  color: white;
}

.dialog-header h3 {
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.8rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.dialog-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .exercise-dialog {
    width: 95%;
    height: 95vh;
  }
}

/* 全局加载遮罩样式 */
.global-loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.global-loading-container {
  background-color: white;
  padding: 40px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  min-width: 300px;
}

.global-loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}
</style>
<template>
  <div class="student-exercise-container">
    <!-- 自动批改提示遮罩 -->
    <div v-if="isAutoGrading" class="global-loading-overlay">
      <div class="global-loading-container">
        <div class="global-loading-spinner"></div>
        <p>正在自动批改中，请稍候...</p>
      </div>
    </div>

    <!-- 头部区域 -->
    <div class="exercise-header">
      <div class="header-content">
        <h2 class="exercise-title">{{ exercise.title }}</h2>
        <div v-if="hasGradingResults" class="total-score-display">
          <span class="score-label">总分:</span>
          <span class="score-value">{{ calculateTotalScore() }}</span>
          <span class="score-divider">/</span>
          <span class="score-max">{{ calculateMaxScore() }}</span>
        </div>
      </div>

      <div class="exercise-details">
        <div class="detail-item">
          <span class="detail-label">描述:</span>
          <span class="detail-content">{{ exercise.description }}</span>
        </div>
      </div>
    </div>

    <!-- 题目列表 -->
    <div
      class="questions-container"
      :class="{ 'grading-disabled': isAutoGrading }"
    >
      <div
        class="question-item"
        v-for="(question, index) in questions"
        :key="question.id"
        :class="{ graded: question.gradingResult }"
      >
        <div class="question-header">
          <div class="question-info">
            <h3 class="question-number">第{{ index + 1 }}题</h3>
            <span class="question-points">（{{ question.points }}分）</span>
          </div>

          <!-- 批改结果 -->
          <div v-if="question.gradingResult" class="grading-result-badge">
            <div class="score-display">
              得分：<span class="score-value">{{
                question.gradingResult.score
              }}</span>
              / {{ question.gradingResult.total_score }}
            </div>
          </div>
        </div>

        <!-- 问题内容 -->
        <div class="question-content">
          <p class="question-text">{{ question.question_text }}</p>

          <!-- 单选题 -->
          <div
            v-if="question.question_type === 'single_choice'"
            class="question-options"
          >
            <label
              class="option"
              v-for="(opt, optIndex) in question.options"
              :key="optIndex"
              :class="{
                'selected-option':
                  question.student_answer ===
                  String.fromCharCode(65 + optIndex),
                'correct-option':
                  question.gradingResult &&
                  question.gradingResult.reference_answer ===
                    String.fromCharCode(65 + optIndex),
                'incorrect-option':
                  question.gradingResult &&
                  question.student_answer ===
                    String.fromCharCode(65 + optIndex) &&
                  question.gradingResult.reference_answer !==
                    String.fromCharCode(65 + optIndex),
              }"
            >
              <input
                type="radio"
                :name="'q' + question.id"
                :value="String.fromCharCode(65 + optIndex)"
                v-model="question.student_answer"
                :disabled="question.gradingResult || isAutoGrading"
              />
              <span class="option-letter"
                >{{ String.fromCharCode(65 + optIndex) }}.</span
              >
              <span class="option-text">{{ opt }}</span>
            </label>
          </div>

          <!-- 多选题 -->
          <div
            v-else-if="question.question_type === 'multiple_choice'"
            class="question-options"
          >
            <label
              class="option"
              v-for="(opt, optIndex) in question.options"
              :key="optIndex"
              :class="{
                'selected-option':
                  question.student_answer &&
                  question.student_answer.includes(
                    String.fromCharCode(65 + optIndex)
                  ),
                'correct-option':
                  question.gradingResult &&
                  question.gradingResult.reference_answer &&
                  question.gradingResult.reference_answer.includes(
                    String.fromCharCode(65 + optIndex)
                  ),
                'incorrect-option':
                  question.gradingResult &&
                  question.student_answer &&
                  question.student_answer.includes(
                    String.fromCharCode(65 + optIndex)
                  ) &&
                  (!question.gradingResult.reference_answer ||
                    !question.gradingResult.reference_answer.includes(
                      String.fromCharCode(65 + optIndex)
                    )),
              }"
            >
              <input
                type="checkbox"
                :value="String.fromCharCode(65 + optIndex)"
                v-model="question.student_answer"
                :disabled="question.gradingResult || isAutoGrading"
              />
              <span class="option-letter"
                >{{ String.fromCharCode(65 + optIndex) }}.</span
              >
              <span class="option-text">{{ opt }}</span>
            </label>
          </div>

          <!-- 判断题 -->
          <div
            v-else-if="question.question_type === 'true_false'"
            class="question-options"
          >
            <label
              class="option"
              :class="{
                'selected-option': question.student_answer === 'true',
                'correct-option':
                  question.gradingResult &&
                  question.gradingResult.reference_answer === 'true',
                'incorrect-option':
                  question.gradingResult &&
                  question.student_answer === 'true' &&
                  question.gradingResult.reference_answer !== 'true',
              }"
            >
              <input
                type="radio"
                :name="'q' + question.id"
                value="true"
                v-model="question.student_answer"
                :disabled="question.gradingResult || isAutoGrading"
              />
              <span class="option-text">正确</span>
            </label>
            <label
              class="option"
              :class="{
                'selected-option': question.student_answer === 'false',
                'correct-option':
                  question.gradingResult &&
                  question.gradingResult.reference_answer === 'false',
                'incorrect-option':
                  question.gradingResult &&
                  question.student_answer === 'false' &&
                  question.gradingResult.reference_answer !== 'false',
              }"
            >
              <input
                type="radio"
                :name="'q' + question.id"
                value="false"
                v-model="question.student_answer"
                :disabled="question.gradingResult || isAutoGrading"
              />
              <span class="option-text">错误</span>
            </label>
          </div>

          <!-- 简答题 -->
          <div
            v-else-if="question.question_type === 'short_answer'"
            class="question-options"
          >
            <textarea
              class="short-answer"
              :class="{
                'graded-answer': question.gradingResult,
                'ungraded-answer': !question.gradingResult,
              }"
              placeholder="请输入你的回答..."
              v-model="question.student_answer"
              :disabled="question.gradingResult || isAutoGrading"
              :readonly="question.gradingResult"
              rows="4"
            ></textarea>
          </div>
        </div>

        <!-- 批改详情 -->
        <div v-if="question.gradingResult" class="grading-details">
          <h4 class="details-title">批改详情</h4>
          <div class="details-content">
            <div class="detail-row">
              <span class="detail-label">学生答案:</span>
              <span class="detail-value student-answer">
                {{
                  formatStudentAnswer(
                    question.student_answer,
                    question.question_type
                  )
                }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">参考答案:</span>
              <span class="detail-value reference-answer">
                {{
                  formatReferenceAnswer(
                    question.gradingResult.reference_answer,
                    question.question_type
                  )
                }}
              </span>
            </div>
            <div v-if="question.gradingResult.comment" class="detail-row">
              <span class="detail-label">教师评语:</span>
              <span class="detail-value teacher-comment">
                {{ question.gradingResult.comment }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">批改时间:</span>
              <span class="detail-value grading-time">
                {{ formatDateTime(question.gradingResult.grading_time) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作区域 -->
    <div class="exercise-footer">
      <button
        class="btn btn-submit"
        @click="submitExercise"
        :disabled="isAutoGrading"
      >
        {{ isAutoGrading ? "正在批改中..." : "提交习题" }}
      </button>
      <button class="btn btn-back" @click="goBack" :disabled="isAutoGrading">
        返回
      </button>
    </div>
  </div>
</template>

<script>
import {
  get_exercise_questions,
  submit_exercise,
  get_exercise_response,
  get_grading_results_e,
} from "@/http/api.js";

export default {
  name: "StudentExerciseDetail",
  data() {
    return {
      exercise: {},
      questions: [],
      gradingResults: [],
      isAutoGrading: false, // 新增：自动批改状态
    };
  },
  computed: {
    hasGradingResults() {
      return this.gradingResults && this.gradingResults.length > 0;
    },
  },
  mounted() {
    this.loadExerciseData();
  },
  methods: {
    async loadExerciseData() {
      try {
        const exerciseId = this.$route.params.exerciseId;
        const studentNumber = JSON.parse(
          localStorage.getItem("userInfo")
        ).identifier;

        // 1. 获取题目数据
        const exerciseRes = await get_exercise_questions(exerciseId);
        this.exercise = exerciseRes.data.exercise;

        // 初始化 questions
        this.questions = exerciseRes.data.questions.map((q) => ({
          ...q,
          student_answer:
            q.question_type === "multiple_choice"
              ? [] // 多选题必须是数组
              : "", // 单选、判断、简答是字符串
          gradingResult: null, // 初始化为null
        }));

        // 2. 尝试获取学生已有的答案数据
        try {
          const params = {
            exercise_id: exerciseId,
            student_number: studentNumber,
          };
          const responseRes = await get_exercise_response(params);

          if (responseRes.data && responseRes.data.length > 0) {
            // 有答案数据，填充到 questions 中
            this.fillStudentAnswers(responseRes.data);
          }
        } catch (error) {
          console.log("未找到学生的答案数据，使用初始状态");
          // 如果没有答案数据，保持初始状态
        }

        // 3. 获取批改结果
        await this.loadGradingResults(exerciseId, studentNumber);
      } catch (error) {
        this.$message.error("加载习题失败");
        console.error("加载习题失败:", error);
      }
    },

    // 加载批改结果
    async loadGradingResults(exerciseId, studentNumber) {
      try {
        const params = {
          exercise_id: exerciseId,
          student_number: studentNumber,
        };
        const gradingRes = await get_grading_results_e(params);

        if (gradingRes.code === 200 && gradingRes.data.length > 0) {
          this.gradingResults = gradingRes.data;

          // 将批改结果与题目关联
          this.associateGradingResults();
        }
      } catch (error) {
        console.log("未找到批改结果或批改未完成");
      }
    },

    // 将批改结果关联到对应题目
    associateGradingResults() {
      this.questions.forEach((question) => {
        const gradingResult = this.gradingResults.find(
          (result) => result.question_id === question.id
        );

        if (gradingResult) {
          question.gradingResult = gradingResult;

          // 对于多选题，需要将学生答案转换为数组
          if (
            question.question_type === "multiple_choice" &&
            gradingResult.student_answer
          ) {
            question.student_answer = gradingResult.student_answer
              .split(",")
              .map((item) => item.trim());
          } else {
            question.student_answer = gradingResult.student_answer || "";
          }
        }
      });
    },

    // 填充学生答案数据
    fillStudentAnswers(responseData) {
      responseData.forEach((responseItem) => {
        const question = this.questions.find(
          (q) => q.id === responseItem.question_id
        );

        if (question) {
          // 根据题目类型处理答案数据
          if (question.question_type === "multiple_choice") {
            // 多选题：将逗号分隔的字符串转换为数组
            question.student_answer = responseItem.response
              ? responseItem.response.split(",").map((item) => item.trim())
              : [];
          } else {
            // 其他类型：直接使用字符串
            question.student_answer = responseItem.response || "";
          }
        }
      });
    },

    // 格式化参考答案显示
    formatReferenceAnswer(referenceAnswer, questionType) {
      if (!referenceAnswer) return "无";

      if (questionType === "multiple_choice" && referenceAnswer.includes(",")) {
        return referenceAnswer
          .split(",")
          .map((item) => item.trim())
          .join(", ");
      }

      return referenceAnswer;
    },

    // 格式化学生答案显示
    formatStudentAnswer(studentAnswer, questionType) {
      if (
        !studentAnswer ||
        (Array.isArray(studentAnswer) && studentAnswer.length === 0)
      ) {
        return "未回答";
      }

      if (questionType === "multiple_choice" && Array.isArray(studentAnswer)) {
        return studentAnswer.join(", ");
      }

      return studentAnswer;
    },

    // 计算总得分
    calculateTotalScore() {
      return this.questions.reduce((total, question) => {
        if (question.gradingResult) {
          return total + parseFloat(question.gradingResult.score);
        }
        return total;
      }, 0);
    },

    // 计算满分
    calculateMaxScore() {
      return this.questions.reduce((total, question) => {
        if (question.gradingResult) {
          return total + parseFloat(question.gradingResult.total_score);
        }
        return total + parseFloat(question.points || 0);
      }, 0);
    },

    submitExercise() {
      if (!this.questions || this.questions.length === 0) {
        this.$message.error("没有题目可提交");
        return;
      }

      // 检查是否有未回答的题目
      const hasUnanswered = this.questions.some((q) => {
        if (q.question_type === "multiple_choice") {
          return !q.student_answer || q.student_answer.length === 0;
        } else {
          return !q.student_answer || q.student_answer.trim() === "";
        }
      });

      if (hasUnanswered) {
        this.$message.warning("还有未回答的题目，请完成所有题目后再提交");
        return;
      }

      const submitData = this.questions.map((q) => {
        let finalAnswer;

        if (Array.isArray(q.student_answer)) {
          // 多选题 → 转成字符串 "A,B"
          finalAnswer = q.student_answer.join(",");
        } else {
          // 单选/判断/简答 → 保持字符串即可
          finalAnswer = q.student_answer;
        }

        return {
          exercise_id: q.exercise_id,
          question_id: q.id,
          student_answer: finalAnswer,
          student_number: JSON.parse(localStorage.getItem("userInfo"))
            .identifier,
        };
      });

      console.log("最终提交：", submitData);

      // 开始自动批改
      this.isAutoGrading = true;
      this.$message.info("正在自动批改中，请稍候...");

      submit_exercise(submitData)
        .then(() => {
          this.$message.success("提交成功！自动批改完成");
          // 重新加载数据以获取批改结果
          return this.loadExerciseData();
        })
        .catch((error) => {
          this.$message.error("提交失败：" + (error.message || "请重试"));
          console.error("提交失败:", error);
        })
        .finally(() => {
          // 无论成功失败，都结束批改状态
          this.isAutoGrading = false;
        });
    },

    formatDateTime(isoString) {
      if (!isoString) return "";
      return isoString.slice(0, 16).replace("T", " ");
    },

    goBack() {
      // 返回习题合集页面
      this.$router.push(`/student_exercise/${this.$route.params.courseId}`);
    },
  },
};
</script>

<style scoped>
/* ==================== 自动批改遮罩样式 ==================== */
/* ==================== 全局加载遮罩样式 ==================== */
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

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 批改过程中禁用交互 */
.grading-disabled {
  opacity: 0.6;
  pointer-events: none;
}

/* ==================== 整体布局样式 ==================== */
.student-exercise-container {
  width: 100%;
  position: relative;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 25px;
}

/* ==================== 头部样式 ==================== */
.exercise-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.exercise-title {
  color: #2c3e50;
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
}

.total-score-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
  border-radius: 8px;
  border: 1px solid #b7eb8f;
}

.score-label {
  font-weight: 500;
  color: #389e0d;
}

.score-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: #389e0d;
}

.score-divider {
  color: #999;
  margin: 0 2px;
}

.score-max {
  font-weight: 500;
  color: #666;
}

.exercise-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.detail-label {
  min-width: 70px;
  font-weight: 500;
  color: #666;
}

.detail-content {
  color: #333;
  flex: 1;
}

/* ==================== 问题列表样式 ==================== */
.questions-container {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.question-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 25px;
  transition: all 0.3s ease;
  background-color: #fff;
}

.question-item.graded {
  border-left: 4px solid #2ecc71;
  background-color: rgba(46, 204, 113, 0.03);
}

/* ==================== 问题头部样式 ==================== */
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.question-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.question-number {
  color: #3498db;
  margin: 0;
  font-size: 1.2rem;
}

.question-points {
  color: #e67e22;
  font-weight: 500;
}

.grading-result-badge {
  padding: 8px 16px;
  background-color: #2ecc71;
  color: white;
  border-radius: 20px;
  font-weight: 500;
}

.score-display {
  font-size: 0.95rem;
}

.score-display .score-value {
  font-size: 1.1rem;
  color: white;
}

/* ==================== 问题内容样式 ==================== */
.question-content {
  margin-bottom: 20px;
}

.question-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #333;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

/* ==================== 选项样式 ==================== */
.question-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background-color: #fafafa;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 48px;
}

.option:hover {
  background-color: #f5f5f5;
  border-color: #3498db;
}

.option.selected-option {
  background-color: #e3f2fd;
  border-color: #2196f3;
}

.option.correct-option {
  background-color: #e8f5e9;
  border-color: #4caf50;
}

.option.incorrect-option {
  background-color: #ffebee;
  border-color: #f44336;
}

.option input[type="radio"],
.option input[type="checkbox"] {
  margin-right: 12px;
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #3498db;
}

.option input[type="radio"]:disabled,
.option input[type="checkbox"]:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.option-letter {
  font-weight: 600;
  color: #555;
  min-width: 24px;
  margin-right: 8px;
}

.option-text {
  color: #333;
  font-size: 1rem;
}

/* ==================== 简答题样式 ==================== */
.short-answer {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.5;
  resize: vertical;
  transition: all 0.3s ease;
}

.short-answer.ungraded-answer {
  background-color: #fff;
  border-color: #ddd;
}

.short-answer.ungraded-answer:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  outline: none;
}

.short-answer.graded-answer {
  background-color: #f6ffed;
  border-color: #b7eb8f;
  color: #333;
}

.short-answer:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.7;
}

/* ==================== 批改详情样式 ==================== */
.grading-details {
  margin-top: 25px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.details-title {
  color: #2c3e50;
  margin: 0 0 15px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.detail-label {
  min-width: 80px;
  font-weight: 500;
  color: #666;
}

.detail-value {
  flex: 1;
  color: #333;
  line-height: 1.5;
}

.student-answer {
  color: #1890ff;
  background-color: #fff9e6;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #ffcc00;
}

.reference-answer {
  color: #52c41a;
  background-color: #e8f5e9;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #4caf50;
}

.teacher-comment {
  color: #666;
  font-style: italic;
  background-color: #f0f7ff;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #3498db;
}

.grading-time {
  color: #999;
  font-size: 0.9rem;
}

/* ==================== 底部样式 ==================== */
.exercise-footer {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
  padding-top: 25px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 12px 32px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-submit {
  background-color: #3498db;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-submit:disabled {
  background-color: #a0d2ff;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-back {
  background-color: #95a5a6;
  color: white;
}

.btn-back:hover:not(:disabled) {
  background-color: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

.btn-back:disabled {
  background-color: #c8d6d9;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .student-exercise-container {
    padding: 15px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .question-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .grading-result-badge {
    align-self: flex-start;
  }

  .detail-row {
    flex-direction: column;
    gap: 5px;
  }

  .detail-label {
    min-width: auto;
  }

  .exercise-footer {
    flex-direction: column;
    gap: 10px;
  }

  .btn {
    width: 100%;
  }
}
</style>
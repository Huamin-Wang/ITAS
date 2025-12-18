<template>
  <div class="grading-component">
    <div class="grading-header">
      <h3>题目批改</h3>
      <div class="grading-stats">
        <span class="stat-item">总分: {{ totalScore }}</span>
        <span class="stat-item"
          >已批改: {{ gradedCount }}/{{ totalQuestions }}</span
        >
        <button class="btn-auto-grade" @click="showAutoGradeDialog">
          自动批改全部题目
        </button>
      </div>
    </div>

    <!-- 自动批改弹窗 -->
    <div
      v-if="showAutoGradeModal"
      class="modal-overlay"
      @click="closeAutoGradeModal"
    >
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h4>自动批改设置</h4>
          <button class="modal-close" @click="closeAutoGradeModal">
            &times;
          </button>
        </div>
        <div class="modal-body">
          <div class="modal-intro">
            <p class="intro-main">请选择要自动批改的题目类型:</p>
            <p class="intro-hint">
              <span class="hint-icon">💡</span>
              客观题默认批改完成，此处选中客观题，可自动添加评语
            </p>
          </div>
          <div class="question-type-options">
            <label class="option-item">
              <input
                type="checkbox"
                v-model="autoGradeOptions.objective"
                :checked="autoGradeOptions.objective"
              />
              <span class="option-text">客观题（单选题、多选题、判断题）</span>
            </label>
            <label class="option-item">
              <input
                type="checkbox"
                v-model="autoGradeOptions.subjective"
                :checked="autoGradeOptions.subjective"
                disabled
              />
              <span class="option-text">主观题（简答题）</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeAutoGradeModal">取消</button>
          <button class="btn-confirm" @click="confirmAutoGrade">确定</button>
        </div>
      </div>
    </div>

    <div class="questions-container">
      <div
        v-for="(item, index) in localQuizData"
        :key="item.id"
        class="question-item"
        :class="{ graded: item.graded }"
      >
        <div class="question-header">
          <h4>第{{ index + 1 }}题 ({{ item.question.points }}分)</h4>
          <span class="question-type">{{
            formatQuestionType(item.question.question_type)
          }}</span>
        </div>

        <div class="question-content">
          <p>{{ item.question.question_text }}</p>
          <!-- 显示选择题选项 -->
          <div
            v-if="
              item.question.question_type === 'single_choice' ||
              item.question.question_type === 'multiple_choice'
            "
            class="options"
          >
            <div
              v-for="(option, optIndex) in item.question.options"
              :key="optIndex"
              class="option"
            >
              {{ String.fromCharCode(65 + optIndex) }}. {{ option }}
            </div>
          </div>
          <!-- 显示判断题选项 -->
          <div
            v-if="item.question.question_type === 'true_false'"
            class="options"
          >
            <div class="option">A. 正确</div>
            <div class="option">B. 错误</div>
          </div>
        </div>

        <div class="student-answer-section">
          <h5>学生答案:</h5>
          <div class="student-answer">
            <!-- 根据题目类型格式化显示答案 -->
            <div v-if="item.question.question_type === 'single_choice'">
              {{ formatChoiceAnswer(item.response, item.question.options) }}
            </div>
            <div v-else-if="item.question.question_type === 'multiple_choice'">
              {{ formatChoiceAnswer(item.response, item.question.options) }}
            </div>
            <div v-else-if="item.question.question_type === 'true_false'">
              {{ item.response === "true" ? "正确" : "错误" }}
            </div>
            <div v-else>
              {{ item.response }}
            </div>
          </div>
          <!-- 显示正确答案 -->
          <div class="correct-answer">
            <h5>正确答案:</h5>
            <div class="correct-answer-content">
              <div
                v-if="
                  item.question.question_type === 'single_choice' ||
                  item.question.question_type === 'multiple_choice'
                "
              >
                {{
                  formatChoiceAnswer(
                    item.question.correct_answer,
                    item.question.options
                  )
                }}
              </div>
              <div v-else-if="item.question.question_type === 'true_false'">
                {{ item.question.correct_answer === "true" ? "正确" : "错误" }}
              </div>
              <div v-else>
                {{
                  item.question.correct_answer
                    ? item.question.correct_answer
                    : "暂无正确答案"
                }}
              </div>
            </div>
          </div>
        </div>

        <div class="grading-section">
          <h5>批改:</h5>
          <div class="grading-actions">
            <div class="score-input">
              <label for="score">得分:</label>
              <input
                type="number"
                :min="0"
                :max="item.question.points"
                v-model.number="item.assignedScore"
                @change="updateGradingStatus(item)"
                :disabled="autoGrade && item.autoGraded"
              />
              <span>/ {{ item.question.points }}</span>
              <!-- 自动批改标记 -->
              <span v-if="item.autoGraded" class="auto-grade-tag"
                >(自动批改)</span
              >
            </div>

            <div class="feedback-section">
              <label for="feedback">评语:</label>
              <textarea
                v-model="item.feedback"
                placeholder="请输入评语..."
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="grading-footer">
      <button class="btn-grading-complete" @click="completeGrading">
        完成批改
      </button>
    </div>
  </div>
</template>

<script>
import {
  get_quiz_response,
  batch_score_assignments,
  add_grading_results,
  get_grading_results,
} from "@/http/api.js";
import { ElLoading, ElMessage } from "element-plus";

export default {
  name: "Grading",
  props: {
    quiz_id: {
      type: Number,
      required: true,
    },
    student_number: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      localQuizData: [],
      autoGrade: true,
      showAutoGradeModal: false, // 控制弹窗显示
      autoGradeOptions: {
        objective: false, // 客观题
        subjective: true, // 主观题，默认选中
      },
    };
  },
  computed: {
    totalQuestions() {
      return this.localQuizData.length;
    },
    gradedCount() {
      return this.localQuizData.filter((q) => q.graded).length;
    },
    totalScore() {
      return this.localQuizData.reduce(
        (sum, q) => sum + (q.assignedScore || 0),
        0
      );
    },
  },
  methods: {
    //初始化批改数据
    init_quiz_data() {
      const params = {
        quiz_id: this.quiz_id,
        student_number: this.student_number,
      };

      // 使用 Promise.all 并行获取答题数据和批改结果
      Promise.all([get_quiz_response(params), get_grading_results(params)])
        .then(([responseResponse, gradingResponse]) => {
          // 获取学生答题数据
          const data = responseResponse.data;

          // 初始化本地数据
          this.localQuizData = data.map((item) => ({
            ...item,
            assignedScore: null,
            feedback: "",
            graded: false,
            autoGraded: false,
          }));

          // 如果有批改结果，合并到本地数据中
          if (gradingResponse.code === 200 && gradingResponse.data) {
            const gradingResults = gradingResponse.data;

            gradingResults.forEach((result) => {
              const targetQuestion = this.localQuizData.find(
                (q) => q.question_id === result.question_id
              );

              if (targetQuestion) {
                // 更新批改信息
                targetQuestion.assignedScore = Number(result.score) || 0;
                targetQuestion.feedback = result.comment || "";
                targetQuestion.graded = true;
                targetQuestion.autoGraded = result.auto_graded || false; // 根据后端返回判断是否为自动批改
              }
            });
          }

          // 初始化后自动批改未批改的客观题
          if (this.autoGrade) {
            this.autoGradeObj();
          }
        })
        .catch((error) => {
          console.error("初始化数据失败:", error);
          ElMessage.error("获取数据失败，请重试");
        });
    },

    // 格式化题目类型
    formatQuestionType(type) {
      const typeMap = {
        single_choice: "单选题",
        multiple_choice: "多选题",
        true_false: "判断题",
        short_answer: "简答题",
      };
      return typeMap[type] || type;
    },

    // 格式化选择题答案
    formatChoiceAnswer(answer, options) {
      if (!answer) return "未作答";

      // 分割多选题答案（如"A,B" -> ["A", "B"]）
      const answerLetters = answer.split(",").map((a) => a.trim());

      return answerLetters
        .map((letter) => {
          const index = letter.charCodeAt(0) - 65; // A->0, B->1, etc.
          if (options && options[index] !== undefined) {
            return `${letter}. ${options[index]}`;
          }
          return letter;
        })
        .join("，");
    },

    // 更新批改状态
    updateGradingStatus(question) {
      if (question.assignedScore !== null && question.assignedScore !== "") {
        question.graded = true;
      } else {
        question.graded = false;
      }
    },

    // 自动批改客观题
    autoGradeObj() {
      this.localQuizData.forEach((item) => {
        if (!item.graded && !item.autoGraded) {
          if (item.question.question_type === "short_answer") {
            // 简答题需要手动批改，跳过
            return;
          }

          // 自动判断对错
          if (item.response === item.question.correct_answer) {
            item.assignedScore = item.question.points;
          } else {
            item.assignedScore = 0;
          }

          item.autoGraded = true;
          item.graded = true;
          item.feedback = "";
        }
      });
    },

    // 完成批改
    completeGrading() {
      // 检查是否所有题目都已批改
      const ungraded = this.localQuizData.filter((q) => !q.graded);
      if (ungraded.length > 0) {
        alert(`还有${ungraded.length}道题目未批改`);
        return;
      }

      // 准备批量提交的数据，使用grading_list字段

      const grading_list = this.localQuizData.map((item) => {
        console.log(item);

        const question = item.question || {};
        return {
          quiz_id: this.quiz_id,
          question_id: item.question_id,
          student_number: this.student_number,
          title: question.question_text || "",
          description: question.question_text || "",
          student_answer: item.response || "",
          reference_answer: question.correct_answer || "",
          total_score: question.points || 0,
          score: item.assignedScore || 0,
          comment: item.feedback || "",
          status: "completed",
        };
      });

      const submitData = {
        grading_list: grading_list,
      };

      add_grading_results(submitData)
        .then((response) => {
          if (response.code === 200) {
            ElMessage.success(
              `批改完成！已成功保存${grading_list.length}条记录，总分：${this.totalScore}`
            );
            this.$emit("grading-completed", {
              totalScore: this.totalScore,
              gradedCount: this.gradedCount,
            });
          } else {
            ElMessage.error(response.message || "批改结果保存失败");
          }
        })
        .catch((error) => {
          console.error("批量提交批改结果失败:", error);
          ElMessage.error("批量提交失败，请重试");
        })
        .finally(() => {
          loading.close();
        });
    },

    // 显示自动批改弹窗
    showAutoGradeDialog() {
      // 重置选项：客观题不选，主观题默认选中
      this.autoGradeOptions = {
        objective: false,
        subjective: true,
      };
      this.showAutoGradeModal = true;
    },

    // 关闭自动批改弹窗
    closeAutoGradeModal() {
      this.showAutoGradeModal = false;
    },

    // 确认自动批改
    confirmAutoGrade() {
      this.showAutoGradeModal = false;

      // 主观题是必选的，所以至少会有主观题
      const assignments_list = this.localQuizData
        .filter((item) => {
          const questionType = item.question.question_type;

          if (this.autoGradeOptions.objective) {
            return true;
          }

          // 如果未选择客观题，只包括主观题
          return questionType === "short_answer";
        })
        .map((item) => {
          const question = item.question || {};
          return {
            quiz_id: item.quiz_id,
            question_id: item.question_id,
            title: question.question_text || "",
            description: question.question_text || "",
            student_answer: item.response || "",
            reference_answer: question.correct_answer || "",
            total_score: question.points || 0,
          };
        });

      // 准备请求参数
      const requestData = {
        assignments_list: assignments_list,
      };

      const loading = ElLoading.service({
        lock: true,
        text: "正在进行自动批改，请稍候…",
        background: "rgba(0, 0, 0, 0.5)",
      });

      batch_score_assignments(requestData)
        .then((res) => {
          if (res.code !== 200) {
            ElMessage.error(res.message || "自动批改失败");
            return;
          }

          const results = res.data?.results || [];

          results.forEach((r) => {
            const target = this.localQuizData.find(
              (q) => q.question_id === r.question_id
            );

            if (target) {
              target.assignedScore = Number(r.score);
              target.feedback = r.comment;
              target.graded = true;
              target.autoGraded = true;
            }
          });

          // 更新批改统计
          const gradedCount = results.length;
          ElMessage.success(`自动批改完成，共批改${gradedCount}道题目`);
        })
        .catch((err) => {
          console.error(err);
          ElMessage.error("自动批改请求失败");
        })
        .finally(() => {
          loading.close();
        });
    },
  },
  mounted() {
    this.init_quiz_data();
  },
};
</script>

<style scoped>
/* ==================== 整体布局样式 ==================== */
.grading-component {
  width: 100%;
  position: relative;
}

/* ==================== 头部样式 ==================== */
.grading-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.grading-header h3 {
  color: #2c3e50;
  margin: 0;
}

.grading-stats {
  display: flex;
  gap: 20px;
  align-items: center;
}

.stat-item {
  padding: 8px 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-weight: 500;
  color: #555;
}

.btn-auto-grade {
  padding: 8px 16px;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-auto-grade:hover {
  background-color: #27ae60;
  transform: translateY(-2px);
}

/* ==================== 弹窗样式 ==================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 460px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  background-color: #f8f9fa;
}

.modal-header h4 {
  margin: 0;
  color: #2c3e50;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: #666;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
  background-color: #f8f9fa;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel {
  background-color: #f8f9fa;
  color: #666;
  border: 1px solid #ddd;
}

.btn-cancel:hover {
  background-color: #e9ecef;
}

.btn-confirm {
  background-color: #3498db;
  color: white;
}

.btn-confirm:hover {
  background-color: #2980b9;
}

/* ==================== 弹窗提示样式 ==================== */
.modal-intro {
  margin-bottom: 20px;
}

.intro-main {
  font-size: 1rem;
  font-weight: 500;
  color: #333;
  margin: 0 0 8px 0;
}

.intro-hint {
  font-size: 0.9rem;
  color: #666;
  background-color: #f0f7ff;
  padding: 10px 12px;
  border-radius: 6px;
  border-left: 3px solid #3498db;
  margin: 0;
  display: flex;
  align-items: center;
  line-height: 1.4;
}

.hint-icon {
  margin-right: 8px;
  font-size: 1rem;
}

/* ==================== 选项样式 ==================== */
.question-type-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 15px;
}

.option-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 12px 15px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
  background-color: #fafafa;
}

.option-item:hover {
  background-color: #f5f5f5;
  border-color: #3498db;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.1);
}

.option-item input[type="checkbox"] {
  margin-right: 12px;
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #3498db;
}

.option-text {
  font-size: 0.95rem;
  color: #333;
  font-weight: 500;
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
  padding: 20px;
  transition: all 0.3s ease;
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
  margin-bottom: 15px;
}

.question-header h4 {
  color: #3498db;
  margin: 0;
}

.question-type {
  padding: 4px 10px;
  background-color: #e3f2fd;
  color: #1976d2;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

/* ==================== 问题内容样式 ==================== */
.question-content {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.options {
  margin-top: 10px;
}

.option {
  padding: 5px 0;
  color: #555;
}

/* ==================== 答案区域样式 ==================== */
.student-answer-section h5,
.grading-section h5 {
  color: #555;
  margin-bottom: 10px;
  font-weight: 500;
}

.student-answer {
  padding: 15px;
  background-color: #fff9e6;
  border-radius: 6px;
  margin-bottom: 10px;
  border-left: 4px solid #ffcc00;
}

.correct-answer {
  margin-bottom: 20px;
}

.correct-answer-content {
  padding: 15px;
  background-color: #e8f5e9;
  border-radius: 6px;
  border-left: 4px solid #4caf50;
  color: #2e7d32;
}

/* ==================== 批改区域样式 ==================== */
.grading-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.score-input {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-input label {
  font-weight: 500;
  color: #555;
}

.score-input input {
  width: 80px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.auto-grade-tag {
  color: #666;
  font-size: 0.8rem;
  font-style: italic;
}

.feedback-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feedback-section label {
  font-weight: 500;
  color: #555;
}

.feedback-section textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 0.9rem;
  resize: vertical;
}

/* ==================== 底部样式 ==================== */
.grading-footer {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.btn-grading-complete {
  padding: 12px 30px;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #3498db;
}

.btn-grading-complete:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
}
</style>
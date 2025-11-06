<template>
  <div id="app" class="quizzes-page">
    <span @click="goBack" class="back-home">
      <i class="fas fa-arrow-left"></i> 返回课程
    </span>

    <div class="container">
      <div class="left-panel">
        <div class="page-section">
          <h2>
            <b>{{ course.name }}- 课堂小测列表</b>
          </h2>

          <div class="alert" :class="alertClass" v-if="alertMessage">
            {{ alertMessage }}
          </div>

          <table class="quiz-table" v-if="quizzes.length > 0">
            <thead>
              <tr>
                <th>小测名称</th>
                <th>题目数量</th>
                <th>创建日期</th>
                <th style="text-align: center">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="quiz in quizzes" :key="quiz.id">
                <td>{{ quiz.title }}</td>
                <td>{{ quiz.question_count }}</td>
                <td>
                  {{ quiz.create_time.replace("T", " ").substring(0, 16) }}
                </td>
                <td class="td-btn">
                  <span @click="editQuiz(quiz.id)" class="btn btn-edit"
                    >编辑</span
                  >
                  <span @click="releaseQuiz(quiz.id)" class="btn btn-release"
                    >发布</span
                  >
                  <span @click="editQuiz(quiz.id)" class="btn btn-delete"
                    >删除</span
                  >
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else style="text-align: center; padding: 20px">暂无小测</div>
        </div>
        <div class="form-container">
          <h2 class="form-title">发布新小测</h2>
          <form @submit.prevent="submitQuiz">
            <div class="form-group">
              <label for="title">小测标题</label>
              <input
                type="text"
                id="title"
                name="title"
                maxlength="200"
                required
                placeholder="请输入小测标题"
                v-model="quizForm.title"
              />
            </div>

            <div class="form-group">
              <label for="description">小测说明</label>
              <textarea
                id="description"
                name="description"
                placeholder="请输入小测说明"
                v-model="quizForm.description"
              ></textarea>
            </div>

            <!-- <div class="form-group">
              <label for="due_date">截止日期</label>
              <input
                type="date"
                id="due_date"
                name="due_date"
                required
                v-model="quizForm.due_date"
              />
            </div> -->

            <!-- <div class="form-group">
              <label for="time_limit">时间限制（分钟）</label>
              <input
                type="number"
                id="time_limit"
                name="time_limit"
                min="1"
                max="180"
                v-model="quizForm.time_limit"
              />
            </div> -->
            <div class="page-section">
              <h2>已添加题目</h2>
              <div class="question-list">
                <div
                  v-for="(question, index) in questions"
                  :key="index"
                  class="question-item"
                >
                  <div class="question-item-header">
                    <h4>题目 {{ index + 1 }}</h4>
                    <span class="question-item-type">{{
                      getQuestionTypeName(question.question_type)
                    }}</span>
                  </div>
                  <div class="question-item-content">
                    <p>{{ question.question_text }}</p>
                    <div
                      v-if="
                        question.question_type === 'single_choice' ||
                        question.question_type === 'multiple_choice'
                      "
                      class="question-item-options"
                    >
                      <div
                        v-for="(option, optIndex) in question.options"
                        :key="optIndex"
                        class="question-item-option"
                      >
                        {{ String.fromCharCode(65 + optIndex) }}.
                        {{ option }}
                        <span
                          v-if="
                            question.correct_answer &&
                            question.correct_answer
                              .split(',')
                              .includes(String.fromCharCode(65 + optIndex))
                          "
                          class="correct-indicator"
                          >✓</span
                        >
                      </div>
                    </div>
                    <div v-else-if="question.question_type === 'true_false'">
                      <p>
                        正确答案:
                        {{
                          question.correct_answer === "true" ? "正确" : "错误"
                        }}
                      </p>
                    </div>
                    <div v-else-if="question.question_type === 'short_answer'">
                      <p>参考答案: {{ question.correct_answer }}</p>
                    </div>
                  </div>
                  <div class="question-item-actions">
                    <button @click="editQuestion(index)" class="btn btn-small">
                      编辑
                    </button>
                    <button
                      @click="removeQuestion(index)"
                      class="btn btn-small btn-danger"
                    >
                      删除
                    </button>
                  </div>
                </div>
                <div
                  v-if="questions.length === 0"
                  style="text-align: center; padding: 20px; color: #7f8c8d"
                >
                  暂无题目，请先添加题目
                </div>
              </div>
            </div>
            <!-- 题目类型选择区域 -->
            <div
              class="question-types-section"
              v-if="!currentQuestion.question_type"
            >
              <h3 class="section-title">选择题目类型</h3>
              <div class="question-types">
                <div
                  class="type-option"
                  @click="selectQuestionType('single_choice')"
                >
                  <div class="type-icon">
                    <i class="fas fa-dot-circle" style="color: #3498db"></i>
                  </div>
                  <div class="type-info">
                    <h4>单选题</h4>
                    <p>只有一个正确答案的选择题</p>
                  </div>
                  <div class="type-check">
                    <div
                      class="check-circle"
                      :class="{ active: selectedType === 'single_choice' }"
                    ></div>
                  </div>
                </div>

                <div
                  class="type-option"
                  @click="selectQuestionType('multiple_choice')"
                >
                  <div class="type-icon">
                    <i class="fas fa-check-square" style="color: #3498db"></i>
                  </div>
                  <div class="type-info">
                    <h4>多选题</h4>
                    <p>有多个正确答案的选择题</p>
                  </div>
                  <div class="type-check">
                    <div
                      class="check-circle"
                      :class="{ active: selectedType === 'multiple_choice' }"
                    ></div>
                  </div>
                </div>

                <div
                  class="type-option"
                  @click="selectQuestionType('true_false')"
                >
                  <div class="type-icon">
                    <i class="fas fa-balance-scale" style="color: #3498db"></i>
                  </div>
                  <div class="type-info">
                    <h4>判断题</h4>
                    <p>判断陈述是否正确</p>
                  </div>
                  <div class="type-check">
                    <div
                      class="check-circle"
                      :class="{ active: selectedType === 'true_false' }"
                    ></div>
                  </div>
                </div>

                <div
                  class="type-option"
                  @click="selectQuestionType('short_answer')"
                >
                  <div class="type-icon">
                    <i class="fas fa-align-left" style="color: #3498db"></i>
                  </div>
                  <div class="type-info">
                    <h4>简答题</h4>
                    <p>需要文字回答的开放式问题</p>
                  </div>
                  <div class="type-check">
                    <div
                      class="check-circle"
                      :class="{ active: selectedType === 'short_answer' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 题目编辑区域 -->
            <div
              class="question-edit-section"
              v-if="currentQuestion.question_type"
            >
              <div class="question-header">
                <h3>
                  添加{{ getQuestionTypeName(currentQuestion.question_type) }}
                </h3>
                <span class="question-type-badge">{{
                  getQuestionTypeName(currentQuestion.question_type)
                }}</span>
              </div>

              <div class="form-group">
                <label for="question_title">题目内容</label>
                <textarea
                  id="question_title"
                  name="question_title"
                  placeholder="请输入题目内容"
                  v-model="currentQuestion.question_text"
                  required
                ></textarea>
              </div>

              <!-- 单选题和多选题选项 -->
              <div
                v-if="
                  currentQuestion.question_type === 'single_choice' ||
                  currentQuestion.question_type === 'multiple_choice'
                "
              >
                <div class="form-group">
                  <label>选项</label>
                  <div
                    v-for="(option, index) in currentQuestion.options"
                    :key="index"
                    class="option-item"
                  >
                    <input
                      type="text"
                      :placeholder="'选项 ' + String.fromCharCode(65 + index)"
                      v-model="currentQuestion.options[index]"
                      required
                    />
                    <div class="option-actions">
                      <button
                        type="button"
                        @click="toggleOptionCorrect(index)"
                        class="btn btn-small"
                        :class="{
                          'btn-submit': isOptionMarkedCorrect(index),
                        }"
                      >
                        {{ isOptionMarkedCorrect(index) ? "正确" : "设为正确" }}
                      </button>
                      <button
                        type="button"
                        @click="removeOption(index)"
                        class="btn btn-small btn-danger"
                        v-if="currentQuestion.options.length > 2"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                  <button type="button" @click="addOption" class="btn">
                    添加选项
                  </button>
                </div>
              </div>

              <!-- 判断题选项 -->
              <div v-else-if="currentQuestion.question_type === 'true_false'">
                <div class="form-group correct-answer">
                  <label>正确答案</label>
                  <div style="display: flex; gap: 15px; margin-top: 10px">
                    <label
                      style="
                        display: flex;
                        align-items: center;
                        cursor: pointer;
                      "
                    >
                      <input
                        type="radio"
                        v-model="currentQuestion.correct_answer"
                        :value="'true'"
                        style="margin-right: 5px"
                      />
                      正确
                    </label>
                    <label
                      style="
                        display: flex;
                        align-items: center;
                        cursor: pointer;
                      "
                    >
                      <input
                        type="radio"
                        v-model="currentQuestion.correct_answer"
                        :value="'false'"
                        style="margin-right: 5px"
                      />
                      错误
                    </label>
                  </div>
                </div>
              </div>

              <!-- 简答题 -->
              <div v-else-if="currentQuestion.question_type === 'short_answer'">
                <div class="form-group">
                  <label for="reference_answer">参考答案</label>
                  <textarea
                    id="reference_answer"
                    name="reference_answer"
                    placeholder="请输入参考答案（供批改参考）"
                    v-model="currentQuestion.correct_answer"
                  ></textarea>
                </div>
              </div>

              <div class="form-group">
                <label for="question_score">题目分值</label>
                <input
                  type="number"
                  id="question_score"
                  name="question_score"
                  min="1"
                  max="10"
                  v-model="currentQuestion.score"
                />
              </div>

              <div class="actions">
                <button
                  type="button"
                  @click="saveQuestion"
                  class="btn btn-submit"
                >
                  保存题目
                </button>
                <button
                  type="button"
                  @click="cancelQuestion"
                  class="btn btn-back"
                >
                  取消
                </button>
              </div>
            </div>

            <!-- 题目类型选择（在题目编辑下方） -->
            <div
              class="question-types-section"
              v-if="currentQuestion.question_type"
            >
              <h3 class="section-title">继续添加题目</h3>
              <div class="question-types">
                <div
                  class="type-option"
                  @click="selectQuestionType('single_choice')"
                >
                  <div class="type-icon">
                    <i class="fas fa-dot-circle" style="color: #3498db"></i>
                  </div>
                  <div class="type-info">
                    <h4>单选题</h4>
                  </div>
                </div>

                <div
                  class="type-option"
                  @click="selectQuestionType('multiple_choice')"
                >
                  <div class="type-icon">
                    <i class="fas fa-check-square" style="color: #3498db"></i>
                  </div>
                  <div class="type-info">
                    <h4>多选题</h4>
                  </div>
                </div>

                <div
                  class="type-option"
                  @click="selectQuestionType('true_false')"
                >
                  <div class="type-icon">
                    <i class="fas fa-balance-scale" style="color: #3498db"></i>
                  </div>
                  <div class="type-info">
                    <h4>判断题</h4>
                  </div>
                </div>

                <div
                  class="type-option"
                  @click="selectQuestionType('short_answer')"
                >
                  <div class="type-icon">
                    <i class="fas fa-align-left" style="color: #3498db"></i>
                  </div>
                  <div class="type-info">
                    <h4>简答题</h4>
                  </div>
                </div>
              </div>
            </div>

            <div class="actions">
              <button
                type="submit"
                class="btn btn-submit"
                :disabled="questions.length === 0"
              >
                发布小测
              </button>
              <button type="button" @click="goBack" class="btn btn-back">
                返回课程管理
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  get_course_by_id,
  get_quizzes,
  create_quiz,
  add_quiz_questions,
} from "@/http/api.js";
export default {
  data() {
    return {
      course: {},
      quizzes: [],
      questions: [],
      quizForm: {
        title: "",
        description: "",
      },
      selectedType: null,
      // 使用与后端提交一致的字段名：question_type, question_text, options (字符串数组), correct_answer (字符串)
      currentQuestion: {
        question_type: null,
        question_text: "",
        options: ["", ""],
        // 单选：'A'，多选：'A,B'，判断：'true' 或 'false'，简答：文本
        correct_answer: "",
        score: 1,
      },
      alertMessage: "",
      alertClass: "alert-success",
    };
  },

  mounted() {
    this.init_course();
    this.init_quizzes();
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

    //初始化小测列表
    init_quizzes() {
      const courseId = this.$route.params.courseId;
      if (courseId) {
        get_quizzes(courseId)
          .then((response) => {
            this.quizzes = response.data;
          })
          .catch((error) => {
            console.error("获取小测列表失败:", error);
            this.$message.error("获取小测列表失败");
          });
      }
    },

    goBack() {
      this.$router.push(`/teachers/course/${this.course.id}`);
    },

    //选择题目类型
    selectQuestionType(type) {
      this.selectedType = type;
      this.currentQuestion.question_type = type;

      // 重置当前题目数据（使用新的字段名）
      this.currentQuestion.question_text = "";
      this.currentQuestion.options = ["", ""];
      this.currentQuestion.correct_answer = "";
      this.currentQuestion.score = 1;
    },

    //获取题目类型名称
    getQuestionTypeName(type) {
      const typeNames = {
        single_choice: "单选题",
        multiple_choice: "多选题",
        true_false: "判断题",
        short_answer: "简答题",
      };
      return typeNames[type] || "未知类型";
    },
    //添加选项
    addOption() {
      this.currentQuestion.options.push("");
    },

    //移除选项
    removeOption(index) {
      if (this.currentQuestion.options.length > 2) {
        this.currentQuestion.options.splice(index, 1);

        // 如果 correct_answer 包含被删除的选项字母，则移除它
        if (this.currentQuestion.correct_answer) {
          const letters = this.currentQuestion.correct_answer.split(",");
          const removed = String.fromCharCode(65 + index);
          const newLetters = letters.filter((l) => l !== removed);
          this.currentQuestion.correct_answer = newLetters.join(",");
        }
      }
    },

    // 判断某个选项是否被标记为正确（基于 currentQuestion.correct_answer 字符串）
    isOptionMarkedCorrect(index) {
      if (!this.currentQuestion.correct_answer) return false;
      const letter = String.fromCharCode(65 + index);
      const parts = this.currentQuestion.correct_answer.split(",");
      return parts.includes(letter);
    },

    //切换选项为正确答案
    toggleOptionCorrect(index) {
      const letter = String.fromCharCode(65 + index);
      if (this.currentQuestion.question_type === "single_choice") {
        // 单选题只能有一个正确答案，用字母表示
        this.currentQuestion.correct_answer = letter;
      } else {
        // 多选题可以切换正确答案状态，使用逗号分隔的字母列表
        const parts = this.currentQuestion.correct_answer
          ? this.currentQuestion.correct_answer.split(",")
          : [];
        const i = parts.indexOf(letter);
        if (i > -1) parts.splice(i, 1);
        else parts.push(letter);
        parts.sort();
        this.currentQuestion.correct_answer = parts.join(",");
      }
    },

    //保存题目
    saveQuestion() {
      // 验证题目数据
      if (!this.currentQuestion.question_text.trim()) {
        this.$message.error("请输入题目内容");
        return;
      }

      if (
        (this.currentQuestion.question_type === "single_choice" ||
          this.currentQuestion.question_type === "multiple_choice") &&
        !this.currentQuestion.correct_answer
      ) {
        this.$message.error("请至少设置一个正确答案");
        return;
      }

      // 添加到题目列表（使用新的字段名）
      this.questions.push({ ...this.currentQuestion });

      // 重置当前题目
      this.currentQuestion.question_type = null;
      this.selectedType = null;

      this.$message("题目添加成功");
    },

    //取消题目编辑
    cancelQuestion() {
      this.currentQuestion.question_type = null;
      this.selectedType = null;
    },

    // 编辑题目
    editQuestion(index) {
      // 将题目数据复制到当前编辑区域，兼容旧结构（type/title/options 为对象数组等）
      const q = this.questions[index];
      // 判断是否为旧格式
      if (q && q.type && (q.title || q.referenceAnswer || q.correctAnswers)) {
        // 映射旧格式到新格式
        const mapped = {
          question_type: q.type,
          question_text: q.title || "",
          options: Array.isArray(q.options)
            ? q.options.map((o) => (o && o.text ? o.text : o))
            : [],
          correct_answer: "",
          score: q.score || 1,
        };
        if (q.type === "single_choice") {
          mapped.correct_answer =
            q.correctAnswers && q.correctAnswers.length
              ? String.fromCharCode(65 + q.correctAnswers[0])
              : "";
        } else if (q.type === "multiple_choice") {
          mapped.correct_answer = (q.correctAnswers || [])
            .map((i) => String.fromCharCode(65 + i))
            .join(",");
        } else if (q.type === "true_false") {
          mapped.correct_answer = q.correctAnswer ? "true" : "false";
        } else if (q.type === "short_answer") {
          mapped.correct_answer = q.referenceAnswer || "";
        }
        this.currentQuestion = mapped;
      } else {
        // 已经是新格式
        this.currentQuestion = { ...q };
      }

      this.selectedType = this.currentQuestion.question_type;

      // 从题目列表中移除该题目
      this.questions.splice(index, 1);
    },

    // 删除题目
    removeQuestion(index) {
      if (confirm("确定要删除这个题目吗？")) {
        this.questions.splice(index, 1);
        this.showAlert("题目删除成功", "alert-success");
      }
    },

    // 提交小测
    submitQuiz() {
      if (this.questions.length === 0) {
        this.$message.error("请至少添加一个题目");
        return;
      }
      const data = {
        course_id: this.course.id,
        teacher_id: JSON.parse(sessionStorage.getItem("userInfo")).user_id,
        title: this.quizForm.title,
        description: this.quizForm.description,
        create_time: this.formatDateToYYYYMMDDHHMM,
      };
      create_quiz(data)
        .then((response) => {
          const quiz_id = response.data.id; // 假设后端返回新创建的小测ID
          const formattedQuestions = this.questions.map((q) => ({
            question_type: q.question_type,
            question_text: q.question_text,
            options: q.options,
            correct_answer: q.correct_answer,
            score: q.score,
          }));
          console.log(formattedQuestions);
          const params = {
            quiz_id: quiz_id,
            questions: formattedQuestions,
          };
          return add_quiz_questions(params);
        })
        .then(() => {
          this.$message.success("小测发布成功");
          // 重置表单
          // this.quizForm = {
          //   title: "",
          //   description: "",
          // };
          // this.questions = [];
        })
        .catch((error) => {
          console.error("发布小测失败:", error);
          this.$message.error("发布小测失败，请稍后重试");
        });
      // 模拟提交数据
      // console.log("提交小测数据:", {
      //   ...this.quizForm,
      //   questions: this.questions,
      // });
    },

    //编辑小测
    editQuiz(id) {
      alert(`编辑小测 ID: ${id}`);
    },

    //发布小测
    releaseQuiz(id) {
    },
  },
  computed: {
    formatDateToYYYYMMDDHHMM() {
      const date = new Date();
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, "0");
      const day = String(date.getDate()).padStart(2, "0");
      const hours = String(date.getHours()).padStart(2, "0");
      const minutes = String(date.getMinutes()).padStart(2, "0");

      return `${year}-${month}-${day} ${hours}:${minutes}`;
    },
  },
};
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.quizzes-page {
  max-width: 1200px;
  margin: 0 auto;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  line-height: 1.6;
  padding: 20px;
}

.back-home {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  background-color: #4299e1;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 200;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(66, 153, 225, 0.1);
  cursor: pointer;
  margin-bottom: 20px;
}

.back-home:hover {
  background-color: #2acb11;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(66, 153, 225, 0.2);
}

.container {
  display: flex;
  gap: 30px;
}

.left-panel {
  flex: 1;
}

.right-panel {
  flex: 1;
}

h2 {
  color: #2980b9;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
}

.page-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 25px;
  margin-bottom: 30px;
}

/* Alert messages */
.alert {
  padding: 12px 15px;
  margin-bottom: 20px;
  border-radius: 4px;
  font-weight: 500;
}

.alert-success {
  background-color: rgba(46, 204, 113, 0.15);
  border-left: 4px solid #2ecc71;
  color: #27ae60;
}

.alert-danger {
  background-color: rgba(231, 76, 60, 0.15);
  border-left: 4px solid #e74c3c;
  color: #c0392b;
}

/* Table styling */
.quiz-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.quiz-table th,
.quiz-table td {
  padding: 12px 15px;
  text-align: left;
}

.quiz-table th {
  background-color: #3498db;
  color: white;
  font-weight: 500;
}

.quiz-table tr:nth-child(even) {
  background-color: #f8f9fa;
}

.quiz-table tr:hover {
  background-color: rgba(52, 152, 219, 0.05);
}

/* Form styling */
.form-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 25px;
}

.form-title {
  margin-bottom: 20px;
  color: #2980b9;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-group input[type="text"],
.form-group input[type="date"],
.form-group textarea,
.form-group input[type="number"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 1rem;
  transition: border 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-group textarea {
  min-height: 120px;
  resize: vertical;
}

/* 题目类型选择区域 */
.question-types-section {
  margin: 30px 0;
  padding: 20px 0;
}

.section-title {
  color: #2980b9;
  margin-bottom: 20px;
  font-size: 1.2rem;
}

.question-types {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.type-option {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
}

.type-option:hover {
  border-color: #3498db;
  background-color: rgba(52, 152, 219, 0.05);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.type-icon {
  margin-right: 15px;
  flex-shrink: 0;
}

.type-info {
  flex-grow: 1;
}

.type-info h4 {
  color: #2c3e50;
  margin-bottom: 5px;
  font-size: 1rem;
}

.type-info p {
  color: #7f8c8d;
  font-size: 0.85rem;
  margin: 0;
}

.type-check {
  margin-left: 10px;
  flex-shrink: 0;
}

.check-circle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #bdc3c7;
  position: relative;
  transition: all 0.3s ease;
}

.check-circle.active {
  border-color: #3498db;
  background-color: #3498db;
}

.check-circle.active::after {
  content: "";
  position: absolute;
  top: 4px;
  left: 4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: white;
}

/* 题目编辑区域 */
.question-edit-section {
  margin: 30px 0;
  padding: 20px;
  border: 2px dashed #3498db;
  border-radius: 8px;
  background-color: rgba(52, 152, 219, 0.05);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.question-type-badge {
  padding: 5px 10px;
  background-color: #3498db;
  color: white;
  border-radius: 4px;
  font-size: 0.9rem;
}

.option-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.option-item input[type="text"] {
  flex-grow: 1;
  margin-right: 10px;
  width: 70%;
}

.option-actions {
  display: flex;
  gap: 5px;
}

.option-actions .btn {
  padding: 5px 10px;
  font-size: 0.8rem;
}

.correct-answer {
  margin-top: 15px;
}

.td-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

/* Buttons */
.btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #3498db;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s, transform 0.2s;
}

.btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
}

.btn-small {
  width: 75px;
  padding: 6px 12px;
  font-size: 0.9rem;
}

.btn-edit {
  padding: 8px 15px;
  font-size: 0.9rem;
}

.btn-release {
  padding: 8px 15px;
  font-size: 0.9rem;
  background-color: #27ae60;
}

.btn-delete {
  padding: 8px 15px;
  font-size: 0.9rem;
  background-color: #e74c3c;
}

.btn-submit {
  background-color: #2ecc71;
}

.btn-submit:hover {
  background-color: #27ae60;
}

.btn-back {
  background-color: #95a5a6;
}

.btn-back:hover {
  background-color: #7f8c8d;
}

.btn-danger {
  background-color: #e74c3c;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

/* 题目列表 */
.question-list {
  margin-top: 20px;
}

.question-item {
  padding: 15px;
  margin-bottom: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.question-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.question-item-type {
  font-size: 0.9rem;
  color: #7f8c8d;
}

.question-item-content {
  margin-bottom: 10px;
}

.question-item-options {
  margin-left: 20px;
}

.question-item-option {
  margin-bottom: 5px;
}

.question-item-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
</style>
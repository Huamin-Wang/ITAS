<template>
  <div class="form-container">
    <h2 class="form-title">{{ isEditMode ? "编辑小测" : "新建新小测" }}</h2>
    <form>
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
                  {{ question.correct_answer === "true" ? "正确" : "错误" }}
                </p>
              </div>
              <div v-else-if="question.question_type === 'short_answer'">
                <p>参考答案: {{ question.correct_answer }}</p>
              </div>
            </div>

            <!-- 编辑区域 - 在题目下方显示 -->
            <div v-if="editingIndex === index" class="question-edit-section">
              <div class="form-group">
                <label>题目内容</label>
                <textarea
                  placeholder="请输入题目内容"
                  v-model="editingQuestion.question_text"
                  required
                ></textarea>
              </div>

              <!-- 单选题和多选题选项编辑 -->
              <div
                v-if="
                  editingQuestion.question_type === 'single_choice' ||
                  editingQuestion.question_type === 'multiple_choice'
                "
              >
                <div class="form-group">
                  <label>选项</label>
                  <div
                    v-for="(option, optIndex) in editingQuestion.options"
                    :key="optIndex"
                    class="option-item"
                  >
                    <input
                      type="text"
                      :placeholder="
                        '选项 ' + String.fromCharCode(65 + optIndex)
                      "
                      v-model="editingQuestion.options[optIndex]"
                      required
                    />
                    <div class="option-actions">
                      <button
                        type="button"
                        @click="editToggleOptionCorrect(optIndex)"
                        class="btn btn-small"
                        :class="{
                          'btn-submit': editIsOptionMarkedCorrect(optIndex),
                        }"
                      >
                        {{
                          editIsOptionMarkedCorrect(optIndex)
                            ? "正确"
                            : "设为正确"
                        }}
                      </button>
                      <button
                        type="button"
                        @click="editRemoveOption(optIndex)"
                        class="btn btn-small btn-danger"
                        v-if="editingQuestion.options.length > 2"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                  <button type="button" @click="editAddOption" class="btn">
                    添加选项
                  </button>
                </div>
              </div>

              <!-- 判断题选项编辑 -->
              <div v-else-if="editingQuestion.question_type === 'true_false'">
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
                        v-model="editingQuestion.correct_answer"
                        value="true"
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
                        v-model="editingQuestion.correct_answer"
                        value="false"
                        style="margin-right: 5px"
                      />
                      错误
                    </label>
                  </div>
                </div>
              </div>

              <!-- 简答题编辑 -->
              <div v-else-if="editingQuestion.question_type === 'short_answer'">
                <div class="form-group">
                  <label>参考答案</label>
                  <textarea
                    placeholder="请输入参考答案（供批改参考）"
                    v-model="editingQuestion.correct_answer"
                  ></textarea>
                </div>
              </div>

              <div class="form-group">
                <label>题目分值</label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  v-model="editingQuestion.points"
                />
              </div>

              <div class="actions">
                <button
                  type="button"
                  @click="updateQuestion(index)"
                  class="btn btn-submit"
                >
                  更新题目
                </button>
                <button type="button" @click="cancelEdit" class="btn btn-back">
                  取消
                </button>
              </div>
            </div>

            <div class="question-item-actions">
              <button
                type="button"
                @click="startEdit(index)"
                class="btn btn-small"
              >
                编辑
              </button>
              <button
                type="button"
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
      <div class="question-types-section" v-if="!currentQuestion.question_type">
        <h3 class="section-title">选择题目类型</h3>
        <div class="question-types">
          <div class="type-option" @click="selectQuestionType('single_choice')">
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

          <div class="type-option" @click="selectQuestionType('true_false')">
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

          <div class="type-option" @click="selectQuestionType('short_answer')">
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

      <!-- 新增题目编辑区域 -->
      <div class="question-edit-section" v-if="currentQuestion.question_type">
        <div class="question-header">
          <h3>添加{{ getQuestionTypeName(currentQuestion.question_type) }}</h3>
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
                style="display: flex; align-items: center; cursor: pointer"
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
                style="display: flex; align-items: center; cursor: pointer"
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
          <label for="question_points">题目分值</label>
          <input
            type="number"
            id="question_points"
            name="question_points"
            min="1"
            max="10"
            v-model="currentQuestion.points"
          />
        </div>

        <div class="actions">
          <button type="button" @click="saveQuestion" class="btn btn-submit">
            保存题目
          </button>
          <button type="button" @click="cancelQuestion" class="btn btn-back">
            取消
          </button>
        </div>
      </div>

      <!-- 题目类型选择（在题目编辑下方） -->
      <div class="question-types-section" v-if="currentQuestion.question_type">
        <h3 class="section-title">继续添加题目</h3>
        <div class="question-types">
          <div class="type-option" @click="selectQuestionType('single_choice')">
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

          <div class="type-option" @click="selectQuestionType('true_false')">
            <div class="type-icon">
              <i class="fas fa-balance-scale" style="color: #3498db"></i>
            </div>
            <div class="type-info">
              <h4>判断题</h4>
            </div>
          </div>

          <div class="type-option" @click="selectQuestionType('short_answer')">
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
          type="button"
          @click="submitQuiz()"
          class="btn btn-submit"
          :disabled="questions.length === 0"
        >
          {{ isEditMode ? "更新小测" : "新建小测" }}
        </button>
        <button type="button" @click="cancel" class="btn btn-back">取消</button>
      </div>
    </form>
  </div>
</template>

<script>
import {
  get_quiz_questions,
  create_quiz,
  add_quiz_questions,
  update_quiz,
} from "@/http/api.js";

export default {
  name: "QuizEditor",
  props: {
    mode: {
      type: String,
      default: "create", // 'create' 或 'edit'
      validator: (value) => ["create", "edit"].includes(value),
    },
    courseId: {
      type: [String, Number],
      required: true,
    },
    quizId: {
      type: [String, Number],
      default: null,
    },
  },
  data() {
    return {
      isEditMode: this.mode === "edit",
      quizForm: {
        title: "",
        description: "",
      },
      questions: [],
      selectedType: null,
      currentQuestion: {
        question_type: null,
        question_text: "",
        options: ["", ""],
        correct_answer: "",
        points: 1,
      },
      editingIndex: null, // 正在编辑的题目索引
      editingQuestion: {
        // 编辑中的题目数据
        id: null,
        question_type: null,
        question_text: "",
        options: ["", ""],
        correct_answer: "",
        points: 1,
      },
      alertMessage: "",
      alertClass: "alert-success",
    };
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
  mounted() {
    if (this.isEditMode && this.quizId) {
      this.loadQuizData();
    }
  },
  methods: {
    async loadQuizData() {
      try {
        const response = await get_quiz_questions(this.quizId);
        const quizData = response.data;

        // 填充表单数据
        this.quizForm = {
          title: quizData.quiz.title,
          description: quizData.quiz.description,
        };

        // 加载题目数据
        if (quizData.questions && quizData.questions.length > 0) {
          this.questions = quizData.questions.map((q) => ({
            id: q.id,
            question_type: q.question_type,
            question_text: q.question_text,
            options: q.options || [],
            correct_answer: q.correct_answer,
            points: q.points || 1,
          }));
        }
      } catch (error) {
        console.error("获取小测数据失败:", error);
        this.$message.error("获取小测数据失败");
      }
    },

    selectQuestionType(type) {
      this.selectedType = type;
      this.currentQuestion.question_type = type;
      this.currentQuestion.question_text = "";
      this.currentQuestion.options = ["", ""];
      this.currentQuestion.correct_answer = "";
      this.currentQuestion.points = 1;
    },

    getQuestionTypeName(type) {
      const typeNames = {
        single_choice: "单选题",
        multiple_choice: "多选题",
        true_false: "判断题",
        short_answer: "简答题",
      };
      return typeNames[type] || "未知类型";
    },

    addOption() {
      this.currentQuestion.options.push("");
    },

    removeOption(index) {
      if (this.currentQuestion.options.length > 2) {
        this.currentQuestion.options.splice(index, 1);

        if (this.currentQuestion.correct_answer) {
          const letters = this.currentQuestion.correct_answer.split(",");
          const removed = String.fromCharCode(65 + index);
          const newLetters = letters.filter((l) => l !== removed);
          this.currentQuestion.correct_answer = newLetters.join(",");
        }
      }
    },

    isOptionMarkedCorrect(index) {
      if (!this.currentQuestion.correct_answer) return false;
      const letter = String.fromCharCode(65 + index);
      const parts = this.currentQuestion.correct_answer.split(",");
      return parts.includes(letter);
    },

    toggleOptionCorrect(index) {
      const letter = String.fromCharCode(65 + index);
      if (this.currentQuestion.question_type === "single_choice") {
        this.currentQuestion.correct_answer = letter;
      } else {
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

    // 编辑题目相关方法
    startEdit(index) {
      const question = this.questions[index];
      this.editingIndex = index;
      this.editingQuestion = {
        id: question.id,
        question_type: question.question_type,
        question_text: question.question_text,
        options: [...question.options],
        correct_answer: question.correct_answer,
        points: question.points,
      };
    },

    cancelEdit() {
      this.editingIndex = null;
      this.editingQuestion = {
        question_type: null,
        question_text: "",
        options: ["", ""],
        correct_answer: "",
        points: 1,
      };
    },

    updateQuestion(index) {
      if (!this.editingQuestion.question_text.trim()) {
        this.$message.error("请输入题目内容");
        return;
      }

      if (
        (this.editingQuestion.question_type === "single_choice" ||
          this.editingQuestion.question_type === "multiple_choice") &&
        !this.editingQuestion.correct_answer
      ) {
        this.$message.error("请至少设置一个正确答案");
        return;
      }

      this.questions[index] = { ...this.editingQuestion };
      this.cancelEdit();
      this.$message.success("题目保存成功");
    },

    editAddOption() {
      this.editingQuestion.options.push("");
    },

    editRemoveOption(index) {
      if (this.editingQuestion.options.length > 2) {
        this.editingQuestion.options.splice(index, 1);

        if (this.editingQuestion.correct_answer) {
          const letters = this.editingQuestion.correct_answer.split(",");
          const removed = String.fromCharCode(65 + index);
          const newLetters = letters.filter((l) => l !== removed);
          this.editingQuestion.correct_answer = newLetters.join(",");
        }
      }
    },

    editIsOptionMarkedCorrect(index) {
      if (!this.editingQuestion.correct_answer) return false;
      const letter = String.fromCharCode(65 + index);
      const parts = this.editingQuestion.correct_answer.split(",");
      return parts.includes(letter);
    },

    editToggleOptionCorrect(index) {
      const letter = String.fromCharCode(65 + index);
      if (this.editingQuestion.question_type === "single_choice") {
        this.editingQuestion.correct_answer = letter;
      } else {
        const parts = this.editingQuestion.correct_answer
          ? this.editingQuestion.correct_answer.split(",")
          : [];
        const i = parts.indexOf(letter);
        if (i > -1) parts.splice(i, 1);
        else parts.push(letter);
        parts.sort();
        this.editingQuestion.correct_answer = parts.join(",");
      }
    },

    saveQuestion() {
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

      this.questions.push({ ...this.currentQuestion });
      this.currentQuestion.question_type = null;
      this.selectedType = null;
      this.$message.success("题目添加成功");
    },

    cancelQuestion() {
      this.currentQuestion.question_type = null;
      this.selectedType = null;
    },

    removeQuestion(index) {
      if (confirm("确定要删除这个题目吗？")) {
        this.questions.splice(index, 1);
        this.showAlert("题目删除成功", "alert-success");
      }
    },

    async submitQuiz() {
      if (this.questions.length === 0) {
        this.$message.error("请至少添加一个题目");
        return;
      }

      try {
        if (this.isEditMode) {
          // 编辑模式 - 更新小测
          const updateData = {
            id: this.quizId,
            title: this.quizForm.title,
            description: this.quizForm.description,
            questions: this.questions.map((q) => ({
              id: q.id,
              question_type: q.question_type,
              question_text: q.question_text,
              options: q.options,
              correct_answer: q.correct_answer,
              points: q.points,
            })),
          };
          console.log(updateData);

          await update_quiz(updateData);
          this.$message.success("小测更新成功");
        } else {
          // 新增模式 - 创建小测
          const data = {
            course_id: this.courseId,
            teacher_id: JSON.parse(localStorage.getItem("userInfo")).user_id,
            title: this.quizForm.title,
            description: this.quizForm.description,
            create_time: this.formatDateToYYYYMMDDHHMM,
          };

          const response = await create_quiz(data);
          const quiz_id = response.data.id;

          const formattedQuestions = this.questions.map((q) => ({
            question_type: q.question_type,
            question_text: q.question_text,
            options: q.options,
            correct_answer: q.correct_answer,
            points: q.points,
          }));

          const params = {
            quiz_id: quiz_id,
            questions: formattedQuestions,
          };

          await add_quiz_questions(params);
          this.$message.success("小测新建成功");
        }

        this.$emit("success");
        this.resetForm();
      } catch (error) {
        console.error(`${this.isEditMode ? "更新" : "新建"}小测失败:`, error);
        this.$message.error(
          `${this.isEditMode ? "更新" : "新建"}小测失败，请稍后重试`
        );
      }
    },

    resetForm() {
      this.quizForm = {
        title: "",
        description: "",
      };
      this.questions = [];
      this.currentQuestion = {
        question_type: null,
        question_text: "",
        options: ["", ""],
        correct_answer: "",
        points: 1,
      };
      this.selectedType = null;
      this.cancelEdit();
    },

    cancel() {
      this.$emit("cancel");
    },

    showAlert(message, type) {
      this.alertMessage = message;
      this.alertClass = type;
      setTimeout(() => {
        this.alertMessage = "";
      }, 3000);
    },
  },
};
</script>

<style scoped>
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
  margin: 20px 0;
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
  align-items: center;
  justify-content: center;
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

.correct-indicator {
  color: #27ae60;
  font-weight: bold;
  margin-left: 5px;
}
</style>
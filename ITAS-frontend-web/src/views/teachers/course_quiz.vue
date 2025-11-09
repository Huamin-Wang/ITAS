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
                  <span @click="deleteQuiz(quiz.id)" class="btn btn-delete"
                    >删除</span
                  >
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else style="text-align: center; padding: 20px">暂无小测</div>
        </div>

        <!-- 使用封装的组件 -->
        <QuizEditor
          v-if="showQuizEditor"
          :mode="editorMode"
          :courseId="course.id"
          :quizId="currentQuizId"
          @cancel="handleEditorCancel"
          @success="handleEditorSuccess"
        />

        <!-- 新增小测按钮（当不在编辑模式时显示） -->
        <div v-else class="release-btn">
          <button @click="createNewQuiz()" class="btn btn-submit">
            发布新小测
          </button>
        </div>
      </div>
    </div>
    <el-dialog
      v-model="showDeadLineDialog"
      @close="closeDeadlineDialog"
      title="设置截止时间"
      width="400px"
    >
      <div class="deadline-dialog-content">
        <p>请设置小测的截止时间（分钟）：</p>
        <el-input-number
          v-model="deadlineMinutes"
          :min="1"
          :max="1440"
          placeholder="请输入分钟数"
          class="deadline-input"
        ></el-input-number>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeDeadlineDialog">取消</el-button>
          <el-button type="primary" @click="confirmRelease()"
            >确认发布</el-button
          >
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { get_course_by_id, get_quizzes, update_quiz } from "@/http/api.js";
import QuizEditor from "@/components/QuizEditor.vue"; // 导入组件

export default {
  name: "CourseQuiz",
  components: {
    QuizEditor,
  },
  data() {
    return {
      course: {},
      quizzes: [],
      showQuizEditor: false,
      editorMode: "create",
      currentQuizId: null,
      alertMessage: "",
      alertClass: "alert-success",
      showDeadLineDialog: false,
      deadlineMinutes: 30, // 默认30分钟
      releaseQuizId: null, // 用于存储要发布的小测ID
    };
  },
  mounted() {
    this.init_course();
    this.init_quizzes();
  },
  methods: {
    init_course() {
      const courseId = this.$route.params.courseId;
      if (courseId) {
        get_course_by_id(courseId)
          .then((response) => {
            this.course = response.data;
            document.title = `课程管理 - ${this.course.name}`;
          })
          .catch((error) => {
            console.error("获取课程信息失败:", error);
            this.$message.error("获取课程信息失败");
          });
      } else {
        this.$message.error("未提供课程ID");
      }
    },

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
      this.$router.push(`/course_manager/${this.course.id}`);
    },

    createNewQuiz() {
      this.editorMode = "create";
      this.currentQuizId = null;
      this.showQuizEditor = true;
    },

    editQuiz(quizId) {
      this.editorMode = "edit";
      this.currentQuizId = quizId;
      this.showQuizEditor = true;
    },

    releaseQuiz(quizId) {
      this.releaseQuizId = quizId;
      this.showDeadLineDialog = true;
    },

    deleteQuiz(quizId) {},

    // 关闭截止时间弹窗
    closeDeadlineDialog() {
      this.showDeadLineDialog = false;
      this.deadlineMinutes = 30; // 重置为默认值
      this.releaseQuizId = null;
    },

    // 确认发布小测
    confirmRelease() {
      if (!this.releaseQuizId) {
        this.$message.error("未找到要发布的小测");
        return;
      }

      if (!this.deadlineMinutes || this.deadlineMinutes <= 0) {
        this.$message.error("请输入有效的截止时间");
        return;
      }

      const updateData = {
        id: this.releaseQuizId,
        deadline_time: this.deadlineMinutes,
      };

      update_quiz(updateData)
        .then((res) => {
          if (res.code == 200) {
            this.$message.success("小测发布成功");
            this.closeDeadlineDialog();
            this.init_quizzes();
          }
        })
        .catch((error) => {
          console.error("发布小测失败:", error);
          this.$message.error("发布小测失败");
        });
    },

    handleEditorCancel() {
      this.showQuizEditor = false;
      this.currentQuizId = null;
    },

    //小测新建或编辑成功
    handleEditorSuccess() {
      this.showQuizEditor = false;
      this.currentQuizId = null;
      this.init_quizzes(); // 刷新小测列表
      this.showAlert(
        this.editorMode === "create" ? "小测新建成功" : "小测更新成功",
        "alert-success"
      );
    },

    //消息提示
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
  box-shadow: 1px 2px 10px rgba(0, 0, 0, 0.05);
  padding: 25px;
  margin-bottom: 30px;
}

.release-btn {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
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

/* 弹窗相关样式 */
.deadline-dialog-content {
  text-align: center;
  padding: 10px 0;
}

.deadline-input {
  margin: 15px 0;
  width: 100%;
}

.deadline-hint {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}
</style>
<template>
  <div class="quiz-grading-page">
    <span @click="go_to_course_quiz(this.course_id)" class="back-home"
      >返回课堂小测</span
    >
    <div class="container">
      <div class="page-section">
        <h2>
          <b>{{ quiz_title }} - 小测列表</b>
        </h2>

        <div class="alert" :class="alertClass" v-if="alertMessage">
          {{ alertMessage }}
        </div>

        <table class="assignment-table">
          <thead>
            <tr>
              <th>学号</th>
              <th>姓名</th>
              <th>提交时间</th>
              <th>提交状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="student in this.quiz_students"
              :key="student.student_number"
              @click="viewStudentSubmission(student)"
              style="cursor: pointer"
            >
              <td>{{ student.identifier }}</td>
              <td>{{ student.student_name }}</td>
              <td>{{ formatDateTime(student.response_time) }}</td>
              <td :class="student.submitted ? 'submitted' : 'not-submitted'">
                {{ student.submitted ? "已提交" : "未提交" }}
              </td>
              <td>
                <button @click="viewStudentSubmission(student)">查看</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { get_student_numbers, has_submitted_quiz } from "@/http/api.js";
export default {
  data() {
    return {
      quiz_id: null,
      course_id: null,
      quiz_title: "",
      quiz_students: [],
      alertMessage: "",
      alertClass: "alert-success",
    };
  },
  methods: {
    init_quiz_grading_list(course_id, quiz_id) {
      get_student_numbers(course_id).then((response) => {
        const params = {
          quiz_id: quiz_id,
          identifier_arr: response.data.student_numbers,
        };
        has_submitted_quiz(params).then((response) => {
          this.quiz_title = response.data.quiz_title;
          this.quiz_students = response.data.result_list;
        });
      });
    },

    // 格式化日期时间
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return "";

      try {
        const date = new Date(dateTimeStr);

        // 检查日期是否有效
        if (isNaN(date.getTime())) {
          return dateTimeStr; // 返回原始字符串
        }

        // 格式化为 YYYY-MM-DD HH:MM
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");

        return `${year}-${month}-${day} ${hours}:${minutes}`;
      } catch (error) {
        console.error("日期格式转换错误:", error);
        return dateTimeStr; // 如果转换失败，返回原始字符串
      }
    },

    //返回课堂测试页面
    go_to_course_quiz(course_id) {
      this.$router.push(`/course_quiz/${course_id}`);
    },

    // 查看学生提交详情
    viewStudentSubmission(student) {
      if (student.submitted) {
        // 如果已提交，可以跳转到批改页面
        console.log("查看学生提交:", student);
        this.showAlert(`查看 ${student.student_name} 的提交`, "alert-success");
        this.$router.push({
          name: "detail_grading",
          params: {
            courseId: this.course_id,
            quizId: this.quiz_id,
            studentNumber: student.identifier,
          },
        });
      } else {
        // 如果未提交，显示提示
        this.showAlert(`${student.student_name} 未提交`, "alert-danger");
      }
    },

    // 显示提示信息
    showAlert(message, type) {
      this.alertMessage = message;
      this.alertClass = type;
      setTimeout(() => {
        this.alertMessage = "";
      }, 3000);
    },
  },

  mounted() {
    this.quiz_id = this.$route.params.quizId;
    this.course_id = this.$route.params.courseId;
    this.init_quiz_grading_list(this.course_id, this.quiz_id);
  },
};
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.quiz-grading-page {
  margin: 0 auto;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  line-height: 1.6;
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
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
  border: none;
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

.page-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 25px;
  margin-bottom: 30px;
  width: 100%;
}

h2 {
  color: #2980b9;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
}

/* Table styling */
.assignment-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.assignment-table th,
.assignment-table td {
  padding: 12px 15px;
  text-align: left;
}

.assignment-table th {
  background-color: #3498db;
  color: white;
  font-weight: 500;
}

.assignment-table tr:nth-child(even) {
  background-color: #f8f9fa;
}

.assignment-table tr:hover {
  background-color: rgba(52, 152, 219, 0.05);
}

/* Button styling */
.assignment-table button {
  display: inline-block;
  padding: 8px 15px;
  background-color: #3498db;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.3s, transform 0.2s;
}

.assignment-table button:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
}

/* Alert styling */
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

/* Status colors */
.submitted {
  color: #27ae60;
  font-weight: 500;
}

.not-submitted {
  color: #e74c3c;
  font-weight: 500;
}
</style>
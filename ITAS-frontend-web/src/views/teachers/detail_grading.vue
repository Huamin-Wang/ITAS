<template>
  <div class="detail-grading-page">
    <span @click="goBackToQuizGrading" class="back-home">返回批改列表</span>

    <div class="container">
      <div class="page-section student-info-section">
        <h2>
          <b>{{ studentInfo.student_name }} - {{ quizTitle }} </b>
        </h2>

        <div class="student-details">
          <div class="detail-item">
            <span class="detail-label">学号:</span>
            <span class="detail-value">{{ studentInfo.identifier }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">提交时间:</span>
            <span class="detail-value">{{
              formatDateTime(studentInfo.response_time)
            }}</span>
          </div>
          <!-- <div class="detail-item">
            <span class="detail-label">提交状态:</span>
            <span
              :class="studentInfo.submitted ? 'submitted' : 'not-submitted'"
            >
              {{ studentInfo.submitted ? "已提交" : "未提交" }}
            </span>
          </div> -->
        </div>
      </div>

      <div class="page-section">
        <div class="alert" :class="alertClass" v-if="alertMessage">
          {{ alertMessage }}
        </div>

        <!-- Grading组件 -->
        <Grading
          v-if="quizId != null && studentNumber != null"
          :quiz_id="quizId"
          :student_number="studentNumber"
          @grading-completed="goBackToQuizGrading"
        ></Grading>
      </div>
    </div>
  </div>
</template>

<script>
import Grading from "@/components/Grading.vue";
import { has_submitted_quiz } from "@/http/api.js";
export default {
  name: "DetailGrading",
  components: {
    Grading,
  },
  data() {
    return {
      courseId: null,
      quizId: null,
      studentNumber: null,
      quizTitle: "",
      studentInfo: {},
      quizData: [],
      studentAnswers: [],
      alertMessage: "",
      alertClass: "alert-success",
      showSummary: false,
    };
  },
  methods: {
    //初始化批改信息
    init_grading(quizId, studentNumber) {
      const identifier_arr = [];
      identifier_arr.push(studentNumber);
      console.log(identifier_arr);

      const params = {
        quiz_id: quizId,
        identifier_arr: identifier_arr,
      };
      has_submitted_quiz(params).then((response) => {
        this.quizTitle = response.data.quiz_title;
        this.studentInfo = response.data.result_list[0];
      });
    },

    // 返回批改列表
    goBackToQuizGrading() {
      this.$router.push(`/quiz_grading/${this.courseId}/${this.quizId}`);
    },

    // 格式化日期时间
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return "";

      try {
        const date = new Date(dateTimeStr);

        if (isNaN(date.getTime())) {
          return dateTimeStr;
        }

        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");

        return `${year}-${month}-${day} ${hours}:${minutes}`;
      } catch (error) {
        console.error("日期格式转换错误:", error);
        return dateTimeStr;
      }
    },

    // 保存批改
    saveGrading() {
      console.log("保存批改");
      this.showAlert("批改已保存", "alert-success");
    },

    // 提交批改结果
    submitGrading() {
      console.log("提交批改结果");
      this.showAlert("批改结果已提交", "alert-success");
    },

    // 处理批改完成事件
    handleGradingComplete(gradingData) {
      console.log("批改完成:", gradingData);
      this.showSummary = true;
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
    this.courseId = this.$route.params.courseId;
    this.quizId = this.$route.params.quizId;
    this.studentNumber = this.$route.params.studentNumber;
    this.init_grading(this.quizId, this.studentNumber);
  },
};
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.detail-grading-page {
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
  flex-direction: column;
  gap: 20px;
}

.page-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 25px;
  margin-bottom: 10px;
}

.student-info-section h2 {
  color: #2980b9;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
}

.student-details {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.detail-label {
  font-weight: 500;
  color: #555;
}

.detail-value {
  font-weight: 400;
}

.submitted {
  color: #27ae60;
  font-weight: 500;
}

.not-submitted {
  color: #e74c3c;
  font-weight: 500;
}

.actions-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.action-buttons button {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-save {
  background-color: #3498db;
  color: white;
}

.btn-save:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
}

.btn-submit {
  background-color: #2ecc71;
  color: white;
}

.btn-submit:hover {
  background-color: #27ae60;
  transform: translateY(-2px);
}

.btn-cancel {
  background-color: #e74c3c;
  color: white;
}

.btn-cancel:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
}

.no-submission {
  padding: 40px;
  text-align: center;
  color: #7f8c8d;
  font-size: 1.1rem;
}

.grading-summary {
  border-top: 1px solid #eee;
  padding-top: 20px;
  margin-top: 10px;
}

.grading-summary h3 {
  color: #2c3e50;
  margin-bottom: 15px;
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
</style>
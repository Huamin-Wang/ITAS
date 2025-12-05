<template>
  <div class="quiz-container">
    <h2 class="quiz-title">{{ quiz.title }}</h2>
    <div class="quiz-detail">
      <p class="quiz-description">{{ quiz.description }}</p>
      <p class="quiz-description">
        截止时间：{{ formatDateTime(quiz.end_time) }}
      </p>
    </div>
    <div class="quiz-questions">
      <div
        class="question-item"
        v-for="(question, index) in questions"
        :key="question.id"
      >
        <h3 class="question-title">
          {{ index + 1 }}. {{ question.question_text }}
          <span class="points">（{{ question.points }} 分）</span>
        </h3>

        <!-- 单选题 -->
        <div v-if="question.question_type === 'single_choice'">
          <label
            class="option"
            v-for="(opt, optIndex) in question.options"
            :key="optIndex"
          >
            <input
              type="radio"
              :name="'q' + question.id"
              :value="String.fromCharCode(65 + optIndex)"
              v-model="question.student_answer"
            />
            {{ String.fromCharCode(65 + optIndex) }}. {{ opt }}
          </label>
        </div>

        <!-- 多选题 -->
        <div v-else-if="question.question_type === 'multiple_choice'">
          <label
            class="option"
            v-for="(opt, optIndex) in question.options"
            :key="optIndex"
          >
            <input
              type="checkbox"
              :value="String.fromCharCode(65 + optIndex)"
              v-model="question.student_answer"
            />
            {{ String.fromCharCode(65 + optIndex) }}. {{ opt }}
          </label>
        </div>

        <!-- 判断题 -->
        <div v-else-if="question.question_type === 'true_false'">
          <label class="option">
            <input
              type="radio"
              :name="'q' + question.id"
              value="true"
              v-model="question.student_answer"
            />
            正确
          </label>
          <label class="option">
            <input
              type="radio"
              :name="'q' + question.id"
              value="false"
              v-model="question.student_answer"
            />
            错误
          </label>
        </div>

        <!-- 简答题 -->
        <div v-else-if="question.question_type === 'short_answer'">
          <textarea
            class="short-answer"
            placeholder="请输入你的回答"
            v-model="question.student_answer"
          ></textarea>
        </div>
      </div>
    </div>

    <div class="actions">
      <button class="btn btn-submit" @click="submitQuiz">提交小测</button>
      <button class="btn btn-back" @click="go_to_student_profile()">
        返回
      </button>
    </div>
  </div>
</template>

<script>
import { get_quiz_questions, submit_quiz } from "@/http/api.js";

export default {
  name: "StudentQuizPage",
  data() {
    return {
      quiz: {},
      questions: [],
    };
  },
  mounted() {
    this.loadQuizData();
  },
  methods: {
    async loadQuizData() {
      try {
        const quizId = this.$route.params.quizId;
        const res = await get_quiz_questions(quizId);

        this.quiz = res.data.quiz;
        this.questions = res.data.questions;

        // 初始化 answers
        this.questions = res.data.questions.map((q) => ({
          ...q,
          student_answer:
            q.question_type === "multiple_choice"
              ? [] // 多选题必须是数组
              : "", // 单选、判断、简答是字符串
        }));
        console.log(this.questions);
      } catch (error) {
        console.error("加载小测失败：", error);
        this.$message.error("加载小测失败");
      }
    },

    submitQuiz() {
      if (!this.questions || this.questions.length === 0) {
        this.$message.error("没有题目可提交");
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
          quiz_id: q.quiz_id,
          question_id: q.id,
          student_answer: finalAnswer,
          student_id: JSON.parse(localStorage.getItem("userInfo")).user_id,
        };
      });

      console.log("最终提交：", submitData); // 你应该在此能看到 "A,B"

      submit_quiz(submitData)
        .then(() => {
          this.$router.push("/student_profile");
          this.$message.success("提交成功！");
        })
        .catch(() => {
          this.$message.error("提交失败");
        });
    },
    formatDateTime(isoString) {
      if (!isoString) return "";
      return isoString.slice(0, 16).replace("T", " ");
    },
    go_to_student_profile() {
      this.$router.push("/student_profile");
    },
  },
};
</script>

<style scoped>
.quiz-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quiz-title {
  font-size: 1.8rem;
  color: #2c3e50;
  margin-left: 10px;
}
.quiz-detail {
  display: flex;
  justify-content: space-between;
}
.quiz-description {
  color: #7f8c8d;
  margin-bottom: 20px;
  margin-left: 10px;
}

.question-item {
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  border: 1px solid #e8e8e8;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.question-title {
  margin-bottom: 10px;
  font-size: 1.1rem;
}

.points {
  color: #3498db;
  font-size: 0.9rem;
}

.option {
  display: flex;
  align-items: center;
  margin: 8px 0;
  cursor: pointer;
}

.short-answer {
  width: 100%;
  min-height: 100px;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-submit {
  background: #3498db;
  color: white;
}

.btn-back {
  background: #bdc3c7;
  color: white;
}
</style>

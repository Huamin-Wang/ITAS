<template>
  <div class="ranking-page">
    <span @click="go_to_add_score()" class="back-home">返回</span>
    <div class="container">
      <div class="header">
        <h1>课程名称 - 学生成绩排名</h1>
        <div class="actions">
          <button class="btn btn-outline" @click="printRanking">
            <i class="fas fa-print"></i> 打印排名
          </button>

          <button class="btn btn-outline" @click="refreshRanking">
            <i class="fas fa-sync-alt"></i> 刷新成绩
          </button>
        </div>
      </div>

      <div class="info-panel">
        <i class="fas fa-info-circle"></i>
        本排名根据最终成绩排序，更新时间：{{ updateTime }}
      </div>

      <div class="course-stats">
        <div class="stat-card">
          <div class="stat-value">{{ displayStudents.length }}</div>
          <div class="stat-label">参与学生</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ averageScore.toFixed(1) }}</div>
          <div class="stat-label">平均分</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ maxScore }}</div>
          <div class="stat-label">最高分</div>
        </div>
      </div>

      <div class="search-box">
        <input
          type="text"
          v-model="searchQuery"
          class="search-input"
          placeholder="搜索学生姓名..."
        />
      </div>

      <table id="rankingTable">
        <thead>
          <tr>
            <th width="10%">排名</th>
            <th width="30%">学生姓名</th>
            <th width="30%">学号</th>
            <th width="20%">成绩</th>
            <th width="20%">等级</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(student, index) in displayStudents"
            :key="student.student_number"
            :class="{ 'top-3': student.rank <= 3 }"
          >
            <td>
              <i
                v-if="student.rank === 1"
                class="fas fa-trophy"
                style="color: gold"
              ></i>
              <i
                v-else-if="student.rank === 2"
                class="fas fa-trophy"
                style="color: silver"
              ></i>
              <i
                v-else-if="student.rank === 3"
                class="fas fa-trophy"
                style="color: #cd7f32"
              ></i>
              <span v-else>{{ student.rank }}</span>
            </td>
            <td>{{ student.student_name }}</td>
            <td>{{ student.student_number }}</td>
            <td class="score">{{ student.score }}</td>
            <td>
              <span class="badge" :class="getGradeClass(student.score)">{{
                getGradeText(student.score)
              }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ranking } from "@/http/api.js";

export default {
  data() {
    return {
      students: [],
      searchQuery: "",
      updateTime: "--",
    };
  },
  computed: {
    // 计算显示的学生列表（包含搜索过滤）
    displayStudents() {
      if (!this.searchQuery) {
        return this.students;
      }
      const query = this.searchQuery.toLowerCase();
      return this.students.filter(
        (student) =>
          student.student_name.toLowerCase().includes(query) ||
          student.student_number.toLowerCase().includes(query)
      );
    },
    // 计算平均分
    averageScore() {
      if (this.students.length === 0) return 0;
      const total = this.students.reduce(
        (sum, student) => sum + student.score,
        0
      );
      return total / this.students.length;
    },
    // 计算最高分
    maxScore() {
      if (this.students.length === 0) return 0;
      return Math.max(...this.students.map((student) => student.score));
    },
  },
  methods: {
    // 初始化学生列表
    async init_students() {
      const courseId = this.$route.params.courseId;
      if (courseId) {
        try {
          const response = await ranking(courseId);
          this.processStudentData(response.data);
          this.updateTime = new Date().toLocaleString();
        } catch (error) {
          console.error("获取排名失败:", error);
          this.$message.error("获取排名失败");
        }
      } else {
        this.$message.error("未提供课程ID");
      }
    },
    // 处理学生数据，计算排名
    processStudentData(students) {
      // 按成绩降序排序
      const sortedStudents = [...students].sort((a, b) => b.score - a.score);

      // 计算排名（处理相同成绩的情况）
      let currentRank = 1;
      let previousScore = null;
      let skipCount = 0;

      sortedStudents.forEach((student, index) => {
        if (student.score === previousScore) {
          // 成绩相同，排名相同
          student.rank = currentRank;
          skipCount++;
        } else {
          // 成绩不同，更新排名
          currentRank += skipCount + 1;
          skipCount = 0;
          student.rank = currentRank;
          previousScore = student.score;
        }
      });

      this.students = sortedStudents;
    },
    // 根据分数获取等级文本
    getGradeText(score) {
      if (score >= 90) return "优秀";
      if (score >= 80) return "良好";
      if (score >= 70) return "中等";
      if (score >= 60) return "及格";
      return "不及格";
    },
    // 根据分数获取等级样式类
    getGradeClass(score) {
      if (score >= 90) return "badge-top";
      if (score >= 70) return "badge-middle";
      return "badge-bottom";
    },
    // 打印排名
    printRanking() {
      window.print();
    },
    // 刷新排名
    refreshRanking() {
      this.init_students();
    },
    //跳转加分页面
    go_to_add_score() {
      const courseId = this.$route.params.courseId;
      this.$router.push(`/add_score/${courseId}`);
    },
  },
  mounted() {
    this.init_students();
  },
};
</script>

<style scoped>
/* 原有的样式保持不变，只添加必要的样式 */
.ranking-page {
  position: relative;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  background-color: #f5f5f5;
  margin: 0;
  padding: 0;
  color: #333;
}

.container {
  width: 90%;
  max-width: 1200px;
  margin: 20px auto;
  padding: 25px;
  background-color: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e8e8e8;
}

h1 {
  color: #1890ff;
  margin: 0;
  font-size: 24px;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #1890ff;
  color: white;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #40a9ff;
}

.btn-outline {
  background-color: transparent;
  border: 1px solid #1890ff;
  color: #1890ff;
}

.btn-outline:hover {
  background-color: rgba(24, 144, 255, 0.1);
}

.info-panel {
  background-color: #e6f7ff;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 20px;
  border-left: 4px solid #1890ff;
}

.course-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  background: white;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
}

th,
td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

th {
  background-color: #fafafa;
  font-weight: 600;
}

tr:hover {
  background-color: #f5f5f5;
}

.badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: white;
}

.badge-top {
  background-color: #52c41a;
}

.badge-middle {
  background-color: #faad14;
}

.badge-bottom {
  background-color: #f5222d;
}

.score {
  font-weight: bold;
}

.top-3 {
  background-color: rgba(82, 196, 26, 0.1);
}

.search-box {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.search-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  gap: 5px;
}

.page-btn {
  padding: 5px 10px;
  border: 1px solid #e8e8e8;
  background-color: white;
  cursor: pointer;
  border-radius: 4px;
}

.page-btn.active {
  background-color: #1890ff;
  color: white;
  border-color: #1890ff;
}

@media (max-width: 768px) {
  .container {
    width: 95%;
    padding: 15px;
  }

  .course-stats {
    flex-direction: column;
    gap: 10px;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  table {
    font-size: 14px;
  }

  th,
  td {
    padding: 8px 10px;
  }
}

.back-home {
  position: fixed;
  top: 10px;
  left: 10px;
  padding: 0.4rem 1rem;
  background-color: #4299e1;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 200;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(66, 153, 225, 0.1);
  z-index: 1000;
}

.back-home:hover {
  background-color: #2acb11;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(66, 153, 225, 0.2);
}
</style>
<template>
  <div class="student-select-page">
    <header>
      <span @click="go_to_course_manager(this.course_id)" class="back-to-home"
        >返回课程</span
      >
      <h1>分析管理</h1>
      <p>选择学生查看详细学习分析报告</p>
    </header>

    <div class="container">
      <div class="page-controls">
        <div class="search-bar">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="搜索学生姓名或学号"
            @input="filterStudents"
            class="search-input"
          />
          <span class="search-icon">🔍</span>
        </div>

        <div class="filter-controls">
          <div class="filter-tags">
            <span
              v-for="tag in filterTags"
              :key="tag"
              :class="['filter-tag', { active: activeFilter === tag }]"
              @click="toggleFilter(tag)"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在加载学生数据...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">!</div>
        <p>{{ error }}</p>
        <button class="action-button" @click="fetchStudents">重试</button>
      </div>

      <!-- 空状态 -->
      <div v-else-if="filteredStudents.length === 0" class="empty-state">
        <div class="empty-icon">📚</div>
        <h3>未找到学生</h3>
        <p>没有找到匹配搜索条件的学生</p>
        <button class="action-button" @click="clearFilters">
          清除筛选条件
        </button>
      </div>

      <!-- 学生列表 -->
      <div v-else class="students-container">
        <div class="students-grid">
          <div
            v-for="student in paginatedStudents"
            :key="student.student_number"
            class="student-card"
            @click="viewStudentAnalysis(student.student_number)"
          >
            <div class="student-avatar">
              {{ student.student_name?.charAt(0) || "?" }}
            </div>
            <div class="student-info">
              <h3>{{ student.student_name || "未知学生" }}</h3>
              <p class="student-id">学号: {{ student.student_number }}</p>
              <!-- <div class="student-stats">
                <div class="stat-item">
                  <span class="stat-label">学习状态</span>
                  <span :class="['stat-value', getStatusClass(student.status)]">
                    {{ student.status }}
                  </span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">得分率</span>
                  <span class="stat-value">{{ student.scoreRate }}</span>
                </div>
              </div> -->
              <!-- <div class="student-tags">
                <span v-if="student.hasWeakness" class="tag weakness-tag"
                  >有薄弱点</span
                >
                <span v-if="student.needsAttention" class="tag attention-tag"
                  >需关注</span
                >
                <span v-if="student.recentActive" class="tag active-tag"
                  >活跃</span
                >
              </div> -->
            </div>
            <div class="view-analysis-btn">
              <span>查看分析 →</span>
            </div>
          </div>
        </div>

        <!-- 分页控制（如果数据多） -->
        <div class="pagination" v-if="totalPages > 1">
          <button
            class="page-btn"
            :disabled="currentPage === 1"
            @click="prevPage"
          >
            上一页
          </button>
          <span class="page-info"
            >第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span
          >
          <button
            class="page-btn"
            :disabled="currentPage === totalPages"
            @click="nextPage"
          >
            下一页
          </button>
        </div>
      </div>

      <!-- <div class="summary-section">
        <h2 class="section-title">班级学习概况</h2>
        <div class="summary-cards">
          <div class="summary-card">
            <div class="summary-icon">👨‍🎓</div>
            <div class="summary-content">
              <h4>学生总数</h4>
              <p class="summary-number">{{ totalStudents }}</p>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">📈</div>
            <div class="summary-content">
              <h4>平均得分率</h4>
              <p class="summary-number">{{ averageScoreRate }}</p>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">⚠️</div>
            <div class="summary-content">
              <h4>需关注学生</h4>
              <p class="summary-number">{{ studentsNeedingAttention }}</p>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">🎯</div>
            <div class="summary-content">
              <h4>有薄弱点学生</h4>
              <p class="summary-number">{{ studentsWithWeakness }}</p>
            </div>
          </div>
        </div>
      </div> -->
    </div>

    <footer>
      <p>&copy; 2025 基于大模型的智能教学辅助系统. All Rights Reserved.</p>
    </footer>
  </div>
</template>

<script>
import { course_students } from "@/http/api.js";
export default {
  name: "StudentSelect",
  data() {
    return {
      loading: true,
      error: null,
      searchQuery: "",
      activeFilter: "全部",
      course_id: null,
      filterTags: [
        "全部",
        // "需关注",
        // "有薄弱点",
        // "学习困难",
        // "学习优秀",
        // "近期活跃",
      ],
      currentPage: 1,
      pageSize: 12,
      allStudents: [], // 原始学生数据
      filteredStudents: [], // 过滤后的学生数据

      // 统计信息
      totalStudents: 0,
      averageScoreRate: "75.2%",
      studentsNeedingAttention: 0,
      studentsWithWeakness: 0,
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.filteredStudents.length / this.pageSize);
    },
    paginatedStudents() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredStudents.slice(start, end);
    },
  },
  methods: {
    async fetchStudents(courseId) {
      this.loading = true;
      this.error = null;

      try {
        const response = await course_students(courseId);

        if (response.data) {
          this.allStudents = [
            ...(response.data.enrolled_students || []),
            ...(response.data.not_enrolled_students || []),
          ];
          this.filteredStudents = [...this.allStudents];
          this.totalStudents = this.allStudents.length;

          // 确保数据格式正确
          this.allStudents.forEach((student) => {
            student.student_name = student.student_name || "";
            student.student_number = student.student_number || "";
          });
        } else {
          this.allStudents = [];
          this.filteredStudents = [];
          this.totalStudents = 0;
        }
      } catch (err) {
        console.error("加载学生数据失败:", err);
        this.error = "加载学生数据失败，请稍后重试";
        this.allStudents = [];
        this.filteredStudents = [];
      } finally {
        this.loading = false;
      }
    },

    filterStudents() {
      if (!this.searchQuery.trim()) {
        // 如果搜索框为空，显示所有学生
        this.filteredStudents = [...this.allStudents];
      } else {
        const query = this.searchQuery.trim().toLowerCase();

        // 模糊搜索：检查姓名或学号是否包含搜索关键词
        this.filteredStudents = this.allStudents.filter((student) => {
          // 获取学生姓名和学号，确保它们是字符串
          const name = (student.student_name || "").toLowerCase();
          const number = (student.student_number || "").toLowerCase();

          // 检查是否包含搜索关键词
          return name.includes(query) || number.includes(query);
        });
      }

      // 重置到第一页
      this.currentPage = 1;

      // 应用筛选标签
      this.applyFilter();
    },

    toggleFilter(tag) {
      this.activeFilter = tag;
      this.applyFilter();
    },

    applyFilter() {
      // 首先根据搜索条件过滤
      let result = this.allStudents;

      if (this.searchQuery.trim()) {
        const query = this.searchQuery.trim().toLowerCase();
        result = result.filter((student) => {
          const name = (student.student_name || "").toLowerCase();
          const number = (student.student_number || "").toLowerCase();
          return name.includes(query) || number.includes(query);
        });
      }

      // 然后根据筛选标签过滤
      switch (this.activeFilter) {
        case "全部":
          // 保持原样
          break;
        // 可以根据需要添加其他筛选条件
        // case "需关注":
        //   result = result.filter(student => student.needsAttention);
        //   break;
        default:
          // 对于未实现的筛选条件，显示全部
          break;
      }

      this.filteredStudents = result;
      this.currentPage = 1; // 重置到第一页
    },

    clearFilters() {
      this.searchQuery = "";
      this.activeFilter = "全部";
      this.filteredStudents = [...this.allStudents];
      this.currentPage = 1;
    },

    viewStudentAnalysis(studentNumber) {
      const courseId = this.$route.params.courseId;
      this.$router.push({
        name: "course_analysis",
        params: {
          courseId: courseId,
          studentNumber: studentNumber,
        },
      });
    },

    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    },

    // 跳转课程管理
    go_to_course_manager(id) {
      this.$router.push(`/course_manager/${id}`);
    },
  },
  mounted() {
    const courseId = this.$route.params.courseId;
    this.course_id = this.$route.params.courseId;
    this.fetchStudents(courseId);
  },
};
</script>

<style scoped>
.student-select-page {
  font-family: "Arial", sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f5f5f5;
  color: #333;
  min-height: 100vh;
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

header p {
  margin: 10px 0 0;
  opacity: 0.9;
}

.container {
  width: 90%;
  max-width: 1200px;
  margin: 20px auto;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.page-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.search-bar {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-input {
  width: 100%;
  padding: 12px 20px 12px 40px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.filter-controls {
  display: flex;
  align-items: center;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-tag {
  padding: 6px 12px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #d9d9d9;
}

.filter-tag:hover {
  background-color: #e6f7ff;
  border-color: #1890ff;
  color: #1890ff;
}

.filter-tag.active {
  background-color: #1890ff;
  color: white;
  border-color: #1890ff;
}

.loading-container,
.error-container,
.empty-state {
  text-align: center;
  padding: 60px 0;
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

.empty-state {
  padding: 40px 0;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px;
  color: #666;
}

.empty-state p {
  margin: 0 0 20px;
  color: #999;
}

.students-container {
  margin-bottom: 30px;
}

.students-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.student-card {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.student-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border-color: #1890ff;
}

.student-avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2em;
  font-weight: bold;
  margin-right: 15px;
  flex-shrink: 0;
}

.student-info {
  flex: 1;
}

.student-info h3 {
  margin: 0 0 5px;
  color: #1890ff;
  font-size: 1.2em;
}

.student-id {
  margin: 0 0 10px;
  color: #666;
  font-size: 0.9em;
}

.student-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.8em;
  color: #999;
  margin-bottom: 2px;
}

.stat-value {
  font-weight: bold;
  font-size: 0.95em;
}

.status-excellent {
  color: #52c41a;
}

.status-good {
  color: #1890ff;
}

.status-normal {
  color: #faad14;
}

.status-poor {
  color: #ff4d4f;
}

.student-tags {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 0.75em;
  font-weight: 500;
}

.weakness-tag {
  background-color: #fff2e8;
  color: #fa541c;
}

.attention-tag {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.active-tag {
  background-color: #f6ffed;
  color: #52c41a;
}

.view-analysis-btn {
  color: #1890ff;
  font-weight: 500;
  font-size: 0.9em;
  transition: all 0.3s;
  opacity: 0;
  transform: translateX(10px);
}

.student-card:hover .view-analysis-btn {
  opacity: 1;
  transform: translateX(0);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.page-btn {
  padding: 8px 16px;
  background-color: #f5f5f5;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background-color: #e6f7ff;
  border-color: #1890ff;
  color: #1890ff;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
}

.summary-section {
  margin-top: 40px;
}

.section-title {
  color: #1890ff;
  border-bottom: 2px solid #1890ff;
  padding-bottom: 10px;
  margin-top: 25px;
  margin-bottom: 20px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.summary-card {
  background-color: #f0f8ff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  border-left: 4px solid #1890ff;
}

.summary-icon {
  font-size: 32px;
  margin-right: 15px;
}

.summary-content h4 {
  margin: 0 0 5px;
  color: #666;
  font-size: 0.95em;
}

.summary-number {
  margin: 0;
  font-size: 1.5em;
  font-weight: bold;
  color: #1890ff;
}

footer {
  background-color: #001529;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 20px 0;
  margin-top: 30px;
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

@media (max-width: 768px) {
  .container {
    width: 95%;
    padding: 15px;
  }

  .page-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .search-bar {
    min-width: 100%;
  }

  .students-grid {
    grid-template-columns: 1fr;
  }

  .summary-cards {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 480px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
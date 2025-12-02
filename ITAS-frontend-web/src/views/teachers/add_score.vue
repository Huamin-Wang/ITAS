<template>
  <!-- 模板部分保持不变 -->
  <div class="add-score-page">
    <span @click="go_to_course_manager(this.course.id)" class="back-home"
      >返回课程</span
    >
    <div class="container">
      <div class="card">
        <div class="header">
          <h1>{{ this.course.name }}- 问答成绩管理</h1>
          <div class="header-actions">
            <span
              @click="go_to_ranking(this.course.id)"
              class="action-btn rank-btn"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                style="margin-right: 6px"
              >
                <polygon
                  points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                />
              </svg>
              查看排名
            </span>
          </div>
        </div>

        <div class="recent-scores-container">
          <div>
            <form>
              <div class="search-container">
                <input
                  type="text"
                  class="search-input"
                  id="search"
                  placeholder="输入学号或姓名搜索学生"
                  autocomplete="off"
                  v-model="search_info"
                  @input="search_student()"
                />
              </div>

              <ul class="student-list" id="student-list">
                <li
                  class="student-item"
                  data-student=""
                  v-for="student in this.filter_students"
                >
                  <div class="student-info">
                    <span
                      ><strong>学号:</strong>
                      {{ student.student_number }}
                    </span>
                    <span
                      ><strong>姓名:</strong>
                      {{ student.student_name }}
                    </span>
                    <span>
                      <strong>备注:</strong>
                      <input
                        type="text"
                        class="remark-input"
                        v-model="student.remark"
                        @change="update_record(student.id, student.remark)"
                        placeholder="输入备注"
                      />
                    </span>

                    <span class="score-badge current-score"
                      >当前分值: {{ student.score }}</span
                    >
                    <span class="score-badge score-change"></span>
                  </div>
                  <input
                    type="number"
                    class="score-input"
                    name="score_"
                    data-student-number=""
                    placeholder="输入分数"
                    value="0"
                    step="0.5"
                    @change.lazy="add_student_to_list(student, $event)"
                  />
                </li>
              </ul>

              <div class="submit-container">
                <button
                  type="button"
                  class="btn btn-primary"
                  @click="update_score()"
                >
                  <!-- <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="16"></line>
                    <line x1="8" y1="12" x2="16" y2="12"></line>
                  </svg> -->
                  确定提交
                </button>
                <!-- <button
                  type="button"
                  class="btn btn-danger"
                  onclick="confirmSubmit()"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="8" y1="12" x2="16" y2="12"></line>
                  </svg>
                  扣除分数
                </button> -->
              </div>
              <div class="shortcut-hint">键盘快捷键: Ctrl+S = 提交增加分数</div>
            </form>
          </div>

          <div class="recent-scores">
            <h2>最近操作记录</h2>
            <ul class="student-list" v-if="operation_list.length > 0">
              <li class="student-item" v-for="operation in operation_list">
                <span>{{ operation.student_name }}</span>
                <span
                  class="score-badge"
                  :class="
                    operation.score_change < 0
                      ? 'score-negative'
                      : 'score-positive'
                  "
                >
                  {{ operation.score_change }}分
                </span>
              </li>
            </ul>
            <p class="no-records" v-else>暂无记录</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import {
  get_course_by_id,
  course_students,
  update_score,
  update_record,
} from "@/http/api.js";
export default {
  data() {
    return {
      course: {},
      course_students: {},
      students: {},
      filter_students: [],
      score_change_list: [],
      operation_list: [],
      search_info: "",
    };
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

    //初始化课程学生名单
    init_course_students() {
      const courseId = this.$route.params.courseId;
      course_students(courseId)
        .then((response) => {
          this.course_students = response.data;
          this.students = this.course_students.enrolled_students.concat(
            this.course_students.not_enrolled_students
          );
          this.filter_students = this.students;
        })
        .catch((error) => {
          console.error("获取课程学生数失败:", error);
        });
    },

    //添加学生到分数变更列表
    add_student_to_list(student, event) {
      // 获取输入的分数值
      const scoreValue = parseFloat(event.target.value) || 0;

      // 检查该学生是否已经在变更列表中
      const existingIndex = this.score_change_list.findIndex(
        (item) => item.student_number === student.student_number
      );

      if (existingIndex !== -1) {
        // 如果学生已存在，更新分数
        this.score_change_list[existingIndex].score_change = scoreValue;
        console.log(
          `更新学生 ${student.student_name} 的分数变更为: ${scoreValue}`
        );
      } else {
        // 如果学生不存在，添加新记录
        this.score_change_list.push({
          student_name: student.student_name,
          student_number: student.student_number,
          score_change: scoreValue,
        });
      }
      console.log("当前分数变更列表:", this.score_change_list);
    },

    //更新学生分数
    update_score() {
      const data = {
        course_id: this.$route.params.courseId,
        list: this.score_change_list,
      };
      update_score(data)
        .then((response) => {
          this.operation_list = response.data;
          this.init_course_students();
        })
        .catch((error) => {
          console.error("更新学生分数失败:", error);
        });
    },

    //搜索学生
    search_student() {
      this.filter_students = this.students.filter((student) => {
        const studentNumber = student.student_number
          ? student.student_number.toString().toLowerCase()
          : "";
        const studentName = student.student_name
          ? student.student_name.toLowerCase()
          : "";
        return (
          studentNumber.includes(this.search_info) ||
          studentName.includes(this.search_info)
        );
      });
    },

    //返回课程管理
    go_to_course_manager(courseId) {
      this.$router.push({ path: `/course_manager/${courseId}` });
    },

    //跳转学生排名
    go_to_ranking(courseId) {
      this.$router.push({ path: `/ranking/${courseId}` });
    },
    //修改备注
    update_record(course_student_id, remark) {
      const courseId = this.$route.params.courseId;
      const teacherId = JSON.parse(localStorage.getItem("userInfo")).user_id;
      const data = {
        course_student_id: course_student_id,
        remark: remark,
        course_id: courseId,
        teacher_id: teacherId,
      };
      update_record(data)
        .then((response) => {
          this.$message.success("备注更新成功");
        })
        .catch((error) => {
          console.error("更新备注失败:", error);
          this.$message.error("更新备注失败");
        });
    },
  },
  mounted() {
    this.init_course();
    this.init_course_students();
  },
};
</script>
<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.add-score-page {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  line-height: 1.6;
  color: #2d3748;
  background: #f7f9fc;
  padding: 0;
  margin: 0;
  min-height: 100vh;
}

.container {
  max-width: 1500px;
  margin: 2rem auto;
  padding: 0 1rem;
  animation: fadeIn 0.4s ease;
}

.card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
}

/* 优化备注输入框样式（仅视觉，不影响逻辑） */
.remark-input {
  width: 150px;
  padding: 6px 10px;
  border: 1.5px solid #cbd5e0; /* 浅灰 */
  border-radius: 6px;
  background-color: #f9fafb;
  font-size: 0.85rem;
  color: #2d3748;
  transition: all 0.2s ease;
  margin-left: 10px;
}

/* hover 更显可编辑 */
.remark-input:hover {
  background-color: #ffffff;
  border-color: #a0aec0;
}

/* 聚焦时蓝色高亮，与系统主色调一致 */
.remark-input:focus {
  outline: none;
  background-color: #ffffff;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.25);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
  position: relative;
}

.header h1 {
  font-size: 1.8rem;
  color: #3182ce;
  margin: 0;
}

.action-btn {
  padding: 0.6rem 1.2rem;
  color: #ffffff;
  background: #4299e1;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.action-btn:hover {
  background: #3182ce;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.back-btn {
  background-color: #48bb78;
}

.back-btn:hover {
  background-color: #2f855a;
}

.rank-btn {
  background-color: #4299e1;
}

.rank-btn:hover {
  background-color: #3182ce;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-container {
  position: sticky;
  top: 0;
  background: #ffffff;
  padding: 1rem;
  z-index: 20;
  border-radius: 8px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background-color: #ffffff;
}

.search-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
}

.student-list {
  list-style: none;
  border-radius: 8px;
  overflow: hidden;
}

.student-item {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
  background-color: #ffffff;
}

.student-item:last-child {
  border-bottom: none;
}

.student-item:hover {
  background-color: rgba(66, 153, 225, 0.05);
}

.student-info {
  display: grid;
  grid-template-columns: 150px 120px auto auto;
  gap: 1.5rem;
  align-items: center;
}

.score-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 500;
  display: inline-block;
}

.current-score {
  background: #ebf8ff;
  color: #4299e1;
}

.score-change {
  display: none;
  animation: slideIn 0.3s ease;
}

.score-positive {
  background: #c6f6d5;
  color: #2f855a;
}

.score-negative {
  background: #fed7d7;
  color: #c53030;
}

@keyframes slideIn {
  from {
    transform: translateX(-10px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.score-input {
  width: 120px;
  padding: 0.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  text-align: center;
}

.score-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
}

.submit-container {
  position: sticky;
  bottom: 0;
  background: #ffffff;
  padding: 1rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  z-index: 10;
  border-radius: 8px;
  margin-top: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  min-width: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  background: #4299e1;
  color: #ffffff;
}

.btn-primary:hover {
  background: #3182ce;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn-danger {
  background: #e53e3e;
  color: #ffffff;
}

.btn-danger:hover {
  background: #c53030;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.recent-scores {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  z-index: 30;
  max-height: 80vh;
  overflow-y: auto;
  margin-top: 2rem;
}

.recent-scores h2 {
  margin-bottom: 1rem;
  color: #3182ce;
  font-size: 1.4rem;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

.no-records {
  color: #718096;
  font-style: italic;
  text-align: center;
  padding: 1rem;
}

.shortcut-hint {
  font-size: 0.85rem;
  color: #718096;
  margin-top: 0.5rem;
  text-align: center;
}

@media (max-width: 768px) {
  .container {
    margin: 1rem auto;
  }

  .card {
    padding: 1rem;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    flex-direction: row;
    width: 100%;
    justify-content: space-between;
  }

  .student-item {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .student-info {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    width: 100%;
  }

  .score-input {
    width: 100%;
  }

  .submit-container {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .action-btn {
    width: auto;
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .student-info {
    grid-template-columns: 100px 100px auto auto;
  }
}

/* For tablets and medium screens */
@media (min-width: 768px) {
  .recent-scores-container {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 1.5rem;
    align-items: start;
  }

  .recent-scores {
    margin-top: 0;
    position: sticky;
    top: 1rem;
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
  cursor: pointer;
}

.back-home:hover {
  background-color: #2acb11;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(66, 153, 225, 0.2);
}
</style>
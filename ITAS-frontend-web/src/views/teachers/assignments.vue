<template>
  <div class="assignments-page">
    <span @click="go_to_course_manager(this.course.id)" class="back-home"
      >返回课程</span
    >
    <div class="container">
      <div class="page-section">
        <h2>
          <b>{{ course.name }}- 作业列表</b>
        </h2>

        <div class="alert alert-{{ category }}"></div>

        <table class="assignment-table">
          <thead>
            <tr>
              <th>作业名称</th>
              <th>作业描述</th>
              <th>截止日期</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="assignment in this.assignments"
              v-if="assignments.length > 0"
            >
              <td>{{ assignment.title }}</td>
              <td>{{ assignment.description }}</td>
              <td>{{ assignment.due_date }}</td>
              <td>
                <span
                  @click="go_to_assignment_detail(assignment.id)"
                  class="btn btn-small"
                  >编辑</span
                >
              </td>
            </tr>
            <tr v-else>
              <td colspan="4" style="text-align: center; padding: 20px">
                暂无作业
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="form-container">
        <h2 class="form-title">发布新作业</h2>
        <form @submit.prevent="submitForm" enctype="multipart/form-data">
          <div class="form-group">
            <label for="title">作业标题</label>
            <input
              type="text"
              id="title"
              name="title"
              maxlength="200"
              required
              placeholder="请输入作业标题"
              v-model="formData.title"
            />
          </div>

          <div class="form-group">
            <label for="description">作业描述</label>
            <textarea
              id="description"
              name="description"
              placeholder="请输入作业详细说明"
              v-model="formData.description"
            ></textarea>
          </div>

          <div class="form-group">
            <label for="due_date">截止日期</label>
            <input
              type="date"
              id="due_date"
              name="due_date"
              required
              v-model="formData.due_date"
            />
          </div>

          <div class="actions">
            <button type="submit" class="btn btn-submit">提交作业</button>
            <span
              @click="go_to_course_manager(this.course.id)"
              class="btn btn-back"
              >返回课程管理</span
            >
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { get_course_by_id, get_assignments, assignments } from "@/http/api.js";
export default {
  name: "Assignments",
  data() {
    return {
      course: {},
      assignments: {},
      formData: {
        title: "",
        description: "",
        due_date: "",
      },
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

    //初始化课程作业列表
    init_assignments() {
      const courseId = this.$route.params.courseId;
      if (courseId) {
        get_assignments(courseId)
          .then((response) => {
            this.assignments = response.data;
          })
          .catch((error) => {
            console.error("获取课程作业列表失败:", error);
            this.$message.error("获取课程作业列表失败");
          });
      } else {
        this.$message.error("未提供课程ID");
      }
    },

    // 跳转课程管理
    go_to_course_manager(id) {
      this.$router.push(`/course_manager/${id}`);
    },

    //创建作业
    async submitForm() {
      try {
        const data = new FormData();
        const teacherId = JSON.parse(
          sessionStorage.getItem("userInfo")
        ).user_id;
        data.append("teacher_id", teacherId);
        data.append("course_id", this.course.id);
        data.append("title", this.formData.title);
        data.append("due_date", this.formData.due_date);
        data.append("description", this.formData.description);
        const response = await assignments(data);
        if (response.code === 200) {
          this.$message.success("作业创建成功！");
          this.init_assignments();
        } else {
          this.$message.error("课程创建失败，请重试。");
        }
      } catch (error) {
        console.error("提交表单时出错:", error);
        this.$message.error("发生错误，请稍后重试。");
      }
    },

    //跳转作业编辑
    go_to_assignment_detail(id) {
      this.$router.push(`/assignment_detail/${id}`);
    },
  },
  mounted() {
    this.init_course();
    this.init_assignments();
  },
};
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.assignments-page {
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  line-height: 1.6;
  background-color: #f5f7fa;
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

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px 20px;
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
.form-group textarea {
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

.btn-submit {
  background-color: #2ecc71;
}

.btn-submit:hover {
  background-color: #27ae60;
}

.btn-back {
  background-color: #95a5a6;
  margin-top: 20px;
}

.btn-back:hover {
  background-color: #7f8c8d;
}

.actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>
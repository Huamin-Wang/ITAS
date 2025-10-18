<template>
  <div class="course_students-page">
    <span @click="go_to_course_manager(this.course.id)" class="back-home"
      >返回课程</span
    >
    <div class="container">
      <!-- 课程信息 -->
      <h1><i class="fas fa-book-open icon"></i>课程: {{ this.course.name }}</h1>
      <p class="course-info">
        <i class="fas fa-info-circle icon"></i>课程代码: {{ this.course.code }}
      </p>
      <!--/* 重新上传学生名单，以新名单为准 */-->
      <button @click="go_to_update_course(this.course.id)">
        更新教务系统学生名单
      </button>
      <!-- 已选课学生名单 -->
      <h2><i class="fas fa-users icon"></i>已注册账号学生名单</h2>
      <p class="count">
        <i class="fas fa-check-circle icon"></i>已注册学生数量:
        {{ this.course_students.enrolled_students_count }}
      </p>
      <button @click="update_registration_status(this.course.id)">
        刷新注册状态
      </button>

      <table>
        <thead>
          <tr>
            <th>学生学号</th>
            <th>学生姓名</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody v-if="enrolled_students.length > 0">
          <tr v-for="student in this.enrolled_students">
            <td>{{ student.student_number }}</td>
            <td>{{ student.student_name }}</td>
            <td>
              <span style="color: #27ae60">{{ student.course_status }}</span>
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr>
            <td colspan="3" style="text-align: center">暂无已注册学生</td>
          </tr>
        </tbody>
      </table>

      <!-- 未选课学生名单 -->
      <h2><i class="fas fa-user-times icon"></i>未加入学生名单</h2>
      <table>
        <thead>
          <tr>
            <th>学号</th>
            <th>学生姓名</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody v-if="not_enrolled_students.length > 0">
          <tr v-for="student in this.not_enrolled_students">
            <td>{{ student.student_number }}</td>
            <td>{{ student.student_name }}</td>
            <td>
              <span style="color: #e74c3c">{{ student.course_status }}</span>
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr>
            <td colspan="3" style="text-align: center">暂无未注册学生</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import {
  get_course_by_id,
  update_registration_status,
  course_students,
} from "@/http/api.js";
export default {
  name: "course_students",
  data() {
    return {
      course: {},
      course_students: {},
      enrolled_students: {},
      not_enrolled_students: {},
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
            document.title = `课程学生名单 - ${courseName}`;
          })
          .catch((error) => {
            console.error("获取课程信息失败:", error);
            this.$message.error("获取课程信息失败");
          });
      } else {
        this.$message.error("未提供课程ID");
      }
    },

    //返回课程管理
    go_to_course_manager(courseId) {
      this.$router.push({ path: `/course_manager/${courseId}` });
    },

    //更新学生注册信息
    update_registration_status(course_id) {
      update_registration_status(course_id)
        .then((response) => {
          this.$message.success("学生注册信息更新成功");
        })
        .catch((error) => {
          console.error("更新学生注册信息失败:", error);
        });
    },

    //初始化课程学生名单
    init_course_students(course_id) {
      course_students(course_id)
        .then((response) => {
          this.course_students = response.data;
          this.enrolled_students = this.course_students.enrolled_students;
          this.not_enrolled_students =
            this.course_students.not_enrolled_students;
        })
        .catch((error) => {
          console.error("获取课程学生数失败:", error);
        });
    },

    //转跳到更新课程信息
    go_to_update_course(course_id) {
      this.$router.push(`/update_course/${course_id}`);
    },
  },
  mounted() {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href =
      "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css";
    document.head.appendChild(link);

    this.init_course();
    this.init_course_students(this.$route.params.courseId);
  },
};
</script>

<style scoped>
/* 全局样式 */
.course_students-page {
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  margin: 0;
  padding: 20px;
  color: #333;
}

/* 容器样式 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 标题样式 */
h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 10px;
}

h2 {
  color: #34495e;
  font-size: 1.8rem;
  margin-top: 30px;
  margin-bottom: 15px;
}

/* 课程信息样式 */
.course-info {
  font-size: 1.1rem;
  color: #7f8c8d;
  margin-bottom: 20px;
}

/* 表格样式 */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

th,
td {
  padding: 12px 15px;
  text-align: left;
}

th {
  background-color: #34495e;
  color: #fff;
  font-weight: 600;
}

td {
  border-bottom: 1px solid #ddd;
}

tr:hover {
  background-color: #f1f1f1;
}

/* 已选课学生数量样式 */
.count {
  font-size: 1.2rem;
  color: #27ae60;
  font-weight: bold;
  margin-top: 10px;
}

/* 按钮样式（可选） */
.btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #3498db;
  color: #fff;
  border-radius: 5px;
  text-decoration: none;
  transition: background-color 0.3s ease;
}

.btn:hover {
  background-color: #2980b9;
}

/* 图标样式 */
.icon {
  margin-right: 8px;
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
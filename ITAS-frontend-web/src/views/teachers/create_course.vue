<template>
  <div class="create-course-page">
    <header>
      <a href="/" class="back-to-home">
        <i class="fas fa-home">返回首页</i>
      </a>
      <h1>创建新课程</h1>
    </header>

    <div class="container">
      <form @submit.prevent="submitForm" enctype="multipart/form-data">
        <!-- 课程名称 -->
        <div class="form-group">
          <label for="course_name">课程名称:</label>
          <input
            type="text"
            id="course_name"
            v-model="formData.course_name"
            required
          />
        </div>

        <!-- 课程代码 -->
        <div class="form-group">
          <label for="course_code">课程代码:</label>
          <input
            type="text"
            id="course_code"
            v-model="formData.course_code"
            required
          />
        </div>

        <!-- 开课学期 -->
        <div class="form-group">
          <label for="semester">开课学期:</label>
          <select id="semester" v-model="formData.semester" required>
            <option value="">请选择学期</option>
            <option
              v-for="semester in semesters"
              :key="semester.value"
              :value="semester.value"
            >
              {{ semester.text }}
            </option>
          </select>
        </div>

        <!-- 开课学生名单 -->
        <div class="form-group">
          <label for="student_list">完整开课学生名单:</label>
          <span class="reminder"
            >（可为空，但如果需要更新上传，注意请上传教务系统完整名单，系统会自动比对，缺则添，多则删）</span
          >
          <div class="file-upload" @click="triggerFileInput">
            <input
              type="file"
              id="student_list"
              ref="fileInput"
              @change="onFileChange"
              accept=".csv,.xlsx"
            />
            <span :class="{ highlight: selectedFileName }">{{
              selectedFileName || "点击上传"
            }}</span>
          </div>
          <div class="hint">
            请从教务系统下载学生名单并上传（支持 .csv格式）
          </div>
          <a href="/static/example_student_list.csv" class="example-file"
            >下载示例文件</a
          >
        </div>

        <!-- 课程介绍 -->
        <div class="form-group">
          <label for="course_description">课程介绍:</label>
          <textarea
            id="course_description"
            v-model="formData.course_description"
            rows="4"
          ></textarea>
          <div class="hint">（可选）填写课程简介，帮助学生了解课程内容。</div>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <button type="button" class="cancel">
            <a href="/teacher_profile">取消</a>
          </button>
          <button type="submit" class="submit">确定</button>
        </div>
      </form>
    </div>

    <footer>
      <p>&copy; 2024 基于大模型的智能教学辅助系统. All Rights Reserved.</p>
    </footer>
  </div>
</template>

<script>
import { create_course } from "@/http/api.js";
export default {
  data() {
    const currentYear = new Date().getFullYear();
    return {
      formData: {
        course_name: this.course?.name || "",
        course_code: this.course?.code || "",
        semester: this.course?.semester || "",
        course_description: "",
      },
      selectedFileName: "",
      semesters: [
        {
          value: `${currentYear - 1}-spring`,
          text: `${currentYear - 1} 春季学期`,
        },
        {
          value: `${currentYear - 1}-fall`,
          text: `${currentYear - 1} 秋季学期`,
        },
        { value: `${currentYear}-spring`, text: `${currentYear} 春季学期` },
        { value: `${currentYear}-fall`, text: `${currentYear} 秋季学期` },
        {
          value: `${currentYear + 1}-spring`,
          text: `${currentYear + 1} 春季学期`,
        },
        {
          value: `${currentYear + 1}-fall`,
          text: `${currentYear + 1} 秋季学期`,
        },
      ],
    };
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    onFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFileName = file.name;
      }
    },

    //创建课程
    async submitForm() {
      try {
        const data = new FormData();
        data.append("teacher_id", this.$route.params.teacherId);
        data.append("course_name", this.formData.course_name);
        data.append("course_code", this.formData.course_code);
        data.append("semester", this.formData.semester);
        data.append("course_description", this.formData.course_description);
        const fileInput = this.$refs.fileInput;
        if (fileInput.files.length > 0) {
          data.append("student_file", fileInput.files[0]);
        }

        const response = await create_course(data);
        if (response.code === 200) {
          this.$message.success("课程创建成功！");
          this.$router.push("/teacher_profile");
        } else {
          this.$message.error("课程创建失败，请重试。");
        }
      } catch (error) {
        console.error("提交表单时出错:", error);
        this.$message.error("发生错误，请稍后重试。");
      }
    },
  },
};
</script>

<style scoped>
.create-course-page {
  font-family: "Microsoft YaHei", sans-serif;
  background-color: #f4f6f8;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

header {
  background: linear-gradient(135deg, #2196f3, #1976d2);
  color: white;
  text-align: center;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
}

header h1 {
  margin: 0;
  font-size: 2.2em;
  font-weight: bold;
}

.back-to-home {
  position: absolute;
  top: 25px;
  left: 25px;
  color: white;
  text-decoration: none;
  font-size: 1.1em;
  display: flex;
  align-items: center;
}

.back-to-home i {
  margin-right: 5px;
}

.container {
  flex: 1;
  width: 90%;
  max-width: 650px;
  margin: 40px auto;
  padding: 30px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  font-size: 1.2em;
  color: #2c3e50;
  margin-bottom: 10px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  font-size: 1.05em;
  border: 1px solid #dfe4ea;
  border-radius: 8px;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #2196f3;
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.form-group .file-upload {
  border: 2px dashed #dfe4ea;
  padding: 25px;
  text-align: center;
  border-radius: 8px;
  background-color: #f9fafb;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.form-group .file-upload:hover {
  border-color: #2196f3;
}

.form-group .file-upload input[type="file"] {
  display: none;
}

.form-group .file-upload span {
  color: #7f8c8d;
}

.form-group .file-upload span.highlight {
  color: #2196f3;
  font-weight: bold;
}

.form-group .hint {
  font-size: 0.95em;
  color: #7f8c8d;
  margin-top: 10px;
}

.form-group .example-file {
  margin-top: 12px;
  font-size: 0.95em;
  color: #2196f3;
  text-decoration: none;
  display: inline-block;
}

.form-group .example-file:hover {
  text-decoration: underline;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 35px;
}

.form-actions button {
  padding: 14px 28px;
  font-size: 1.05em;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.form-actions button.cancel {
  background: #ecf0f1;
  color: #2c3e50;
}

.form-actions button.cancel:hover {
  background: #dfe6e9;
}

.form-actions button.submit {
  background: #2196f3;
  color: white;
}

.form-actions button.submit:hover {
  background: #1976d2;
}

footer {
  background-color: #2c3e50;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 25px 0;
}

@media (max-width: 768px) {
  header h1 {
    font-size: 1.8em;
  }

  .container {
    width: 95%;
    margin: 20px auto;
    padding: 20px;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions button {
    width: 100%;
  }
}

/* 新增提醒样式 */
.reminder {
  color: #ff5722;
  font-size: 0.9em;
  margin-top: 5px;
}
</style>
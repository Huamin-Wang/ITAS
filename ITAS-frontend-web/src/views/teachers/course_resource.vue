<template>
  <div id="app" class="resource-page">
    <!-- 返回课程 -->
    <span @click="goBack" class="back-home">
      <i class="fas fa-arrow-left"></i> 返回课程
    </span>

    <div class="container">
      <div class="left-panel">
        <div class="page-section">
          <h2>
            <b>{{ course.name }} - 教学资源分享</b>
          </h2>

          <!-- 成功 / 失败消息提示 -->
          <div class="alert" :class="alertClass" v-if="alertMessage">
            {{ alertMessage }}
          </div>

          <!-- 分享资源表单 -->
          <div class="form-section">
            <div class="form-item">
              <label>资源标题</label>
              <el-input
                v-model="form.title"
                placeholder="请输入资源标题，例如：高效理解CNN卷积讲解"
              ></el-input>
            </div>

            <div class="form-item">
              <label>资源链接</label>
              <el-input
                v-model="form.url"
                placeholder="粘贴外部网站链接，如：https://www.bilibili.com/video/XXXX"
              ></el-input>
            </div>

            <div class="form-item">
              <label>资源简介（可选）</label>
              <el-input
                type="textarea"
                :rows="4"
                v-model="form.description"
                placeholder="请输入简要描述"
              ></el-input>
            </div>

            <div class="actions">
              <button @click="resetForm" class="btn btn-back">重置</button>
              <button @click="submit" class="btn btn-submit">发布资源</button>
            </div>
          </div>
        </div>

        <!-- 已发布资源列表 -->
        <div class="page-section">
          <h2><b>已分享资源列表</b></h2>

          <table class="resource-table" v-if="resources.length > 0">
            <thead>
              <tr>
                <th>标题</th>
                <th>简介（点击直接跳转）</th>
                <th style="text-align: center">操作</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="item in resources" :key="item.id">
                <td>{{ item.title }}</td>

                <!-- 简介本身是一个可点击超链接 -->
                <td>
                  <a
                    :href="item.url"
                    target="_blank"
                    style="color: #3498db; text-decoration: underline"
                  >
                    {{
                      item.description && item.description.length > 50
                        ? item.description.substring(0, 50) + "..."
                        : item.description || "无简介"
                    }}
                  </a>
                </td>

                <td class="td-btn">
                  <span @click="deleteResource(item.id)" class="btn btn-delete">
                    删除
                  </span>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-else style="text-align: center; padding: 15px">
            暂无资源分享
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <el-dialog v-model="showDeleteDialog" width="350px" title="确认删除">
      <p style="text-align: center; padding: 10px">您确定要删除该资源吗？</p>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDeleteDialog = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete">删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import {
  get_course_by_id,
  get_resources,
  create_resource,
  delete_resource,
} from "@/http/api.js";

export default {
  name: "TeacherResourcePage",
  data() {
    return {
      course: {},
      form: {
        title: "",
        url: "",
        description: "",
      },
      resources: [],
      alertMessage: "",
      alertClass: "alert-success",

      showDeleteDialog: false,
      deleteId: null,
    };
  },

  mounted() {
    this.init_course();
    this.init_resources();
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

    /** 加载已分享的资源 */
    init_resources() {
      const courseId = this.$route.params.courseId;
      get_resources(courseId).then((res) => {
        this.resources = res.data.reverse();
      });
    },

    /** 返回课程主页 */
    goBack() {
      this.$router.push(`/course_manager/${this.course.id}`);
    },

    /** 重置表单 */
    resetForm() {
      this.form = { title: "", url: "", description: "" };
    },

    /** 发布资源 */
    submit() {
      if (!this.form.title || !this.form.url) {
        this.showAlert("标题和链接不能为空！", "alert-danger");
        return;
      }
      const teacherId = JSON.parse(localStorage.getItem("userInfo")).user_id;
      const data = {
        course_id: this.course.id,
        teacher_id: teacherId,
        title: this.form.title,
        url: this.form.url,
        description: this.form.description,
      };

      create_resource(data).then((res) => {
        this.showAlert("资源发布成功", "alert-success");
        this.resetForm();
        this.init_resources();
      });
    },

    /** 点击“删除” */
    deleteResource(id) {
      this.deleteId = id;
      this.showDeleteDialog = true;
    },

    /** 确认删除 */
    confirmDelete() {
      delete_resource({ resource_id: this.deleteId }).then(() => {
        this.showAlert("删除成功", "alert-success");
        this.init_resources();
        this.showDeleteDialog = false;
        this.deleteId = null;
      });
    },

    /** 提示消息 */
    showAlert(message, type) {
      this.alertMessage = message;
      this.alertClass = type;
      setTimeout(() => (this.alertMessage = ""), 3000);
    },
  },
};
</script>

<style scoped>
/* —— 继承你的小测页面同款样式 —— */

* {
  box-sizing: border-box;
}

.resource-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.back-home {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  background-color: #4299e1;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: 0.3s;
}

.back-home:hover {
  background-color: #2acb11;
}

.container {
  display: flex;
  gap: 30px;
}

.left-panel {
  flex: 1;
}

.page-section {
  background: white;
  padding: 25px;
  border-radius: 8px;
  margin-bottom: 25px;
  box-shadow: 1px 2px 10px rgba(0, 0, 0, 0.05);
}

h2 {
  color: #2980b9;
  margin-bottom: 20px;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
}

.actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

/* 按钮样式同小测页面 */
.btn {
  padding: 8px 15px;
  border-radius: 4px;
  background-color: #3498db;
  color: white;
  border: none;
  cursor: pointer;
  transition: 0.3s;
}

.btn:hover {
  background: #2980b9;
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

.btn-delete {
  background-color: #e74c3c;
}

.btn-delete:hover {
  background-color: #c0392b;
}

.td-btn {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.resource-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.resource-table th,
.resource-table td {
  padding: 12px 14px;
}

.resource-table th {
  background-color: #3498db;
  color: white;
}

.resource-table tr:nth-child(even) {
  background-color: #f8f9fa;
}

.resource-table tr:hover {
  background-color: rgba(52, 152, 219, 0.05);
}

/* Alert */
.alert {
  padding: 12px 15px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.alert-success {
  background: rgba(46, 204, 113, 0.15);
  border-left: 4px solid #2ecc71;
  color: #27ae60;
}

.alert-danger {
  background: rgba(231, 76, 60, 0.15);
  border-left: 4px solid #e74c3c;
  color: #c0392b;
}

th,
td {
  padding: 12px 15px;
  text-align: center;
}
</style>

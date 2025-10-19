<template>
  <div class="assignment_detail-page">
    <span @click="go_to_course_assignments(this.formData.course_id)" class="back-home">返回课程</span>
    <div class="container py-4 bg-light rounded">
      <div class="card shadow-sm border-0 rounded-lg">
        <div class="card-header bg-primary text-white py-3">
          <h2 class="mb-0 fs-4"><i class="fas fa-edit me-2"></i>作业详情</h2>
          <a
            href="/course/assignment_detail/{{ assignment.id }}?flag=1"
            class="btn btn-danger shadow-sm"
          >
            <i class="fas fa-trash me-1"></i> 删除作业
          </a>
        </div>
        <div class="card-body p-4">
          <form
            @submit.prevent="submitForm"
            enctype="multipart/form-data"
            class="needs-validation"
            novalidate
          >
            <div class="form-group mb-4">
              <label for="title" class="form-label fw-bold">作业标题</label>
              <input
                type="text"
                class="form-control form-control-lg shadow-sm"
                id="title"
                name="title"
                v-model="formData.title"
                required
              />
              <div class="invalid-feedback">请输入作业标题</div>
            </div>
            <div class="form-group mb-4">
              <label for="description" class="form-label fw-bold"
                >作业描述</label
              >
              <textarea
                class="form-control shadow-sm"
                id="description"
                name="description"
                rows="6"
                required
                v-model="formData.description"
              ></textarea>
              <div class="invalid-feedback">请输入作业描述</div>
            </div>
            <div class="form-group mb-4">
              <label for="due_date" class="form-label fw-bold">截止日期</label>
              <input
                type="date"
                class="form-control shadow-sm"
                id="due_date"
                name="due_date"
                v-model="formData.due_date"
                required
              />
              <div class="invalid-feedback">请选择截止日期</div>
            </div>
            <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
              <span
                @click="go_to_course_assignments(this.formData.course_id)"
                class="btn btn-outline-secondary me-md-2 shadow-sm"
              >
                <i class="fas fa-arrow-left me-1"></i> 返回作业列表
              </span>
              <button type="submit" class="btn btn-primary shadow-sm">
                <i class="fas fa-save me-1"></i> 保存修改
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { get_assignment_by_id, update_assignment } from "@/http/api.js";
export default {
  name: "assignment_detail",
  data() {
    return {
      formData: {
        title: "",
        description: "",
        dur_date: "",
      },
    };
  },
  methods: {
    //初始化作业
    init_assignment() {
      const assignmentId = this.$route.params.assignmentId;
      if (assignmentId) {
        get_assignment_by_id(assignmentId)
          .then((response) => {
            this.formData = response.data;
          })
          .catch((error) => {
            console.error("获取作业信息失败:", error);
            this.$message.error("获取作业信息失败");
          });
      } else {
        this.$message.error("未提供作业ID");
      }
    },

    //编辑作业
    async submitForm() {
      try {
        const data = new FormData();
        data.append('id',this.formData.id);
        data.append("title", this.formData.title);
        data.append("due_date", this.formData.due_date);
        data.append("description", this.formData.description);
        const response = await update_assignment(data);
        if (response.code === 200) {
          this.$message.success("作业编辑成功！");
          this.$router.push(`/assignments/${this.formData.course_id}`);
        } else {
          this.$message.error("作业编辑失败，请重试。");
        }
      } catch (error) {
        console.error("提交表单时出错:", error);
        this.$message.error("发生错误，请稍后重试。");
      }
    },

    //转跳到课程作业页面
    go_to_course_assignments(course_id) {
      this.$router.push(`/assignments/${course_id}`);
    },
  },
  mounted() {
    const link1 = document.createElement("link");
    const link2 = document.createElement("link");
    link1.rel = "stylesheet";
    link1.href =
      "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css";
    link2.rel = "stylesheet";
    link2.href =
      "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css";
    document.head.appendChild(link1);
    document.head.appendChild(link2);

    this.init_assignment();
  },
};
</script>

<style scoped>
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
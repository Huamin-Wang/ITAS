<template>
  <div class="random-select-page">
    <span @click="go_to_course_manager()" class="back-home">返回课程</span>
    <div class="animation-container" id="animationContainer"></div>
    <div class="container">
      <h1>Random Select</h1>

      <div class="name-scroll-container">
        <div class="highlight-zone"></div>
        <div
          class="name-scroll"
          id="nameScroll"
          :style="{ transform: `translateY(-${currentOffset}px)` }"
        >
          <div
            v-for="(student, index) in duplicatedStudents"
            :key="index"
            :data-student-id="student.student_number"
          >
            {{ student.student_name }}
          </div>
        </div>
      </div>

      <!-- 添加"停止滚动"按钮 -->
      <div style="display: flex; justify-content: center; gap: 10px">
        <button
          class="random-button"
          @click="startSelection"
          :disabled="isSelecting"
        >
          开始随机挑选幸运儿
        </button>
        <button
          class="random-button"
          @click="stopSelection"
          :disabled="!isSelecting"
        >
          停止滚动
        </button>
      </div>
      <div
        class="winner-announcement"
        :class="{ show: showWinner }"
        id="winner"
      >
        {{ winnerText }}
      </div>

      <!-- 修改为加分按钮，添加加载状态 -->
      <button
        class="random-button"
        id="addScoreButton"
        v-show="showAddScoreButton"
        @click="addScoreToWinner"
        :disabled="isAddingScore"
      >
        {{ isAddingScore ? "加分中..." : "给幸运观众加分" }}
      </button>

      <!-- 添加分数选择器 -->
      <div v-if="showScoreSelector" class="score-selector">
        <h3>选择加分分数</h3>
        <div class="score-options">
          <button
            v-for="score in scoreOptions"
            :key="score"
            @click="addScoreWithValue(score)"
            class="score-button"
          >
            +{{ score }} 分
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { random_select_list, update_score } from "@/http/api.js";

export default {
  data() {
    return {
      random_list: [],
      isSelecting: false,
      stopRequested: false,
      currentOffset: 0,
      winnerText: "",
      showWinner: false,
      showAddScoreButton: false,
      animationInterval: null,
      selectedStudent: null, // 存储选中的学生信息
      isAddingScore: false, // 加分加载状态
      showScoreSelector: false, // 显示分数选择器
      scoreOptions: [1, 2, 3, 5, 10], // 可选的分数
    };
  },
  computed: {
    // 复制名单使其循环显示
    duplicatedStudents() {
      return [...this.random_list, ...this.random_list];
    },
  },
  methods: {
    // 获取随机选择学生列表
    init_random_select_list() {
      const courseId = this.$route.params.courseId;
      if (courseId) {
        random_select_list(courseId)
          .then((response) => {
            this.random_list = response.data.course_students;
            this.courseName = response.data.course_name || "当前课程";
          })
          .catch((error) => {
            console.error("获取选择列表失败:", error);
            this.$message.error("获取选择列表失败");
          });
      } else {
        this.$message.error("未提供课程ID");
      }
    },

    // 返回课程管理
    go_to_course_manager() {
      const courseId = this.$route.params.courseId;
      this.$router.push({ path: `/course_manager/${courseId}` });
    },

    // 生成随机整数
    getRandomInt(min, max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    },

    // 延时函数
    sleep(ms) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    },

    // 创建星星动画
    createStars() {
      const animationContainer = document.getElementById("animationContainer");
      for (let i = 0; i < 100; i++) {
        const star = document.createElement("div");
        star.className = "star";
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.animationDelay = `${Math.random() * 2}s`;
        animationContainer.appendChild(star);
      }
    },

    // 创建流星动画
    createMeteors() {
      const animationContainer = document.getElementById("animationContainer");
      for (let i = 0; i < 3; i++) {
        const meteor = document.createElement("div");
        meteor.className = "meteor";
        meteor.style.left = `${Math.random() * 100}%`;
        meteor.style.top = `${Math.random() * 100}%`;
        meteor.style.animationDelay = `${Math.random() * 3}s`;
        animationContainer.appendChild(meteor);
      }
    },

    // 开始选择
    async startSelection() {
      if (this.isSelecting) return;

      this.isSelecting = true;
      this.stopRequested = false;
      this.showWinner = false;
      this.showAddScoreButton = false;
      this.showScoreSelector = false;
      this.winnerText = "";
      this.selectedStudent = null;

      const itemHeight = 60; // 每个名字的高度
      const totalHeight = (this.duplicatedStudents.length * itemHeight) / 2;

      // 快速滚动阶段
      let duration = 20;
      for (let i = 0; i < 30; i++) {
        if (this.stopRequested) break;
        this.currentOffset = this.getRandomInt(0, totalHeight);
        await this.sleep(duration);
        duration += 1;
      }

      // 减速滚动阶段
      duration = 50;
      for (let i = 0; i < 20; i++) {
        if (this.stopRequested) break;
        this.currentOffset = this.getRandomInt(0, totalHeight);
        await this.sleep(duration);
        duration += 30;
      }

      // 显示结果
      await this.showResult();

      this.isSelecting = false;
    },

    // 停止选择
    stopSelection() {
      this.stopRequested = true;
    },

    // 显示结果
    async showResult() {
      const itemHeight = 60;
      const totalStudents = this.duplicatedStudents.length / 2;

      // 计算选中的名字
      const selectedIndex =
        Math.round(this.currentOffset / itemHeight) % totalStudents;
      const selectedStudent = this.random_list[selectedIndex];

      if (selectedStudent) {
        // 将选中的名字对齐到 highlight-zone 的中间
        const highlightZoneCenter = 90;
        const selectedItemCenter = selectedIndex * itemHeight + itemHeight / 2;
        const offsetToCenter = selectedItemCenter - highlightZoneCenter;
        this.currentOffset = offsetToCenter;

        await this.sleep(500);

        // 存储选中的学生信息
        this.selectedStudent = selectedStudent;

        // 显示结果（学号和姓名）
        this.winnerText = `幸运观众: ${selectedStudent.student_number} - ${selectedStudent.student_name}`;
        this.showWinner = true;

        // 显示加分按钮
        this.showAddScoreButton = true;

        this.createConfetti();
      }
    },

    // 创建庆祝彩带
    createConfetti() {
      for (let i = 0; i < 50; i++) {
        const confetti = document.createElement("div");
        confetti.style.cssText = `
          position: fixed;
          width: 10px;
          height: 10px;
          background: ${
            ["#00ff88", "#00b8ff", "#ff0088"][Math.floor(Math.random() * 3)]
          };
          left: ${Math.random() * 100}vw;
          top: -10px;
          opacity: 1;
          pointer-events: none;
          transform: rotate(${Math.random() * 360}deg);
          z-index: 1000;
        `;

        document.body.appendChild(confetti);

        const animation = confetti.animate(
          [
            { transform: `translate(0, 0) rotate(0deg)`, opacity: 1 },
            {
              transform: `translate(${Math.random() * 100 - 50}px, ${
                window.innerHeight
              }px) rotate(${Math.random() * 720}deg)`,
              opacity: 0,
            },
          ],
          {
            duration: 1000 + Math.random() * 1000,
            easing: "cubic-bezier(.37,0,.63,1)",
          }
        );

        animation.onfinish = () => confetti.remove();
      }
    },

    // 给选中的学生加分
    addScoreToWinner() {
      this.showScoreSelector = true;
    },

    // 使用指定分数加分
    async addScoreWithValue(score) {
      if (!this.selectedStudent || this.isAddingScore) return;

      this.isAddingScore = true;
      this.showScoreSelector = false;

      try {
        const courseId = this.$route.params.courseId;
        const studentId = this.selectedStudent.student_number;

        // 调用加分API
        const response = await update_score(courseId, studentId, score);

        if (response.code === 200) {
          this.$message.success(
            `成功为 ${this.selectedStudent.student_name} 加 ${score} 分`
          );
          this.showAddScoreButton = false;
        } else {
          this.$message.error("加分失败: " + response.msg);
        }
      } catch (error) {
        console.error("加分失败:", error);
        this.$message.error("加分失败，请重试");
      } finally {
        this.isAddingScore = false;
      }
    },
  },
  mounted() {
    this.init_random_select_list();
    this.createStars();
    this.createMeteors();
  },
};
</script>

<style scoped>
/* 原有的样式保持不变 */
.random-select-page {
  font-family: Arial, sans-serif;
  background: linear-gradient(135deg, #1a1a1a, #4a4a4a);
  margin: 0;
  padding: 0;
  min-height: 100vh;
  color: #fff;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}
.container {
  width: 80%;
  max-width: 600px;
  max-height: 90vh; /* 限制最大高度，避免超出屏幕 */
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow-y: auto; /* 如果内容超出容器高度，允许滚动 */
  position: relative;
  z-index: 2; /* 确保抽奖窗口在动画之上 */
}
h1 {
  color: #00ff88;
  text-align: center;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
  animation: glow 2s ease-in-out infinite alternate;
  margin-bottom: 30px;
}
@keyframes glow {
  from {
    text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
  }
  to {
    text-shadow: 0 0 20px rgba(0, 255, 136, 0.8),
      0 0 30px rgba(0, 255, 136, 0.6);
  }
}

.name-scroll-container {
  height: 180px; /* 增加高度以显示更多名字 */
  position: relative;
  overflow: hidden;
  margin: 20px 0;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.highlight-zone {
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  height: 60px; /* 增加高度以突出显示更多名字 */
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(0, 255, 136, 0.2) 20%,
    rgba(0, 255, 136, 0.2) 80%,
    transparent 100%
  );
  pointer-events: none;
  z-index: 1;
}

.name-scroll {
  position: absolute;
  width: 100%;
  text-align: center;
  transition: transform 0.3s cubic-bezier(0.21, 0.53, 0.29, 0.99);
}

.name-scroll div {
  height: 60px; /* 增加高度以显示更多名字 */
  line-height: 60px; /* 增加行高以显示更多名字 */
  font-size: 28px; /* 增加字体大小以显示更多名字 */
  font-weight: bold;
  white-space: nowrap;
  text-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.random-button {
  display: block;
  width: 200px;
  margin: 20px auto;
  padding: 15px;
  background: linear-gradient(45deg, #00ff88, #00b8ff);
  color: white;
  text-align: center;
  border-radius: 25px;
  cursor: pointer;
  text-transform: uppercase;
  font-weight: bold;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  border: none;
  outline: none;
}

.random-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 255, 136, 0.4);
}

.random-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.winner-announcement {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  color: #00ff88;
  margin-top: 20px;
  min-height: 36px;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.5s ease;
}

.winner-announcement.show {
  opacity: 1;
  transform: translateY(0);
}

@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

/* 动画容器 */
.animation-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

/* 星星 */
.star {
  position: absolute;
  width: 2px;
  height: 2px;
  background: white;
  border-radius: 50%;
  opacity: 0;
  animation: twinkle 2s infinite ease-in-out;
}

@keyframes twinkle {
  0%,
  100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

/* 流星 */
.meteor {
  position: absolute;
  width: 80px;
  height: 2px;
  background: linear-gradient(90deg, transparent, white);
  transform: rotate(-45deg);
  opacity: 0;
  animation: meteor-fall 3s infinite linear;
}

@keyframes meteor-fall {
  0% {
    opacity: 1;
    transform: translate(-100px, -100px) rotate(-45deg);
  }
  100% {
    opacity: 0;
    transform: translate(200px, 200px) rotate(-45deg);
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
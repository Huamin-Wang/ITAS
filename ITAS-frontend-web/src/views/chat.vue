<template>
  <div class="chat-page">
    <span @click="go_to_course_manager()" class="back-to-home">
      <svg
        width="20"
        height="20"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        style="margin-right: 4px"
        viewBox="0 0 24 24"
      >
        <path d="M15 18l-6-6 6-6" />
      </svg>
      返回
    </span>
    <div class="header">
      <span
        style="
          font-size: 1.4rem;
          font-weight: bold;
          color: #1976d2;
          margin-left: 48px;
        "
        >AI问答小助手</span
      >
    </div>
    <div class="alert-box">
      <p>
        由于运行成本，本聊天不具备连续对话功能，有更复杂的需求请访问其他大模型。
      </p>
      <button @click="closeAlert">×</button>
    </div>

    <div class="chat-container" id="chatContainer">
      <div class="chat-history" id="chatHistory">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="message ai-message">
            <div class="message-content">
              您好！我是AI问答助手，有什么可以帮您的吗？
            </div>
            <div class="message-time">
              {{ new Date().toLocaleTimeString() }}
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="[
            'message',
            msg.type === 'user' ? 'user-message' : 'ai-message',
          ]"
        >
          <div
            class="message-content"
            v-html="formatMessage(msg.content)"
          ></div>
          <div class="message-time">
            {{ new Date(msg.timestamp).toLocaleTimeString() }}
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div class="loading" :style="{ display: isLoading ? 'block' : 'none' }">
        AI正在思考中...
      </div>

      <div class="browser-warning">
        <svg
          class="warning-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
          ></path>
          <line x1="12" y1="9" x2="12" y2="13"></line>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
        <span>如果发送后没有显示"AI正在思考中..."，请使用更新版本的浏览器</span>
      </div>
      <div class="input-wrapper">
        <div class="input-container">
          <input
            type="text"
            id="messageInput"
            placeholder="请输入您的问题..."
            v-model="message"
            :disabled="isLoading"
            @keypress="handleKeyPress"
          />
          <button
            @click="sendMessage()"
            id="sendButton"
            :disabled="isLoading || !message.trim()"
          >
            {{ isLoading ? "发送中..." : "发送" }}
          </button>
        </div>
        <div class="input-hint">💡 按回车键也可以快速发送消息</div>
      </div>
    </div>
  </div>
</template>

<script>
import { chat_handle } from "@/http/api.js";

export default {
  data() {
    return {
      message: "",
      messages: [], // 存储所有消息
      isLoading: false, // 加载状态
    };
  },
  methods: {
    async sendMessage() {
      if (!this.message.trim()) return;

      // 添加用户消息
      const userMessage = {
        id: Date.now(),
        content: this.message,
        type: "user",
        timestamp: new Date(),
      };
      this.messages.push(userMessage);

      // 清空输入框
      const messageToSend = this.message;
      this.message = "";

      // 显示加载状态
      this.isLoading = true;

      try {
        const data = {
          message: messageToSend,
        };

        const response = await chat_handle(data);

        // 根据接口返回结构获取AI回复内容
        let aiResponse = "";
        if (response.data && response.data.success) {
          // 从 response 字段获取AI回复
          aiResponse = response.data.response || "抱歉，我没有理解您的问题";
        } else {
          aiResponse = "抱歉，AI服务返回了错误响应";
        }

        // 添加AI回复
        const aiMessage = {
          id: Date.now() + 1,
          content: aiResponse,
          type: "ai",
          timestamp: new Date(),
          format: response.data?.format || "text", // 保存消息格式
        };
        this.messages.push(aiMessage);
      } catch (error) {
        console.error("AI解答失败:", error);
        this.$message.error("AI解答失败");

        // 添加错误消息
        const errorMessage = {
          id: Date.now() + 1,
          content: "抱歉，AI服务暂时不可用，请稍后重试",
          type: "ai",
          timestamp: new Date(),
        };
        this.messages.push(errorMessage);
      } finally {
        this.isLoading = false;
        // 滚动到底部
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },

    // 处理回车键
    handleKeyPress(e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (!this.isLoading && this.message.trim()) {
          this.sendMessage();
        }
      }
    },

    // 滚动到底部
    scrollToBottom() {
      const container = this.$el.querySelector(".chat-history");
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },

    // 格式化消息内容
    formatMessage(content) {
      if (!content) return "";

      // 处理换行
      let formatted = content.replace(/\n/g, "<br>");

      // 简单的代码块检测（如果内容包含 ``` 则视为代码块）
      if (content.includes("```")) {
        // 这里可以添加更复杂的markdown解析逻辑
        // 暂时简单处理：将 ```code``` 转换为 <pre><code>code</code></pre>
        formatted = formatted.replace(
          /```([^`]+)```/g,
          '<pre class="code-block"><code>$1</code></pre>'
        );
      }

      return formatted;
    },

    // 关闭警告框
    closeAlert() {
      const alertBox = this.$el.querySelector(".alert-box");
      if (alertBox) {
        alertBox.style.display = "none";
      }
    },

    // 返回课程管理
    go_to_course_manager() {
      const courseId = this.$route.params.courseId;
      this.$router.push({ path: `/course_manager/${courseId}` });
    },
  },
  mounted() {
    // 初始滚动到底部
    this.$nextTick(() => {
      this.scrollToBottom();
    });
  },
};
</script>

<style scoped>
.chat-page {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f0f2f5;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  overflow-y: auto;
}

/* 底部背景 */
body::after {
  content: "";
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 150px; /* 底部背景高度 */
  background: linear-gradient(
    to top,
    rgba(240, 242, 245, 1),
    rgba(240, 242, 245, 0)
  );
  pointer-events: none; /* 防止遮挡点击事件 */
  z-index: -1; /* 置于底层 */
}

.header {
  width: 100%;
  max-width: 800px;
  display: flex;
  justify-content: flex-start; /* 将内容靠左对齐 */
  align-items: center;
  padding: 15px 20px;
  background-color: white;
  border-radius: 10px 10px 0 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
  position: relative; /* 添加相对定位 */
}

.back-to-home {
  position: absolute;
  top: 30px;
  left: 30px;
  color: #1976d2;
  text-decoration: none;
  padding: 8px 18px;
  background-color: #fff;
  border: 1px solid #1976d2;
  border-radius: 20px;
  font-weight: bold;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.08);
  transition: all 0.2s;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.back-to-home:hover {
  background-color: #1976d2;
  color: #fff;
  border-color: #1976d2;
}

.alert-box {
  position: fixed;
  right: 20px;
  top: 20px;
  width: 300px;
  padding: 15px;
  background-color: #f9edbe;
  border: 1px solid #f0c36d;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  font-size: 14px;
  color: #856404;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.alert-box button {
  background: transparent;
  border: none;
  color: #856404;
  font-size: 16px;
  position: absolute;
  top: 5px;
  right: 5px;
  cursor: pointer;
  transition: color 0.3s;
}

.alert-box button:hover {
  color: #d9534f;
}

.chat-container {
  width: 100%;
  max-width: 800px;
  background: white;
  border-radius: 0 0 10px 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin: 0 20px 100px; /* 增加 margin-bottom，避免输入框贴底 */
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-bottom: 20px;
  max-height: 60vh;
}

.welcome-message {
  text-align: center;
  color: #666;
  margin-bottom: 20px;
}

.message {
  margin-bottom: 20px;
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 80%;
  animation: messageAppear 0.3s ease-out;
}

@keyframes messageAppear {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.user-message {
  background: linear-gradient(135deg, #1976d2, #1565c0);
  color: white;
  margin-left: auto;
  border-bottom-right-radius: 4px;
}

.ai-message {
  background: #f5f5f5;
  color: #333;
  margin-right: auto;
  border-bottom-left-radius: 4px;
}

.message-content {
  line-height: 1.5;
  word-wrap: break-word;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 8px;
  text-align: right;
}

.user-message .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.ai-message .message-time {
  color: #666;
}

.browser-warning {
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  color: #856404;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.warning-icon {
  color: #856404;
  width: 18px;
  height: 18px;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  position: sticky;
  bottom: 20px; /* 固定在底部，但留出一定距离 */
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 -2px 6px rgba(0, 0, 0, 0.05);
}

.input-container {
  display: flex;
  gap: 10px;
}

#messageInput {
  flex-grow: 1;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 18px;
  transition: border-color 0.3s;
  min-height: 60px;
}

#messageInput:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

#messageInput:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.input-hint {
  font-size: 0.85rem;
  color: #666;
  padding: 0 4px;
}

button {
  padding: 12px 24px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s, transform 0.1s;
}

button:hover:not(:disabled) {
  background-color: #1565c0;
}

button:active:not(:disabled) {
  transform: scale(0.98);
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  transform: none;
}

.loading {
  margin: 10px 0;
  color: #666;
  text-align: center;
  font-style: italic;
}

.loading::after {
  content: "";
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0%,
  20% {
    content: ".";
  }
  40% {
    content: "..";
  }
  60%,
  100% {
    content: "...";
  }
}

/* 代码块样式 */
.message-content pre.code-block {
  background-color: #272822;
  color: #f8f8f2;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: "Courier New", monospace;
  margin: 8px 0;
}

.message-content code {
  background: #f1f1f1;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: "Courier New", monospace;
  font-size: 0.9rem;
}

.user-message .message-content code {
  background: rgba(255, 255, 255, 0.2);
  color: inherit;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header,
  .chat-container {
    margin: 10px;
    padding: 15px;
  }

  .message {
    max-width: 90%;
  }

  #messageInput {
    font-size: 16px;
    padding: 12px;
  }

  button {
    padding: 10px 20px;
  }
}

@media (max-width: 480px) {
  .alert-box {
    width: 90%;
    right: 5%;
    top: 10px;
  }

  .header,
  .chat-container {
    margin: 5px;
    padding: 10px;
  }

  .message {
    max-width: 95%;
  }

  #messageInput {
    font-size: 14px;
    padding: 10px;
  }

  button {
    padding: 8px 16px;
  }
}
</style>
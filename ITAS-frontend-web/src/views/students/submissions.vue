<template>
    <div class="submissions-page">
        <nav class="navigation">
            <a href="#" class="back-home" @click.prevent="goBack">返回课程列表</a>
        </nav>

        <div class="container">
            <h1>{{ user_name }}的所有作业</h1>

            <div v-if="assignments.length > 0">
                <ul class="assignment-list">
                    <li v-for="assignment in assignments" :key="assignment.id">
                        <div class="assignment-info">
                            <span class="assignment-title">{{ assignment.title }}</span>
                            <span class="assignment-deadline">
                                截止日期：{{ formatDate(assignment.due_date) }}
                                <span class="deadline-passed" v-if="isDeadlinePassed(assignment.due_date)">
                                    已截止
                                </span>
                            </span>
                        </div>
                        <a href="#" class="submit-link" @click.prevent="goToSubmission(assignment.id)"
                            :class="{ 'disabled-link': isDeadlinePassed(assignment.due_date) }">
                            {{ isDeadlinePassed(assignment.due_date) ? '已截止' : '进入提交' }}
                        </a>
                    </li>
                </ul>
            </div>

            <div v-else>
                <p class="no-assignments">暂无作业</p>
            </div>
        </div>
    </div>
</template>

<script>
import { getAllAssignments } from '@/http/api';
export default {
    data() {
        return {
            user_name: '',
            userInfo: {},
            assignments: []
        }
    },
    methods: {
        async loadSubmissions() {
            try {
                const userInfo = JSON.parse(sessionStorage.getItem('userInfo'))
                this.user_name = userInfo.name;
                const response = await getAllAssignments();
                if(response.code === 200){
                    this.assignments = response.data;
                }
            } catch (error) {
                console.error('加载作业失败:', error);
            }
        },

        // 格式化日期
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        // 检查是否已过截止日期
        isDeadlinePassed(dueDate) {
            return new Date() > new Date(dueDate);
        },

        // 返回课程列表
        goBack() {
            alert('返回课程列表功能');
            // 实际应用中这里应该是路由跳转
            this.$router.push('/course_detail');
        },

        // 进入提交页面
        goToSubmission(assignmentId) {
            const assignment = this.assignments.find(a => a.id === assignmentId);
            if (this.isDeadlinePassed(assignment.due_date)) {
                alert('该作业已截止，无法提交');
                return;
            }

            alert(`进入作业提交页面，作业ID: ${assignmentId}`);
            // 实际应用中这里应该是路由跳转
            // this.$router.push(`/submission/${assignmentId}`);
        }
    },
    mounted() {
        // 模拟从API获取数据
        // 实际应用中这里应该是API调用
        // this.fetchAssignments();
        this.loadSubmissions();
    }
}
</script>

<style scoped>
.submissions-page {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    margin: 0;
    padding: 0;
}

/* Navigation Styles */
.navigation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.back-button {
    text-decoration: none;
    color: #666;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background 0.3s ease;
}

.back-button:hover {
    background: #f4f4f4;
}

.current-time {
    color: #666;
    font-size: 0.9rem;
}

/* Container Styles */
.container {
    width: 80%;
    max-width: 1200px;
    margin: 2rem auto;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h1 {
    color: #1890ff;
    text-align: center;
    margin-bottom: 2rem;
}

/* Assignment List Styles */
.assignment-list {
    list-style: none;
    padding: 0;
}

.assignment-list li {
    background: #fff;
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.assignment-info {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.assignment-title {
    font-weight: bold;
    color: #333;
}

.assignment-deadline {
    color: #666;
    font-size: 0.9rem;
}

.deadline-passed {
    color: #ff4d4f;
    font-weight: bold;
    margin-left: 0.5rem;
}

.submit-link {
    text-decoration: none;
    color: #1890ff;
    padding: 0.5rem 1rem;
    border: 1px solid #1890ff;
    border-radius: 4px;
    transition: all 0.3s ease;
}

.submit-link:hover {
    background: #1890ff;
    color: white;
}

.no-assignments {
    text-align: center;
    color: #666;
    font-style: italic;
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
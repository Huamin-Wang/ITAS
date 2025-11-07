<template>
    <div class="submission_detail-page">
        <div id="loadingOverlay" class="loading-overlay" :class="{ active: isLoading }">
            <div class="spinner"></div>
        </div>

        <div class="container">
            <div class="card">
                <div class="card-header">
                    <h2>作业详情</h2>
                    <a :href="`/submissions`" class="back-home">返回作业列表</a>
                </div>
                <div class="card-body">
                    <div class="assignment-header">
                        <h3 class="assignment-title">{{ assignment.title }}</h3>
                        <div class="assignment-meta">
                            <p class="deadline" :class="deadlineClass">
                                <i class="far fa-calendar-alt"></i>
                                {{ deadlineText }}
                            </p>
                            <span class="status-badge" :class="submissionStatusClass">
                                <i :class="submissionStatusIcon"></i> {{ submissionStatusText }}
                            </span>
                        </div>
                    </div>

                    <div class="section">
                        <div class="section-header">
                            <i class="fas fa-file-alt"></i> 作业说明
                        </div>
                        <div class="section-body">
                            <p>{{ assignment.description }}</p>
                        </div>
                    </div>

                    <template v-if="submission">
                        <div class="section">
                            <div class="section-header">
                                <i class="fas fa-paper-plane"></i> 提交状态
                            </div>
                            <div class="section-body">
                                <div class="submission-info">
                                    <div class="info-item">
                                        <span class="info-label">提交时间</span>
                                        <span class="info-value">{{ formattedSubmissionDate }}</span>
                                    </div>
                                </div>

                                <div class="section">
                                    <div class="section-header">
                                        <i class="fas fa-file-alt"></i> 提交内容
                                    </div>
                                    <div class="section-body">
                                        <p>{{ submission.data }}</p>
                                    </div>
                                </div>

                                <div v-if="submission.feedback" class="feedback-box">
                                    <h4><i class="fas fa-robot"></i> AI评语</h4>
                                    <p>{{ submission.feedback }}</p>
                                </div>
                            </div>
                        </div>
                    </template>
                    <template v-else>
                        <div class="section">
                            <div class="section-header">
                                <i class="fas fa-exclamation-circle"></i> 提交状态
                            </div>
                            <div class="section-body">
                                <p>您尚未提交此作业，请在截止日期前完成提交。</p>
                            </div>
                        </div>
                    </template>

                    <div class="section">
                        <div class="section-header">
                            <i class="fas fa-edit"></i> {{ submission ? '更新作业' : '提交作业' }}
                        </div>
                        <div class="section-body">
                            <form @submit.prevent="submitForm">
                                <div class="form-group">
                                    <label class="form-label" for="content">作业内容:</label>
                                    <textarea id="content" v-model="submissionContent" @input="updateWordCount"
                                        required></textarea>
                                    <div id="wordCounter" class="word-counter"
                                        :class="{ 'character-limit-warning': isOverLimit }">
                                        {{ wordCountText }}
                                    </div>
                                </div>
                                <button type="submit" id="submitButton" class="button" :disabled="isSubmitting">
                                    <i class="fas fa-paper-plane"></i>
                                    {{ isSubmitting ? '正在提交...' : (submission ? '更新提交' : '提交作业') }}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { getAssignmentDetail } from '@/http/api';
export default {
    data() {
        return {
            isLoading: false,
            isSubmitting: false,
            assignment: {},
            submission: {},
            user: {
                id: 12345
            },
            submissionContent: '',
            wordCount: 0,
            MAX_CHARS: 5000,
            typingTimer: null,
            TYPING_INTERVAL: 2000
        }
    },
    computed: {
        submissionListUrl() {
            // 这里应该根据实际路由生成
            return `/submission/${this.user.id}`;
        },
        deadlineClass() {
            const daysRemaining = this.daysRemaining;
            if (daysRemaining <= 2 && daysRemaining >= 0) {
                return 'deadline-approaching';
            } else if (daysRemaining < 0) {
                return 'deadline-passed';
            } else {
                return 'deadline-normal';
            }
        },
        deadlineText() {
            const daysRemaining = this.daysRemaining;
            if (daysRemaining <= 2 && daysRemaining >= 0) {
                return `截止日期: ${this.assignment.due_date} (还剩 ${daysRemaining} 天)`;
            } else if (daysRemaining < 0) {
                return `截止日期: ${this.assignment.due_date} (已过期)`;
            } else {
                return `截止日期: ${this.assignment.due_date} (还剩 ${daysRemaining} 天)`;
            }
        },
        daysRemaining() {
            const dueDate = new Date(this.assignment.due_date);
            const now = new Date();
            const timeDiff = dueDate - now;
            return Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
        },
        submissionStatusClass() {
            return this.submission ? 'status-success' : 'status-warning';
        },
        submissionStatusIcon() {
            return this.submission ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle';
        },
        submissionStatusText() {
            return this.submission ? '已提交' : '未提交';
        },
        formattedSubmissionDate() {
            if (!this.submission) return '';
            return this.submission.submission_date;
        },
        wordCountText() {
            if (this.isOverLimit) {
                return `${this.wordCount}个字符 (超出限制)`;
            }
            return `${this.wordCount}个字符`;
        },
        isOverLimit() {
            return this.wordCount > this.MAX_CHARS;
        }
    },
    methods: {
        async loadSubmissionDetail(){
            const assignmentId = this.$route.params.assignmentId;
            try{
                const response = await getAssignmentDetail(assignmentId);
                if(response.code === 200){
                    this.assignment = response.data;
                }

            }catch(error){
                console.error('加载作业详情失败:', error);
            }
        },

        updateWordCount() {
            this.wordCount = this.submissionContent.length;

            // 自动保存草稿
            clearTimeout(this.typingTimer);
            this.typingTimer = setTimeout(this.saveDraft, this.TYPING_INTERVAL);
        },
        saveDraft() {
            if (this.submissionContent) {
                localStorage.setItem(`assignment_draft_${this.assignment.id}`, this.submissionContent);
                console.log('Draft saved');
            }
        },
        loadDraft() {
            const savedDraft = localStorage.getItem(`assignment_draft_${this.assignment.id}`);
            if (savedDraft && !this.submissionContent) {
                this.submissionContent = savedDraft;
                this.updateWordCount();
            }
        },
        submitForm() {
            // 验证
            if (!this.submissionContent.trim()) {
                alert('请输入作业内容');
                return;
            }

            if (this.isOverLimit) {
                alert('作业内容超出字符限制，请删减内容后重新提交');
                return;
            }

            // 显示加载状态
            this.isSubmitting = true;
            this.isLoading = true;

            // 模拟提交
            setTimeout(() => {
                // 在实际应用中，这里应该发送AJAX请求
                console.log('提交内容:', this.submissionContent);

                // 清除草稿
                localStorage.removeItem(`assignment_draft_${this.assignment.id}`);

                // 更新提交状态
                this.submission = {
                    submission_date: new Date().toLocaleString(),
                    data: this.submissionContent,
                    feedback: null
                };

                // 重置状态
                this.isSubmitting = false;
                this.isLoading = false;

                alert('提交成功！');
            }, 1500);
        }
    },
    mounted() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css';
        document.head.appendChild(link);

        // if (this.submission) {
        //     this.submissionContent = this.submission.data;
        //     this.updateWordCount();
        // } else {
        //     // 否则尝试加载草稿
        //     this.loadDraft();
        // }

        this.loadSubmissionDetail();
    }
}
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.submission_detail-page {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #2c3e50;
    background: #f5f6fa;
    padding: 1.5rem;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
}

.card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    margin-bottom: 2rem;
    overflow: hidden;
}

.card-header {
    padding: 1.5rem;
    border-bottom: 1px solid #dfe6e9;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
}

.card-body {
    padding: 1.5rem;
}

.back-button {
    text-decoration: none;
    color: #2c3e50;
    background: #f5f6fa;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.back-button:hover {
    background: #e0e0e0;
    transform: translateY(-2px);
}

.assignment-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.assignment-title {
    color: #4a90e2;
    margin: 0;
    font-size: 1.5rem;
}

.assignment-meta {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.deadline {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.9rem;
}

.deadline-approaching {
    color: white;
    background-color: #e74c3c;
}

.deadline-normal {
    color: white;
    background-color: #2ecc71;
}

.deadline-passed {
    color: white;
    background-color: #95a5a6;
}

.section {
    margin-bottom: 2rem;
    border: 1px solid #dfe6e9;
    border-radius: 8px;
    overflow: hidden;
}

.section-header {
    background: #eaf2fd;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    color: #4a90e2;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-body {
    padding: 1.5rem;
    background: white;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.75rem;
    border-radius: 4px;
    font-size: 0.85rem;
    font-weight: 600;
    color: white;
}

.status-success {
    background: #2ecc71;
}

.status-warning {
    background: #f1c40f;
}

.submission-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.info-label {
    font-size: 0.85rem;
    color: #7f8c8d;
}

.info-value {
    font-weight: 600;
    color: #2c3e50;
}

.grade-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.75rem;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 600;
    color: white;
}

.grade-value {
    background: #2ecc71;
}

.grade-pending {
    background: #95a5a6;
}

.feedback-box {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid #4a90e2;
    margin: 1rem 0;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

textarea {
    width: 100%;
    min-height: 200px;
    padding: 1rem;
    border: 1px solid #dfe6e9;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    resize: vertical;
    transition: all 0.3s ease;
}

textarea:focus {
    outline: none;
    border-color: #4a90e2;
    box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2);
}

.button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    background: #4a90e2;
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.button:hover {
    background: #357abd;
    transform: translateY(-2px);
}

.button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
}

.word-counter {
    color: #7f8c8d;
    font-size: 0.85rem;
    text-align: right;
    margin-top: 0.5rem;
}

.character-limit-warning {
    color: #e74c3c;
}

.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    visibility: hidden;
    opacity: 0;
    transition: all 0.3s ease;
}

.loading-overlay.active {
    visibility: visible;
    opacity: 1;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(74, 144, 226, 0.2);
    border-radius: 50%;
    border-top-color: #4a90e2;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

@media (max-width: 768px) {
    body {
        padding: 1rem;
    }

    .card-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }

    .back-button {
        align-self: flex-start;
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
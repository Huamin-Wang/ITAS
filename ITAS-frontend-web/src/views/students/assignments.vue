<template>
    <div class="assignments-page">
        <a href="/course_manage/{{ course.id }}" class="back-home">返回课程</a>
        <div class="container">
            <div class="page-section">
                <h1> - 作业列表</h1>

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
                        
                        <tr>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td>
                                <a href=""
                                    class="btn btn-small">编辑</a>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="4" style="text-align: center; padding: 20px;">暂无作业</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <div class="form-container">
                <h2 class="form-title">发布新作业</h2>
                <form action="/course/assignments/{{ course.id }}" method="post">
                    <div class="form-group">
                        <label for="title">作业标题</label>
                        <input type="text" id="title" name="title" maxlength="200" required placeholder="请输入作业标题">
                    </div>

                    <div class="form-group">
                        <label for="description">作业描述</label>
                        <textarea id="description" name="description" placeholder="请输入作业详细说明"></textarea>
                    </div>

                    <div class="form-group">
                        <label for="due_date">截止日期</label>
                        <input type="date" id="due_date" name="due_date" required>
                    </div>

                    <div class="actions">
                        <button type="submit" class="btn btn-submit">提交作业</button>
                        <a href="{{ url_for('course_manage', course_id=course.id) }}" class="btn btn-back">返回课程管理</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "Assignments",
    data() {
        return {
            //
        };
    },
    methods: {
        //
    },
    mounted() {
        //
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
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: var(--text);
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
}

.back-home:hover {
    background-color: #2acb11;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px rgba(66, 153, 225, 0.2);
}

:root {
    --primary: #3498db;
    --primary-dark: #2980b9;
    --secondary: #2ecc71;
    --secondary-dark: #27ae60;
    --text: #333;
    --light-gray: #f8f9fa;
    --border: #e0e0e0;
    --danger: #e74c3c;
    --success: #2ecc71;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 30px 20px;
}

h1 {
    color: var(--primary-dark);
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--primary);
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
    border-left: 4px solid var(--success);
    color: #27ae60;
}

.alert-danger {
    background-color: rgba(231, 76, 60, 0.15);
    border-left: 4px solid var(--danger);
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
    background-color: var(--primary);
    color: white;
    font-weight: 500;
}

.assignment-table tr:nth-child(even) {
    background-color: var(--light-gray);
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
    color: var(--primary-dark);
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
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 1rem;
    transition: border 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: var(--primary);
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
    background-color: var(--primary);
    color: white;
    text-decoration: none;
    border-radius: 4px;
    border: none;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.3s, transform 0.2s;
}

.btn:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
}

.btn-submit {
    background-color: var(--secondary);
}

.btn-submit:hover {
    background-color: var(--secondary-dark);
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
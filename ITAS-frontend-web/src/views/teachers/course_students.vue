<template>
    <div class="course_students-page">
        <a href="/course_manage/{{course.id}}" class="back-home">返回课程</a>
        <div class="container">
            <!-- 课程信息 -->
            <h1><i class="fas fa-book-open icon"></i>课程: </h1>
            <p class="course-info"><i class="fas fa-info-circle icon"></i>课程代码: </p>
            <!--/* 重新上传学生名单，以新名单为准 */-->
            <button onclick="window.location.href='/update_course/{{ course.id }}';">更新教务系统学生名单</button>
            <!-- 已选课学生名单 -->
            <h2><i class="fas fa-users icon"></i>已注册账号学生名单</h2>
            <p class="count"><i class="fas fa-check-circle icon"></i>已注册学生数量: </p>
            <form action="/course_students/{{ course.id }}" method="POST">
                <button type="submit">刷新注册状态</button>
            </form>
            <table>
                <thead>
                    <tr>
                        <th>学生学号</th>
                        <th>学生姓名</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody>

                    <tr>
                        <td></td>
                        <td></td>
                        <td><span style="color: #27ae60;"></span></td>
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
                <tbody>

                    <tr>
                        <td></td>
                        <td></td>
                        <td><span style="color: #e74c3c;"></span></td>
                    </tr>

                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
export default {
    name: "course_students",
    data() {
        return {

        }
    },
    methods: {

    },
    mounted() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
        document.head.appendChild(link);
    }
}
</script>

<style scoped>
/* 全局样式 */
.course_students-page {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
}

.back-home:hover {
    background-color: #2acb11;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px rgba(66, 153, 225, 0.2);
}
</style>
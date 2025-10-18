<template>
    <div class="course_analysis-page">
        <header>
            <a href="/course_manage/{{ course.id }}" class="back-to-home">返回课程管理</a>
            <h1> - 学生学习状况分析</h1>
            <p>智能分析学生薄弱知识点，助力精准教学</p>
        </header>

        <div class="container">
            <h2 class="section-title">整体学习表现分析</h2>

            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>

            <h2 class="section-title">薄弱知识点分布</h2>

            <div class="chart-container">
                <canvas id="weaknessChart"></canvas>
            </div>

            <h2 class="section-title">个性化学习分析</h2>

            <div class="grid-container">
                <div class="insight-card">
                    <h3>学习困难点</h3>
                    <p>以下知识点学生普遍掌握不佳：</p>
                    <div>
                        <span class="tag weakness-tag">微积分基础</span>
                        <span class="tag weakness-tag">线性代数</span>
                        <span class="tag weakness-tag">概率论</span>
                    </div>
                    <button class="action-button" onclick="generateLearningMaterials()">生成专项练习</button>
                </div>

                <div class="insight-card">
                    <h3>需要关注的学生</h3>
                    <p>以下学生在近期作业中表现不佳：</p>
                    <ul class="student-list">
                        <li><span>张三</span> <span>3次作业不及格</span></li>
                        <li><span>李四</span> <span>参与度低</span></li>
                        <li><span>王五</span> <span>缺勤率高</span></li>
                    </ul>
                    <button class="action-button" onclick="scheduleInterventions()">安排辅导</button>
                </div>

                <div class="insight-card">
                    <h3>学习趋势</h3>
                    <p>近期学生整体掌握情况：</p>
                    <div class="chart-container" style="height: 150px;">
                        <canvas id="trendChart"></canvas>
                    </div>
                </div>

                <div class="insight-card">
                    <h3>知识点掌握情况</h3>
                    <p>基于作业、考试和课堂互动的综合分析：</p>
                    <div>
                        <span class="tag">数据结构 (85%)</span>
                        <span class="tag">算法设计 (72%)</span>
                        <span class="tag weakness-tag">高级编程 (45%)</span>
                        <span class="tag">软件工程 (68%)</span>
                    </div>
                    <button class="action-button" onclick="adjustTeachingPlan()">调整教学计划</button>
                </div>
            </div>

            <h2 class="section-title">教学建议</h2>
            <div class="insight-card">
                <h3>智能教学建议</h3>
                <p>基于大数据分析和人工智能算法，我们建议：</p>
                <ol>
                    <li>增加微积分基础的复习和实践课时，尤其是导数应用部分</li>
                    <li>为线性代数安排更多小组讨论课，提高学生参与度</li>
                    <li>概率论章节建议采用案例教学法，增强学生的理解</li>
                    <li>可考虑对张三、李四、王五等学生进行一对一辅导</li>
                </ol>
                <button class="action-button" onclick="generateDetailedReport()">生成详细报告</button>
            </div>
        </div>

        <footer>
            <p>&copy; 2025 基于大模型的智能教学辅助系统. All Rights Reserved.</p>
        </footer>
    </div>
</template>

<script>
export default {
    name: "course_analysis",
    data() {
        return {

        }
    },
    methods: {

    },
    mounted() {

    }
}
</script>

<style scoped>
.course_analysis-page {
    font-family: 'Arial', sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
    color: #333;
}

header {
    background: linear-gradient(135deg, #001529, #003a70);
    color: white;
    padding: 20px 0;
    text-align: center;
    position: relative;
}

.back-to-home {
    position: absolute;
    top: 20px;
    left: 20px;
    color: white;
    text-decoration: none;
    padding: 5px 10px;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    transition: all 0.3s ease;
}

.back-to-home:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

header h1 {
    margin: 0;
    padding: 0;
    font-size: 2em;
}

.container {
    width: 85%;
    margin: 20px auto;
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.section-title {
    color: #1890ff;
    border-bottom: 2px solid #1890ff;
    padding-bottom: 10px;
    margin-top: 25px;
}

.chart-container {
    margin: 20px 0;
    height: 300px;
}

.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.insight-card {
    background-color: #f9f9f9;
    border-left: 4px solid #1890ff;
    padding: 15px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.insight-card h3 {
    margin-top: 0;
    color: #1890ff;
}

.student-list {
    margin-top: 15px;
    list-style-type: none;
    padding: 0;
}

.student-list li {
    background-color: #f0f8ff;
    margin-bottom: 8px;
    padding: 8px 12px;
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
}

.action-button {
    background: #1890ff;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 10px;
}

.action-button:hover {
    background: #096dd9;
}

footer {
    background-color: #001529;
    color: rgba(255, 255, 255, 0.8);
    text-align: center;
    padding: 20px 0;
    margin-top: 30px;
}

.tag {
    display: inline-block;
    padding: 3px 8px;
    background-color: #e6f7ff;
    color: #1890ff;
    border-radius: 3px;
    margin-right: 5px;
    font-size: 0.9em;
}

.weakness-tag {
    background-color: #fff2e8;
    color: #fa541c;
}
</style>
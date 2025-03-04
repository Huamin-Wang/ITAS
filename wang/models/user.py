# wang/models/user.py
from wang.models import db
from werkzeug.security import check_password_hash

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    identifier = db.Column(db.String(50), unique=True, nullable=False)  # 用户标识符
    role = db.Column(db.String(10), nullable=False)  # 用户角色
    name = db.Column(db.String(100), nullable=False)  # 用户名
    email = db.Column(db.String(120), unique=True, nullable=False)  # 邮箱
    password = db.Column(db.String(256), nullable=False)  # 密码
    openid = db.Column(db.String(100),  nullable=True) # 微信openid
    # 学生关系
    attendances = db.relationship('Attendance', backref='student', lazy=True)  # 学生的考勤记录
    submissions = db.relationship('Submission', backref='student', lazy=True)  # 学生的作业提交
    quiz_responses = db.relationship('QuizResponse', backref='student', lazy=True)  # 学生的抢答记录
    reports = db.relationship('Report', backref='student', lazy=True)  # 学生的学习数据分析报告
    # 教师关系
    assigned_homeworks = db.relationship('Assignment', backref='teacher', lazy=True)  # 教师发布的作业
    quizzes = db.relationship('Quiz', backref='teacher', lazy=True)  # 教师发布的抢答
    # 检查用户密码与数据库中的密码是否匹配
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.id} - {self.name}>'
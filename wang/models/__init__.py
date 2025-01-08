from flask_sqlalchemy import SQLAlchemy

print("导入了wang/models模块！")

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db
# 导入所有模型
from .attendance import Attendance
from .report import Report
from .submission import Submission
from .user import User
from .assignment import Assignment
from .quiz import Quiz
from .quizResponse import QuizResponse

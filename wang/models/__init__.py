from flask_sqlalchemy import SQLAlchemy


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

from .course import Course
from .course_students import Course_Students

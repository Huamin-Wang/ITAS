# 导入所有模型，方便在其他地方导入
from .Result import Result
from .attendance import Attendance
from .report import Report
from .submission import Submission
from .user import User
from .assignment import Assignment
from .quiz import Quiz
from .quizResponse import QuizResponse
from .course import Course
from .course_students import Course_Students
__all__ = ['Account','Result','Attendance','Report','Submission','User','Assignment','Quiz','QuizResponse','Course','Course_Students']
from app.controllers.userController import bp as user_bp
from app.controllers.studentController import bp as students_bp
from app.controllers.courseStudentController import bp as course_student_bp
from app.controllers.chatController import bp as chat_bp
from app.controllers.aiController import bp as ai_bp

__all__ = ['user_bp','course_student_bp','chat_bp','ai_bp','students_bp']
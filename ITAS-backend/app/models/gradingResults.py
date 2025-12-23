from app import db
from datetime import datetime

class GradingResult(db.Model):
    __tablename__ = 'grading_results'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, nullable=True)  # 作业ID
    quiz_id = db.Column(db.Integer, nullable=True)        # 小测ID
    question_id = db.Column(db.Integer, nullable=True)       # 小测题目ID
    student_number = db.Column(db.String(50), nullable=False)  # 学生ID
    title = db.Column(db.Text, nullable=False)               # 作业标题
    description = db.Column(db.Text, nullable=True)          # 作业描述
    student_answer = db.Column(db.Text, nullable=True)       # 学生答案
    reference_answer = db.Column(db.Text, nullable=True)     # 参考答案
    total_score = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)  # 总分
    score = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)        # 得分
    comment = db.Column(db.Text, nullable=True)              # 评语
    grading_time = db.Column(db.DateTime, default=datetime.now())  # 批改时间
    status = db.Column(db.String(20), default='completed')   # 状态
    course_id = db.Column(db.Integer, primary_key=True)      #班级ID
    
    def __repr__(self):
        return f'<GradingResult {self.id}: {self.student_number} - {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'quiz_id': self.quiz_id,
            'question_id': self.question_id,
            'student_number': self.student_number,
            'title': self.title,
            'description': self.description,
            'student_answer': self.student_answer,
            'reference_answer': self.reference_answer,
            'total_score': float(self.total_score) if self.total_score else 0.0,
            'score': float(self.score) if self.score else 0.0,
            'comment': self.comment,
            'grading_time': self.grading_time.isoformat() if self.grading_time else None,
            'status': self.status,
            'course_id':self.course_id
        }
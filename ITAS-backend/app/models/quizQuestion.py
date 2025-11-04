from app import db
import json
class QuizQuestion(db.Model):
    __tablename__ = 'quiz_question'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # 'choice' 'multiple_choice', 'true_false','short_answer'
    options = db.Column(db.Text, nullable=True)
    correct_answer = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=1)
    
    
    def __repr__(self):
        return f'<QuizQuestion {self.id} for Quiz {self.quiz_id}>'
    
    def to_dict(self):
        """将题目对象转换为字典"""
        try:
            # 尝试解析options为JSON
            options_data = json.loads(self.options) if self.options else []
        except (json.JSONDecodeError, TypeError):
            options_data = self.options  # 如果解析失败，返回原始字符串
        
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'options': options_data,  # 已经是解析后的数据
            'correct_answer': self.correct_answer,
            'points': self.points
        }
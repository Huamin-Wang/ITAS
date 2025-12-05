from datetime import datetime
from app import db
class QuizResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    response = db.Column(db.Text, nullable=False)
    response_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    question_id = db.Column(db.Integer, nullable=False)


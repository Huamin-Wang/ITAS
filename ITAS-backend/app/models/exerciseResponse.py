from datetime import datetime
from app import db
class ExerciseResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    student_number = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    response_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    question_id = db.Column(db.Integer, nullable=False)

def __repr__(self):
    return f"<exerciseResponse id={self.id} exercise_id={self.exercise_id} student_number={self.student_number} question_id={self.question_id}>"

def to_dict(self):
    return {
        'id': self.id,
        'exercise_id': self.exercise_id,
        'student_number': self.student_number,
        'response': self.response,
        'response_time': self.response_time.isoformat(),
        'question_id': self.question_id
    }


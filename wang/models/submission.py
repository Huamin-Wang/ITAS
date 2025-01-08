from wang.models import db
from datetime import datetime

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submission_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    grade = db.Column(db.Float)
# wang/models/enrollment.py
from wang.models import db

class Enrollment(db.Model):
    __tablename__ = 'enrollment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship
    student = db.relationship('User', backref='enrollment')

    def __repr__(self):
        return f'<Enrollment {self.id} - Course {self.course_id} - Student {self.student_id}>'
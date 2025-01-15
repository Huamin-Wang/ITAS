# wang/models/course.py
from wang.models import db


class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    # Relationship
    teacher = db.relationship('User', backref='courses')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.id} - {self.name}>'
# wang/models/course.py
from wang.models import db


class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    semester = db.Column(db.String, nullable=False)
    # 课程简介
    description = db.Column(db.Text)
    # 课程代码
    code = db.Column(db.String(10), nullable=False)

    # Relationship
    teacher = db.relationship('User', backref='courses')
    course_students = db.relationship('Course_Students',  back_populates='course')

    def __repr__(self):
        return f'<Course {self.id} - {self.name}>'

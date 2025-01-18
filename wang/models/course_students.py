#格式为：学号、姓名、拼音姓名、年级、专业、方向、行政班级、学籍状态、修课方式
from wang.models import db


class Course_Students(db.Model):
    __tablename__ = 'course_students'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_number = db.Column(db.String(20), nullable=False)
    student_name = db.Column(db.String(20), nullable=False)
    student_pinyin_name = db.Column(db.String(20), nullable=False)
    student_grade = db.Column(db.String(20), nullable=False)
    student_major = db.Column(db.String(20), nullable=False)
    student_direction = db.Column(db.String(20), nullable=True)
    student_class = db.Column(db.String(20), nullable=False)
    student_status = db.Column(db.String(20), nullable=False)
    student_course_method = db.Column(db.String(20), nullable=False)
    #加入课程状态
    # 当学生用户加入时，状态为"enrolled"，当学生退出时，状态为"not_enrolled"，默认为"not_enrolled"
    course_status = db.Column(db.String(20), nullable=False, server_default='not_enrolled')
    # Relationship
    course = db.relationship('Course', back_populates='course_students')

from app import db


class Course_Students(db.Model):
    __tablename__ = 'course_students'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_number = db.Column(db.String(20), nullable=False) #学号
    student_name = db.Column(db.String(20), nullable=False)
    student_pinyin_name = db.Column(db.String(20), nullable=True)
    student_grade = db.Column(db.String(20), nullable=True)
    student_major = db.Column(db.String(20), nullable=True)
    student_direction = db.Column(db.String(20), nullable=True)
    student_class = db.Column(db.String(20), nullable=True)
    student_status = db.Column(db.String(20), nullable=True) #学籍状态
    student_course_method = db.Column(db.String(20), nullable=True)
    #加入课程状态
    # 当学生用户加入时，状态为"enrolled"，当学生退出时，状态为"not_enrolled"，默认为"not_enrolled"
    course_status = db.Column(db.String(20), nullable=False, server_default='not_enrolled')
    # 平时表现分数
    score = db.Column(db.Float, nullable=True, server_default='0')  # 假设分数为浮点数类型
    # 总分数
    finally_score = db.Column(db.Float, nullable=True, server_default='0')  # 假设分数为浮点数类型
    # Relationship
    course = db.relationship('Course', back_populates='course_students')

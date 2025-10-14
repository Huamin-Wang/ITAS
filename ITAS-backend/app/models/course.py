from app import db

class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    semester = db.Column(db.String, nullable=False)  # 开课学期
    # 课程简介
    description = db.Column(db.Text)
    # 课程代码
    code = db.Column(db.String(10), nullable=False)

    # Relationship
    teacher = db.relationship('User', backref='courses')
    course_students = db.relationship('Course_Students',  back_populates='course')

    def __repr__(self):
        return f'<Course {self.id} - {self.name}>'
    
    def to_dict(self):
        """将课程对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'teacher_id': self.teacher_id,
            'semester': self.semester,
            'description': self.description,
            'code': self.code
        }
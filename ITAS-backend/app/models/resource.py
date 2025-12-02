from app import db

class Resource(db.Model):
    __tablename__ = 'resource'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.Text, nullable=False)
    
    # 定义关系
    teacher = db.relationship("User", foreign_keys=[teacher_id])
    
    def __init__(self, teacher_id, course_id,title=None,description=None, url=None):
        self.teacher_id = teacher_id
        self.course_id = course_id
        self.title = title
        self.description = description
        self.url = url    
    def __repr__(self):
        return f"<Resource(id={self.id}, title={self.title}, course_id={self.course_id})>"
    
    def to_dict(self):
        """将记录转换为字典格式"""
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'url': self.url
        }
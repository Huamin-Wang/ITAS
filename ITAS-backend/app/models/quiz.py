from app import db

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False, default=0)
    
    # 关联关系
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('QuizResponse', backref='quiz', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Quiz {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'title': self.title,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'course_id': self.course_id
        }
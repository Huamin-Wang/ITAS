from app import db

class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, nullable=False)
    student_number = db.Column(db.Text, nullable=True)
    title = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, nullable=True)
    course_id = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='draft')  #'draft', 'published', 'closed'
    
    # 关联关系
    questions = db.relationship('ExerciseQuestion', backref='exercise', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('ExerciseResponse', backref='exercise', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<exercise {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'student_number': self.student_number,
            'title': self.title,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'course_id': self.course_id,
            'description': self.description,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status
        }
from wang.models import db
class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False,default=0)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False,default=0)
    # Relationship
    responses = db.relationship('QuizResponse', backref='quiz', lazy=True)
    def __repr__(self):
        return f'<Quiz {self.id}>'


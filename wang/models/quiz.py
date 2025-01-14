from wang.models import db
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    # Relationship
    responses = db.relationship('QuizResponse', backref='quiz', lazy=True)
    def __repr__(self):
        return f'<Quiz {self.id}>'
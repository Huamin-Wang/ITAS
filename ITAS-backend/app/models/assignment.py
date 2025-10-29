from app import db

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    tags = db.Column(db.Text)
    # Relationship
    submissions = db.relationship('Submission', backref='assignment', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'course_id':self.course_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'tags':self.tags
        }

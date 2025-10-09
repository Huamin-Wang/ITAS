from app import db
# StudyMaterial model学习资料模型
class StudyMaterial(db.Model):
    __tablename__ = 'study_material'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file = db.Column(db.String(255), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    # Relationship 可以通过课程找到学习资料，也可以通过学习资料找到课程
    course = db.relationship('Course', backref='study_materials', lazy=True)
    def __repr__(self):
        return f'<StudyMaterial {self.id}>'

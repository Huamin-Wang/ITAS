from app import db

class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'gender': self.gender,
            'birth_date': self.birth_date,
            'phone': self.phone,
            'address': self.address,
        }
    
    def __repr__(self):
        return f'<Student {self.name}>'
from app import db

class Attendance(db.Model):
    __tablename__ = 'attendance'  # 表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('user.id', name='fk_attendance_user_id'),  # 显式命名外键
        nullable=False
    )
    
    date = db.Column(db.Date, nullable=False)  # 考勤日期
    status = db.Column(db.String(10), nullable=False)  # 签到状态 ('present' or 'absent')
    
    course_id = db.Column(
        db.Integer,
        db.ForeignKey('course.id', name='fk_attendance_course_id'),  # 显式命名外键
        nullable=False
    )

    def __repr__(self):
        return f"<Attendance(id={self.id}, user_id={self.user_id}, date={self.date}, status={self.status})>"

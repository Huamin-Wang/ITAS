
from wang.models import db

class Attendance(db.Model):
    __tablename__ = 'attendance' # 表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 关联到 Users 表的主键
    date = db.Column(db.Date, nullable=False)  # 考勤日期
    status = db.Column(db.String(10), nullable=False)  # 签到状态 ('present' or 'absent')

    def __repr__(self):
        return f"<Attendance(id={self.id}, user_id={self.user_id}, date={self.date}, status={self.status})>"

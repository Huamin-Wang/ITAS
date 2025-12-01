from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app import db
Base = declarative_base()

class Records(Base):
    __tablename__ = 'records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_student_id = Column(Integer, ForeignKey('course_student.id', ondelete='CASCADE'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    remark = Column(Text)
    
    # 定义关系
    course_student = relationship("CourseStudent", back_populates="records")
    teacher = relationship("User", foreign_keys=[teacher_id])
    
    def __init__(self, course_student_id, teacher_id, remark=None):
        self.course_student_id = course_student_id
        self.teacher_id = teacher_id
        self.remark = remark
    
    def __repr__(self):
        return f"<Records(id={self.id}, course_student_id={self.course_student_id}, teacher_id={self.teacher_id})>"
    
    def to_dict(self):
        """将记录转换为字典格式"""
        return {
            'id': self.id,
            'course_student_id': self.course_student_id,
            'teacher_id': self.teacher_id,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
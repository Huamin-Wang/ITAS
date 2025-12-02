from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app import db

class Records(db.Model):
    __tablename__ = 'records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course_student_id = db.Column(db.Integer, db.ForeignKey('course_students.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    remark = db.Column(db.Text)
    
    # 定义关系
    # course_student = db.relationship("CourseStudent", back_populates="remarks")
    teacher = db.relationship("User", foreign_keys=[teacher_id])
    
    def __init__(self, course_student_id, teacher_id, course_id,remark=None):
        self.course_student_id = course_student_id
        self.teacher_id = teacher_id
        self.course_id = course_id
        self.remark = remark
    
    def __repr__(self):
        return f"<Records(id={self.id}, course_student_id={self.course_student_id}, teacher_id={self.teacher_id})>"
    
    def to_dict(self):
        """将记录转换为字典格式"""
        return {
            'id': self.id,
            'course_student_id': self.course_student_id,
            'teacher_id': self.teacher_id,
            'course_id': self.course_id,
            'remark': self.remark,
        }
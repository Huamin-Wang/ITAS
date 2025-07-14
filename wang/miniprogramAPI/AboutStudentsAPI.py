# 微信小程序：返回学生的课程列表
from flask import Blueprint, request, jsonify, session

from wang.models import User, Course_Students, Course

# 获取学生课程列表
def getStudentCourses():
    # 从数据库中查找用户，与用户输入的密码进行比对
    openid = request.args.get('openid')
    print(f"openid:{openid}")
    user = User.query.filter_by(openid=openid).first()
    if user:
        print(f"{user.name}在微信小程序获取课程列表中！")
    print(session)
    if user:
        # 返回学生的课程列表
        course_students = Course_Students.query.filter_by(student_number=user.identifier,
                                                          ).all()
        courses = []
        for course_student in course_students:
            course = Course.query.get(course_student.course_id)
            # 课程序列化
            courses.append({
                'course_id': course.id,
                'course_name': course.name,
                'semester': course.semester,
                'description': course.description,
                "teacher": course.teacher.name
            })
        print("课程列表获取成功！")
        return jsonify({'success': True, 'courses': courses})
    print("用户不存在！")
    return jsonify({'success': False, 'message': '用户不存在！'})
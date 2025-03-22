from wang.models import User, Course_Students,Assignment


# 做一次更新总分操作，将学生的总分更新为平时分+作业总分
# 参数：学生ID，数据库对象
def  updateFinallyScore(studentID,db):
    # 获取学生的平时分和作业总分
    student=User.query.get(studentID)
    # 根据学号获取学生对应不同课程所处名单course_name_list
    course_name_list = Course_Students.query.filter_by(student_number=student.identifier).all()   # 这里会返回学生对应的好几门课的course_student
    # 根据课程匹配获取所有作业分数
    if course_name_list:
        for courseName in course_name_list:
            # 根据课程名单找到所处课程，并通过课程id找到所有作业
            all_assignments = []
            assignments = Assignment.query.filter_by(course_id=courseName.course.id).all()
            # 遍历当前课程所有作业，找到提交的作业
            for assignment in assignments:
                submissions = assignment.submissions
                # 遍历作业提交，找到当前学生的提交
                for submission in submissions:
                    # 如果提交的学生ID与当前学生ID匹配，则添加到作业列表中
                    if submission.student_id == student.id:
                        # 添加作业分数
                        if submission and submission.grade is not None:
                            all_assignments.append(submission.grade)
        # 计算作业总分
            total_assignment_score = sum(all_assignments) if all_assignments else 0
        # 获取平时分
            score = courseName.score
        # !!!!!!!!!!!当前课程总分，这里可以调整成绩比例，作业目前默认每道题10分!!!!!!!!!!!!
            finally_score = score*10+ total_assignment_score/2
        # 更新数据库总分
            courseName.finally_score = finally_score
        # 提交更改
            db.session.commit()
            print(f"Student {student.name} ({student.identifier})'s final score updated to {finally_score} for course {courseName.course.name}.")
    return finally_score



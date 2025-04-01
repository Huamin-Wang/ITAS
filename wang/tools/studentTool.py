from wang.models import User, Course_Students,Assignment


# 做一次更新总分操作，将学生的总分更新为平时分+作业分
# 参数：学生用户ID，数据库对象
def  updateFinallyScore_byUserID(studentID,db):
    finally_score = 0  # 初始化 finally_score
    # 获取学生的平时分和作业总分
    student=User.query.get(studentID)
    # 根据学号获取学生对应不同课程所处名单course_name_list
    course_name_list = Course_Students.query.filter_by(student_number=student.identifier).all()   # 这里会返回学生对应的好几门课的course_student
    # 根据课程匹配获取所有作业分数
    if course_name_list:
        for name_in_course in course_name_list:
            # 根据课程名单找到所处课程，并通过课程id找到所有作业
            all_assignments = []
            assignments = Assignment.query.filter_by(course_id=name_in_course.course.id).all()
            # 遍历当前课程所有作业，找到提交的作业
            for assignment in assignments:
                submissions = assignment.submissions
                # 遍历作业提交，找到当前学生的提交
                for submission in submissions:
                    # 如果提交的学生ID与当前学生ID匹配，则添加到作业列表中
                    if submission.student_id == student.id:
                        # 添加作业分数
                        if submission and submission.grade is not None:
                            # all_assignments.append(submission.grade)
                            all_assignments.append(1) # 由于豆包评分不准，交了作业就是1分
        # 计算作业总分
            total_assignment_score = sum(all_assignments) if all_assignments else 0
        # 获取平时分
            score = name_in_course.score
            if score is None:
                score = 0
        # !!!!!!!!!!!当前课程总分，这里可以调整成绩比例，作业目前默认每道题10分!!!!!!!!!!!!
            finally_score = score*10+ total_assignment_score #score：平时分 total_assignment_score：作业总分
        # 更新数据库总分
            name_in_course.finally_score = finally_score
        # 提交更改
            db.session.commit()
            # print(f"Student {student.name} ({student.identifier})'s final score updated to {finally_score} for course {courseName.course.name}.")
    return finally_score

# # 根据course_students表中的id更新当前课程的finally_score
# def updateScoreByCourseStudentID(course_student_id, db):
#     course_student = Course_Students.query.get(course_student_id)
#     # 根据course_student的学号获取当前学生用户
#     student = User.query.get(course_student.student_number)
#     # 获取作业总分
#     all_assignments_score = []
#     assignments= Assignment.query.filter_by(course_id=course_student.course_id).all()
#     for assignment in assignments:
#         # 遍历作业提交，找到当前学生的提交
#         submissions = assignment.submissions
#         print(f"作业提交为：{submissions}")
#         for submission in submissions:
#             if student:
#                 # 如果提交的学生ID与当前学生ID匹配，则添加到作业列表中
#                 if submission.student_id == student.id:
#                     print(f"提交为：{submission.student_id}  学生ID：{student.id}")
#                     # 添加作业分数
#                     if submission and submission.grade is not None:
#                         all_assignments_score.append(1) # 由于豆包评分不准，交了作业就是1分
#
#     # 计算作业总分
#     total_assignment_score = sum(all_assignments_score) if all_assignments_score else 0
#     # 获取平时分
#     score = course_student.score
#     # !!!!!!!!!!!当前课程总分，这里可以调整成绩比例，作业目前默认每道题10分!!!!!!!!!!!!
#     finally_score = score*10 + total_assignment_score #score：平时分 total_assignment_score：作业总分
#     # 更新数据库总分
#     course_student.finally_score = finally_score
#     # 提交更改
#     db.session.commit()
#     # print(f"Student {student.name} ({student.identifier})'s final score updated to {finally_score} for course {course_student.course.name}.")
#     print(f"{course_student.student_name}分数已经更新为{finally_score}，当前课程为{course_student.course.name}")
#     return finally_score



# 根据学生id输出所有作业以及待完成作业
def assignments(studentID,db):
    from wang.models.submission import Submission
    from wang.models.course import Course
    user = User.query.get(studentID)
    # 获取学生名下的课程：把course_students表中学号能匹配上的所有记录中的课程id找出来
    course_students = Course_Students.query.filter_by(student_number=user.identifier,
                                                      ).all()
    # 将course_students表中自己的学号对应的记录中的状态改为enrolled
    for course_student in course_students:
        course_student.course_status = 'enrolled'
        db.session.commit()  # 提交事务
    # 获取学生所有课程
    courses = []
    for course_student in course_students:
        course = Course.query.get(course_student.course_id)
        courses.append(course)
    # 获取学生所有课程的作业
    Allassignments = []
    # 根据courses获取所有的作业
    for course in courses:
        assignments = Assignment.query.filter_by(course_id=course.id).all()
        for assignment in assignments:
            Allassignments.append(assignment)
    # 输出待完成的作业
    assignments_to_do = []
    # 判断作业是否已经提交
    for assignment in Allassignments:
        # 通过student_id和assignment_id查找submission表中的记录
        # 如果有记录，说明已经提交
        submission = Submission.query.filter_by(student_id=user.id, assignment_id=assignment.id).first()
        if submission:
            pass   # 如果有记录，说明已经提交
        else:
            # 如果没有记录，说明未提交，输出未提交的作业
            # 将未提交作业添加到assignments_to_do中
            assignments_to_do.append(assignment)
    return Allassignments,assignments_to_do



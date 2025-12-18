from app import db
from app.models.course_students import Course_Students
from app.models.course import Course
from app.models.user import User
from app.models.Result import Result
from app.models.assignment import Assignment
from app.models.quiz import Quiz
from app.models.quizQuestion import QuizQuestion
from app.models.quizResponse import QuizResponse
from app.models.gradingResults import GradingResult
from app.models.records import Records
from app.models.resource import Resource
import chardet
import io
import csv
import json
from typing import Any

class CourseStudentService:
    
    #教师获取对应课程
    @staticmethod
    def get_all_course_by_teacher_id(teacher_id: int) -> Result:
        try:
            # 使用 filter_by 按教师ID查询所有课程
            courses = Course.query.filter_by(teacher_id=teacher_id).all()

            if not courses:
                return Result.success('暂无课程')

            # 获取所有课程ID，用于批量查询学生数量
            course_ids = [course.id for course in courses]

            # 批量查询每个课程的学生数量
            from sqlalchemy import func
            student_counts = db.session.query(
                Course_Students.course_id,
                func.count(Course_Students.id).label('student_count')
            ).filter(
                Course_Students.course_id.in_(course_ids)
            ).group_by(Course_Students.course_id).all()

            # 将学生数量转换为字典，便于查找
            student_count_dict = {course_id: count for course_id, count in student_counts}

            # 按学期分类课程
            courses_by_semester = {}
            for course in courses:
                # 转换学期格式
                semester = course.semester
                if semester:
                    # 将英文季节转换为中文
                    season_mapping = {
                        'spring': '春季学期',
                        'autumn': '秋季学期',
                        'fall': '秋季学期',
                    }

                    # 处理格式如 "2024-spring" 的学期
                    if '-' in semester:
                        year, season = semester.split('-', 1)
                        season = season.lower()
                        if season in season_mapping:
                            semester = f"{year} {season_mapping[season]}"
                    # 处理其他可能的格式，确保返回中文
                    else:
                        # 如果是纯英文季节，直接转换
                        semester_lower = semester.lower()
                        if semester_lower in season_mapping:
                            semester = season_mapping[semester_lower]

                course_dict = course.to_dict()

                # 添加学生数量信息
                course_dict['student_count'] = student_count_dict.get(course.id, 0)

                if semester not in courses_by_semester:
                    courses_by_semester[semester] = []

                courses_by_semester[semester].append(course_dict)

            # 按学期排序（按年份和季节排序）
            def semester_sort_key(semester):
                """为学期生成排序键"""
                if not semester or '-' not in semester:
                    return (0, semester)

                try:
                    year_part, season_part = semester.split('-', 1)
                    year = int(year_part) if year_part.isdigit() else 0

                    # 季节排序权重
                    season_weights = {'春季学期': 1, '秋季学期': 2}
                    season_weight = season_weights.get(season_part, 5)

                    return (year, season_weight)
                except:
                    return (0, semester)

            sorted_semesters = sorted(courses_by_semester.keys(), key=semester_sort_key, reverse=True)

            # 构建返回数据
            result_data = []
            for semester in sorted_semesters:
                result_data.append({
                    'semester': semester,
                    'courses': courses_by_semester[semester],
                    'course_count': len(courses_by_semester[semester])
                })

            return Result.success(data=result_data)

        except Exception as e:
            return Result.internal_error(f'获取课程失败: {str(e)}')
    
    #课程id获取课程
    @staticmethod
    def get_course_by_id(course_id: int) -> Result:
        try:
            course = Course.query.get(course_id)
            if not course:
                return Result.not_found('课程不存在')
            return Result.success(data=course.to_dict())
        except Exception as e:
            return Result.internal_error(f'获取课程失败: {str(e)}')

    #创建课程
    @staticmethod
    def create_course(data: dict[str, Any], student_file) -> Result:
        try:
            required_fields = ['course_name', 'semester', 'course_code','teacher_id']
            for field in required_fields:
             if not data.get(field):
                return Result.bad_request(f'缺少必填字段: {field}')
            # 获取课程数据
            course_name = data.get('course_name')
            semester = data.get('semester')
            course_description = data.get('course_description')
            code = data.get('course_code')
            teacher_id = data.get('teacher_id')
            course = Course(name=course_name, semester=semester, description=course_description, code=code,
                        teacher_id=teacher_id)
            db.session.add(course)
            db.session.commit()

            if student_file:
                try:
                    raw_data = getattr(student_file, 'stream', None)
                    if raw_data is not None:
                        raw_bytes = raw_data.read()
                    else:
                        raw_bytes = student_file.read()
                except Exception:
                    raw_bytes = None

                if raw_bytes:
                    result = chardet.detect(raw_bytes)
                    encoding = result.get('encoding') or 'utf-8'
                    try:
                        file_str = io.StringIO(raw_bytes.decode(encoding), newline=None)
                    except Exception:
                        try:
                            file_str = io.StringIO(raw_bytes.decode('utf-8'), newline=None)
                        except Exception:
                            file_str = io.StringIO(raw_bytes.decode('gbk', errors='ignore'), newline=None)

                    csv_reader = csv.reader(file_str)
                    # 尝试跳过表头
                    try:
                        next(csv_reader)
                    except StopIteration:
                        pass

                    students_to_add = []
                    for row in csv_reader:
                        if len(row) < 1:
                            continue
                        student_number = row[0] if len(row) > 0 else None
                        student_name = row[1] if len(row) > 1 else None
                        student_pinyin_name = row[2] if len(row) > 2 else None
                        student_grade = row[3] if len(row) > 3 else None
                        student_major = row[4] if len(row) > 4 else None
                        student_direction = row[5] if len(row) > 5 else None
                        student_class = row[6] if len(row) > 6 else None
                        student_status = row[7] if len(row) > 7 else None
                        student_course_method = row[8] if len(row) > 8 else None

                        course_student = Course_Students(
                            course_id=course.id,
                            student_number=student_number,
                            student_name=student_name,
                            student_pinyin_name=student_pinyin_name,
                            student_grade=student_grade,
                            student_major=student_major,
                            student_direction=student_direction,
                            student_class=student_class,
                            student_status=student_status,
                            student_course_method=student_course_method
                        )
                        students_to_add.append(course_student)

                    if students_to_add:
                        db.session.add_all(students_to_add)
                else:
                    return Result.bad_request('请上传的学生文件')

            db.session.commit()
            return Result.success(data=course.to_dict())
        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'创建课程失败: {str(e)}')
    
    #更新学生注册状态
    @staticmethod
    def update_registration_status(course_id) -> Result:
        try:
            course = Course.query.get(course_id)
            if not course:
                return Result.not_found('课程不存在')

            course_students = course.course_students

            # 批量获取所有学生的注册状态
            student_numbers = [cs.student_number for cs in course_students if cs.student_number]
            existing_users = User.query.filter(User.identifier.in_(student_numbers)).all()
            existing_user_identifiers = {user.identifier for user in existing_users}

            # 批量更新状态
            for course_student in course_students:
                if course_student.student_number in existing_user_identifiers:
                    course_student.course_status = 'enrolled'
                else:
                    course_student.course_status = 'not_enrolled'

            # 一次性提交
            db.session.commit()

            return Result.success(data={'course_id': course.id})

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'更新学生状态失败: {str(e)}')

    #获取课程学生数量
    @staticmethod
    def get_course_student_count(course_id) -> Result:
        try:
            course = Course.query.get(course_id)
            if not course:
                return Result.not_found('课程不存在')

            # 初始化计数器
            enrolled_count = 0
            not_enrolled_count = 0

            # 遍历课程学生并统计不同状态的数量
            for student in course.course_students:
                if student.course_status == 'enrolled':
                    enrolled_count += 1
                elif student.course_status == 'not_enrolled':
                    not_enrolled_count += 1

            return Result.success(data={
                'course_id': course.id,
                'enrolled_count': enrolled_count,
                'not_enrolled_count': not_enrolled_count,
                'total_count': enrolled_count + not_enrolled_count
            })

        except Exception as e:
            return Result.internal_error(f'获取学生数量失败: {str(e)}')

    #获取课程学生
    @staticmethod
    def course_students(course_id):
        try:
            course = Course.query.get(course_id)
            if not course:
                return Result.not_found('课程不存在')

            # 获取课程学生及其备注（假设有relationship）
            course_students = course.course_students

            # 处理学生数据
            enrolled_students = []
            not_enrolled_students = []

            for student in course_students:
                student_data = student.to_dict()

                # 假设 student 有一个 remarks 关系属性
                # 或者通过 Records.query 获取该学生的备注
                remark = Records.query.filter_by(
                    course_id=course_id, 
                    course_student_id=student.id
                ).first()

                if remark:
                    student_data['remark'] = remark.to_dict()['remark']
                    # 或者 student_data['remark'] = remark.content 如果只需要内容
                else:
                    student_data['remark'] = None

                if student.course_status == 'enrolled':
                    enrolled_students.append(student_data)
                else:
                    not_enrolled_students.append(student_data)

            data = {
                'enrolled_students': enrolled_students,
                'not_enrolled_students': not_enrolled_students,
                'enrolled_students_count': len(enrolled_students),
            }

            return Result.success(data=data)

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'获取学生失败: {str(e)}')

    #更新课程 
    @staticmethod
    def update_course(data: dict[str, Any],student_file) -> Result:
        try:
            course_id = data.get('course_id')
            course = Course.query.get(course_id)
            if not course:
                return Result.internal_error(f'课程 {course_id} 未找到')

            # 更新课程信息
            if data:
                name = data.get('name') or data.get('course_name')
                semester = data.get('semester')
                description = data.get('description') or data.get('course_description')
                code = data.get('code') or data.get('course_code')
                if name is not None:
                    course.name = name
                if semester is not None:
                    course.semester = semester
                if description is not None:
                    course.description = description
                if code is not None:
                    course.code = code
            if student_file:
                try:
                    # 将文件内容读取为字符串
                    raw_data = student_file.stream.read()
                    # 检测文件编码
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']
                    # 尝试用检测到的编码解码文件
                    try:
                        file_str = io.StringIO(raw_data.decode(encoding), newline=None)
                    except UnicodeDecodeError:
                        # 如果检测到的编码失败，尝试 utf-8 或 gbk
                        try:
                            file_str = io.StringIO(raw_data.decode('utf-8'), newline=None)
                        except UnicodeDecodeError:
                            file_str = io.StringIO(raw_data.decode('gbk'), newline=None)
                    # 解析CSV文件
                    csv_reader = csv.reader(file_str)
                    next(csv_reader)  # 跳过表头
                    students_to_add = []
                    for row in csv_reader:
                        # 格式为：学号、姓名、拼音姓名、年级、专业、方向、行政班级、学籍状态、修课方式
                        # 将每条数据存储到数据库
                        student_number = row[0]
                        student_name = row[1]
                        student_pinyin_name = row[2]
                        student_grade = row[3]
                        student_major = row[4]
                        student_direction = row[5]
                        student_class = row[6]
                        student_status = row[7]
                        student_course_method = row[8]
                        course_student = Course_Students(course_id=course.id, student_number=student_number,
                                                         student_name=student_name,
                                                         student_pinyin_name=student_pinyin_name,
                                                         student_grade=student_grade, student_major=student_major,
                                                         student_direction=student_direction,
                                                         student_class=student_class,
                                                         student_status=student_status,
                                                         student_course_method=student_course_method)
                        students_to_add.append(course_student)
                    # 取出当前课程中的学生名单
                    course_students = course.course_students
                    # 通过对比course_students与students_to_add中学生的学号（student_number），如果course_students中有的学生在students_to_add中没有，则删除，如果有，则不进行操作，对于students_to_add中有而course_students中没有的学生，则添加
                    # 提取所有学生编号到集合中，提升查找效率
                    existing_student_numbers = {student1.student_number for student1 in course_students}
                    new_student_numbers = {student2.student_number for student2 in students_to_add}

                    # 删除新表中没有的学生
                    for student1 in course_students:
                        if student1.student_number not in new_student_numbers:
                            db.session.delete(student1)

                    # 增加旧表中缺的学生
                    for student2 in students_to_add:
                        if student2.student_number not in existing_student_numbers:
                            db.session.add(student2)
                except Exception as e:
                    return Result.internal_error(f'更新学生列表失败: {str(e)}')
            db.session.commit()
            return Result.success(data={'course_id': course.id})
        except Exception as e:
            try:
                db.session.rollback()
            except Exception:
                pass
            return Result.internal_error(f'更新课程失败: {str(e)}')
    
    #随机选择学生
    @staticmethod
    def random_select_list(course_id):
        try:
            course = Course.query.get(course_id)
            course_students = course.course_students
            data = {
            'course_students': [student.to_dict() for student in course_students],
            }
            return Result.success(data=data)
        except Exception as e:
            return Result.internal_error(f'获取学生失败: {str(e)}')
    
    #更新学生分数
    @staticmethod
    def update_score(data: list[dict[str, Any]], course_id) -> Result:
        try:
            # 检查课程是否存在
            course = Course.query.get(course_id)
            if not course:
                return Result.error("课程不存在")
            result_data = []
            # 遍历前端传来的加分数据
            for student_data in data:
                student_name = student_data.get('student_name')
                student_number = student_data.get('student_number')
                score_change = student_data.get('score_change', 0)
                try:
                    score_change = float(score_change)
                except (ValueError, TypeError):
                    score_change = 0

                # 直接查询该课程下对应学号的学生
                course_student = Course_Students.query.filter_by(
                    course_id=course_id,
                    student_number=student_number
                ).first()

                if course_student:
                    # 直接更新该学生分数
                    course_student.score += score_change
                    result_data.append({
                    'student_name': student_name,
                    'score_change': score_change
                })
                else:
                    # 记录警告或跳过不存在的学生
                    print(f"警告: 课程 {course_id} 中未找到学号为 {student_number} 的学生")

            db.session.commit()
            return Result.success(result_data)

        except Exception as e:
            try:
                db.session.rollback()
            except Exception:
                pass
            return Result.internal_error(f'学生加分失败: {str(e)}')
    
    # 获取课程学生排名
    @staticmethod
    def ranking(course_id) -> Result:
            try:
                # 检查课程是否存在
                course = Course.query.get(course_id)
                if not course:
                    return Result.error("课程不存在")

                # 获取该课程下所有学生并按分数降序排序
                ranked_students = Course_Students.query.filter_by(course_id=course_id).order_by(
                    Course_Students.score.desc()
                ).all()

                # 准备返回数据
                ranked_list = [
                    {
                        'student_number': student.student_number,
                        'student_name': student.student_name,
                        'score': student.score
                    }
                    for student in ranked_students
                ]

                return Result.success(data=ranked_list)

            except Exception as e:
                try:
                    db.session.rollback()
                except Exception:
                    pass
                return Result.internal_error(f'获取排名失败: {str(e)}')

    #查询作业
    @staticmethod
    def get_assignments(course_id: int) -> Result:
        try:
            assignments = Assignment.query.filter_by(course_id=course_id).all()
            if not assignments:
                return Result.success('')
            assignments_data = [assignment.to_dict() for assignment in assignments]
            return Result.success(data=assignments_data)
        except Exception as e:
            return Result.internal_error(f'获取作业失败: {str(e)}')

    #通过id查询作业
    @staticmethod
    def get_assignment_by_id(assignment_id: int) -> Result:
        try:
            assigment = Assignment.query.get(assignment_id)
            if not assigment:
                return Result.not_found('作业不存在')
            return Result.success(data=assigment.to_dict())
        except Exception as e:
            return Result.internal_error(f'获取作业失败: {str(e)}')

    #创建作业
    @staticmethod
    def assignments(data: dict[str, Any]) -> Result:
        try:
            # 检查课程是否存在
            course_id = data.get('course_id')
            course = Course.query.get(course_id)
            if not course:
                return Result.internal_error(f'课程 {course_id} 未找到')

            # 获取表单数据
            assignment_name = data.get('title')
            assignment_description = data.get('description')
            assignment_deadline_str = data.get('due_date')
            teacher_id = data.get('teacher_id')
            # tags = data.get('tags')
            # 验证必填字段
            if not all([assignment_name, assignment_deadline_str]):
                return Result.internal_error(f'作业名称和截止日期是必填的')

            # 转换日期格式
            from datetime import datetime
            try:
                assignment_deadline = datetime.strptime(assignment_deadline_str, '%Y-%m-%d').date()
            except ValueError:
                return Result.internal_error(f'截止日期格式错误，应为 YYYY-MM-DD')

            # 创建作业
            assignment = Assignment(
                teacher_id=teacher_id, 
                course_id=course_id,
                title=assignment_name,
                description=assignment_description, 
                due_date=assignment_deadline,
                # tags = tags
            )

            db.session.add(assignment)
            db.session.commit()


            # 返回成功响应
            return Result.success(data=assignment.to_dict())

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'创建作业失败: {str(e)}')
        
    #编辑作业
    @staticmethod
    def update_assignment(data: dict[str, Any]) -> Result:
        try:
            assignment_id = data.get('id')
            assignment = Assignment.query.get(assignment_id)
            if not assignment:
                return Result.not_found(f'作业 {assignment_id} 未找到')
            
            # 更新作业信息
            assignment.title = data.get('title', assignment.title)
            assignment.description = data.get('description', assignment.description)
            # assignment.tags = data.get('tags',assignment.tags)
            due_date_str = data.get('due_date')
            if due_date_str:
                from datetime import datetime
                try:
                    assignment.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Result.internal_error(f'截止日期格式错误，应为 YYYY-MM-DD')

            db.session.commit()
            return Result.success(data=assignment.to_dict())

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'更新作业失败: {str(e)}')
    

    #创建小测
    @staticmethod
    def create_quiz(data: dict[str, Any]) -> Result:
        try:
            # 检查课程是否存在
            course_id = data.get('course_id')
            course = Course.query.get(course_id)
            if not course:
                return Result.internal_error(f'课程 {course_id} 未找到')

            # 获取表单数据
            title = data.get('title')
            teacher_id = data.get('teacher_id')
            create_time = data.get('create_time')
            description = data.get('description')
            # 验证必填字段
            if not all([title, teacher_id]):
                return Result.internal_error(f'小测标题和教师id是必填的')
            # 转换日期格式
            from datetime import datetime
            try:
                create_time = datetime.strptime(create_time, '%Y-%m-%d %H:%M')
            except ValueError:
                return Result.internal_error(f'截止日期格式错误，应为 YYYY-MM-DD HH:MM')
            # 创建作业
            quiz = Quiz(
                teacher_id=teacher_id, 
                course_id=course_id,
                title=title,
                description=description,
                create_time=create_time
            )

            db.session.add(quiz)
            db.session.commit()


            # 返回成功响应
            return Result.success(data=quiz.to_dict())

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'创建小测失败: {str(e)}')
        
    #存储小测题目
    @staticmethod
    def add_quiz_questions(quiz_id: int, questions: list[dict[str, Any]]) -> Result:
        try:
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return Result.not_found(f'小测 {quiz_id} 未找到')
            quiz_questions = []
            print(questions)
            for question_data in questions:
                question_text = question_data.get('question_text')
                question_type = question_data.get('question_type')
                options = json.dumps(question_data.get('options'))
                correct_answer = question_data.get('correct_answer')
                points = question_data.get('points', 1)
                if not all([question_text, question_type]):
                    return Result.bad_request('题目文本、题目类型是必填的')
                quiz_question = QuizQuestion(
                    quiz_id=quiz_id,
                    question_text=question_text,
                    question_type=question_type,
                    options=options,
                    correct_answer=correct_answer,
                    points=points
                )
                quiz_questions.append(quiz_question)
            db.session.add_all(quiz_questions)
            db.session.commit()
            return Result.success(data={'quiz_id': quiz_id, 'added_questions': len(quiz_questions)})
        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'添加小测题目失败: {str(e)}')
    
   #获取小测列表
    @staticmethod
    def get_quizzes(course_id: int) -> Result:
        try:
            quizzes = Quiz.query.filter_by(course_id=course_id).all()
            if not quizzes:
                return Result.success('')

            # 📌 获取当前时间
            from datetime import datetime
            now = datetime.now()
            # 📌 批量更新已超时的小测状态
            need_commit = False
            for quiz in quizzes:
                if quiz.end_time and quiz.status != "finished":
                    if now > quiz.end_time:
                        quiz.status = "finished"
                        need_commit = True

            # 若有更新则提交数据库
            if need_commit:
                db.session.commit()

            # 批量统计每个 quiz 的题目数量以避免 N+1 查询
            quiz_ids = [q.id for q in quizzes]
            from sqlalchemy import func
            counts = db.session.query(
                QuizQuestion.quiz_id,
                func.count(QuizQuestion.id).label('question_count')
            ).filter(QuizQuestion.quiz_id.in_(quiz_ids)).group_by(QuizQuestion.quiz_id).all()

            counts_dict = {quiz_id: cnt for quiz_id, cnt in counts}

            quizzes_data = []
            for quiz in quizzes:
                qd = quiz.to_dict()
                qd['question_count'] = counts_dict.get(quiz.id, 0)
                quizzes_data.append(qd)

            return Result.success(data=quizzes_data)

        except Exception as e:
            return Result.internal_error(f'获取小测失败: {str(e)}')
       
    #获取小测详情
    @staticmethod
    def get_quiz_questions(quiz_id: int) -> Result:
        try:
            # 获取小测信息
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return Result.not_found('小测不存在')

            # 获取题目列表
            quiz_questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
            questions_list = [question.to_dict() for question in quiz_questions]

            # 组合数据
            result_data = {
                'quiz': quiz.to_dict(),
                'questions': questions_list
            }

            return Result.success(data=result_data)
        except Exception as e:
            return Result.internal_error(f'获取小测详情失败: {str(e)}')
        
    #更新小测
    @staticmethod
    def update_quiz(data: dict[str, Any]) -> Result:
        try:
            quiz_id = data.get('id')
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return Result.not_found(f'小测 {quiz_id} 未找到')

            # 允许更新的字段列表
            updatable_fields = ['title', 'description','end_time']

            # 简单字段直接赋值
            for field in ['title', 'description']:
                if field in data:
                    setattr(quiz, field, data.get(field))


            # 更新题目信息
            if 'questions' in data:
                questions_data = data.get('questions')
                incoming_question_ids = set()

                for question_data in questions_data:
                    question_id = question_data.get('id')
                    if question_id:
                        # 更新现有题目
                        question = QuizQuestion.query.get(question_id)
                        if question and question.quiz_id == quiz_id:
                            # 更新题目的各个字段
                            question.question_text = question_data.get('question_text', question.question_text)
                            question.question_type = question_data.get('question_type', question.question_type)
                            question.correct_answer = question_data.get('correct_answer', question.correct_answer)
                            question.points = question_data.get('points', question.points)

                            # 处理选项字段
                            if 'options' in question_data:
                                question.options = json.dumps(question_data['options'])

                            incoming_question_ids.add(question_id)
                    else:
                        # 创建新题目
                        new_question = QuizQuestion(
                            quiz_id=quiz_id,
                            question_text=question_data.get('question_text', ''),
                            question_type=question_data.get('question_type', 'single_choice'),
                            correct_answer=question_data.get('correct_answer', ''),
                            points=question_data.get('points', 1),
                            options=json.dumps(question_data.get('options', []))
                        )
                        db.session.add(new_question)
                        db.session.flush()
                        incoming_question_ids.add(new_question.id)
                # 删除不在传入列表中的题目
                existing_questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
                for existing_question in existing_questions:
                    if existing_question.id not in incoming_question_ids:
                        db.session.delete(existing_question)

            db.session.commit()
            return Result.success(data=quiz.to_dict())

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'更新小测失败: {str(e)}')

        #发布小测
    
    #发布小测
    @staticmethod
    def publish_quiz(data: dict[str, Any]) -> Result:
        """教师发布小测，同时触发 SSE 推送"""
        quiz_id = data.get('quiz_id')
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return Result.not_found("小测不存在")
        # 转换日期格式
        from datetime import datetime, timedelta
        if 'deadline_time' in data:
            deadline_time = data.get('deadline_time')
            quiz.end_time = datetime.now() + timedelta(minutes=int(deadline_time))
            quiz.status = 'published'
            db.session.commit()

        return Result.success("发布成功")
    
    #删除小测
    @staticmethod
    def delete_quiz(quiz_id: int) -> Result:
        try:
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return Result.not_found(f'小测 {quiz_id} 未找到')

            db.session.delete(quiz)
            db.session.commit()
            return Result.success(data={'quiz_id': quiz_id})

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'删除小测失败: {str(e)}')

    #获取学生小测提交详情
    @staticmethod
    def get_quiz_response(data: dict[str, Any]) -> Result:
        try:
            quiz_id = data.get('quiz_id')
            student_number = data.get('student_number')
            if not quiz_id or not student_number:
                return Result.error("quiz_id和student_number不能为空")

            # 一次性获取所有相关的题目信息
            quiz_responses = QuizResponse.query.filter_by(
                quiz_id=quiz_id,
                student_number=student_number
            ).all()

            # 收集所有题目ID
            question_ids = [response.question_id for response in quiz_responses]

            # 批量查询题目信息
            questions = QuizQuestion.query.filter(
                QuizQuestion.id.in_(question_ids)
            ).all()

            # 创建题目ID到题目信息的映射
            questions_map = {question.id: question.to_dict() for question in questions}

            # 转换为字典列表并添加题目信息
            responses_list = []
            for response in quiz_responses:
                response_dict = {
                    'id': response.id,
                    'quiz_id': response.quiz_id,
                    'student_number': response.student_number,
                    'response': response.response,
                    'question_id': response.question_id,
                }

                # 添加对应的题目信息
                if response.question_id in questions_map:
                    response_dict['question'] = questions_map[response.question_id]
                else:
                    response_dict['question'] = None

                responses_list.append(response_dict)

            return Result.success(responses_list)
        except Exception as e:
            return Result.internal_error(f'获取小测提交详情失败: {str(e)}')

    #判断学生是否提交小测
    def has_submitted_quiz(data: dict[str, Any]) -> Result:
        try:
            quiz_id = data.get('quiz_id')
            identifier_arr = data.get('identifier_arr')

            # 确保identifier_arr是列表格式
            if isinstance(identifier_arr, (str, int, float)):
                identifier_arr = [identifier_arr]
            elif not identifier_arr:
                identifier_arr = []

            if not quiz_id or not identifier_arr:
                return Result.error("quiz_id和identifier_arr不能为空")
            quiz = Quiz.query.filter_by(id=quiz_id).first()
            if not quiz:
                return Result.error("指定的测试不存在")

            quiz_title = quiz.title
            # 批量查询提交记录 - 查询每个学生的student_number和response_time
            submitted_students = QuizResponse.query.filter(
                QuizResponse.quiz_id == quiz_id,
                QuizResponse.student_number.in_(identifier_arr)
            ).with_entities(
                QuizResponse.student_number,
                QuizResponse.response_time
            ).distinct(QuizResponse.student_number).all()

            # 转换为字典，方便快速查找
            submitted_info = {student.student_number: student.response_time for student in submitted_students}

            # 批量查询用户信息
            students = Course_Students.query.filter(Course_Students.student_number.in_(identifier_arr)).all()
            user_map = {user.student_number: user for user in students}

            # 构建结果列表
            result_list = []
            for identifier in identifier_arr:
                user = user_map.get(identifier)
                submitted = identifier in submitted_info
                result_list.append({
                    'identifier': identifier,
                    'student_name': user.student_name if user else '用户不存在',
                    'submitted': submitted,
                    'response_time': submitted_info.get(identifier) if submitted else None
                })

            return Result.success(data={'quiz_title': quiz_title, 'result_list': result_list})

        except Exception as e:
            return Result.internal_error(f'检查提交状态失败: {str(e)}')
    
    #获取班级学生学号
    def get_student_numbers(course_id: int) -> Result:
        try:
            course_students = Course_Students.query.filter_by(course_id=course_id).all()
            student_numbers = [student.student_number for student in course_students if student.student_number]
            return Result.success(data={'student_numbers': student_numbers})
        except Exception as e:
            return Result.internal_error(f'获取学生学号失败: {str(e)}')

    #创建更新备注
    @staticmethod
    def create_update_record(data: dict[str, Any]) -> Result:
        try:
            course_student_id = data.get('course_student_id')
            teacher_id = data.get('teacher_id')
            course_id = data.get('course_id')
            remark = data.get('remark')

            if not all([course_student_id, teacher_id, course_id]):
                return Result.bad_request('缺少必填字段: course_student_id 或 teacher_id 或 course_id')

            existing_record = Records.query.filter_by(
                course_student_id=course_student_id
            ).first()

            if existing_record:
                # 更新备注
                existing_record.remark = remark
                db.session.commit()
                return Result.success(data=existing_record.to_dict())

            else:
                # 创建新的备注记录
                new_record = Records(
                    course_student_id=course_student_id,
                    teacher_id=teacher_id,
                    course_id=course_id,
                    remark=remark
                )

                db.session.add(new_record)
                db.session.commit()
                return Result.success(data=new_record.to_dict())

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'创建备注失败: {str(e)}')

        #通知学生小测更新
    
    # #获取备注
    # @staticmethod
    # def get_records(course_id: int) -> Result:
    #     try:
    #         records = Records.query.filter_by(course_id=course_id).all()
    #         records_data = [record.to_dict() for record in records]
    #         return Result.success(data=records_data)
    #     except Exception as e:
    #         return Result.internal_error(f'获取备注失败: {str(e)}')

    #获取课程资源
    @staticmethod
    def get_resources(course_id: int) -> Result:
        try:
            resources = Resource.query.filter_by(course_id=course_id).all()
            if not resources:
                return Result.success('')

            resources_data = [resource.to_dict() for resource in resources]
            return Result.success(data=resources_data)
        except Exception as e:
            return Result.internal_error(f'获取资源失败: {str(e)}')
    
    #创建课程资源
    @staticmethod
    def create_resource(data: dict[str, Any]) -> Result:
        try:
            # 检查课程是否存在
            course_id = data.get('course_id')
            course = Course.query.get(course_id)
            if not course:
                return Result.internal_error(f'课程 {course_id} 未找到')

            # 获取数据
            title = data.get('title')
            description = data.get('description')
            url = data.get('url')
            teacher_id = data.get('teacher_id')

            # 验证必填字段
            if not all([title, url, teacher_id]):
                return Result.internal_error(f'资源标题、URL和教师ID是必填的')

            # 创建资源
            resource = Resource(
                teacher_id=teacher_id, 
                course_id=course_id,
                title=title,
                description=description,
                url=url
            )

            db.session.add(resource)
            db.session.commit()

            # 返回成功响应
            return Result.success(data=resource.to_dict())

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'创建资源失败: {str(e)}')
        
    #删除课程资源
    @staticmethod
    def delete_resource(resource_id: int) -> Result:
        try:
            resource = Resource.query.get(resource_id)
            if not resource:
                return Result.not_found(f'资源 {resource_id} 未找到')

            db.session.delete(resource)
            db.session.commit()
            return Result.success(data={'resource_id': resource_id})

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'删除资源失败: {str(e)}')
        
    #存储批改结果
    @staticmethod
    def add_grading_results(data: dict[str, Any]) -> Result:
        """
        添加或更新批改结果
        支持批量提交，通过grading_list字段传递批改结果列表
        """
        try:
            # 获取批改列表
            grading_list = data.get('grading_list', [])

            if not grading_list or not isinstance(grading_list, list):
                return Result.validation_error('批改结果列表不能为空')

            results = []
            from datetime import datetime

            for item_data in grading_list:
                # 获取关键字段
                assignment_id = item_data.get('assignment_id')
                quiz_id = item_data.get('quiz_id')
                question_id = item_data.get('question_id')
                student_number = item_data.get('student_number')
                title = item_data.get('title')

                # 验证必要字段
                if not student_number:
                    return Result.validation_error('学生学号不能为空')

                if not title:
                    return Result.validation_error('作业/小测标题不能为空')

                # 必须要有 assignment_id 或 quiz_id 中的一个
                if not assignment_id and not quiz_id:
                    return Result.validation_error('必须提供 assignment_id 或 quiz_id')

                # 构建查询条件
                filter_condition = {
                    'student_number': student_number
                }

                if assignment_id:
                    filter_condition['assignment_id'] = assignment_id
                else:
                    filter_condition['quiz_id'] = quiz_id

                # 如果有 question_id，也作为查询条件
                if question_id:
                    filter_condition['question_id'] = question_id

                # 检查是否已存在该学生的批改记录
                existing_record = GradingResult.query.filter_by(**filter_condition).first()

                if existing_record:
                    # 更新现有记录
                    existing_record.score = item_data.get('score', existing_record.score)
                    existing_record.total_score = item_data.get('total_score', existing_record.total_score)
                    existing_record.comment = item_data.get('comment', existing_record.comment)
                    existing_record.student_answer = item_data.get('student_answer', existing_record.student_answer)
                    existing_record.reference_answer = item_data.get('reference_answer', existing_record.reference_answer)
                    existing_record.status = item_data.get('status', existing_record.status)
                    existing_record.grading_time = datetime.now()
                    results.append(existing_record)
                else:
                    # 创建新的批改记录
                    new_record = GradingResult(
                        assignment_id=item_data.get('assignment_id'),
                        quiz_id=item_data.get('quiz_id'),
                        question_id=item_data.get('question_id', ''),
                        student_number=student_number,
                        title=title,
                        description=item_data.get('description', ''),
                        student_answer=item_data.get('student_answer', ''),
                        reference_answer=item_data.get('reference_answer', ''),
                        total_score=item_data.get('total_score', 0.0),
                        score=item_data.get('score', 0.0),
                        comment=item_data.get('comment', ''),
                        status=item_data.get('status', 'completed')
                    )
                    db.session.add(new_record)
                    results.append(new_record)

            db.session.commit()

            return Result.success(
                message=f'成功保存{len(results)}条批改结果'
            )

        except KeyError as e:
            db.session.rollback()
            return Result.validation_error(f'缺少必要字段: {str(e)}')
        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'存储批改结果失败: {str(e)}')
        
    #获取批改结果
    @staticmethod
    def get_grading_results(data: dict[str, Any]) -> Result:
        try:
            quiz_id = data.get('quiz_id')
            student_number = data.get('student_number')

            if not quiz_id or not student_number:
                return Result.error('quiz_id和student_number不能为空')

            # 查询批改结果
            grading_results = GradingResult.query.filter_by(
                quiz_id=quiz_id,
                student_number=student_number
            ).all()

            results_data = [result.to_dict() for result in grading_results]

            return Result.success(results_data)

        except Exception as e:
            return Result.internal_error(f'获取批改结果失败: {str(e)}')
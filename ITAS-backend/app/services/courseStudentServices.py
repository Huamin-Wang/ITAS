from app import db
from app.models.course_students import Course_Students
from app.models.course import Course
from app.models.user import User
from app.models.Result import Result
from app.models.assignment import Assignment
import chardet
import io
import csv
from typing import Any

class CourseStudentService:
    
    #教师获取对应课程
    @staticmethod
    def get_all_course_by_teacher_id(teacher_id: int) -> Result:
        try:
            # 使用 filter_by 按教师ID查询所有课程
            courses = Course.query.filter_by(teacher_id=teacher_id).all()

            if not courses:
                return Result.not_found('暂无课程')

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
                
            course_students = course.course_students
            
            # 使用模型的 to_dict 方法序列化数据
            enrolled_students = [
                student.to_dict()
                for student in course_students if student.course_status == 'enrolled'
            ]
            
            not_enrolled_students = [
                student.to_dict()
                for student in course_students if student.course_status == 'not_enrolled'
            ]
            
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
                due_date=assignment_deadline
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
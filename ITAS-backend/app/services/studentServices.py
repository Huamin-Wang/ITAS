from app import db
from app.models.user import User
from app.models.course import Course
from app.models.course_students import Course_Students
from app.models.assignment import Assignment
from app.models.quiz import Quiz
from app.models.quizResponse import QuizResponse
from app.models.exercise import Exercise
from app.models.exerciseQuestion import ExerciseQuestion
from app.models.exerciseResponse import ExerciseResponse
from app.models.gradingResults import GradingResult
from app.models.Result import Result
from typing import Any
from datetime import datetime,timezone

class StudentService:
    @staticmethod
    def get_user_by_id(user_id: int) :
        try:
            user = User.query.get(user_id)
            if not user:
                return None

            return {
                'user_id': user.id,
                'name': user.name,
                'identifier': user.identifier,
                'role': user.role,
                'email': user.email
            }
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None

    @staticmethod
    def get_all_courses():
        return Course.query.all()
    
    @staticmethod
    def get_course_by_id(course_id):
        # 根据课程ID获取课程详情
        try:
            course = Course.query.filter_by(id=course_id).first()
            if course:
                return course
            else:
                return None
        except Exception as e:
            print(f"获取课程详情失败: {str(e)}")
            return None 
    
    @staticmethod
    def get_course_detail(course_id) -> Result:
        try:
            course = Course.query.filter_by(id=course_id).first()
            if course:
                # 返回包含教师信息的课程详情
                course_data = course.to_dict()
                course_data['teacher_name'] = course.teacher.name if course.teacher else '未知教师'
                return Result.success(course_data) 
            return None
        except Exception as e:
            print(f"获取课程详情失败: {str(e)}")
            return None

    @staticmethod
    def get_course_students_by_identifier(identifier: str) -> Result:
        """根据用户identifier获取课程学生信息"""
        try:
            course_student = Course_Students.query.filter_by(
                student_number=identifier
            ).first()

            if not course_student:
                user = User.query.filter_by(identifier=identifier).first()
                return Result.success(message="未找到该学生的课程信息",data={
                    'student_name': user.name,
                    'student_number': user.identifier,
                    'E-mail': user.email,
                    'user_id': user.id
                })
            return Result.success(course_student.to_dict())
        except Exception as e:
            return Result.internal_error(f'获取学生课程信息失败: {str(e)}')
    
    #获取课程id
    @staticmethod
    def get_course_by_identifier(identifier: str) -> Result:
        """根据用户identifier获取课程学生信息"""
        try:
            course_student = Course_Students.query.filter_by(
                student_number=identifier
            ).all()

            if not course_student:
                user = User.query.filter_by(identifier=identifier).first()
                return Result.success(message="未找到该学生的课程信息",data={
                    'student_name': user.name,
                    'student_number': user.identifier,
                    'E-mail': user.email,
                    'user_id': user.id
                })
            results = [cs.to_dict() for cs in course_student]
            print(results)
            return Result.success(results)
        except Exception as e:
            return Result.internal_error(f'获取学生课程信息失败: {str(e)}')
    
    #根据学生课程表的课程id获取对应课程信息
    @staticmethod
    def get_course_by_student(course_id: int) -> Result:
        try:
            course = Course.query.filter_by(id=course_id).first()
            if not course:
                return Result.not_found("课程不存在")
            course_data = course.to_dict()
            return Result.success(course_data)
            
        except Exception as e:
            return Result.internal_error(f'获取课程信息失败: {str(e)}')
       

    #获取所有作业列表
    @staticmethod
    def get_all_assignments() -> Result:
        try:
            assignments = Assignment.query.all()
            if not assignments:
                return Result.success('')

            assignments_data = [assignment.to_dict() for assignment in assignments]
            return Result.success(data=assignments_data)
        except Exception as e:
            return Result.internal_error(f'获取作业失败: {str(e)}')
        
    #获取课程id作业列表
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
        
    #根据作业id获取作业详情
    @staticmethod
    def get_assignment_by_id(assignment_id: int) -> Result:
        try:
            assignment = Assignment.query.filter_by(id=assignment_id).first()
            if not assignment:
                return Result.not_found("作业不存在")
            assignment_data = assignment.to_dict()
            return Result.success(assignment_data)
        except Exception as e:
            return Result.internal_error(f'获取作业详情失败: {str(e)}')
    
    #获取小测列表
    @staticmethod
    def get_quizzes_student(data) -> Result:
        try:
            from datetime import datetime

            now = datetime.now()
            course_id = data.get('course_id')
            student_number = data.get('student_number')

            # 更新已超时的小测
            Quiz.query.filter(
                Quiz.course_id == course_id,
                Quiz.status.in_(['not_started', 'published']),
                Quiz.end_time.isnot(None),
                Quiz.end_time <= now
            ).update(
                {'status': 'finished'},
            )

            # 查询课程的小测列表
            quizzes = Quiz.query.filter(
                Quiz.course_id == course_id,
                Quiz.status != 'draft'
            ).order_by(Quiz.create_time.desc()).all()

            if not quizzes:
                return Result.not_found("课程不存在或无可用小测")

            quiz_ids = [quiz.id for quiz in quizzes]

            # 批量查询学生已提交的小测ID列表
            submitted_quiz_ids = []
            if student_number:
                submitted_responses = QuizResponse.query.filter(
                    QuizResponse.student_number == student_number,
                    QuizResponse.quiz_id.in_(quiz_ids)
                ).with_entities(QuizResponse.quiz_id).all()
                submitted_quiz_ids = [resp.quiz_id for resp in submitted_responses]

            # 批量查询学生已批改的小测ID列表（新增部分）
            graded_quiz_ids = []
            if student_number:
                print(f"正在查询学生 {student_number} 的批改结果...")
                print(f"小测IDs列表: {quiz_ids}")
                graded_results = GradingResult.query.filter(
                    GradingResult.student_number == student_number,
                    GradingResult.quiz_id.in_(quiz_ids)
                ).with_entities(GradingResult.quiz_id).all()
                graded_quiz_ids = [result.quiz_id for result in graded_results]
                print(f"已批改的小测IDs: {graded_quiz_ids}")
            # 构建返回数据，添加提交状态和批改状态
            quizzes_data = []
            for quiz in quizzes:
                quiz_dict = quiz.to_dict()
                # 添加提交状态字段（动态计算）
                quiz_dict['is_submitted'] = quiz.id in submitted_quiz_ids
                # 添加批改状态字段（动态计算） - GradingResult表有记录就表示已批改
                quiz_dict['is_graded'] = quiz.id in graded_quiz_ids
                quizzes_data.append(quiz_dict)

            # 如果有更新操作，提交事务
            db.session.commit()

            print(f"查询到的小测数量: {len(quizzes)}")
            return Result.success(quizzes_data)

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'获取小测失败: {str(e)}')
    
    #提交小测  
    @staticmethod
    def submit_quiz(data: dict[str, Any]) -> Result:
        try:
            for answer in data:
                quiz_id = answer.get('quiz_id')
                question_id = answer.get('question_id')
                student_answer = answer.get('student_answer')
                student_number = answer.get('student_number')

                # 查是否已有记录
                existing = QuizResponse.query.filter_by(
                    quiz_id=quiz_id,
                    question_id=question_id,
                    student_number=student_number
                ).first()

                from datetime import datetime
                now = datetime.now()
                if existing:
                    existing.response = student_answer
                    existing.response_time = now
                else:
                    new_response = QuizResponse(
                        quiz_id=quiz_id,
                        question_id=question_id,
                        student_number=student_number,
                        response=student_answer,
                        response_time=now
                    )
                    db.session.add(new_response)

            db.session.commit()
            return Result.success(message="小测提交成功")

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'提交小测失败: {str(e)}')
    
    #获取习题列表
    @staticmethod
    def get_exercises_student(data) -> Result:
        try:
            course_id = data.get('course_id')
            student_number = data.get('student_number')

            # 查询课程的小测列表
            exercises = Exercise.query.filter(
                Exercise.course_id == course_id,
                Exercise.status != 'draft'
            ).order_by(Exercise.create_time.desc()).all()

            if not exercises:
                return Result.not_found("课程不存在或无可用小测")

            exercise_ids = [exercise.id for exercise in exercises]

            # 批量查询学生已提交的小测ID列表
            submitted_exercise_ids = []
            if student_number:
                submitted_responses = ExerciseResponse.query.filter(
                    ExerciseResponse.student_number == student_number,
                    ExerciseResponse.exercise_id.in_(exercise_ids)
                ).with_entities(ExerciseResponse.exercise_id).all()
                submitted_exercise_ids = [resp.exercise_id for resp in submitted_responses]

            # 批量查询学生已批改的小测ID列表
            # graded_quiz_ids = []
            # if student_number:
            #     print(f"正在查询学生 {student_number} 的批改结果...")
            #     print(f"小测IDs列表: {quiz_ids}")
            #     graded_results = GradingResult.query.filter(
            #         GradingResult.student_number == student_number,
            #         GradingResult.quiz_id.in_(quiz_ids)
            #     ).with_entities(GradingResult.quiz_id).all()
            #     graded_quiz_ids = [result.quiz_id for result in graded_results]
            #     print(f"已批改的小测IDs: {graded_quiz_ids}")
            # 构建返回数据，添加提交状态和批改状态
            exercises_data = []
            for exercise in exercises:
                exercise_dict = exercise.to_dict()
                # 添加提交状态字段（动态计算）
                exercise_dict['is_submitted'] = exercise.id in submitted_exercise_ids
                exercises_data.append(exercise_dict)

            # 如果有更新操作，提交事务
            db.session.commit()

            print(f"查询到的小测数量: {len(exercises)}")
            return Result.success(exercises_data)

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'获取小测失败: {str(e)}')
        
    #提交习题  
    @staticmethod
    def submit_exercise(data: dict[str, Any]) -> Result:
        try:
            exercise_responses = []
            questions_info = []  # 收集题目信息用于批改
            student_number = None

            # 先收集所有提交的数据
            for answer in data:
                exercise_id = answer.get('exercise_id')
                question_id = answer.get('question_id')
                student_answer = answer.get('student_answer')
                student_number = answer.get('student_number')

                # 收集题目信息（需要从数据库查询题目详情）
                question = ExerciseQuestion.query.get(question_id)
                if question:
                    questions_info.append({
                        'question_id': question_id,
                        'exercise_id': exercise_id,
                        'title': question.question_text[:100] if question.question_text else '',
                        'description': question.question_text,
                        'total_score': question.points,
                        'student_answer': student_answer,
                        'reference_answer': question.correct_answer
                    })

                # 查是否已有记录
                existing = ExerciseResponse.query.filter_by(
                    exercise_id=exercise_id,
                    question_id=question_id,
                    student_number=student_number
                ).first()

                from datetime import datetime
                now = datetime.now()
                if existing:
                    existing.response = student_answer
                    existing.response_time = now
                else:
                    new_response = ExerciseResponse(
                        exercise_id=exercise_id,
                        question_id=question_id,
                        student_number=student_number,
                        response=student_answer,
                        response_time=now
                    )
                    db.session.add(new_response)
                    exercise_responses.append(new_response)

            # 提交到数据库
            db.session.commit()

            # 自动批改逻辑
            if questions_info and student_number:
                try:
                    # 构建批改请求数据
                    grading_data = {
                        'assignments_list': questions_info
                    }

                    # 调用AI批改服务
                    from app.services.aiServices import AiServices
                    grading_result = AiServices.batch_score_assignments(grading_data)

                    if grading_result and grading_result.code == 200:
                        # 保存批改结果到GradingResult表
                        from app.models.gradingResults import GradingResult

                        # 构建question_id到题目信息的映射，便于查找title
                        question_info_dict = {str(q['question_id']): q for q in questions_info}

                        for result in grading_result.data.get('results', []):
                            question_id = str(result.get('question_id'))  # 转换为字符串确保匹配
                            question_info = question_info_dict.get(question_id, {})

                            existing_grading = GradingResult.query.filter_by(
                                exercise_id=result.get('exercise_id'),
                                question_id=result.get('question_id'),
                                student_number=student_number
                            ).first()

                            if existing_grading:
                                # 更新现有记录
                                existing_grading.title = question_info.get('title', '')
                                existing_grading.description = question_info.get('description', '')
                                existing_grading.student_answer = question_info.get('student_answer', '')
                                existing_grading.score = result.get('score')
                                existing_grading.total_score = result.get('total_score')
                                existing_grading.comment = result.get('comment')
                                existing_grading.reference_answer = result.get('reference_answer', '')
                                existing_grading.grading_time = datetime.now()
                            else:
                                # 创建新记录 - 确保包含所有必需的字段
                                new_grading = GradingResult(
                                    exercise_id=result.get('exercise_id'),
                                    question_id=result.get('question_id'),
                                    student_number=student_number,
                                    title=question_info.get('title', ''),  # 添加title字段
                                    description=question_info.get('description', ''),  # 添加description字段
                                    student_answer=question_info.get('student_answer', ''),  # 添加student_answer字段
                                    reference_answer=result.get('reference_answer', ''),
                                    total_score=result.get('total_score'),
                                    score=result.get('score'),
                                    comment=result.get('comment'),
                                    grading_time=datetime.now(),
                                    status='completed'  # 添加status字段
                                )
                                db.session.add(new_grading)

                        db.session.commit()
                        print("自动批改完成并保存到数据库")
                except Exception as e:
                    print(f"自动批改失败: {str(e)}")
            return Result.success(message="习题提交成功")

        except Exception as e:
            db.session.rollback()
            return Result.internal_error(f'提交习题失败: {str(e)}')
        
    
        
        
        
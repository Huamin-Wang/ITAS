from app import db
from app.models.user import User
from app.models.course import Course
from app.models.course_students import Course_Students
from app.models.assignment import Assignment
from app.models.Result import Result


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
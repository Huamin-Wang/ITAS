from app import db
from app.models.course import Course
from app.models.assignment import Assignment
from app.models.Result import Result


class StudentService:
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
from flask import Blueprint, request
from app.models.Result import Result
from app.services.courseStudentServices import CourseStudentService
bp = Blueprint('course_student', __name__)

#教师获取对应课程
@bp.route('/teacher_course', methods=['GET'])
def get_all_course_by_teacher_id():
    try:
        teacher_id = request.args.get('teacher_id', type=int)
        if teacher_id is None:
            return Result.bad_request("教师ID是必需的").to_json(), 400

        result = CourseStudentService.get_all_course_by_teacher_id(teacher_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取课程错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取课程时发生错误: {str(e)}').to_json(), 500

#创建课程
@bp.route('/create_course', methods=['POST'])
def create_course():
    try:
        data = request.form.to_dict()
        student_file = request.files.get('student_file')

        if not all(key in data for key in ['course_name', 'semester', 'course_code', 'teacher_id']):
            return Result.bad_request("缺少必要的字段").to_json(), 400

        result = CourseStudentService.create_course(data, student_file)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"创建课程错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'创建课程时发生错误: {str(e)}').to_json(), 500

#更新课程
@bp.route('/update_course', methods=['POST'])
def update_course():
    try:
        data = request.form.to_dict()
        student_file = request.files.get('student_file')

        if 'course_id' not in data:
            return Result.bad_request("课程ID是必需的").to_json(), 400

        result = CourseStudentService.update_course(data, student_file)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"更新课程错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'更新课程时发生错误: {str(e)}').to_json(), 500

#获取课程学生
@bp.route('/course_students', methods=['GET'])
def get_course_students():
    try:
        course_id = request.args.get('course_id', type=int)
        if course_id is None:
            return Result.bad_request("课程ID是必需的").to_json(), 400

        result = CourseStudentService.course_students(course_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取课程学生错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取课程学生时发生错误: {str(e)}').to_json(), 500

#获取随机选择学生
@bp.route('/random_select_list', methods=['GET'])
def get_random_select_list():
    try:
        course_id = request.args.get('course_id', type=int)
        if course_id is None:
            return Result.bad_request("课程ID是必需的").to_json(), 400

        result = CourseStudentService.random_select_list(course_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取随机选择学生错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取随机选择学生时发生错误: {str(e)}').to_json(), 500
    
#学生加分
@bp.route('/add_score', methods=['POST'])
def add_score():
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        list = data.get('list')
        if course_id is None or list is None:
            return Result.bad_request("缺少必要的字段").to_json(), 400
        result = CourseStudentService.add_score(list, course_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"学生加分错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'学生加分时发生错误: {str(e)}').to_json(), 500
    
# 获取课程学生排名
@bp.route('/ranking', methods=['GET'])
def ranking():
    try:
        course_id = request.args.get('course_id', type=int)
        if course_id is None:
            return Result.bad_request("课程ID是必需的").to_json(), 400

        result = CourseStudentService.ranking(course_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取课程学生排名错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取课程学生排名时发生错误: {str(e)}').to_json(), 500

# 发布作业
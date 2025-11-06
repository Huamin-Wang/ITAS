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

#课程id获取课程
@bp.route('/course_by_id', methods=['GET'])
def get_course_by_id():
    try:
        course_id = request.args.get('course_id', type=int)
        print(f"Received course_id: {course_id}")
        if course_id is None:
            return Result.bad_request("课程ID是必需的").to_json(), 400

        result = CourseStudentService.get_course_by_id(course_id)
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

#更新学生注册状态
@bp.route('/update_registration_status', methods=['GET'])
def update_registration_status():
    try:
        course_id = request.args.get('course_id', type=int)
        if course_id is None:
            return Result.bad_request("课程ID是必需的").to_json(), 400
        result = CourseStudentService.update_registration_status(course_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"更新学生注册状态错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'更新学生注册状态时发生错误: {str(e)}').to_json(), 500

#获取课程学生数
@bp.route('/course_student_count', methods=['GET'])
def get_course_student_count():
    try:
        course_id = request.args.get('course_id', type=int)
        if course_id is None:
            return Result.bad_request("课程ID是必需的").to_json(), 400

        result = CourseStudentService.get_course_student_count(course_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取课程学生数错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取课程学生数时发生错误: {str(e)}').to_json(), 500

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
    
#更新学生分数
@bp.route('/update_score', methods=['POST'])
def update_score():
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        list = data.get('list')
        if course_id is None or list is None:
            return Result.bad_request("缺少必要的字段").to_json(), 400
        result = CourseStudentService.update_score(list, course_id)
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

#获取作业列表
@bp.route('/get_assignments', methods=['GET'])
def get_assignments():
    try:
        course_id = request.args.get('course_id', type=int)
        if course_id is None:
            return Result.bad_request("课程ID是必需的").to_json(), 400

        result = CourseStudentService.get_assignments(course_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取作业列表错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取作业列表时发生错误: {str(e)}').to_json(), 500

#作业id获取作业
@bp.route('/get_assignment_by_id', methods=['GET'])
def get_assignment_by_id():
    try:
        assignment_id = request.args.get('assignment_id', type=int)
        print(f"Received course_id: {assignment_id}")
        if assignment_id is None:
            return Result.bad_request("作业ID是必需的").to_json(), 400

        result = CourseStudentService.get_assignment_by_id(assignment_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取作业错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取作业时发生错误: {str(e)}').to_json(), 500

# 发布作业
@bp.route('/assignments', methods=['POST'])
def assignments():
    try:
        data = request.form.to_dict()
        if not all(key in data for key in ['course_id', 'title', 'description', 'due_date','teacher_id']):
            return Result.bad_request("缺少必要的字段").to_json(), 400
        result = CourseStudentService.assignments(data)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"发布作业错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'发布作业时发生错误: {str(e)}').to_json(), 500
    
#编辑作业
@bp.route('/update_assignment', methods=['POST'])
def update_assignment():
    try:
        data = request.form.to_dict()
        if 'id' not in data or not any(key in data for key in ['title', 'description', 'due_date','tags']):
            return Result.bad_request("缺少必要的字段").to_json(), 400
        result = CourseStudentService.update_assignment(data)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"编辑作业错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'编辑作业时发生错误: {str(e)}').to_json(), 500
    
#新建小测
@bp.route('/create_quiz', methods=['POST'])
def create_quiz():
    try:
        data = request.get_json()
        if not all(key in data for key in ['teacher_id', 'title', 'course_id','create_time']):
            return Result.bad_request("缺少必要的字段").to_json(), 400
        result = CourseStudentService.create_quiz(data)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"新建小测错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'新建小测时发生错误: {str(e)}').to_json(), 500
    
#存储小测题目
@bp.route('/add_quiz_questions', methods=['POST'])
def add_quiz_questions():
    try:
        data = request.get_json()
        print(f"Received data for adding quiz questions: {data}")
        if 'quiz_id' not in data or 'questions' not in data:
            return Result.bad_request("缺少必要的字段").to_json(), 400
        quiz_id = data.get('quiz_id')
        questions = data.get('questions')
        result = CourseStudentService.add_quiz_questions(quiz_id, questions)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"存储小测题目错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'存储小测题目时发生错误: {str(e)}').to_json(), 500

#获取小测列表    
@bp.route('/get_quizzes', methods=['GET'])
def get_quizzes():
    try:
        course_id = request.args.get('course_id', type=int)
        if course_id is None:
            return Result.bad_request("课程ID是必需的").to_json(), 400

        result = CourseStudentService.get_quizzes(course_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取小测列表错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取小测列表时发生错误: {str(e)}').to_json(), 500
    
#获取小测详情
@bp.route('/get_quiz_questions', methods=['GET'])
def get_quiz_questions():
    try:
        quiz_id = request.args.get('quiz_id', type=int)
        if quiz_id is None:
            return Result.bad_request("小测ID是必需的").to_json(), 400

        result = CourseStudentService.get_quiz_questions(quiz_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取小测详情错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取小测详情时发生错误: {str(e)}').to_json(), 500
    
#编辑小测
@bp.route('/update_quiz', methods=['POST'])
def update_quiz():
    try:
        data = request.get_json()
        if 'id' not in data:
            return Result.bad_request("小测ID是必需的").to_json(), 400
        result = CourseStudentService.update_quiz(data)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"编辑小测错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'编辑小测时发生错误: {str(e)}').to_json(), 500
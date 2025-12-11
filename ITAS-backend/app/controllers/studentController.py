from flask import Blueprint, request, jsonify
from app import db
from app.models import Student
from app.services.studentServices import StudentService
from app.services.userServices import UserService
from app.models.Result import Result

bp = Blueprint('students', __name__)

@bp.route('/getStudents', methods=['GET'])
def get_all_students():
    """获取所有学生"""
    students = Student.query.all()
    return jsonify({
        'success': True,
        'count': len(students),
        'students': [student.to_dict() for student in students]
    })

@bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """获取单个学生"""
    student = Student.query.get(student_id)
    if student:
        return jsonify({
            'success': True,
            'student': student.to_dict()
        })
    return jsonify({
        'success': False,
        'message': '学生不存在'
    }), 404

@bp.route('/', methods=['POST'])
def create_student():
    """创建新学生"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({
            'success': False,
            'message': '姓名是必填字段'
        }), 400
    
    student = Student(
        name=data.get('name'),
        gender=data.get('gender'),
        birth_date=data.get('birth_date'),
        class_name=data.get('class_name'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address')
    )
    
    try:
        db.session.add(student)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '学生创建成功',
            'student': student.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'创建失败: {str(e)}'
        }), 500

@bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """更新学生信息"""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({
            'success': False,
            'message': '学生不存在'
        }), 404
    
    data = request.get_json()
    
    # 更新字段
    if 'name' in data:
        student.name = data['name']
    if 'gender' in data:
        student.gender = data['gender']
    if 'birth_date' in data:
        student.birth_date = data['birth_date']
    if 'class_name' in data:
        student.class_name = data['class_name']
    if 'phone' in data:
        student.phone = data['phone']
    if 'email' in data:
        student.email = data['email']
    if 'address' in data:
        student.address = data['address']
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '学生信息更新成功',
            'student': student.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500

@bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """删除学生"""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({
            'success': False,
            'message': '学生不存在'
        }), 404
    
    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '学生删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 500

# 学生中心获取用户信息
@bp.route('/me', methods=['GET'])
# @jwt_required()
def get_current_user():
    """获取当前用户信息"""
    try:
        # user_id = get_jwt_identity()
        user_id = request.args.get('user_id')
        user_data = UserService.get_user_by_id(user_id)

        if not user_data:
            return Result.not_found("用户不存在").to_json(), 404

        return Result.success(user_data).to_json(), 200

    except Exception as e:
        print(f"获取当前用户信息失败: {str(e)}")
        return Result.internal_error("服务器内部错误").to_json(), 500

# 学生中心--根据用户identifier获取课程学生信息
@bp.route('/course_student_info', methods=['GET'])
def get_course_student_info():
    """根据用户identifier获取课程学生信息"""
    try:
        identifier = request.args.get('identifier')
        user_id = request.args.get('user_id')
        if user_id and not identifier:
            user_data = StudentService.get_user_by_id(user_id)
            if not user_data:
                return Result.not_found("用户不存在").to_json(), 404
            identifier = user_data.get('identifier')
        if not identifier:
            return Result.bad_request("用户标识符不能为空").to_json(), 400
        
        result = StudentService.get_course_students_by_identifier(identifier)
        return result.to_json(), result.code
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取课程学生信息失败: {str(e)}'
        }), 500
    
@bp.route('/student_course_info', methods=['GET'])
def get_student_course_info():
    try:
        identifier = request.args.get('identifier')
        user_id = request.args.get('user_id')
        if user_id and not identifier:
            user_data = StudentService.get_user_by_id(user_id)
            if not user_data:
                return Result.not_found("用户不存在").to_json(), 404
            identifier = user_data.get('identifier')
        if not identifier:
            return Result.bad_request("用户标识符不能为空").to_json(), 400
        
        result = StudentService.get_course_by_identifier(identifier)
        return result.to_json(), result.code
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取课程学生信息失败: {str(e)}'
        }), 500

# # 学生中心获取课程列表
@bp.route('/getCourses', methods=['GET'])
def get_all_courses():
    
    courses = StudentService.get_all_courses() 
    courses_data = [course.to_dict() for course in courses]
    return jsonify({
        'success': True,
        'courses': courses_data
    })

# 学生中心--根据课程id获取课程信息
@bp.route('/get_student_course', methods=['GET'])
def get_student_course():
    try:
        course_id = request.args.get('course_id', type=int)
        if course_id is None:
            return Result.bad_request("课程ID是必需的").to_json(), 400

        result = StudentService.get_course_by_student(course_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取学生课程信息错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取学生课程信息时发生错误: {str(e)}').to_json(), 500


# 学生中心--根据课程id进入不同课程
@bp.route('/course_detail', methods=['GET'])
def get_course_detail():
    """获取特定课程的详情"""
    try:
        course_id = request.args.get('course_id',type=int)
        result = StudentService.get_course_detail(course_id)
        
        if course_id is None:
            return Result.bad_request("课程ID是必填字段").to_json(), 400
        return result.to_json(), result.code
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取课程详情失败: {str(e)}'
        }), 500


#学生中心 -- 获取所有作业列表
@bp.route('/get_all_assignments', methods=['GET'])
def get_all_assignments():
    try:
        result = StudentService.get_all_assignments()
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取所有作业列表错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取所有作业列表时发生错误: {str(e)}').to_json(), 500

# 学生中心 -- 根据课程id获取作业信息assignment
@bp.route('/get_assignments', methods=['GET'])
def get_assignments():
    try:
        course_id = request.args.get('course_id', type=int)
        if course_id is None:
            return Result.bad_request("课程ID是必需的").to_json(), 400

        result = StudentService.get_assignments(course_id)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取作业列表错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取作业列表时发生错误: {str(e)}').to_json(), 500


# 学生中心 -- 根据作业id获取作业详情
@bp.route('/assignment_detail', methods=['GET'])
def get_assignment_detail():
    """获取特定作业的详情"""
    try:
        assignment_id = request.args.get('assignment_id', type=int)
        if assignment_id is None:
            return Result.bad_request("作业ID是必填字段").to_json(), 400
        
        result = StudentService.get_assignment_by_id(assignment_id)
        return result.to_json(), result.code  # 直接返回服务层的结果
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取作业详情失败: {str(e)}'
        }), 500

# 学生中心 -- 获取小测列表
@bp.route('/get_quizzes_student', methods=['POST'])
def get_quizzes():
    try:
        data = request.get_json()
        if not all(key in data for key in ['student_id', 'course_id']):
            return Result.bad_request("缺少必要的字段").to_json(), 400

        result = StudentService.get_quizzes_student(data)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"获取小测列表错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取小测列表时发生错误: {str(e)}').to_json(), 500
    
# 学生端 -- 提交小测
@bp.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    try:
        data = request.get_json()
        result = StudentService.submit_quiz(data)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"提交小测错误详情: {traceback.format_exc()}")
        return
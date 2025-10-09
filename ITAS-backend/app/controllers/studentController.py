from flask import Blueprint, request, jsonify
from app import db
from app.models import Student

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
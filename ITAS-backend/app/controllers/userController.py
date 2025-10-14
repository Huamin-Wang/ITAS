from flask import Blueprint, request
from app.models.Result import Result
from app.services.userServices import UserService
bp = Blueprint('user', __name__)

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return Result.bad_request("请求数据不能为空").to_json(), 400
        result = UserService.register(data)
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"注册错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'注册过程中发生错误: {str(e)}').to_json(), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        print("注册请求数据:", request.get_json())
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        if not data:
            return Result.bad_request("请求数据不能为空").to_json(), 400
        result = UserService.login(data)
        return result.to_json(), result.code
        
    except Exception as e:
        import traceback
        print(f"登录错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'登录过程中发生错误: {str(e)}').to_json(), 500
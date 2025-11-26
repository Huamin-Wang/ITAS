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
        return result
    except Exception as e:
        import traceback
        print(f"注册错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'注册过程中发生错误: {str(e)}').to_json(), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        if not data:
            return Result.bad_request("请求数据不能为空").to_json(), 400
        result = UserService.login(data)
        return result
        
    except Exception as e:
        import traceback
        print(f"登录错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'登录过程中发生错误: {str(e)}').to_json(), 500
    
@bp.route('/logout', methods=['POST'])
def logout():
    try:
        UserService.logout()
        return Result.success(message='登出成功').to_json(), 200
    except Exception as e:
        import traceback
        print(f"登出错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'登出过程中发生错误: {str(e)}').to_json(), 500
    
@bp.route('/getOpenId', methods=['POST'])
def get_openid():
    """获取微信openid接口"""
    try:
        data = request.get_json()
        if not data:
            return Result.bad_request("请求数据不能为空").to_json(), 400
        
        result = UserService.get_openid_unlocked(data)
        return result
        
    except Exception as e:
        import traceback
        print(f"获取openid错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'获取openid过程中发生错误: {str(e)}').to_json(), 500

@bp.route('/minilogin', methods=['POST'])
def mini_login():
    """微信小程序登录绑定接口"""
    try:
        data = request.get_json()
        if not data:
            return Result.bad_request("请求数据不能为空").to_json(), 400
        
        result = UserService.minilogin(data)
        return result
        
    except Exception as e:
        import traceback
        print(f"微信登录错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'微信登录过程中发生错误: {str(e)}').to_json(), 500

@bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    心跳检测接口 - 只负责路由和返回
    """
    try:
        result = UserService.heartbeat()
        return result
    except Exception as e:
        import traceback
        print(f"心跳控制器错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'心跳接口错误: {str(e)}').to_json(), 500
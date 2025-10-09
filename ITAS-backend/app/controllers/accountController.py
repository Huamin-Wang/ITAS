from flask import Blueprint, request, session
from app.services.accountServices import AccountService
from app.models.Result import Result

bp = Blueprint('account', __name__)

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return Result.bad_request("请输入用户名和密码").to_json(), 400
        
        username = data.get('username').strip()
        password = data.get('password')
        
        if not username or not password:
            return Result.bad_request("用户名和密码不能为空").to_json(), 400
        
        result = AccountService.verify_login(username, password)
        
        # 如果登录成功，设置session 并生成JWT Token
        if result.code == Result.SUCCESS:
            session['user_id'] = result.data.get('user_id')
            session['username'] = username
            
            #生成JWT Token
            user_id = result.data.get('user_id')
            additional_claims = {
                'username': username,
                'account_category': result.data.get('account_category', 'user')
            }
            
            from app.utils.jwt import JWTUtils
            access_token = JWTUtils.create_access_token(
                identity=user_id, 
                additional_claims=additional_claims
            )
            
            # 在返回数据中添加token
            result.data['access_token'] = access_token
        
        return result.to_json(), result.code
    except Exception as e:
        import traceback
        print(f"登录错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'登录过程中发生错误: {str(e)}').to_json(), 500
    

@bp.route('/register', methods=['POST'])
def register():
    try:
        # 获取请求数据
        data = request.get_json()
        # 验证必要字段
        if not data or 'username' not in data or 'password' not in data or 'account_category' not in data:
            return Result.bad_request("请输入用户名、密码和账户分类").to_json(), 400
        username = data.get('username').strip()
        password = data.get('password')
        account_category = data.get('account_category').strip()
        # 基本验证
        if not username or not password or not account_category:
            return Result.bad_request("用户名、密码和账户分类不能为空").to_json(), 400
        # 调用服务层创建账户
        result = AccountService.create_account(username, password, account_category)
        # 直接返回服务层的结果
        return result.to_json(), result.code
    except Exception as e:
        # 处理意外错误
        import traceback
        print(f"注册错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'注册过程中发生错误: {str(e)}').to_json(), 500
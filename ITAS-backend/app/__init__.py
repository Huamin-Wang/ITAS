from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # 导入CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from .interceptors.jwtInterceptor import AuthInterceptor
db = SQLAlchemy()

# 在 __init__.py 中修改 CORS 配置
def create_app(config_name='default'):
    app = Flask(__name__)

    # 配置
    from .config import config
    app.config.from_object(config[config_name])
    # 初始化JWT扩展
    jwt = JWTManager(app)
    # 配置令牌吊销检查
    jwt.token_in_blocklist_loader(AuthInterceptor.is_token_revoked)
    # 初始化扩展
    db.init_app(app)

    # 更全面的 CORS 配置
    CORS(app, 
         origins=["http://localhost:5173", "http://127.0.0.1:5173"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
         expose_headers=["Content-Range", "X-Content-Range"],
         supports_credentials=True,
         max_age=3600)
    # 全局请求拦截器
    @app.before_request
    def global_auth_interceptor():
        # 定义不需要token的白名单路由
        excluded_paths = [
            '/login',      # 登录
            '/register',   # 注册
            '/',                       # 根路径
            '/favicon.ico'            # 网站图标
        ]
        
        # 检查当前请求路径是否在白名单中
        if request.path in excluded_paths:
            return None
        
        # 检查请求方法为OPTIONS的预检请求（CORS）
        if request.method == 'OPTIONS':
            return None  
        
        # 对其他所有请求进行token验证
        try:
            verify_jwt_in_request()
            
            # 检查令牌是否在黑名单中
            jwt_data = get_jwt()
            jti = jwt_data["jti"]
            if jti in AuthInterceptor.token_blacklist:
                return jsonify({'error': '令牌已失效'}), 401
                
        except Exception as e:
            # Token验证失败，返回401错误
            return jsonify({
                'error': '访问被拒绝', 
                'message': '请先登录',
                'details': str(e)
            }), 401
        
        # Token验证通过，继续处理请求
        return None
    # 注册蓝图
    from app.controllers.studentController import bp as students_bp
    from app.controllers.accountController import bp as account_bp
    app.register_blueprint(account_bp)
    app.register_blueprint(students_bp)

    return app
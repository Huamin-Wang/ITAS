from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # 导入CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from .interceptors.jwtInterceptor import AuthInterceptor

# 给 db 添加类型注解，方便静态分析器（如 Pylance）识别 db.Column 等属性
db: SQLAlchemy = SQLAlchemy()

# 在 __init__.py 中修改 CORS 配置
def create_app(config_name='default'):
    app = Flask(__name__)

    # 配置
    from .config import config
    app.config.from_object(config[config_name])
    # 确保 instance 目录存在，避免 sqlite 无法打开文件
    try:
        import os
        instance_dir = app.config.get('SQLALCHEMY_DATABASE_URI')
        # 如果使用相对 sqlite 路径，Flask 的 instance_path 可用于存放数据库文件
        # 但我们先确保 app.instance_path 存在
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception:
        # 忽略创建 instance 目录时的异常，但保留运行时日志
        pass
    # 初始化JWT扩展
    jwt = JWTManager(app)
    # 配置令牌吊销检查
    jwt.token_in_blocklist_loader(AuthInterceptor.is_token_revoked)
    # 初始化扩展
    db.init_app(app)

    # 更全面的 CORS 配置
    CORS(app, 
         origins="*",
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
         expose_headers=["Content-Range", "X-Content-Range"],
         supports_credentials=False, #调试阶段关闭，允许全部跨域请求
         max_age=3600)
    
    # 初始化聊天服务
    from .services.sparkClientServices import SparkClient
    from .services.chatServices import ChatService
    
    # 创建 SparkClient 实例
    spark_client = SparkClient(
        app_id=app.config['SPARK_APP_ID'],
        api_key=app.config['SPARK_API_KEY'],
        api_secret=app.config['SPARK_API_SECRET'],
        spark_url=app.config['SPARK_URL'],
        domain=app.config['SPARK_DOMAIN']
    )
    
    # 创建 ChatService 实例
    chat_service = ChatService(spark_client)
    
    # 将聊天服务存储在 app 上下文中
    app.chat_service = chat_service
    
    # 全局请求拦截器
    @app.before_request
    def global_auth_interceptor():
        # 定义不需要token的白名单路由
        excluded_paths = [
            '/login',      # 登录
            '/register',   # 注册
            '/logout',      # 登出
            '/',                       # 根路径
            '/favicon.ico',            # 网站图标
            '/update_assignment',
            # 聊天相关路由 - 添加到白名单
            '/chat_handle',
            '/chat/stats',
            '/chat/history',
            '/chat/history/clear',
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
    from app.controllers.userController import bp as user_bp
    from app.controllers.courseStudentController import bp as course_student_bp
    # 注册聊天控制器蓝图
    from app.controllers.chatController import bp as chat_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(course_student_bp)
    app.register_blueprint(chat_bp)
    
    return app
import os
from datetime import timedelta
environment = os.getenv('FLASK_ENV', 'development')
if "production" in environment:
    environment = 'production'
# 获取当前文件（config.py）的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取app文件夹的绝对路径
app_dir = os.path.dirname(current_file_path)
# 获取项目根目录的绝对路径（app文件夹的父目录）
base_dir = os.path.dirname(app_dir)

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    # Token配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)  # 改为半小时过期
    # Cookie配置
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_NAME = 'access_token'
    JWT_COOKIE_CSRF_PROTECT = False  # 开发环境关闭CSRF保护，生产环境建议开启
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SECURE = True  # 开发环境为False，生产环境应为True
    JWT_COOKIE_SAMESITE = 'None' # 开发环境使用，生产环境使用lax
    JWT_COOKIE_DOMAIN = None  # 设为None，让浏览器自动处理
    # 数据库配置
    if environment == 'development':
        # 数据库文件放在项目根目录下的instance文件夹中
        db_path = os.path.join(base_dir, 'instance', 'test1.db')
    else:
        db_path = os.path.join(base_dir, 'instance','prod.db')
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # -----微信小程序的appid和secret---------
    APP_ID = 'wx3dd32842e9e24690'
    APP_SECRET = '09732f45784f51d2b9e5bad0902ec17a'
    
    # -----讯飞星火配置---------
    SPARK_APP_ID = '39554b86'
    SPARK_API_SECRET = 'NzIwZGRkZGIxN2Y3ZDU3MzgwZjY3ZGM5'
    SPARK_API_KEY = 'ce8eb8ca38ffa7a3fde99f78d57980c4'
    SPARK_DOMAIN = '4.0Ultra'
    SPARK_URL = 'wss://spark-api.xf-yun.com/v4.0/chat'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    JWT_COOKIE_SECURE = True  # 生产环境启用Secure

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
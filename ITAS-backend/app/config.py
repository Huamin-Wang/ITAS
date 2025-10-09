import os
from datetime import timedelta
environment = os.getenv('FLASK_ENV', 'development')
if "production" in environment:
    environment = 'production'
class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    # Token配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)  # 1天过期
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/test1.db' if environment == 'development' else 'sqlite:///prod.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # -----微信小程序的appid和secret---------
    APP_ID = 'wx3dd32842e9e24690'
    APP_SECRET = '09732f45784f51d2b9e5bad0902ec17a'
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
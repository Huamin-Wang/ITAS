from flask_jwt_extended import (
    create_access_token, get_jwt_identity, 
    get_jwt, decode_token
)
from datetime import timedelta

class JWTUtils:
    @staticmethod
    def create_access_token(identity, additional_claims=None):
        """创建访问令牌"""
        return create_access_token(
            identity=identity,
            additional_claims=additional_claims
        )
    
    @staticmethod
    def get_current_user():
        """获取当前用户"""
        return get_jwt_identity()
    
    @staticmethod
    def get_jwt_claims():
        """获取JWT声明"""
        return get_jwt()
    
    @staticmethod
    def get_jwt_identity():
        """获取JWT身份"""
        return get_jwt_identity()
    
    @staticmethod
    def decode_token(token):
        """解码令牌"""
        return decode_token(token)
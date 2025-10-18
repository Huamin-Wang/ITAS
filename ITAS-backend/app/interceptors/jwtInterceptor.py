from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps


class AuthInterceptor:
    token_blacklist = set()


    @staticmethod
    def token_required(f):
        """JWT令牌验证拦截器"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 验证JWT令牌
                verify_jwt_in_request()
                jwt_data = get_jwt()
                jti = jwt_data["jti"]
                
                # 检查令牌是否在黑名单中
                if jti in AuthInterceptor.token_blacklist:
                    return jsonify({'error': '令牌已失效'}), 401
                    
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': '令牌验证失败', 'details': str(e)}), 401
        return decorated_function
    
    @staticmethod
    def revoke_token(jti):
        """撤销令牌（加入黑名单）"""
        AuthInterceptor.token_blacklist.add(jti)
    
    @staticmethod
    def is_token_revoked(jwt_header, jwt_payload):
        """检查令牌是否被撤销"""
        jti = jwt_payload["jti"]
        return jti in AuthInterceptor.token_blacklist
    
    @staticmethod
    def get_token_from_header():
        """从请求头获取令牌"""
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None
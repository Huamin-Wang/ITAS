from typing import Any, Optional, Dict
from flask import jsonify

class Result:
    """统一响应结果类"""
    
    # 常用状态码
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    
    def __init__(self, code: int = SUCCESS, data: Any = None, message: str = "操作成功"):
        self.code = code
        self.data = data
        self.message = message
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "code": self.code,
            "data": self.data,
            "message": self.message
        }
    
    def to_json(self):
        """转换为JSON响应"""
        return jsonify(self.to_dict())
    
    @classmethod
    def success(cls, data: Any = None, message: str = "操作成功"):
        """成功响应"""
        return cls(cls.SUCCESS, data, message)
    
    @classmethod
    def created(cls, data: Any = None, message: str = "创建成功"):
        """创建成功响应"""
        return cls(cls.CREATED, data, message)
    
    @classmethod
    def error(cls, message: str = "操作失败", code: int = BAD_REQUEST):
        """错误响应"""
        return cls(code, None, message)
    
    @classmethod
    def bad_request(cls, message: str = "请求参数错误"):
        """请求参数错误"""
        return cls(cls.BAD_REQUEST, None, message)
    
    @classmethod
    def unauthorized(cls, message: str = "未授权访问"):
        """未授权"""
        return cls(cls.UNAUTHORIZED, None, message)
    
    @classmethod
    def forbidden(cls, message: str = "禁止访问"):
        """禁止访问"""
        return cls(cls.FORBIDDEN, None, message)
    
    @classmethod
    def not_found(cls, message: str = "资源不存在"):
        """资源不存在"""
        return cls(cls.NOT_FOUND, None, message)
    
    @classmethod
    def internal_error(cls, message: str = "服务器内部错误"):
        """服务器错误"""
        return cls(cls.INTERNAL_SERVER_ERROR, None, message)
    
    def __repr__(self):
        return f"Result(code={self.code}, message='{self.message}', data={self.data})"
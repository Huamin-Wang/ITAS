from typing import Dict, Any
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models.user import User
from app.models.Result import Result
from app.utils.jwt import JWTUtils
from app.interceptors.jwtInterceptor import AuthInterceptor
from flask_jwt_extended import decode_token

class UserService:

    @staticmethod
    def set_password(password: str) -> str:
        """生成密码哈希"""
        return generate_password_hash(password)

    @staticmethod
    def check_password(password_hash: str, password: str) -> bool:
        """验证密码是否匹配哈希"""
        return check_password_hash(password_hash, password)

    @staticmethod
    def login(data: Dict[str, Any]) -> Result:
        """用户登录方法"""
        try:
            identifier = data.get('identifier') or data.get('xuehao')
            password = data.get('password')
            
            # 基本校验
            if not identifier:
                return Result.bad_request('请输入学号/标识符')
            if not password:
                return Result.bad_request('请输入密码')
            
            # 统一处理标识符格式（转大写，去空格）
            identifier = identifier.upper().replace(' ', '')
            
            # 查找用户（支持学号/邮箱登录）
            user = User.query.filter(
                (User.identifier == identifier) | (User.email == identifier)
            ).first()
            
            if not user:
                print(f"用户不存在: {identifier}")
                return Result.unauthorized('用户不存在或密码错误')
            
            # 验证密码
            if not UserService.check_password(user.password, password):
                print(f"密码错误: {identifier}")
                return Result.unauthorized('用户不存在或密码错误')
            
            # 生成 JWT token
            additional_claims = {
                'username': user.name,
                'account_category': user.role or 'user',
                'identifier': user.identifier
            }
            access_token = JWTUtils.create_access_token(
                identity=user.id, 
                additional_claims=additional_claims
            )
            
            # 返回登录成功数据
            login_data = {
                'user_id': user.id,
                'name': user.name,
                'identifier': user.identifier,
                'role': user.role,
                'email': user.email,
                'access_token': access_token,
                'login_status': 'success'
            }
            
            print(f'{user.name}登录成功！')
            return Result.success(login_data, '登录成功')
            
        except Exception as e:
            print(f"登录过程中发生错误: {str(e)}")
            return Result.internal_error(f'登录时发生错误: {str(e)}')

    @staticmethod
    def register(data: Dict[str, Any]) -> Result:
        try:
            print(f"注册数据: {data}")
            identifier = data.get('identifier')
            if identifier:
                identifier = identifier.upper().replace(' ', '')

            role = data.get('role')
            name = (data.get('name') or '').replace(' ', '')
            # gender = data.get('gender')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password') or data.get('confirmPassword')

            # 基本校验
            missing = []
            if not identifier:
                missing.append('identifier')
            if not email:
                missing.append('email')
            if not password:
                missing.append('password')
            if not confirm_password:
                missing.append('confirm_password')
            if missing:
                return Result.bad_request(f'Missing fields: {", ".join(missing)}')

            if password != confirm_password:
                return Result.bad_request('密码不一致！')

            # 唯一性检查
            if User.query.filter_by(email=email).first():
                print(User.query.filter_by(email=email).first())
                return Result.bad_request('邮箱已存在！')
            if User.query.filter_by(identifier=identifier).first():
                return Result.bad_request('学号已存在！')

            password_hash = UserService.set_password(password)
            user = User(identifier=identifier, role=role, name=name, email=email,
                        password=password_hash)
            db.session.add(user)
            db.session.commit()

            # 创建 JWT token，返回受限用户信息和 token（不包含敏感字段）
            additional_claims = {
                'username': user.name,
                'account_category': user.role or 'user'
            }
            access_token = JWTUtils.create_access_token(identity=user.id, additional_claims=additional_claims)

            data = {
                'user_id': user.id,
                'name': user.name,
                'access_token': access_token,
                'registration_status': 'complete'
            }

            return Result.created(data, '注册成功')

        except Exception as e:
            try:
                db.session.rollback()
            except Exception:
                pass
            return Result.internal_error(f'注册时发生错误: {str(e)}')
    @staticmethod
    def logout():
        """用户登出方法"""
        try:
            # 获取当前请求的令牌
            token = AuthInterceptor.get_token_from_header()
            if not token:
                return jsonify({'error': '未找到令牌'}), 400
            
            # 解码令牌获取jti
            decoded_token = decode_token(token)
            jti = decoded_token['jti']
            
            # 将令牌加入黑名单
            AuthInterceptor.revoke_token(jti)
            
            return jsonify({'message': '登出成功'}), 200
            
        except Exception as e:
            return jsonify({'error': '登出失败', 'details': str(e)}), 500
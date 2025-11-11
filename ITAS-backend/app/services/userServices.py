from typing import Dict, Any
from flask import jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import decode_token, set_access_cookies, unset_jwt_cookies, get_jwt_identity, create_access_token, get_jwt
from datetime import timedelta

from app import db
from app.models.user import User
from app.models.Result import Result
from app.utils.jwt import JWTUtils
from app.interceptors.jwtInterceptor import AuthInterceptor
from app.config import Config
import requests

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
            
            # 返回登录成功数据（不再返回token到响应体）
            login_data = {
                'user_id': user.id,
                'name': user.name,
                'identifier': user.identifier,
                'role': user.role,
                'email': user.email,
                'login_status': 'success'
            }
            
            print(f'{user.name}登录成功！')
            
            # 创建响应并设置HttpOnly Cookie
            result = Result.success(login_data, '登录成功')
            response = make_response(result.to_dict())
            set_access_cookies(response, access_token)
            return response
            
        except Exception as e:
            print(f"登录过程中发生错误: {str(e)}")
            return Result.internal_error(f'登录时发生错误: {str(e)}')

    # 根据ID获取用户信息 ,用于学生中心获取用户信息 ---慎独、
    @staticmethod
    def get_user_by_id(user_id: int):
        """根据 ID 获取用户信息(用于 /me)"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None

            return {
                'user_id': user.id,
                'name': user.name,
                'identifier': user.identifier,
                'role': user.role,
                'email': user.email
            }
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None

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

            # 创建 JWT token
            additional_claims = {
                'username': user.name,
                'account_category': user.role or 'user'
            }
            access_token = JWTUtils.create_access_token(identity=user.id, additional_claims=additional_claims)

            data = {
                'user_id': user.id,
                'name': user.name,
                'registration_status': 'complete'
            }

            # 创建响应并设置HttpOnly Cookie
            result = Result.created(data, '注册成功')
            response = make_response(result.to_dict())
            set_access_cookies(response, access_token)
            return response

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
            # 从Cookie获取令牌
            from app.interceptors.jwtInterceptor import AuthInterceptor
            token = AuthInterceptor.get_token_from_cookie()
            
            if not token:
                error_result = Result.bad_request('未找到令牌')
                response = make_response(error_result.to_json(), error_result.code)
                response.headers['Content-Type'] = 'application/json'
                return response
            
            # 解码令牌获取jti
            decoded_token = decode_token(token)
            jti = decoded_token['jti']
            
            # 将令牌加入黑名单
            AuthInterceptor.revoke_token(jti)
            
            # 创建响应并清除Cookie
            success_result = Result.success({'message': '登出成功'}, '登出成功')
            response = make_response(success_result.to_json(), success_result.code)
            response.headers['Content-Type'] = 'application/json'
            unset_jwt_cookies(response)
            return response
            
        except Exception as e:
            error_result = Result.internal_error(f'登出失败: {str(e)}')
            response = make_response(error_result.to_json(), error_result.code)
            response.headers['Content-Type'] = 'application/json'
            return response
    
    @staticmethod
    def heartbeat():
        """
        心跳检测服务 - 更新用户token
        """
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            if not current_user_id:
                return Result.unauthorized('用户身份验证失败')
            
            # 获取当前用户信息
            user = User.query.get(current_user_id)
            if not user:
                return Result.not_found('用户不存在')
            
            # 获取当前token的jti（用于后续加入黑名单）
            current_jwt = get_jwt()
            current_jti = current_jwt['jti']
            
            # 创建新的access token（半小时有效期）
            additional_claims = {
                'username': user.name,
                'account_category': user.role or 'user',
                'identifier': user.identifier
            }
            new_token = create_access_token(
                identity=user.id,
                additional_claims=additional_claims,
            )
            
            # 构建响应数据
            heartbeat_data = {
                'success': True,
                'message': '心跳正常，token已更新',
                'userInfo': {
                    'userId': user.id,
                    'name': user.name,
                    'identifier': user.identifier,
                    'role': user.role,
                    'email': user.email
                },
            }
            
            # 创建响应并设置新的token到HttpOnly Cookie
            result = Result.success(heartbeat_data, '心跳正常')
            response = make_response(result.to_dict())
            set_access_cookies(response, new_token)
            
            #将旧token加入黑名单（增强安全性）
            AuthInterceptor.revoke_token(current_jti)
            
            return response
            
        except Exception as e:
            print(f"心跳服务错误: {str(e)}")
            import traceback
            print(f"心跳错误详情: {traceback.format_exc()}")
            return Result.internal_error(f'心跳过程中发生错误: {str(e)}')
    
    #获取openid(一键登录)
    @staticmethod
    def get_openid_unlocked(data):
        print("登录小程序")
        code = data.get('code')
        # userInfo = data.get('userInfo')
        print(f"code:{code}")
        # print(f"userInfo:{userInfo}")
        if not code:
            return jsonify({'success': False, 'message': '缺少 code'})
        # 向微信服务器请求 openid
        wx_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={Config.APP_ID}&secret={Config.APP_SECRET}&js_code={code}&grant_type=authorization_code"
        response = requests.get(wx_url).json()
        openid = response['openid']
        print(f"openid:{openid}")
        # 如果成功获取 openid，则根据openid返回用户信息
        user = User.query.filter_by(openid=response['openid']).first()
        if user:
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
            
            user_data = {
                'user_id': user.id,
                'name': user.name,
                'role': user.role,
                "identifier": user.identifier,
                "openid": openid,
                "email": user.email,
                "gender": user.gender,
                "login_status": "success"
            }
            print(f"用户 {user.name} 通过openid登录成功")
            
            # 创建响应并设置HttpOnly Cookie
            result = Result.success(user_data, '登录成功')
            response = make_response(result.to_dict())
            set_access_cookies(response, access_token)
            return response
        else:
            #   返回信息提示注册登录
            return jsonify(
                {'success': True, 'user_id': -1, 'user_name': "未登录过小程序,退出重新登录", 'user_role': "游客",
                 "openid": openid})
        
    #微信登录绑定
    @staticmethod
    def minilogin(data) -> Result:
        """微信小程序登录绑定"""
        try:
            print("验证小程序登录")
            openid = data.get('openid')
            ident = data.get('identifier')  # 学号
            password = data.get('password')
            
            if not all([openid, ident, password]):
                return Result.bad_request('缺少必要参数')
            
            ident = ident.upper().replace(' ', '')
            print(f"openid:{openid}")
            print(f"ident:{ident}")
            
            # 从数据库中查找用户，与用户输入的密码进行比对
            user = User.query.filter_by(identifier=ident).first()
            if not user:
                return Result.unauthorized('用户不存在')
            
            # 验证密码
            if not UserService.check_password(user.password, password):
                print(f"密码错误: {ident}")
                return Result.unauthorized('密码错误')
            
            # 更新用户的openid
            user.openid = openid
            db.session.commit()
            print(f"用户 {user.name} 绑定openid成功！")
            
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
            
            # 返回登录成功数据（不再返回token到响应体）
            login_data = {
                'user_id': user.id,
                'name': user.name,
                'identifier': user.identifier,
                'role': user.role,
                'email': user.email,
                'login_status': 'success',
                "openid": openid,
                # "gender": user.gender
            }
            
            print(f'{user.name}登录成功！')
            
            # 创建响应并设置HttpOnly Cookie
            result = Result.success(login_data, '登录成功')
            response = make_response(result.to_dict())
            set_access_cookies(response, access_token)
            return response
            
        except Exception as e:
            try:
                db.session.rollback()
            except Exception:
                pass
            print(f"微信登录过程中发生错误: {str(e)}")
            return Result.internal_error(f'登录失败: {str(e)}')
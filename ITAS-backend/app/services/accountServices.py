from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.Account import Account 
from app.models.Result import Result   

class AccountService:
    @staticmethod
    def set_password(password):
        """生成密码哈希"""
        return generate_password_hash(password)
    
    @staticmethod
    def check_password(password_hash, password):
        """验证密码"""
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def create_account(username, password, account_category):
        """创建新账户"""
        print(f"开始创建账户: username={username}, account_category={account_category}")
        
        # 检查用户名是否已存在
        existing_account = Account.query.filter_by(username=username).first()
        if existing_account:
            return Result.error("用户名已存在")
        
        # 验证账户分类
        if account_category not in ['学生', '教师']:
            return Result.error("账户分类必须是'学生'或'教师'")
        
        
        try:
            # 创建账户
            password_hash = AccountService.set_password(password)
            account = Account(
                username=username,
                password_hash=password_hash,
                account_category=account_category
            )
            
            print(f"账户对象创建成功: ID={account.id}")
            
            # 保存到数据库
            db.session.add(account)
            db.session.commit()
            account_data = account.to_dict()
            return Result.success(account_data, "账户创建成功")
            
        except Exception as e:
            db.session.rollback()
            return Result.error(f"创建账户时发生错误: {str(e)}")
    
    @staticmethod
    def verify_login(username, password):
        """验证用户登录"""
        try:
            # 查询用户
            account = Account.query.filter_by(username=username).first()
            print(f"查询结果: {account}")
            
            if not account:
                return Result.error("用户名或密码错误", Result.UNAUTHORIZED)
            # 验证密码
            is_password_correct = AccountService.check_password(account.password_hash, password)
            
            if is_password_correct:
                user_data = account.to_dict()
                return Result.success(user_data, "登录成功")
            else:
                return Result.error("用户名或密码错误", Result.UNAUTHORIZED)
        except Exception as e:
            return Result.error(f"登录验证时发生错误: {str(e)}")
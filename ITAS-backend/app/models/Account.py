from app import db

class Account(db.Model):  # 修改类名为 Account 以匹配代码中的使用
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    account_category = db.Column(db.String(10), nullable=False)
    
    def to_dict(self):
        """将模型转换为字典"""
        return {
            'user_id': self.id,
            'username': self.username,
            'account_category': self.account_category
        }
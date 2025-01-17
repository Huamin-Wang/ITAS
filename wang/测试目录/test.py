from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# 声明基类
Base = declarative_base()

# 用户表
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    orders = relationship("Order", back_populates="user")  # 定义关系

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"

# 订单表
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # 外键，指向users表的id
    user = relationship("User", back_populates="orders")  # 定义反向关系

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id})>"

# 创建数据库引擎（SQLite内存数据库）
engine = create_engine('sqlite:///:memory:')

# 创建表
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 测试用例
def test_back_populates():
    # 添加用户和订单
    user1 = User(name="Alice")
    order1 = Order(user=user1)  # 订单属于用户
    order2 = Order(user=user1)  # 订单属于用户

    session.add_all([user1, order1, order2])
    session.commit()

    # 通过用户查看其所有订单
    user = session.query(User).filter_by(name="Alice").first()
    print(f"User: {user.name}")
    for order in user.orders:
        print(f"  Order ID: {order.id}")

    # 通过订单查看其所属用户
    order = session.query(Order).first()
    print(f"Order ID: {order.id}, User: {order.user.name}")

# 运行测试
if __name__ == "__main__":
    test_back_populates()
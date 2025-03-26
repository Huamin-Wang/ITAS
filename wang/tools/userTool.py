from wang.models import User


def delete_user(user_id, db):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        print(f"User {user.name} ({user.identifier}) deleted successfully.")
        return True
    else:
        print("User not found.")
        return False
# 根据identifier删除用户
def delete_user_by_identifier(identifier, db):
    user = User.query.filter_by(identifier=identifier).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        print(f"User {user.name} ({user.identifier}) deleted successfully.")
        return True
    else:
        print("User not found.")
        return False
def clearOpenid(id, db):
    user = User.query.filter_by(id=id).first()
    if user:
        user.openid = None
        db.session.commit()
        print(f"User {user.name} ({user.identifier})'s openid cleared.")
        return True
    else:
        print("User not found.")
        return False
# 更新用户信息
def update_user(user_id, name, identifier,email,gender,password, role,db):
    user = User.query.get(user_id)
    if user:
        user.username = name
        user.identifier = identifier
        user.email = email
        user.gender=gender
        user.password = password
        user.role = role
        db.session.commit()
        print(f"User {user.name} ({user.identifier}) updated successfully.")
        return True
    else:
        print("User not found.")
        return False



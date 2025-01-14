from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from wang.models import init_db
from wang.models.user import User
import xie.chat as c



def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example1.db'  # 配置数据库
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # 配置密钥
    # 初始化数据库
    db = init_db(app)

    @app.errorhandler(404)
    def page_not_found(e):
        print("404")
        return render_template('wang/404.html'), 404
    # ！！！！！！！！大家注意：这个页面只允许处理route的请求，其他无关代码请放到自己文件夹（包）进行调用！！！！！！！！！！
    @app.route('/')
    def hello_world():
        return render_template('index.html')

    # 注册页面
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            identifier = request.form.get('identifier')
            role = request.form.get('role')
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            # 检查邮箱是否已存在
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('邮箱已存在！', 'danger')
                return redirect(url_for('register')) # 重定向到注册页面

            password_hash = generate_password_hash(password)
            user = User(identifier=identifier, role=role, name=name, email=email, password=password_hash)
            db.session.add(user)
            db.session.commit()
            flash('注册成功，请登录！', 'success')
            # 注册成功后cookie保存用户信息
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('注册成功，您已登录！', 'success')
            return render_template('index.html')
        return render_template('wang/register.html')
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return render_template('wang/login.html')
    @app.route('/loginHandle', methods=['POST'])
    def loginHandle():
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('登录成功！', 'success')
            print("登录成功！")
            return render_template('/index.html')
        else:
            print("用户名或密码错误！")
            return render_template('wang/login.html', error='用户名或密码错误！')
    @app.route('/chat')
    def chat():
        return render_template('xie/chat.html', conversation=c.conversation_history)
    @app.route("/logout", methods=['GET'])
    def logout():
        session.clear()
        flash('您已退出登录！', 'success')
        return render_template('wang/login.html')
    @app.route('/chatHandle', methods=['POST'])
    def chatHandle():
        response = c.chat()
        return response
    return app

if __name__ == '__main__':
    app= create_app() # 创建app
    app.run(host='0.0.0.0', port=5000, debug=True)
    # 0.0.0.0 表示监听所有可用的网络接口
    # host='0.0.0.0' 允许外部访问
    # port=5000 设置端口号
# 如果局域网无法访问用命令行打开：python -m flask run --host=0.0.0.0

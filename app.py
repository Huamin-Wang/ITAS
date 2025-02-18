from zipfile import error
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash
from threading import Thread
import xie.chat as c
from wang.models import init_db
from wang.models.course import Course
from wang.models.course_students import Course_Students
from wang.models.user import User
from datetime import timedelta
import os
from flask_migrate import Migrate
import logging
from functools import wraps
import csv
import io
import chardet
import socket
import ssl
from waitress import serve

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 环境配置
environment = os.getenv('FLASK_ENV', 'development')
if "production" in environment:
    environment = 'production'


# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


def create_app():
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite:///test1.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY='your_secret_key_here',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=90)
    )

    # 初始化数据库
    db = init_db(app)

    @app.before_request
    def before_request():
        # HTTPS重定向
        if environment == 'production' and not request.is_secure:
            logger.info("重定向到HTTPS")
            return redirect(request.url.replace("http://", "https://"), code=301)

        # Session管理
        session.permanent = True

        # 安全检查
        if request.path.startswith(('/wordpress', '/wp-admin')):
            logger.warning(f"检测到可疑请求: {request.path}")
            abort(403)

        # 登录检查
        public_endpoints = ["index", 'loginHandle', 'register', 'login']
        if 'user_id' not in session and request.endpoint not in public_endpoints:
            return redirect(url_for('index'))

    # 统一错误处理
    def handle_error(e, status_code):
        logger.error(f"发生错误: {status_code} - {str(e)}")
        template = 'wang/500.html' if status_code == 500 else 'wang/404.html'
        return render_template(template), status_code

    for error_code in [404, 405, 500]:
        app.errorhandler(error_code)(lambda e, code=error_code: handle_error(e, code))

    @app.route('/')
    def hello_world():
        return render_template('index.html') if not session.get("logged_in") else loginHandle()

    @app.route('/index')
    def index():
        return hello_world()

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if session.get("logged_in"):
            flash('您已注册过了！如需重新注册，请先登出！', 'registerError')
            return loginHandle()

        if request.method == 'POST':
            try:
                return handle_registration()
            except Exception as e:
                logger.error(f"注册失败: {str(e)}")
                flash('注册失败，请稍后重试', 'danger')
                return redirect(url_for('register'))

        return render_template('wang/register.html')

    def handle_registration():
        form_data = request.form
        identifier = form_data.get('identifier').upper()

        # 验证表单数据
        if form_data.get('password') != form_data.get('confirm_password'):
            flash('密码不一致！', 'danger')
            return redirect(url_for('register'))

        # 检查用户是否存在
        if User.query.filter(User.email == form_data.get('email')).first():
            flash('邮箱已存在！', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(identifier=identifier).first():
            flash('学号已存在！', 'danger')
            return redirect(url_for('register'))

        # 创建新用户
        user = User(
            identifier=identifier,
            role=form_data.get('role'),
            name=form_data.get('name'),
            email=form_data.get('email'),
            password=generate_password_hash(form_data.get('password'))
        )

        db.session.add(user)
        db.session.commit()

        # 设置session
        session.update({
            'user_id': user.id,
            'user_name': user.name,
            'user_role': user.role,
            'user_identifier': user.identifier,
            'logged_in': True
        })

        logger.info(f"用户注册成功: {user.name}")
        flash('注册成功，您已登录！', 'success')
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if "logged_in" not in session or session["logged_in"] == False:
            return render_template('wang/login.html')
        else:
            flash('您已登录！', 'success')
            return loginHandle()

    # 登录处理，包括浏览器中后退操作处理（将网页中显示的东西显示完全）
    @app.route('/loginHandle', methods=['POST'])
    def loginHandle():
        # 如果session中登录状态为false，说明是第一次登录，从表单中获取学号和密码
        if "logged_in" not in session or session["logged_in"] == False:
            xuehao = request.form.get('xuehao')
            # 学号统一转大写
            xuehao = xuehao.upper()
            print(f"用户输入的学号为：{xuehao}")
            password = request.form.get('password')
            # 从数据库中查找用户，与用户输入的密码进行比对
            user = User.query.filter_by(identifier=xuehao).first()
            if user and user.check_password(password):
                # 在session中保存登录状态，已供全局使用
                session["logged_in"] = True
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_role'] = user.role
                session['user_identifier'] = user.identifier
                flash('登录成功！', 'success')
                print(f'{user.name}登录成功！')
            else:
                print("用户名或密码错误！")
                return render_template('wang/login.html', error='用户名或密码错误！')
        # 登录成功后才会执行到这里
        # 从数据库中查找用户，与用户输入的密码进行比对
        user = User.query.filter_by(identifier=session['user_identifier']).first()
        if user.role == "student":
            # 输出用戶信息
            print(f"用户{user.name}的学号为：{user.identifier}")

            # 获取学生名下的课程：把course_students表中学号和姓名能匹配上的所有记录中的课程id找出来
            course_students = Course_Students.query.filter_by(student_number=user.identifier,
                                                              student_name=user.name).all()
            print(
                f"用户{user.name}的课程有：{course_students}")

            print(f"course_students:{course_students}")
            # 将course_students表中自己的名字和学号对应的记录中的状态改为enrolled
            for course_student in course_students:
                course_student.course_status = 'enrolled'
                db.session.commit()  # 提交事务
            courses = []
            for course_student in course_students:
                course = Course.query.get(course_student.course_id)
                courses.append(course)
            print(f"用户{user.name}正在查看自己的课程！")
            print(courses)
            return render_template('wang/student_profile.html', courses=courses)
        elif user.role == "teacher":
            # 获取教师名下的课程
            courses = Course.query.filter_by(teacher_id=user.id).all()
            # 将course_students的所有学生的学号进行比对user表中的所有用户，如果有，已经注册为user用户的学生状态改为enrolled
            course_students = Course_Students.query.all()
            for course_student in course_students:
                student = User.query.filter_by(identifier=course_student.student_number).first()
                if student:
                    course_student.course_status = 'enrolled'
                    db.session.commit()

            return render_template('wang/teacher_profile.html', courses=courses)

    # 处理智能聊天请求
    @app.route('/chat')
    def chat():
        return render_template('xie/chat.html', conversation=c.conversation_history)
    @app.route('/chatHandle', methods=['POST'])
    def chatHandle():
        response = c.chat()
        return response
    @app.route("/logout", methods=['GET'])
    def logout():
        session.clear()
        return render_template('wang/login.html')

    @app.route('/student_profile')
    def student_profile():
        return loginHandle()
    # 学生课程详情页面
    @app.route('/course_detail/<int:course_id>')
    def course_detail(course_id):
        course = Course.query.get(course_id)
        user_name = session.get('user_name')
        return render_template('wang/course_detail.html', course=course,user_name=user_name)
    @app.route('/teacher_profile')
    def teacher_profile():
        # 获取教师名下的课程
        user_id = session.get('user_id')
        user_name = session.get('user_name')
        courses = Course.query.filter_by(teacher_id=user_id).all()
        print(f"用户{user_name}正在查看自己的课程列表！")
        print(courses)
        # 把课程传到前端
        return render_template('wang/teacher_profile.html', courses=courses)

    # 创建新的课程请求
    @app.route('/create_course')
    def create_course():
        # 获取用户数据
        user_name = session.get('user_name')
        print(f"{user_name}正在创建新的课程！")
        return render_template('wang/create_course.html')

    # 创建新课程的处理
    @app.route('/create_course_handle', methods=['POST'])
    def create_course_handle():
        # 获取课程数据
        course_name = request.form.get('course_name')
        semester = request.form.get('semester')
        course_description = request.form.get('course_description')
        code = request.form.get('course_code')
        teacher_id = session.get('user_id')
        # 创建课程
        course = Course(name=course_name, semester=semester, description=course_description, code=code,
                        teacher_id=teacher_id)
        db.session.add(course)
        db.session.commit()
        flash('课程创建成功！', 'success')
        # 解析上传的学生名单，并将学生信息添加到course_students表中
        # 获取上传的文件
        print("获取上传的文件")
        file = request.files['student_list']
        print(f"文件为：{file}")

        # 读取csv文件内容存储到数据库，文件格式为：学号、姓名、拼音姓名、年级、专业、方向、行政班级、学籍状态、修课方式
        import csv
        import io
        import chardet
        try:
            # 将文件内容读取为字符串
            raw_data = file.stream.read()
            # 检测文件编码
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            # 尝试用检测到的编码解码文件
            try:
                file_str = io.StringIO(raw_data.decode(encoding), newline=None)
            except UnicodeDecodeError:
                # 如果检测到的编码失败，尝试 utf-8 或 gbk
                try:
                    file_str = io.StringIO(raw_data.decode('utf-8'), newline=None)
                except UnicodeDecodeError:
                    file_str = io.StringIO(raw_data.decode('gbk'), newline=None)
            # 解析CSV文件
            csv_reader = csv.reader(file_str)
            next(csv_reader)  # 跳过表头

            students_to_add = []
            for row in csv_reader:
                # print(row)
                # 格式为：学号、姓名、拼音姓名、年级、专业、方向、行政班级、学籍状态、修课方式
                # 将每条数据存储到数据库
                student_number = row[0]
                student_name = row[1]
                student_pinyin_name = row[2]
                student_grade = row[3]
                student_major = row[4]
                student_direction = row[5]
                student_class = row[6]
                student_status = row[7]
                student_course_method = row[8]
                course_student = Course_Students(course_id=course.id, student_number=student_number,
                                                 student_name=student_name, student_pinyin_name=student_pinyin_name,
                                                 student_grade=student_grade, student_major=student_major,
                                                 student_direction=student_direction, student_class=student_class,
                                                 student_status=student_status,
                                                 student_course_method=student_course_method)
                students_to_add.append(course_student)
            db.session.add_all(students_to_add)
            db.session.commit()
            flash('学生名单导入成功！', 'success')
            # 进入课程管理界面
            return redirect(url_for('course_manage', course_id=course.id))
        except error:
            flash('学生名单导入失败！', 'danger')
            return redirect(url_for('create_course'))

    # 课程管理页面
    @app.route('/course_manage/<int:course_id>')
    def course_manage(course_id):
        course = Course.query.get(course_id)
        # 查看课程下应该选课的学生
        course_students = course.course_students
        # print(f"查看课程{course.name}下的学生！")
        # In your view function
        enrolled_students_count = len(
            [student for student in course.course_students if student.course_status == 'enrolled'])
        # for student in course_students:
        #     print(student.student_name)
        return render_template('wang/courseManager.html', course=course, course_students=course_students,
                               enrolled_students_count=enrolled_students_count)
    # 课程管理页面：显示该课程下的选课情况：显示应选人数、已选人数、未选人数等信息
    @app.route('/course_students/<int:course_id>')
    def course_students(course_id):
        course = Course.query.get(course_id)
        course_students = course.course_students
        # 选课的学生名单
        enrolled_students = [student for student in course.course_students if student.course_status == 'enrolled']
        enrolled_students_count = len(
            [student for student in course.course_students if student.course_status == 'enrolled'])
        # 未选课的学生名单
        not_enrolled_students = [student for student in course.course_students if
                                 student.course_status == 'not_enrolled']
        return render_template('wang/course_students.html', course=course, course_students=course_students,
                               enrolled_students_count=enrolled_students_count, enrolled_students=enrolled_students,
                               not_enrolled_students=not_enrolled_students)
   # 课程管理页面：随机选
    @app.route('/course/random_select/<int:course_id>')
    def random_select(course_id):
        course = Course.query.get(course_id)
        course_students = course.course_students
        return render_template('wang/random_select.html', course=course, course_students=course_students)
    # 学生加分处理
    @app.route('/course/add_score/<int:course_id>', methods=['GET', 'POST'])
    def add_score(course_id):
        course = Course.query.get(course_id)
        course_students = course.course_students
        # 前端已经把所有学生都加分了，这里只是把加分的数据在原基础上加上后存到数据库
        if request.method == 'POST':
            session["scored_students"] = {}
            for student in course_students:
                student_number = student.student_number#学号
                score = request.form.get(f'score_{student_number}')
                score = float(score)
                # 记录下score非0的学生,存到session中
                if score != 0:
                  session["scored_students"][student.student_name] = score
                if student.score is None:
                    student.score = 0
                student.score = score+student.score
                db.session.commit()
            print(session.get("scored_students"))
            return redirect(url_for('add_score', course_id=course.id))
        print(f"用户{course.name}正在为学生加分！")
        return render_template('wang/add_score.html', course=course, course_students=course_students)
    # 列出我们还需要实现的的功能
    @app.route('/fuctions')
    def fuctions():
        return render_template('wang/fuctions.html')
    # 返回app
    return app
    #---迁移数据代码-----
    # # 返回app，db
    # return db,app

# db, app = create_app()  # 创建app
# migrate = Migrate(app, db)  # 添加数据库字段时，用来创建迁移对象
# app.run(host='0.0.0.0', port=80, debug=True)
# ！！！迁移时，请注释掉下述代码if __name__ == '__main__':，否则会报错
#---迁移数据代码-----




import socket
import ssl

from waitress import serve
if __name__ == '__main__':
    app = create_app()

    if environment == 'production':
        logger.info('Starting production server with Waitress...')
        try:
            # SSL配置
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(
                certfile='C:/Certbot/live/001ai.top/fullchain.pem',
                keyfile='C:/Certbot/live/001ai.top/privkey.pem'
            )
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

            # 创建HTTPS服务器
            https_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            https_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            https_sock.bind(('0.0.0.0', 443))
            https_sock.listen(5)
            ssl_sock = ssl_context.wrap_socket(https_sock, server_side=True)

            # HTTP重定向服务器
            redirect_app = Flask(__name__)
            @redirect_app.route('/', defaults={'path': ''})
            @redirect_app.route('/<path:path>')
            def redirect_to_https(path):
                return redirect(f'https://{request.host}{request.path}', code=301)

            http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            http_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            http_sock.bind(('0.0.0.0', 80))
            http_sock.listen(5)

            # 启动服务器
            Thread(target=lambda: serve(app, sockets=[ssl_sock], url_scheme='https')).start()
            Thread(target=lambda: serve(redirect_app, sockets=[http_sock])).start()

            logger.info('Production server is running at https://www.001ai.top')
        except Exception as e:
            logger.error(f"服务器启动失败: {str(e)}")
    else:
        logger.info('Starting development server with Waitress...')
        serve(app, host='0.0.0.0', port=80)

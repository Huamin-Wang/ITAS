from urllib.request import localhost
from zipfile import error
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify, \
    send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from threading import Thread
import xie.chat as c
from wang.models import init_db, Assignment
from wang.models.course import Course
from wang.models.course_students import Course_Students
from wang.models.user import User

from datetime import timedelta
import os
import csv
import io
import chardet
import requests

from xu.views import ai_bp
from flask_migrate import Migrate

# 获取环境变量的值，如果没有设置则默认为 'development'
environment = os.getenv('FLASK_ENV', 'development')
if "production" in environment:
    environment = 'production'


# ！！！！！！！！大家注意：这个页面只允许处理route的请求，其他无关代码请放到自己文件夹（包）进行调用！！！！！！！！！！
# ！！！！！！！！大家注意：这个页面只允许处理route的请求，其他无关代码请放到自己文件夹（包）进行调用！！！！！！！！！！
# 所有的路由处理函数都放到create_app()函数中
def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)  # 启用CORS支持
    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test1.db'  # ！！！配置数据库，提交到git之前改回来test1.db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # 配置密钥
    UPLOAD_FOLDER = 'xie/uploads'  # 确保路径正确
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB
    # 初始化数据库
    db = init_db(app)
    # -----微信小程序的appid和secret---------
    APP_ID = 'wx3dd32842e9e24690'
    APP_SECRET = '09732f45784f51d2b9e5bad0902ec17a'

    app.register_blueprint(ai_bp)  # 注册你的 Blueprint

    @app.route('/getOpenId', methods=['GET', 'POST'])
    def get_openid():
        print("登录小程序")
        data = request.json
        code = data.get('code')
        userInfo = data.get('userInfo')
        print(f"code:{code}")
        print(f"userInfo:{userInfo}")
        if not code:
            return jsonify({'success': False, 'message': '缺少 code'})
        # 向微信服务器请求 openid
        wx_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={APP_ID}&secret={APP_SECRET}&js_code={code}&grant_type=authorization_code"
        response = requests.get(wx_url).json()
        openid = response['openid']
        session['openid'] = openid
        print(f"openid:{openid}")
        # 如果成功获取 openid，则根据openid返回用户信息
        user = User.query.filter_by(openid=response['openid']).first()
        if user:
            return jsonify(
                {'success': True, 'user_id': user.id, 'user_name': user.name, 'user_role': user.role, "openid": openid})
        else:
            #   返回信息提示注册登录
            return jsonify(
                {'success': True, 'user_id': -1, 'user_name': "未登录过小程序", 'user_role': 1, "openid": openid})

    # -----微信小程序登录页面---------
    @app.route('/minilogin', methods=['GET', 'POST'])
    def minilogin():
        print("验证小程序登录")
        data = request.json
        openid = data.get('openid')
        print(f"openid:{openid}")
        ident = data.get('identifier')  # 学号
        ident = ident.upper()
        print(f"ident:{ident}")
        password = data.get('password')
        # 从数据库中查找用户，与用户输入的密码进行比对
        user = User.query.filter_by(identifier=ident).first()
        if user and user.check_password(password):
            print("用户存在库中")
            # 在session中保存登录状态，已供全局使用
            session["logged_in"] = True
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            session['user_identifier'] = user.identifier
            print(f"session:{session}")
            user.openid = openid  # 保存用户的openid，以便下次微信登录时直接登录openid = session.get('openid')
            print("保存openid成功！")
            session["openid"] = openid
            db.session.commit()
            print(f'{user.name}登录成功！')
            return jsonify({'success': True, 'user_id': user.id, 'user_name': user.name, 'user_role': user.role})
        return jsonify({'success': False, 'message': '用户名或密码错误！'})

    # ！！！ ----------以下为电脑端项目中的路由处理函数
    @app.before_request
    def before_request():
        # ----HTTP 请求转发到 HTTPS（服务器代码）------
        # production 环境下，如果请求不是 HTTPS 请求，则重定向到 HTTPS 请求
        if environment == 'production':
            if not request.is_secure:
                print("请求不是HTTPS请求，重定向到HTTPS")
                return redirect(request.url.replace("http://", "https://"), code=301)
        # 超时自动清空session
        # 设置 session 超时时间
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=90)  # 设置 session 有效时间为 90 分钟

        # 如果请求路径是恶意路径，则阻止访问
        if request.path.startswith(('/wordpress', '/wp-admin')):
            abort(403)  # 返回 403 Forbidden

        # 登录状态检查，排除登录和注册页面
        if 'user_id' not in session and request.endpoint not in ["forum", "getCourseById", "getStudentCourses",
                                                                 "minilogin", "index", 'loginHandle', 'register',
                                                                 'login', 'get_openid',
                                                                 'main'] and not request.path.startswith(
                '/getCourseById/'):  # 禁止重定向加的是方法名，不是路由名
            # 如果用户未登录且请求的不是登录或注册页面，重定向到登录页面
            return redirect(url_for('index'))

    # 错误处理
    @app.errorhandler(500)
    def internal_server_error(e):
        print("500错误")
        return render_template('wang/500.html'), 500

        # 405错误处理

    @app.errorhandler(405)
    def method_not_allowed(e):
        print("405")
        return render_template('wang/500.html'), 500

    @app.errorhandler(404)
    def page_not_found(e):
        print("404")
        return render_template('wang/404.html'), 404

    # 首页
    @app.route('/')
    def hello_world():
        # 如果session中登录状态为false或者没有保存登录状态信息，说明是第一次登录，返回登录页面
        if "logged_in" not in session or session["logged_in"] == False:
            return render_template('index.html')
        else:  # 如果session中登录状态为true，说明是已经登录过了，返回loginHandle函数处理
            return loginHandle()

    @app.route('/index')
    def index():
        return hello_world()

    # 注册页面
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        # 如果session中登录状态为false或者没有保存登录状态信息，说明是第一次登录，才能注册
        if "logged_in" not in session or session["logged_in"] == False:
            if request.method == 'POST':
                identifier = request.form.get('identifier')  # 学号
                # 将学号统一转成大写
                identifier = identifier.upper()
                role = request.form.get('role')
                name = request.form.get('name')
                email = request.form.get('email')
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                # 检查密码是否一致
                if password != confirm_password:
                    flash('密码不一致！', 'danger')
                    return redirect(url_for('register'))
                # 检查邮箱是否已存在
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    flash('邮箱已存在！', 'danger')
                    return redirect(url_for('register'))  # 重定向到注册页面
                # 检查学号是否已存在
                existing_user = User.query.filter_by(identifier=identifier).first()
                if existing_user:
                    flash('学号已存在！', 'danger')
                    return redirect(url_for('register'))

                password_hash = generate_password_hash(password)
                user = User(identifier=identifier, role=role, name=name, email=email, password=password_hash)
                db.session.add(user)
                db.session.commit()
                # 注册成功后cookie保存用户信息
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_role'] = user.role
                session['user_identifier'] = user.identifier
                # 在session中保存登录状态，已供全局使用
                session["logged_in"] = True
                print("注册成功！")
                flash('注册成功，您已登录！', 'success')
                return render_template('index.html')
            return render_template('wang/register.html')
        else:  # 如果session中登录状态为true，说明是已经登录过了，返回loginHandle函数处理
            # 提示已经注册过了
            flash('您已注册过了！如需重新注册，请先退出！', 'registerError')
            return loginHandle()

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if "logged_in" not in session or session["logged_in"] == False:
            return render_template('wang/login.html')
        else:
            flash('您已登录！', 'success')
            return loginHandle()

    @app.route('/course/quiz/<int:course_id>', methods=['GET', 'POST'])
    def quiz(course_id):
        if request.method == 'GET':
            # 渲染小测页面模板
            session["currentCourse"] = course_id
            return render_template('qiu/quiz.html', title=course_id)
        elif request.method == 'POST':
            # 处理 POST 请求，假设这里接收一个名为 'answer' 的表单数据
            answer = request.form.get('answer')
            if answer:
                return render_template('result.html', answer=answer)
            else:
                return "未接收到答案，请重新提交。"

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

    # 微信小程序：返回学生的课程列表
    @app.route('/getStudentCourses', methods=['GET', 'POST'])
    def getStudentCourses():
        # 从数据库中查找用户，与用户输入的密码进行比对
        openid = request.args.get('openid')
        print(f"openid:{openid}")
        user = User.query.filter_by(openid=openid).first()
        if user:
            print(f"{user.name}在微信小程序获取课程列表中！")
        print(session)
        if user:
            # 返回学生的课程列表
            course_students = Course_Students.query.filter_by(student_number=user.identifier,
                                                              student_name=user.name).all()
            courses = []
            for course_student in course_students:
                course = Course.query.get(course_student.course_id)
                # 课程序列化
                courses.append({
                    'course_id': course.id,
                    'course_name': course.name,
                    'semester': course.semester,
                    'description': course.description,
                    "teacher": course.teacher.name
                })
            print("课程列表获取成功！")
            return jsonify({'success': True, 'courses': courses})
        print("用户不存在！")
        return jsonify({'success': False, 'message': '用户不存在！'})

    # 处理智能聊天请求
    @app.route('/chat')
    def chat():
        return render_template('xie/chat.html', conversation=c.conversation_history)

    @app.route('/chatHandle', methods=['POST'])
    def chatHandle():
        response = c.chat()
        return response

    # 匿名论坛
    @app.route('/forum')
    def forum():
        print(f"用户{session.get('user_name')}正在查看论坛！")
        # 重定向到http://116.205.170.203:81/forum.html
        return redirect("http://116.205.170.203:81/forum.html", code=302)

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
        return render_template('wang/course_detail.html', course=course, user_name=user_name)

    # 微信小程序：返回单个课程详情
    @app.route('/getCourseById/<int:course_id>', methods=['GET', 'POST'])
    def getCourseById(course_id):
        print("小程序：获取单个课程详情！")
        course = Course.query.get(course_id)
        openid = request.args.get('openid')
        print(f"详情中的用户openid:{openid}")
        # 获取用户数据
        user = User.query.filter_by(openid=openid).first()
        print(f"用户{user.name}正在查看课程{course.name}的详情！")
        # 获取学生本门课的学生
        course_students = course.course_students
        # 获取学生的分数
        score = 0
        for student in course_students:
            if student.student_number == user.identifier:
                print(f"student.student_name:{student.student_name}")
                score = student.score
                print(f"score:{student.score}")
        # 课程详情序列化
        courseInfo = {
            'id': course.id,
            'name': course.name,
            'teacher_id': course.teacher_id,
            'semester': course.semester,
            'description': course.description,
            'code': course.code,
            'teacher_name': course.teacher.name,
            'students': [{'student_name': student.student_name, 'score': student.score} for student in
                         course.course_students]
        }
        print(f"返回课程{course.name}的详情！")
        print(f"分数：{score}")
        return jsonify({'success': True, 'courseInfo': courseInfo, 'score': score})

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

    # 更新课程信息页面
    @app.route('/update_course/<int:course_id>', methods=['GET', 'POST'])
    def update_course(course_id):
        course = Course.query.get(course_id)
        print(f"{session.get('user_name')}用户正在更新课程信息:{course.name}")
        if request.method == 'GET':
            print("进入更新课程页面")
            return render_template("/wang/update_course.html", course=course, course_id=course_id)
        if request.method == 'POST':
            print("提交更新课程信息！")
            course_name = request.form.get('course_name')
            semester = request.form.get('semester')
            course_description = request.form.get('course_description')
            code = request.form.get('course_code')
            course.name = course_name
            course.semester = semester
            course.description = course_description
            course.code = code
            # 更新course_students
            file = request.files['student_list']
            # 文件不为空进行处理
            if file and file.filename:
                # 读取csv文件内容存储到数据库，文件格式为：学号、姓名、拼音姓名、年级、专业、方向、行政班级、学籍状态、修课方式
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
                                                         student_name=student_name,
                                                         student_pinyin_name=student_pinyin_name,
                                                         student_grade=student_grade, student_major=student_major,
                                                         student_direction=student_direction,
                                                         student_class=student_class,
                                                         student_status=student_status,
                                                         student_course_method=student_course_method)
                        students_to_add.append(course_student)
                    # 取出当前课程中的学生名单
                    course_students = course.course_students
                    # 通过对比course_students与students_to_add中学生的学号（student_number），如果course_students中有的学生在students_to_add中没有，则删除，如果有，则不进行操作，对于students_to_add中有而course_students中没有的学生，则添加
                    # 提取所有学生编号到集合中，提升查找效率
                    existing_student_numbers = {student1.student_number for student1 in course_students}
                    new_student_numbers = {student2.student_number for student2 in students_to_add}

                    # 删除新表中没有的学生
                    for student1 in course_students:
                        if student1.student_number not in new_student_numbers:
                            db.session.delete(student1)

                    # 增加旧表中缺的学生
                    for student2 in students_to_add:
                        if student2.student_number not in existing_student_numbers:
                            db.session.add(student2)

                    # 提交更改
                    db.session.commit()
                    flash('课程信息更新成功！', 'success')
                    return redirect(url_for('course_manage', course_id=course.id))
                except:
                    flash('学生名单导入失败！', 'danger')
                    return redirect(url_for('update_course', course_id=course.id))
            db.session.commit()
            flash('课程信息更新成功！', 'success')
            return redirect(url_for('course_manage', course_id=course.id))

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
                student_number = student.student_number  # 学号
                score = request.form.get(f'score_{student_number}')
                score = float(score)
                # 记录下score非0的学生,存到session中
                if score != 0:
                    session["scored_students"][student.student_name] = score
                if student.score is None:
                    student.score = 0
                student.score = score + student.score
                db.session.commit()
            print(session.get("scored_students"))
            return redirect(url_for('add_score', course_id=course.id))
        print(f"用户{course.name}正在为学生加分！")
        return render_template('wang/add_score.html', course=course, course_students=course_students)
    # 课程管理页面：作业布置
    @app.route('/course/assignments/<int:course_id>', methods=['GET', 'POST'])
    def assignments(course_id):
        assignments = Assignment.query.filter_by(course_id=course_id).all()
        if request.method == 'GET':
            course = Course.query.get(course_id)
            # Also fetch existing assignments for this course
            return render_template('wang/assignments.html', course=course, assignments=assignments)
        # 课程管理页面：作业布置处理
        if request.method == 'POST':
            course = Course.query.get(course_id)
            assignment_name = request.form.get('title')  # From form field 'title' in HTML
            assignment_description = request.form.get('description')
            from datetime import datetime

            assignment_deadline = datetime.strptime(request.form.get('due_date'),
                                                    '%Y-%m-%d').date()  # Convert to date object
            # Include teacher_id from session
            teacher_id = session.get('user_id')
            assignment = Assignment(course_id=course_id, teacher_id=teacher_id, title=assignment_name,
                                    description=assignment_description, due_date=assignment_deadline)
            db.session.add(assignment)
            db.session.commit()
            flash('作业布置成功！刷新网页获取！', 'success')
            print(f"用户{session.get('user_name')}为课程{course.name}布置了作业！")
            return render_template('wang/assignments.html', course=course, assignments=assignments)


    # 列出我们还需要实现的的功能
    @app.route('/fuctions')
    def fuctions():
        return render_template('wang/fuctions.html')

    # 上传文件
    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        if request.method == 'GET':
            return render_template('xie/upload.html')

    # 返回app
    return app
    # ---迁移数据代码-----
    # # 返回app，db
    # return db,app


#
from sqlalchemy import text
# db, app = create_app()  # 创建app
# with app.app_context():
#     try:
#         # 使用 text 函数将 SQL 语句包装起来
#         db.session.execute(text('DROP TABLE alembic_version'))
#         db.session.commit()
#         print("alembic_version 表已删除")
#     except Exception as e:
#         print(f"删除 alembic_version 表时出错: {e}")
# migrate = Migrate(app, db)  # 添加数据库字段时，用来创建迁移对象
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=80, debug=True)
# ！！！迁移时，请注释掉下述代码if __name__ == '__main__':，否则会报错
# ---迁移数据代码-----    步骤：  1.模型中创建迁移字段 2.删除alembic_version表（删除完后注释掉删除代码） 3.删除migrationgs文件夹  4.执行迁移命令：1）flask db init   2）flask db migrate -m "信息"     3）flask db upgrade：这步如有问题问ai，可能要修改一下迁移文件


import socket
import ssl

from waitress import serve

if __name__ == '__main__':
    app = create_app()  # 创建 app

    if environment == 'production':
        print('Starting production server with Waitress...')
        # 配置 SSL 证书路径
        certfile = 'C:/Certbot/live/001ai.top/fullchain.pem'
        keyfile = 'C:/Certbot/live/001ai.top/privkey.pem'

        try:
            # 创建 HTTPS 套接字
            https_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            https_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            https_sock.bind(('0.0.0.0', 443))
            https_sock.listen(5)

            # 创建 SSL 上下文 - 更宽松的配置
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=certfile, keyfile=keyfile)

            # 允许更广泛的客户端兼容性
            try:
                context.minimum_version = ssl.TLSVersion.TLSv1
                # 更宽松的加密套件设置
                context.set_ciphers('ALL:@SECLEVEL=0')
            except (AttributeError, ValueError):
                # 如果 Python 版本不支持这些设置选项
                pass

            # 将普通套接字包装成 SSL 套接字
            ssl_sock = context.wrap_socket(https_sock, server_side=True)


            # 启动 HTTPS 服务器
            def run_https_server():
                while True:
                    try:
                        serve(app, sockets=[ssl_sock], url_scheme='https')
                    except ssl.SSLError as e:
                        print(f"SSL error: {e}. Continuing...")
                    except ConnectionError as e:
                        print(f"Connection error: {e}. Continuing...")
                    except Exception as e:
                        print(f"Unexpected error in HTTPS server: {e}")
                        # 在重大错误后短暂暂停以避免资源耗尽
                        import time
                        time.sleep(1)


            # 创建一个简单的 Flask 应用用于处理 HTTP 重定向
            redirect_app = Flask(__name__)


            @redirect_app.route('/', defaults={'path': ''})
            @redirect_app.route('/<path:path>')
            def redirect_to_https(path):
                return redirect(f'https://{request.host}{request.path}', code=301)


            # 创建 HTTP 套接字
            http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            http_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            http_sock.bind(('0.0.0.0', 80))
            http_sock.listen(5)


            # 启动 HTTP 重定向服务器
            def run_http_server():

                try:
                    serve(redirect_app, sockets=[http_sock])
                except Exception as e:
                    print(f"An unexpected error occurred in HTTP server: {e}")

                serve(redirect_app, sockets=[http_sock])


            # 分别在不同线程中启动 HTTP 和 HTTPS 服务器
            from threading import Thread

            https_thread = Thread(target=run_https_server)
            http_thread = Thread(target=run_http_server)

            https_thread.start()
            http_thread.start()

            print('生产服务器正在运行。您可以通过以下网址访问应用程序：')
            print('https://www.001ai.top')
        except Exception as e:
            print(f"An error occurred while starting the server: {e}")
    else:
        print('使用 Waitress 启动开发服务器...')
        print('开发服务器正在运行，您可以通过以下网址访问应用程序：')
        print('http://127.0.0.1')
        print(f'http://{socket.gethostbyname(socket.gethostname())}')
        print('或从本地网络上的其他设备访问')
        serve(app, host='0.0.0.0', port=80)

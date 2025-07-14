from zipfile import error
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
from werkzeug.security import generate_password_hash
from threading import Thread
from werkzeug.utils import secure_filename
import wang.tools.studentTool as studentTool
import wang.tools.studentTool
import xie.chat as c
from wang.models import init_db, Assignment, Submission
from wang.models.course import Course
from wang.models.course_students import Course_Students
from wang.models.user import User
from wang.models.file import File

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

    with app.app_context():
        db.create_all()
    # 学生中心右下角的聊天框
    @app.route('/chat_apis', methods=['GET', 'POST'])
    def chat_apis():
        answer = None
        question = None
        show_dialog = False
        if request.method == 'POST':
            from wang.DouBaoAPI import API
            question = request.form.get('question')
            answer = API.get_answer(question)
            show_dialog = True
        return render_template('wang/student_profile.html', answer=answer, question=question, show_dialog=show_dialog)

    @app.route('/.well-known/acme-challenge/<filename>',methods=['GET'])
    def letsencrypt_challenge_unlocked(filename):
        print("请求了/.well-known/acme-challenge")
        return send_from_directory('.well-known/acme-challenge', filename)
    @app.route('/getOpenId', methods=['GET', 'POST'])
    def get_openid_unlocked():
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
            return jsonify({'success': True, 'user_id': user.id, 'user_name': user.name, 'user_role': user.role,
                            "user_identifier": user.identifier, "openid": openid, "email": user.email,
                            "gender": user.gender})
        else:
            #   返回信息提示注册登录
            return jsonify(
                {'success': True, 'user_id': -1, 'user_name': "未登录过小程序,退出重新登录", 'user_role': "游客",
                 "openid": openid})

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
            print(f"user_identifier{user.identifier}")
            print(f"session:{session}")
            user.openid = openid  # 保存用户的openid，以便下次微信登录时直接登录openid = session.get('openid')
            print("保存openid成功！")
            session["openid"] = openid
            db.session.commit()
            print(f'{user.name}登录成功！')
            # 根据课程信息获取用户性别
            # 获取学生名下的课程：把course_students表中学号和姓名能匹配上的所有记录中的课程id找出来
            course_students = Course_Students.query.filter_by(student_number=user.identifier,
                                                              ).all()
            print(
                f"用户{user.name}的课程有：{course_students}")

            return jsonify({'success': True, 'user_id': user.id, 'user_name': user.name, 'user_role': user.role,
                            "user_identifier": user.identifier, "openid": openid, "email": user.email,
                            "gender": user.gender})
        return jsonify({'success': False, 'message': '用户名或密码错误！'})

    # 微信小程序注册页面
    @app.route('/miniRegister', methods=['GET', 'POST'])
    def miniRegister():
        print("从微信小程序注册")
        data = request.json
        openid = data.get('openid')
        print(f"openid:{openid}")
        identifier = data.get('user_identifier')
        identifier = identifier.upper()
        identifier = identifier.replace(' ', '')
        print(f"identifier:{identifier}")
        role = data.get('user_role')
        name = data.get('user_name')
        name = name.replace(' ', '')
        gender = data.get("gender")
        email = data.get('email')
        password = data.get('password')
        print()
        existing_user = User.query.filter_by(identifier=identifier).first()
        if existing_user:
            return jsonify({'success': False, 'message': '注册失败，检查学号是否已存在！'})
        password_hash = generate_password_hash(password)
        user = User(gender=gender, identifier=identifier, role=role, name=name, email=email, password=password_hash,
                    openid=openid)
        db.session.add(user)
        db.session.commit()
        print("注册成功！")
        # 注册成功后cookie保存用户信息
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_role'] = user.role
        session['user_identifier'] = user.identifier
        # 在session中保存登录状态，已供全局使用
        session["logged_in"] = True
        return jsonify({'success': True, 'user_id': user.id, 'user_name': user.name, 'user_role': user.role,
                        "user_identifier": user.identifier, "openid": openid, "email": email, "gender": gender})

    # 微信小程序资料编辑页面
    @app.route('/miniEdit', methods=['GET', 'POST'])
    def miniEdit():
        print("从微信小程序改个人资料")
        data = request.json
        openid = data.get('openid')
        print(f"openid:{openid}")
        identifier = data.get('user_identifier')
        identifier = identifier.upper()
        print(f"identifier:{identifier}")
        role = data.get('user_role')
        name = data.get('user_name')
        gender = data.get("gender")
        email = data.get('email')
        password = data.get('password')
        password_hash = generate_password_hash(password)
        # 通过openid查找用户
        user = User.query.filter_by(openid=openid).first()
        if user:
            # 如果用户存在，更新用户信息
            user.name = name
            user.role = role
            user.email = email
            user.password = password_hash
            user.gender = gender
            user.identifier = identifier
            db.session.commit()
            print("小程序中更新用户信息成功！")
        # cookie保存用户信息
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_role'] = user.role
        session['user_identifier'] = user.identifier
        # 在session中保存登录状态，已供全局使用
        session["logged_in"] = True
        return jsonify({'success': True, 'user_id': user.id, 'user_name': user.name, 'user_role': user.role,
                        "user_identifier": user.identifier, "openid": openid, "email": email, "gender": gender})

    # ！！！ ----------以下为电脑端项目中的路由处理函数----------------
    @app.before_request
    def before_request():
        # 生产环境才启用
        if environment == 'production':
            # 先检查 Host 是否是裸域（不带 www）
            host = request.host
            # 注意 host 可能带端口，比如 '001ai.top:5000'
            if host.startswith("001ai.top") and not host.startswith("www."):
                # 构造带 www 的 URL
                # 保持 HTTPS（因为要跳转到 HTTPS 的www域名）
                url = request.url
                # 如果是 HTTP，先转 HTTPS
                if url.startswith("http://"):
                    url = url.replace("http://", "https://")
                # 再替换裸域为 www 域名（注意要排除端口部分）
                # 处理端口的情况
                if ':' in host:
                    domain, port = host.split(':', 1)
                    new_host = f"www.{domain}:{port}"
                else:
                    new_host = "www." + host

                # 替换url中的host部分为带www的host
                from urllib.parse import urlparse, urlunparse

                parsed_url = urlparse(url)
                new_url = urlunparse(parsed_url._replace(netloc=new_host))

                return redirect(new_url, code=301)

            # 然后再做 HTTP -> HTTPS 重定向
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
        # 如果openid不为空，则允许
        if request.method == 'GET':
            openid = request.args.get('openid')
            if openid == None and 'user_name' in session:
                print(f'''用户{session["user_name"]}在电脑端操作ing''')
        else:
            data = request.get_json() if request.is_json else {}
            openid = data.get('openid')
        if openid:
            if 'user_name' in session:
                print(f'''用户{session["user_name"]}在微信小程序端操作ing''')
        else:

            # 视图函数我如果允许直接通过函数末尾会加_unlocked，这里判断函数有没有unlocked后缀，如果没有，则进行登录状态检查
            if 'user_id' not in session and (request.endpoint is None or "_unlocked" not in request.endpoint):
                return redirect(url_for('index_unlocked'))


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
    def hello_world_unlocked():
        # 如果session中登录状态为false或者没有保存登录状态信息，说明是第一次登录，返回登录页面
        if "logged_in" not in session or session["logged_in"] == False:
            return render_template('index.html')
        else:  # 如果session中登录状态为true，说明是已经登录过了，返回loginHandle函数处理
            return loginHandle_unlocked()

    @app.route('/index')
    def index_unlocked():
        return hello_world_unlocked()

    # 注册页面
    @app.route('/register', methods=['GET', 'POST'])
    def register_unlocked():
        # 如果session中登录状态为false或者没有保存登录状态信息，说明是第一次登录，才能注册
        if "logged_in" not in session or session["logged_in"] == False:
            if request.method == 'POST':
                identifier = request.form.get('identifier')  # 学号
                # 将学号统一转成大写
                identifier = identifier.upper()
                identifier = identifier.replace(' ', '')
                role = request.form.get('role')
                name = request.form.get('name')
                name = name.replace(' ', '')
                gender = request.form.get('gender')
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
                user = User(gender=gender, identifier=identifier, role=role, name=name, email=email,
                            password=password_hash)
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
            return loginHandle_unlocked()

    @app.route('/login', methods=['GET', 'POST'])
    def login_unlocked():
        if "logged_in" not in session or session["logged_in"] == False:
            return render_template('wang/login.html')
        else:
            flash('您已登录！', 'success')
            return loginHandle_unlocked()
    #个人信息编辑页面
    @app.route('/edit_profile', methods=['GET', 'POST'])
    def edit_profile():
        print(session.get("user_name")+"正在编辑个人资料")
        return render_template("wang/personInfo.html")
    #课程管理：抢答
    @app.route('/course/quiz/<int:course_id>', methods=['GET', 'POST'])
    def quiz(course_id):
        if request.method == 'GET':
            # 找到对应课程
            course = Course.query.get(course_id)
            return render_template('qiu/quiz.html', course=course)
        elif request.method == 'POST':
            # 处理 POST 请求，假设这里接收一个名为 'answer' 的表单数据
            answer = request.form.get('answer')
            if answer:
                return render_template('result.html', answer=answer)
            else:
                return "未接收到答案，请重新提交。"
    # 课程管理：智能生成课程总体学习分析报告
    @app.route('/course/course_analysis/<int:course_id>', methods=['GET', 'POST'])
    def analysis(course_id):
        course= Course.query.get(course_id)
        return  render_template("wang/course_analysis.html",course=course)
    #课程管理：考勤
    @app.route('/course/attendance/<int:course_id>', methods=['GET', 'POST'])
    def attendance(course_id):
        course= Course.query.get(course_id)
        return render_template('wang/attendance.html', course=course, qrcode_url=url_for('static', filename='qrcode_sign_id=abc123.png'))
    @app.route('/loginHandle', methods=['POST'])
    def loginHandle_unlocked():
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
        if user:
            if user.role == "student":
                # 输出用戶信息
                print(f"用户{user.name}的学号为：{user.identifier}")

                # 获取学生名下的课程：把course_students表中学号匹配上的所有记录中的课程id找出来
                course_students = Course_Students.query.filter_by(student_number=user.identifier,
                                                                  ).all()
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
                # 获取学生所有课程的作业,待做作业
                Allassignments, assignments_to_do = wang.tools.studentTool.assignments(user.id, db)
                print(f"assignments_to_do:{assignments_to_do}")
                return render_template('wang/student_profile.html', courses=courses,
                                       assignments_to_do=assignments_to_do)
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
            # 返回首页
        return render_template("index.html")

    # 微信小程序：获取学生的作业列表
    @app.route('/getStudentAssignments', methods=['GET', 'POST'])
    def getStudentAssignments():
        # 从数据库中查找用户，与用户输入的密码进行比对
        openid = request.args.get('openid')
        print(f"getStudentAssignments：openid:{openid}")
        user = User.query.filter_by(openid=openid).first()
        if user:
            print(f"{user.name}在微信小程序获取作业列表中！")
        print(session)
        allAssignments, assignments_to_do = wang.tools.studentTool.assignments(user.id, db)
        if user:
            # 返回学生的所有作业列表
            assignmentsJson = []
            for assignment in allAssignments:
                # 作业序列化
                assignmentsJson.append({
                    'assignment_id': assignment.id,
                    'course_id': assignment.course_id,
                    'title': assignment.title,
                    'description': assignment.description,
                    'deadline': assignment.due_date,
                })
            print("所有作业列表获取成功！")
            # 返回待完成作业列表
            assignments_to_doJson = []
            for assignment in assignments_to_do:
                # 作业序列化
                assignments_to_doJson.append({
                    'assignment_id': assignment.id,
                    'course_id': assignment.course_id,
                    'title': assignment.title,
                    'description': assignment.description,
                    'deadline': assignment.due_date,
                })
            print("待完成作业列表获取成功！")
            print(f"assignments_to_do:{assignments_to_doJson}")
            # 返回作业列表
            return jsonify(
                {'success': True, 'assignments': assignmentsJson, 'assignments_to_do': assignments_to_doJson})

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
                                                              ).all()
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
    def chat_unlocked():
        return render_template('xie/chat.html', conversation=c.conversation_history)

    @app.route('/chatHandle', methods=['POST'])
    def chatHandle_unlocked():
        response = c.chat()
        return response

    @app.route("/logout", methods=['GET'])
    def logout():
        session.clear()
        return render_template('wang/login.html')

    @app.route('/student_profile')
    def student_profile():
        return loginHandle_unlocked()

    # 学生课程详情页面
    @app.route('/course_detail/<int:course_id>', methods=['GET', 'POST'])
    def course_detail(course_id):
        course = Course.query.get(course_id)
        print(f"课程详情页面中的课程为：{course}")
        xuehao = session.get('user_identifier')
        user_name = session.get('user_name')
        print(f"用户{user_name}正在查看课程{course.name}的详情！")
        # 获取学生本门课的学生
        course_students = course.course_students
        # 获取学生的分数
        for student in course_students:
            if student.score==None:
                student.score = 0
        # 提交到数据库
        db.session.commit()
        # 查找本门课的作业
        # 根据学生user_name获取学生所有课程下的作业
        student = User.query.get(user_name)
        Allassignments = []
        # 根据courses获取所有的作业
        assignments = Assignment.query.filter_by(course_id=course.id).all()
        for assignment in assignments:
            Allassignments.append(assignment)
        if request.method == 'POST':
            # 更新final_score=平时分+作业分数
            # 查找所有学生
            students = User.query.filter_by(role="student").all()
            for student in students:  # 每次学生点击都会更新所有人的分数，吃点性能，后期可以优化
                studentTool.updateFinallyScore_byUserID(student.id, db)  # 更新本门课所有人分数即可，不必传值
        return render_template('wang/course_detail.html', course=course, user_name=user_name,xuehao=xuehao,assignments=assignments)

    # 学生作业列表页面
    @app.route('/submissions/<int:student_id>', methods=['GET', 'POST'])
    def submission(student_id):
        # 根据学生id获取学生所有课程下的作业
        student = User.query.get(student_id)
        # 获取学生名下的课程
        course_students = Course_Students.query.filter_by(student_number=student.identifier,
                                                          ).all()
        courses = []
        for course_student in course_students:
            course = Course.query.get(course_student.course_id)
            courses.append(course)
        # 获取学生所有课程的作业
        Allassignments = []
        # 根据courses获取所有的作业
        for course in courses:
            assignments = Assignment.query.filter_by(course_id=course.id).all()
            for assignment in assignments:
                Allassignments.append(assignment)

        return render_template('wang/submissions.html', student=student, Allassignments=Allassignments)

    # 学生作业详情页面
    @app.route('/submission_detail/<int:assignment_id>', methods=['GET', 'POST'])
    def submission_detail(assignment_id):
        assignment = Assignment.query.get(assignment_id)
        # 查找用户
        user = User.query.get(session.get('user_id'))
        content = ""
        # 获取作业提交记录
        submission = Submission.query.filter_by(assignment_id=assignment_id, student_id=user.id).first()
        if request.method == 'POST':
            # 获取提交的作业内容
            content = request.form.get('content')
            print(f"用户{user.name}提交的作业内容为：{content}")
            # 把content存到submission表中
            if submission:  # 说明已经提交，正在做更新提交操作
                submission.data = content
                db.session.commit()
            else:
                # 如果没有记录，说明未提交，则第一次提交到数据库
                print(f"用户{user.name}未提交作业{assignment.title}")
                submission = Submission(assignment_id=assignment_id, student_id=user.id, data=content)
                db.session.add(submission)
                db.session.commit()
            # 对提交作业进行评分
            # 评分逻辑
            assignment = Assignment.query.get(assignment_id)
            import wang.DouBaoAPI.ping_fen as ping_fen
            得分, 评语, answer = ping_fen.test_批阅代码小程序(
                "题目标题：" + assignment.title + "；题目详情：" + assignment.description, 10, content)  # 题目，分数，答案
            print(f"得分：{得分} 评语：{评语}")
            # 更新评分
            submission.grade = 得分
            submission.feedback = 评语
            db.session.commit()
        return render_template('wang/submission_detail.html', assignment=assignment, user=user, submission=submission, )

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
                # 更新final_score=平时分+作业分数
                import wang.tools.studentTool as studentTool
                FinallyScore = studentTool.updateFinallyScore_byUserID(user.id, db)
                print(f"FinallyScore:{FinallyScore}")
                score = student.finally_score
                print(f"score:{student.finally_score}")
        # 课程详情序列化
        courseInfo = {
            'id': course.id,
            'name': course.name,
            'teacher_id': course.teacher_id,
            'semester': course.semester,
            'description': course.description,
            'code': course.code,
            'teacher_name': course.teacher.name,
            'students': [{'student_name': student.student_name, 'score': student.finally_score} for student in
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

    # 匿名论坛
    @app.route('/forum')
    def forum_unlocked():
        print(f"用户{session.get('user_name')}正在查看论坛！")
        # 重定向到http://116.205.170.203:81/forum.html
        return redirect("http://116.205.170.203:81/forum.html", code=302)

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
    @app.route('/course_students/<int:course_id>',methods=['GET','POST'])
    def course_students(course_id):
        course = Course.query.get(course_id)
        course_students = course.course_students
        # 更新本门课学生的注册状态
        if request.method == 'POST':
            print(f"{session['user_name']}正在刷新学生注册状态")
            # 将course_students表的学生与students用户中的学生进行比对，如果有，则将course_students表中的学生状态改为enrolled，没有则改为not_enrolled
            for course_student in course_students:
                student = User.query.filter_by(identifier=course_student.student_number).first()
                if student:
                    course_student.course_status = 'enrolled'
                    db.session.commit()
                else:
                    course_student.course_status = 'not_enrolled'
                    db.session.commit()
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
    # 显示学生排名
    @app.route('/course/ranking/<int:course_id>',methods=['GET', 'POST'])
    def ranking(course_id):
        course = Course.query.get(course_id)
        course_students = course.course_students
        if request.method == 'POST':
            #刷新排名
            import wang.tools.studentTool as studentTool
            # 查找所有学生
            students = User.query.filter_by(role="student").all()
            for student in students:  # 每次学生点击都会更新所有人的分数，吃点性能，后期可以优化
                studentTool.updateFinallyScore_byUserID(student.id, db)
            print(f"用户{course.name}正在刷新课程{course.name}的排名！")
        # 对学生进行排序，按分数从高到低排序
        course_students.sort(key=lambda x: x.finally_score, reverse=True)
        print(f"用户{course.name}正在查看课程{course.name}的排名！")
        from datetime import datetime
        return render_template('wang/ranking.html', course=course, course_students=course_students, now=datetime.now)
    # 课程管理页面：作业布置
    @app.route('/course/assignments/<int:course_id>', methods=['GET', 'POST'])
    def assignments(course_id):
        assignments = Assignment.query.filter_by(course_id=course_id).all()
        if request.method == 'GET':
            course = Course.query.get(course_id)
            # Also fetch existing assignments for this course
            return render_template('wang/assignments.html', course=course, assignments=assignments)
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
            flash('作业布置成功！', 'success')
            print(f"用户{session.get('user_name')}为课程{course.name}布置了作业！")
            # 重新请求'/course/assignments/<int:course_id>'路径，刷新页面
            return redirect(url_for('assignments', course_id=course_id))

    # 课程管理页面：作业详情
    @app.route('/course/assignment_detail/<int:assignment_id>', methods=['GET', 'POST'])
    def assignment_detail(assignment_id):
        flag = int(request.args.get('flag', 0))
        print(type(flag))
        print(f"flag:{flag}")
        # 获取作业信息
        assignment = Assignment.query.get(assignment_id)
        course = Course.query.get(assignment.course_id)

        if request.method == 'GET':
            print(f"用户{session.get('user_name')}正在查看课程{course.name}的作业详情！")
            if flag == 1:
                # 删除作业
                db.session.delete(assignment)
                db.session.commit()
                flash('作业删除成功！', 'success')
                print(f"用户{session.get('user_name')}删除了课程{course.name}的作业！")
                return redirect(url_for('assignments', course_id=course.id))
            return render_template('wang/assignment_detail.html', assignment=assignment, course=course)

        # 处理编辑作业的POST请求
        if request.method == 'POST':
            assignment.title = request.form.get('title')
            assignment.description = request.form.get('description')
            from datetime import datetime
            assignment.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
            db.session.commit()
            flash('作业编辑成功！', 'success')
            print(f"用户{session.get('user_name')}编辑了课程{course.name}的作业！")
            return redirect(url_for('assignments', assignment_id=assignment_id, course_id=course.id))

    # 列出我们还需要实现的的功能
    @app.route('/fuctions')
    def fuctions():
        # 跳转论坛
        return url_for('forum')

    # 超级管理员账户
    @app.route('/admin', methods=['GET', 'POST'])
    def admin():
        import wang.tools.userTool as userTool
        if request.method == 'GET':
            print(f"用户{session.get('user_identifier')}正在查看管理员页面！")
            if session.get('user_identifier') != 'JGXY2459'.upper():  # 开发环境改成你自己的账户即可通过admin直接访问
                return '您没有权限访问此页面！'
            # 查找所有用户
            users = User.query.all()
            return render_template('wang/admin.html', users=users, total_users=len(users))
        if request.method == 'POST':
            data = request.get_json()
            user_id = data.get('delete_id')
            # 根据id删除用户
            if user_id:
                user = User.query.get(user_id)
                if user:
                    userTool.delete_user(user_id, db)
                    print(f"用户{user.name}已被删除！")
                    return jsonify({'success': True, 'user': user.to_dict()})
                return jsonify({'success': False, 'message': '用户不存在！'})
            identifier = data.get('identifier')
            # 根据学号删除用户
            if identifier:
                user = User.query.filter_by(identifier=identifier).first()
                if user:
                    userTool.delete_user(identifier, db)
                    print(f"用户{user.name}已被删除！")
                    return jsonify({'success': True, 'user': user.to_dict()})
                return jsonify({'success': False, 'message': '用户不存在！'})
            # 解绑openid：这里收到的还是用户的id
            openid_id = data.get('openid_id')
            if openid_id:
                user = User.query.filter_by(id=openid_id).first()
                if user:
                    userTool.clearOpenid(openid_id, db)
                    print(f"用户{user.name}的openid已被清除！")
                    return jsonify({'success': True, 'user': user.to_dict()})
                return jsonify({'success': False, 'message': '用户不存在！'})
            # 更新用户信息
            userData = data.get('userData')
            # print(f"用户数据：{userData}")
            if userData:
                user = User.query.filter_by(id=userData['user_id']).first()
                if user:
                    user.name = userData['name']
                    user.identifier = userData['identifier']
                    user.email = userData['email']
                    user.role = userData['role']
                    user.gender = userData['gender']
                    db.session.commit()
                    print(f"用户{user.name}的信息已被更新！")
                    return jsonify({'success': True, 'user': user.to_dict()})
                return jsonify({'success': False, 'message': '用户不存在！'})

    # 解绑微信的openid
    @app.route('/unbindOpenId', methods=['POST'])
    def unbind_openid():
        data = request.get_json()
        openid = data.get('openid')
        # Find the user by the OpenID
        user = User.query.filter_by(openid=openid).first()
        user.openid = None
        db.session.commit()
        # Return a response
        print(f"用户{user.name}的openid已被清除！微信解绑成功！")
        return jsonify({
            'success': True,
            'message': 'OpenID successfully unbound'
        })

    @app.route('/')
    def home():
        return redirect(url_for('upload_file'))

    @app.route('/upload/<int:course_id>', methods=['GET', 'POST'])
    def upload_file(course_id):
        course=Course.query.get(course_id)
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('没有选择文件')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('没有选择文件')
                return redirect(request.url)
            if file:
                filename = secure_filename(file.filename)
                file_data = file.read()
                new_file = File(name=filename, data=file_data, mimetype=file.mimetype)
                db.session.add(new_file)
                db.session.commit()
                flash('文件上传成功')
                return redirect(url_for('list_files'))
        return render_template('xie/upload.html', course=course)

    @app.route('/download/')
    def list_files():
        files = File.query.all()
        return render_template('xie/download.html', files=files)

    @app.route('/download/<int:file_id>')
    def download_file(file_id):
        file = File.query.get(file_id)
        if file is None:
            abort(404)
        return send_file(
            io.BytesIO(file.data),
            mimetype=file.mimetype,
            as_attachment=True,
            download_name=file.name
        )
    # 返回app
    return app
    # ---迁移数据代码-----
    # 返回app，db
    # return db,app


#
from sqlalchemy import text

# db, app = create_app()  # 创建app
# # with app.app_context():
# #     try:
# #         # 使用 text 函数将 SQL 语句包装起来
# #         db.session.execute(text('DROP TABLE alembic_version'))
# #         db.session.commit()
# #         print("alembic_version 表已删除")
# #     except Exception as e:
# #         print(f"删除 alembic_version 表时出错: {e}")
# migrate = Migrate(app, db)  # 添加数据库字段时，用来创建迁移对象
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=80, debug=True)
# ！！！迁移时，请注释掉下述代码if __name__ == '__main__':，否则会报错

# ---迁移数据代码-----   步骤：  1.模型中创建迁移字段 2.删除alembic_version表 3.删除migrationgs文件夹  4.执行迁移命令：1）flask db init   2）flask db migrate -m "信息"     3）flask db upgrade：这步如有问题问ai，可能要修改一下迁移文件


import socket
import ssl

from waitress import serve

if __name__ == '__main__':
    app = create_app()  # 创建 app
    # 输出app启动时间
    from datetime import datetime

    print(f"应用程序启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if environment == 'production':
        print('正在启动生产服务器...')

        # 配置 SSL 证书路径
        certfile = 'C:/Certbot/live/001ai.top/fullchain.pem'
        keyfile = 'C:/Certbot/live/001ai.top/privkey.pem'

        try:
            # 使用 CherryPy 的 WSGI 服务器作为更可靠的SSL解决方案
            from cheroot.wsgi import Server as WSGIServer
            from cheroot.ssl.builtin import BuiltinSSLAdapter

            # 创建 HTTPS 服务器
            server = WSGIServer(('0.0.0.0', 443), app)
            server.ssl_adapter = BuiltinSSLAdapter(
                certificate=certfile,
                private_key=keyfile
            )

            # 创建 HTTP 重定向应用
            redirect_app = Flask(__name__)


            @redirect_app.route('/', defaults={'path': ''})
            @redirect_app.route('/<path:path>')
            def redirect_to_https(path):
                return redirect(f'https://{request.host}{request.path}', code=301)


            # 在单独的线程中启动 HTTP 重定向服务器
            from threading import Thread


            def run_http_server():
                serve(redirect_app, host='0.0.0.0', port=80)


            http_thread = Thread(target=run_http_server)
            http_thread.daemon = True
            http_thread.start()

            print('生产服务器已启动。您可以通过以下网址访问应用：')
            print('https://www.001ai.top')

            # 启动 HTTPS 服务器（主线程）
            server.start()

        except Exception as e:
            print(f"启动服务器时出现错误: {e}")
            import traceback

            traceback.print_exc()
    else:
        print('使用 Waitress 启动开发服务器...')
        print('开发服务器正在运行，您可以通过以下网址访问应用程序：')
        print('http://127.0.0.1')
        print(f'http://{socket.gethostbyname(socket.gethostname())}')
        print('或从本地网络上的其他设备访问')
        serve(app, host='0.0.0.0', port=80)

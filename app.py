from zipfile import error

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from wang.models import init_db
from wang.models.user import User
from wang.models.course import Course
from wang.models.course_students import Course_Students
import xie.chat as c


# ！！！！！！！！大家注意：这个页面只允许处理route的请求，其他无关代码请放到自己文件夹（包）进行调用！！！！！！！！！！
# 所有的路由处理函数都放到create_app()函数中
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # 配置数据库
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # 配置密钥
    # 初始化数据库
    db = init_db(app)

    @app.errorhandler(404)
    def page_not_found(e):
        print("404")
        return render_template('wang/404.html'), 404

    # ！！！！！！！！大家注意：这个页面只允许处理route的请求，其他无关代码请放到自己文件夹（包）进行调用！！！！！！！！！！

    # 首页
    @app.route('/')
    def hello_world():
        #防止用户从其他页面后退直接访问首页造成数据丢失
        #从session中获取用户信息
        user_identifier = session.get('user_identifier')
        password = session.get('user_password')
        print(f"用户密码为：{password}")
        print(f"用户user_identifier为：{user_identifier}")
        if user_identifier and password:
            return loginHandle()
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

            password_hash = generate_password_hash(password)
            user = User(identifier=identifier, role=role, name=name, email=email, password=password_hash)
            db.session.add(user)
            db.session.commit()
            flash('注册成功，请登录！', 'success')
            # 注册成功后cookie保存用户信息
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash('注册成功，您已登录！', 'success')
            return render_template('index.html')
        return render_template('wang/register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # 清了session中的用户信息，防止用户从其他页面后退直接访问登录页面造成数据丢失
        session.clear()
        return render_template('wang/login.html')

    @app.route('/loginHandle', methods=['POST'])
    def loginHandle():
       #如果session中学号和密码为空，说明是第一次登录，从表单中获取学号和密码

        if not session.get('user_identifier') and not session.get('user_password'):
            xuehao = request.form.get('xuehao')
            password = request.form.get('password')
        else: #如果session中学号和密码不为空，说明是已经登录过了，从session中获取学号和密码
            # 从session中获取用户信息
            xuehao = session.get('user_identifier')
            password = session.get('user_password')
            print(f"用户输入的密码为11：{password}")
        user = User.query.filter_by(identifier=xuehao).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            session['user_identifier'] = user.identifier
            session['user_password'] = password
            flash('登录成功！', 'success')
            print("登录成功！")
            if user.role=="student":
                # 获取学生名下的课程：把course_students表中学号和姓名能匹配上的所有记录中的课程id找出来
                course_students = Course_Students.query.filter_by(student_number=user.identifier, student_name=user.name).all()
                #将course_students表中自己的名字和学号对应的记录中的状态改为enrolled
                for course_student in course_students:
                    course_student.course_status = 'enrolled'
                    db.session.commit() # 提交事务
                courses = []
                for course_student in course_students:
                    course = Course.query.get(course_student.course_id)
                    courses.append(course)
                print(f"用户{user.name}正在查看自己的课程！")
                print(courses)
                return render_template('wang/student_profile.html', courses=courses)
            elif user.role=="teacher":
                # 获取教师名下的课程
                courses = Course.query.filter_by(teacher_id=user.id).all()

                return render_template('wang/teacher_profile.html', courses=courses)
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
    @app.route('/student_profile')
    def student_profile():
        return loginHandle()
    @app.route('/teacher_profile')
    def teacher_profile():
        # 获取教师名下的课程
        user_id = session.get('user_id')
        courses = Course.query.filter_by(teacher_id=user_id).all()
        print(f"用户{user_id}正在查看自己的课程！")
        print(courses)
        #把课程传到前端
        return render_template('wang/teacher_profile.html', courses=courses)
    # 创建新的课程
    @app.route('/create_course')
    def create_course():
        # 获取用户数据
        user_name = session.get('user_name')
        print(f"{user_name}正在创建新的课程！")
        return render_template('wang/create_course.html')
    # 处理创建课程的请求
    @app.route('/create_course_handle', methods=['POST'])
    def create_course_handle():
    # 获取课程数据
        course_name = request.form.get('course_name')
        semester = request.form.get('semester')
        course_description = request.form.get('course_description')
        code = request.form.get('course_code')
        teacher_id = session.get('user_id')
        # 创建课程
        course = Course(name=course_name, semester=semester, description=course_description, code=code, teacher_id=teacher_id)
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
                print(row)
                # 格式为：学号、姓名、拼音姓名、年级、专业、方向、行政班级、学籍状态、修课方式
                #将每条数据存储到数据库
                student_number = row[0]
                student_name = row[1]
                student_pinyin_name = row[2]
                student_grade = row[3]
                student_major = row[4]
                student_direction = row[5]
                student_class = row[6]
                student_status = row[7]
                student_course_method = row[8]
                course_student = Course_Students(course_id=course.id, student_number=student_number, student_name=student_name, student_pinyin_name=student_pinyin_name, student_grade=student_grade, student_major=student_major, student_direction=student_direction, student_class=student_class, student_status=student_status, student_course_method=student_course_method)
                students_to_add.append(course_student)
            db.session.add_all(students_to_add)
            db.session.commit()
            flash('学生名单导入成功！', 'success')
            #进入课程管理界面
            return redirect(url_for('course_manage', course_id=course.id))
        except error:
            flash('学生名单导入失败！', 'danger')
            return redirect(url_for('create_course'))
    # 课程管理
    @app.route('/course_manage/<int:course_id>')
    def course_manage(course_id):
        course = Course.query.get(course_id)
        # 查看课程下应该选课的学生
        course_students = course.course_students
        #print(f"查看课程{course.name}下的学生！")
        # In your view function
        enrolled_students_count = len(
            [student for student in course.course_students if student.course_status == 'enrolled'])
        for student in course_students:
            print(student.student_name)
        return render_template('wang/courseManager.html', course=course, course_students=course_students, enrolled_students_count=enrolled_students_count)


    # 列出我们还需要实现的的功能
    @app.route('/fuctions')
    def fuctions():
        return render_template('wang/fuctions.html')
    # 返回app
    return app


if __name__ == '__main__':
    app = create_app()  # 创建app
    app.run(host='0.0.0.0', port=5000, debug=True)
    # 0.0.0.0 表示监听所有可用的网络接口
    # host='0.0.0.0' 允许外部访问
    # port=5000 设置端口号
# 如果局域网无法访问用命令行打开：python -m flask run --host=0.0.0.0

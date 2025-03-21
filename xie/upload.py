import os

from flask import session, abort, request, redirect, flash
from flask import url_for
from flask.templating import render_template
from werkzeug.utils import secure_filename

from ITAS import app

# 在配置后添加目录自动创建
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def upload_page():
    # 获取已上传文件列表
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('xie/upload.html', files=files)


def upload_file():
    if 'user_id' not in session:
        abort(403)
    if 'file' not in request.files:
        flash('没有选择文件')
        return redirect(request.url)

    file = request.files['file']  # 获取文件对象

    if file.filename == '':
        flash('没有选择文件')
        return redirect(request.url)
    # 在原代码基础上增加扩展名验证
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 防止目录遍历
        if '..' in filename or '/' in filename:
            flash('非法文件名')
            return redirect(request.url)
        # 保存路径验证
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not save_path.startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
            flash('非法存储路径')
            return redirect(request.url)

        file.save(save_path)
        flash('文件上传成功')
        return redirect(url_for('upload_page'))


def delete_file(filename):
    if 'user_id' not in session:
        abort(403)

    safe_filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

    if not os.path.abspath(file_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
        abort(400)

    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'文件 {safe_filename} 已删除')
    else:
        flash('文件不存在')

    return redirect(url_for('upload_page'))

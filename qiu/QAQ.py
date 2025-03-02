from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

names_list = []

@app.route('/')
def index():
    return render_template('qiu/index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        global names_list
        try:
            names_list = pd.read_excel(file_path)['Name'].tolist()
            flash('File successfully uploaded and names loaded', 'success')
        except Exception as e:
            flash(f'Error loading names from file: {e}', 'danger')
        return redirect(url_for('index'))

@app.route('/random_name')
def random_name():
    if not names_list:
        flash('No names loaded', 'danger')
        return redirect(url_for('index'))
    selected_name = random.choice(names_list)
    return render_template('qiu/index.html', selected_name=selected_name)

if __name__ == '__main__':
    app.run(debug=True)
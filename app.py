import random
from flask import Flask, render_template_string,render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/random_student')
def random_student():
    with open('students.txt', 'r') as file:
        students = file.readlines()
    student = random.choice(students).strip()
    return render_template_string('<h1>Selected Student: {{ student }}</h1>', student=student)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
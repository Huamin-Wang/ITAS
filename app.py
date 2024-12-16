from flask import Flask, render_template
from flask_cors import CORS
from xxy.iqa import ask_question

app = Flask(__name__)
CORS(app)
#！！！！！！！！大家注意：这个页面只允许处理route的请求，其他无关代码请放到自己文件夹（包）进行调用！！！！！！！！！！
@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/iqa')
def iqa():
    return render_template('xxy/iqa.html')

@app.route('/ask', methods=['POST'])
def ask():
    return ask_question()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

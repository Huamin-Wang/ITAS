from flask import Flask, render_template

import xxy.chat as c

app = Flask(__name__)


# ！！！！！！！！大家注意：这个页面只允许处理route的请求，其他无关代码请放到自己文件夹（包）进行调用！！！！！！！！！！
@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/chat')
def chat():
    return render_template('xxy/chat.html', conversation=c.conversation_history)


@app.route('/chatHandle', methods=['POST'])
def chatHandle():
    response = c.chat()
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
# 如果局域网无法访问用命令行打开：python -m flask run --host=0.0.0.0


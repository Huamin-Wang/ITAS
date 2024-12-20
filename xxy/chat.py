# app.py
from flask import Flask, render_template, request, jsonify
import json
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import time
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket

app = Flask(__name__)

# 配置信息
appid = "af596305"
api_secret = "ZmNjM2Y5OGU3NTNmNTBiNThlZGE4YTZh"
api_key = "4ede90c6451ece9423169972af63f5a7"
domain = "4.0Ultra"
Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat"

# 保存对话历史
conversation_history = []


class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        url = self.Spark_url + '?' + urlencode(v)
        return url


class SparkAPIHandler:
    def __init__(self):
        self.answer = ""

    def on_message(self, ws, message):
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            self.answer += content
            if status == 2:
                ws.close()

    def on_error(self, ws, error):
        print("### error:", error)

    def on_close(self, ws, one, two):
        print("### closed ###")

    def on_open(self, ws):
        def run(*args):
            data = json.dumps(self.gen_params(ws.appid, ws.domain, ws.question))
            ws.send(data)

        thread.start_new_thread(run, ())

    def gen_params(self, appid, domain, question):
        data = {
            "header": {
                "app_id": appid,
                "uid": "1234"
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": 0.8,
                    "max_tokens": 2048,
                    "top_k": 5,
                    "auditing": "default"
                }
            },
            "payload": {
                "message": {
                    "text": [{
                        "type": "text",
                        "content": question,
                        "role": "user"  # Ensure the role field is included and set to a valid value
                    }]
                }
            }
        }
        return data


    def get_spark_response(self, question):
        self.answer = ""
        wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(
            wsUrl,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        ws.appid = appid
        ws.question = question
        ws.domain = domain
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return self.answer


spark_handler = SparkAPIHandler()


@app.route('/')
def home():
    return render_template('chat.html', conversation=conversation_history)



def chat():
    user_message = request.json.get('message', '')

    # 调用讯飞星火API
    ai_response = spark_handler.get_spark_response(user_message)

    # 保存对话历史
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": ai_response})

    # 保持对话历史在合理范围内
    while len(conversation_history) > 20:  # 保留最近的10轮对话
        conversation_history.pop(0)

    return jsonify({
        "response": ai_response
    })


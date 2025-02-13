# app.py
import logging
import subprocess
from ipaddress import ip_address

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
import threading
lock = threading.Lock()
app = Flask(__name__)

# 配置信息
appid = "39554b86"
api_secret = "NzIwZGRkZGIxN2Y3ZDU3MzgwZjY3ZGM5"
api_key = "ce8eb8ca38ffa7a3fde99f78d57980c4"
domain = "4.0Ultra"
Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat"



# 保存对话历史
conversation_history = {}


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

访问总人数 = 0

def chat():
    global 访问总人数
    user_message = request.json.get('message', '')

    ip_address=request.remote_addr #获取用户ip地址
    # 输出信息到终端
    print(f"IP为： {ip_address} 正在访问.")
    if ip_address not in conversation_history.keys():
        访问总人数 += 1
    # # 执行一个 Bash 命令并输出信息，如果用pycharm运行，需要把下面的subprocess.run()注释掉
    # subprocess.run(["echo", f"-----------------------------"])
    # subprocess.run(["echo", f"IP为： {ip_address} 正在访问，目前访问总人数为：{访问总人数}"])
    # subprocess.run(["echo", f"-----------------------------"])

    # 调用讯飞星火API
    ai_response = spark_handler.get_spark_response(user_message)

    # 设置内容格式:暂时统一按照code格式处理(学校的机房浏览器版本太低，chat.html已经自动处理为text格式)
    format_type = 'markdown'
    # 获取该IP地址的对话历史，默认为空列表
    def thread_run():
        lock.acquire()  # 加锁
        if ip_address not in conversation_history.keys():
            conversation_history[ip_address] = []
        # 保存对话历史，把IP地址也存储起来
        conversation_history[ip_address].append({"role": "user", "content": user_message, "ip_address": ip_address})
        conversation_history[ip_address].append(
            {"role": "assistant", "content": ai_response, "format": format_type, "ip_address": ip_address}
        )
        # 保持对话历史在合理范围内
        while len(conversation_history) > 20:  # 保留最近的10轮对话
            conversation_history.pop(0)
        lock.release()  # 释放锁
        # 用户访问后创建新的线程
    t=threading.Thread(target=thread_run)
    t.start()
    t.join()
    #print(f"ai_response: {ai_response}")
        # 返回该IP地址的对话历史
    return jsonify({
        "response": ai_response,
        "format": format_type,
        "conversation": conversation_history[ip_address]
    })




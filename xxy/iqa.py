import _thread as thread
import base64
import hashlib
import hmac
import json
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode, urlparse
from flask import request, jsonify
import websocket
from email.utils import formatdate as format_date_time  # 导入函数

# WebSocket参数类
class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # 创建WebSocket URL
    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        # 创建签名字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"
        # 生成HMAC-SHA256签名
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        # 创建授权头
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 创建带有查询参数的最终URL
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        url = self.gpt_url + '?' + urlencode(v)
        return url

# WebSocket错误处理函数
def on_error(ws, error):
    print("### error:", error)

# WebSocket关闭处理函数
def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

# WebSocket打开处理函数
def on_open(ws):
    thread.start_new_thread(run, (ws,))

# WebSocket运行函数
def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, query=ws.query, domain=ws.domain))
    ws.send(data)

# WebSocket消息处理函数
def on_message(ws, message):
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        print(content, end='')
        if status == 2:
            print("#### 关闭会话")
            ws.close()

# 生成请求参数
def gen_params(appid, query, domain):
    data = {
        "header": {
            "app_id": appid,
            "uid": "1234",
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 0.5,
                "max_tokens": 4096,
                "auditing": "default",
            }
        },
        "payload": {
            "message": {
                "text": [{"role": "user", "content": query}]
            }
        }
    }
    return data

# 处理问答请求
def ask_question():
    data = request.json  # 从请求中获取JSON数据
    appid = data['appid']  # 获取appid
    api_secret = data['api_secret']  # 获取API密钥
    api_key = data['api_key']  # 获取API密钥
    Spark_url = data['Spark_url']  # 获取Spark URL
    domain = data['domain']  # 获取领域
    query = data['query']  # 获取用户查询

    # 创建WebSocket参数对象
    wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
    wsUrl = wsParam.create_url()  # 生成WebSocket URL

    response_data = {"status": "success", "content": ""}  # 初始化响应数据

    # WebSocket消息处理函数
    def on_message(ws, message):
        data = json.loads(message)  # 解析消息
        code = data['header']['code']  # 获取响应代码
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()  # 关闭WebSocket连接
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            response_data["content"] += content  # 追加内容到响应数据
            if status == 2:
                print("#### 关闭会话")
                ws.close()  # 关闭WebSocket连接

    # WebSocket关闭处理函数
    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")
        global final_response_data
        final_response_data = response_data  # 设置最终响应数据

    # 创建WebSocket应用
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.query = query
    ws.domain = domain
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})  # 运行WebSocket，忽略SSL证书验证

    return jsonify(final_response_data)  # 返回JSON格式的最终响应数据
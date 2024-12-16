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
from email.utils import formatdate as format_date_time  # Import the function

class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

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
        url = self.gpt_url + '?' + urlencode(v)
        return url

def on_error(ws, error):
    print("### error:", error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    thread.start_new_thread(run, (ws,))

def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, query=ws.query, domain=ws.domain))
    ws.send(data)

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

def ask_question():
    data = request.json
    appid = data['appid']
    api_secret = data['api_secret']
    api_key = data['api_key']
    Spark_url = data['Spark_url']
    domain = data['domain']
    query = data['query']

    wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
    wsUrl = wsParam.create_url()

    response_data = {"status": "success", "content": ""}

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
            response_data["content"] += content
            if status == 2:
                print("#### 关闭会话")
                ws.close()

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")
        global final_response_data
        final_response_data = response_data

    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.query = query
    ws.domain = domain
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    return jsonify(final_response_data)
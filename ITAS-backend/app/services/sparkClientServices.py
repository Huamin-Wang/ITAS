# services/spark_client.py
import json
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import time
from urllib.parse import urlparse, urlencode
import ssl
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import websocket
import logging

logger = logging.getLogger(__name__)

class WsParam:
    """WebSocket 参数生成器"""
    def __init__(self, app_id, api_key, api_secret, spark_url):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host = urlparse(spark_url).netloc
        self.path = urlparse(spark_url).path
        self.spark_url = spark_url

    def create_url(self):
        """创建认证URL"""
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'), 
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature_sha_base64}"'
        )

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        return self.spark_url + '?' + urlencode(v)


class SparkClient:
    """讯飞星火 API 客户端"""
    
    def __init__(self, app_id, api_key, api_secret, spark_url, domain):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.spark_url = spark_url
        self.domain = domain
        self.answer = ""

    def on_message(self, ws, message):
        """WebSocket 消息处理"""
        try:
            data = json.loads(message)
            code = data['header']['code']
            if code != 0:
                logger.error(f'讯飞API请求错误: {code}, {data}')
                ws.close()
            else:
                choices = data["payload"]["choices"]
                status = choices["status"]
                content = choices["text"][0]["content"]
                self.answer += content
                if status == 2:
                    ws.close()
        except Exception as e:
            logger.error(f"处理讯飞API响应时出错: {e}")
            ws.close()

    def on_error(self, ws, error):
        """WebSocket 错误处理"""
        logger.error(f"讯飞WebSocket错误: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket 连接关闭"""
        logger.info("讯飞WebSocket连接关闭")

    def on_open(self, ws):
        """WebSocket 连接打开"""
        def run(*args):
            try:
                data = json.dumps(self._gen_request_params(ws.question))
                ws.send(data)
            except Exception as e:
                logger.error(f"发送请求时出错: {e}")

        thread.start_new_thread(run, ())

    def _gen_request_params(self, question):
        """生成请求参数"""
        return {
            "header": {
                "app_id": self.app_id,
                "uid": "1234"
            },
            "parameter": {
                "chat": {
                    "domain": self.domain,
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
                        "role": "user"
                    }]
                }
            }
        }

    def get_response(self, question):
        """获取AI回复"""
        self.answer = ""
        try:
            ws_param = WsParam(self.app_id, self.api_key, self.api_secret, self.spark_url)
            websocket.enableTrace(False)
            ws_url = ws_param.create_url()
            
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            ws.question = question
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            return self.answer
        except Exception as e:
            logger.error(f"调用讯飞API时出错: {e}")
            return "抱歉，AI服务暂时不可用，请稍后再试。"
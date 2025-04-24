import requests
from wang import config
url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={config.APP_ID}&secret={config.APP_SECRET}"
res = requests.get(url).json()
ACCESS_TOKEN = res.get("access_token")
def generate_qrcode(scene_value, page="pages/sign_in/index", width=280):
    """生成小程序二维码"""
    url = f"https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={ACCESS_TOKEN}"

    # 请求体
    payload = {
        "scene": scene_value,  # 传递的参数（例如 sign_id）
        "page": "pages/attendance/attendance",  # 小程序签到成功页面
        "width": width  # 二维码的尺寸
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        import os
        # Assuming the static folder is in the project root
        static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static')
        os.makedirs(static_dir, exist_ok=True)
        file_path = os.path.join(static_dir, f"qrcode_{scene_value}.png") # 写入到项目的static文件夹中
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"二维码生成成功: qrcode_signed.png")
    else:
        print("二维码生成失败:", response.text)


# 测试二维码生成
if __name__ == "__main__":
    generate_qrcode("sign_id=abc123")
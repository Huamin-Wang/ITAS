import requests

APP_ID = 'wx3dd32842e9e24690'
APP_SECRET = '09732f45784f51d2b9e5bad0902ec17a'
url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
res = requests.get(url).json()
ACCESS_TOKEN = res.get("access_token")


def generate_qrcode(scene_value, page="pages/sign_in/index", width=280):
    """生成小程序二维码"""
    url = f"https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={ACCESS_TOKEN}"

    # 请求体
    payload = {
        "scene": scene_value,  # 传递的参数（例如 sign_id）
        "page": "pages/forum/forum",  # 小程序页面
        "width": width  # 二维码的尺寸
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        with open(f"qrcode_{scene_value}.png", "wb") as f:
            f.write(response.content)
        print(f"二维码生成成功: qrcode_signed.png")
    else:
        print("二维码生成失败:", response.text)


# 测试二维码生成
if __name__ == "__main__":
    generate_qrcode("sign_id=abc123")
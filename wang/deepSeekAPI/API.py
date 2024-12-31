# 请先安装OpenAI SDK：`pip3 install openai`

from openai import OpenAI

def get_answer(question: str):
    # 请替换为您的API密钥
    # 使用您的API密钥和DeepSeek的API基础URL创建客户端
    client = OpenAI(api_key="sk-720be95e2f414916aac8bf36b1994e83", base_url="https://api.deepseek.com")

    try:
        # 创建聊天完成请求
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": question},
            ],
            stream=False
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        # 打印助手的响应
    return response.choices[0].message.content

# 测试
if __name__ == "__main__":
    question = "你是什麽大模型"
    answer = get_answer(question)
    print(answer)

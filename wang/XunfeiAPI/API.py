import SparkPythondemo


# 控制台会自动把问题和回答打印出来，可连续问答    參數：问题 返回：答案
def get_answer(question: str):
    return SparkPythondemo.intelligenceAPI(question)

# 测试
if __name__ == '__main__':
    question = "你是什麽大模型"
    answer = get_answer(question)
    print(answer)

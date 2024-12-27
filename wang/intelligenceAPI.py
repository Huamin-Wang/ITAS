import SparkPythondemo

# 控制台会自动把问题和回答打印出来，可连续问答
def 智能判定接口(问题):
    return SparkPythondemo.intelligenceAPI(问题)


if __name__ == '__main__':
    while (1):
        问题 = input()
        智能判定接口(问题)


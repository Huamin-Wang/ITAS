import intelligenceAPI as wang
题目="请您完成一个生成4个验证码数字（0-9）或字母（不区分大小写）的程序，用户根据验证码输入答案可以验证其准确性。20分"
学生答案='''num1 = input("请输入一个0-61的随机数，以产生验证码：")
num2 = input("请输入一个0-61的随机数，以产生验证码：")
num3 = input("请输入一个0-61的随机数，以产生验证码：")
num4 = input("请输入一个0-61的随机数，以产生验证码：")
# 将字符串转为数字
num1 = int(num1)
num2 = int(num2)
num3 = int(num3)
num4 = int(num4)
# 验证码存放库
zimu = "abcdefghijklmnopqrstuvwxyzQWERTYUIOPASDFGHJKLZXCVBNM0123456789"
code = zimu[num1] + zimu[num2] + zimu[num3] + zimu[num4]
print("验证码为：" + code)
input = input("请输入验证码：")
# 验证码如果是大写，统一转成小写
code = code.upper()
input = input.upper()
if code == input:
    print("验证通过")
print("END----------")'''
question ="请你根据下面的题目分值以及学生答案，给出得分,给分宽松些，能实现题目要求功能即可。回复格式为：分数|评语。题目:"+题目+"学生答案:"+学生答案
answer=wang.智能判定接口(question)

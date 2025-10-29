from openai import OpenAI
from typing import Any

from app.models.Result import Result

import json
import re

class AiServices:
    
    
    #调用ai接口
    @staticmethod
    def get_answer(question: str):
        try:
            client = OpenAI(
                base_url="https://ark.cn-beijing.volces.com/api/v3",
                api_key="e864c037-480f-4533-bb04-df290365997f",
            )
            completion = client.chat.completions.create(
                model="doubao-lite-4k-character-240828",
                messages=[
                    {"role": "system", "content": "你是教学小助手"},
                    {"role": "user", "content": question},
                ],
            )
            # print(f"回答：\n{completion.choices[0].message.content}")
            return completion.choices[0].message.content
        except Exception as e:
            print(f"大模型调用出错: {e}")
            return "抱歉，大模型调用出错，请稍后再试。"
        
    #作业评分
    @staticmethod
    def test_score(data: dict[str, Any]) -> Result:
        title = data.get('title')
        max_score = data.get('max_score')
        student_answer = data.get('student_answer')
        if student_answer == "":
            student_answer = "空"
        question = f'''
        你是一位阅卷老师，请根据以下题目和学生的答案进行评分。评分标准如下：
        1. 如果是代码，程序能够正常运行，即使存在小问题也可以给满分。
        2. 小缺陷或细节问题给出改进建议即可。
        3. **评分不得超过题目所列的总分值，任何情况下都不能溢出。**
    
        请严格遵循以下格式回复：
        分数（数字）|评语（例如：`10|还存在几个问题,具体如下...`）。
        注意：分数必须小于或等于总分值。
    
        题目: {title}
        总分值: {max_score}
        学生答案: {student_answer}
        '''
    
        answer = AiServices.get_answer(question)
        score = answer.split("|")[0]
        comment = answer.split("|")[1]
        data = {
            'score':score,
            'comment':comment,
            'answer':answer
        }
        return Result.success(data)
    
    #作业标签生成
    @staticmethod
    def generate_tags(data: dict[str, Any]) -> Result:
        title = data.get('title')
        question = f'''
        请扮演一位经验丰富的教育专家，为给定的作业题目生成一套结构化、多维度的标签体系，以辅助题目管理和学习分析。

        作业题目: {title}

        生成要求与维度：
        1. 内容主题：指出题目所属的宏观学科领域和具体主题。
        2. 核心知识点：提炼题目考察的2-4个具体知识点或概念。
        3. 题目类型：标明题目的形式（例如：选择题，计算题，论述题，实验设计题，阅读理解）。

        输出格式：
        请严格按照以下JSON格式输出，不要有任何其他解释。
        {{
            "title": "[作业题目原文]",
            "tags": {{
                "theme": ["标签1", "标签2", ...],
                "core_points": ["标签1", "标签2", ...],
                "category": ["标签1"]
            }}
        }}
        '''
        answer = AiServices.get_answer(question)
        json_match = re.search(r'\{.*\}', answer, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            result = json.loads(json_str)
        return Result.success(result)
   
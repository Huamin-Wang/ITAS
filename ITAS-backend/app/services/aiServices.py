from openai import OpenAI
from typing import Any, List

from app.models.Result import Result

import json
import re

class AiServices:
    
    # 调用ai接口
    @staticmethod
    def get_answer(question: str):
        try:
            client = OpenAI(
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key="sk-c558e163455d47aea80d32afbca39fd2",
            )
            completion = client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "你是教学小助手"},
                    {"role": "user", "content": question},
                ],
            )
            print(f"回答：\n{completion.choices[0].message.content}")
            return completion.choices[0].message.content
        except Exception as e:
            print(f"大模型调用出错: {e}")
            return None
    
    # 批量作业评分
    @staticmethod
    def batch_score_assignments(data: dict[str, Any]) -> Result:
        """
        批量作业评分，支持多个作业
        输入参数格式:
        {
            "assignments_list": [
                {
                    "id": "",
                    "title": "",
                    "description": "",
                    "total_score": "",
                    "student_answer": "",
                    "reference_answer": ""  # 可能为空
                },
                ...
            ]
        }
        """
        assignments_list = data.get('assignments_list', [])
        if not assignments_list:
            return Result.error("作业列表为空")
        
        results = []
        for assignment in assignments_list:
            assignment_id = assignment.get('id', '')
            quiz_id = assignment.get('quiz_id', '')
            question_id = assignment.get('question_id', '')
            title = assignment.get('title', '')
            description = assignment.get('description', '')
            student_answer = assignment.get('student_answer', '')
            reference_answer = assignment.get('reference_answer', '')
            total_score = assignment.get('total_score')
            if student_answer == "":
                student_answer = "空"
            
            # 构建评分提示词
            question = f'''
            你是一位阅卷老师，请根据以下题目和学生的答案进行评分。评分标准如下：
            1. 总分值：根据题目难度和参考答案，给出合理总分值
            2. 评分原则：
               - 如果是代码，程序逻辑正确、能够正常运行，可以给高分
               - 如果答案基本正确但有细节问题，适当扣分并给出改进建议
               - 如果答案错误，给出详细解析
               - 如果只有思路或关键词，酌情给分
            3. 如果有参考答案，请参照参考答案评分
            
            请严格遵循以下格式回复：
            总分值（数字）|实际得分（数字）|评语（例如：`10|8|答案基本正确，但在...方面可以改进`）
            
            题目: {title}
            题目描述: {description}
            题目总分: {total_score}
            学生答案: {student_answer}
            {'参考答案: ' + reference_answer if reference_answer else '无参考答案'}
            '''
            
            answer = AiServices.get_answer(question)
            if answer:
                try:
                    # 解析评分结果
                    parts = answer.split("|")
                    if len(parts) >= 3:
                        total_score = parts[0].strip()
                        score = parts[1].strip()
                        comment = parts[2].strip()
                        
                        # 验证分数是否为数字
                        if not total_score.isdigit():
                            total_score = "5"  # 默认总分
                        if not score.isdigit():
                            score = "0"  # 默认得分
                    else:
                        total_score = "5"
                        score = "0"
                        comment = "评分格式错误"
                except Exception as e:
                    print(f"解析评分结果出错: {e}")
                    total_score = "5"
                    score = "0"
                    comment = "评分解析错误"
            else:
                total_score = "5"
                score = "0"
                comment = "评分失败"
            
            results.append({
                'assignment_id': assignment_id,
                'quiz_id': quiz_id,
                'question_id': question_id,
                'title': title,
                'total_score': total_score,
                'score': score,
                'comment': comment,
                'suggestion': f"建议：{comment}"
            })
        
        return Result.success({'results': results})
    
    # 单个作业评分（兼容旧版本）
    @staticmethod
    def test_score(data: dict[str, Any]) -> Result:
        """
        单个作业评分（保持向后兼容）
        输入参数格式:
        {
            "title": "作业题目",
            "max_score": "总分值",
            "student_answer": "学生答案"
        }
        """
        title = data.get('title')
        max_score = data.get('max_score', '10')
        student_answer = data.get('student_answer')
        
        if student_answer == "":
            student_answer = "空"
        
        question = f'''
        你是一位阅卷老师，请根据以下题目和学生的答案进行评分。评分标准如下：
        1. 如果是代码，程序能够正常运行，即使存在小问题也可以给高分。
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
        if answer:
            parts = answer.split("|")
            if len(parts) >= 2:
                score = parts[0].strip()
                comment = parts[1].strip()
            else:
                score = "0"
                comment = "评分格式错误"
        else:
            score = "0"
            comment = "评分失败"
        
        data = {
            'score': score,
            'comment': comment,
            'total_score': max_score,
            'suggestion': f"建议：{comment}"
        }
        return Result.success(data)
    
    # 习题生成功能（根据错题生成新习题）
    @staticmethod
    def generate_exercises(data: dict[str, Any]) -> Result:
        """
        根据学生的错题生成新的习题
        输入参数格式:
        {
            "wrong_questions": [
                {
                    "id": "",
                    "title": "",
                    "description": "",
                    "score": {
                        "total_score": "",
                        "score": ""
                    },
                    "suggestion": ""
                },
                ...
            ]
        }
        """
        wrong_questions = data.get('wrong_questions', [])
        if not wrong_questions:
            return Result.error("错题列表为空")
        
        # 收集所有错题信息
        topics = []
        for question in wrong_questions:
            title = question.get('title', '')
            description = question.get('description', '')
            suggestion = question.get('suggestion', '')
            score_info = question.get('score', {})
            student_score = score_info.get('score', '0')
            total_score = score_info.get('total_score', '10')
            
            topics.append({
                'title': title,
                'description': description,
                'student_score': student_score,
                'total_score': total_score,
                'suggestion': suggestion
            })
        
        # 构建生成习题的提示词
        question = f'''
        你是一位经验丰富的老师，请根据学生的错题信息，生成5道新的习题，帮助学生巩固薄弱知识点。
        
        学生错题信息如下：
        {json.dumps(topics, ensure_ascii=False, indent=2)}
        
        生成要求：
        1. 针对学生错误的知识点设计新题
        2. 题目难度适中，符合学生当前水平
        3. 题型可以多样化（选择题、填空题、简答题等）
        4. 每道题需要提供参考答案和解析
        
        输出格式（请严格按照以下JSON格式输出）：
        {{
            "exercises": [
                {{
                    "title": "题目1",
                    "type": "题型（如：选择题、填空题等）",
                    "content": "题目内容",
                    "difficulty": "难度级别（简单/中等/困难）",
                    "answer": "参考答案",
                    "analysis": "题目解析",
                    "related_knowledge": ["相关知识点1", "相关知识点2"]
                }},
                ...
            ],
            "summary": "总体建议和说明"
        }}
        '''
        
        try:
            answer = AiServices.get_answer(question)
            if answer:
                json_match = re.search(r'\{.*\}', answer, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    result_data = json.loads(json_str)
                    return Result.success(result_data)
                else:
                    # 如果没有匹配到JSON，返回默认结构
                    default_result = {
                        "exercises": [],
                        "summary": "未能生成习题，请重试"
                    }
                    return Result.success(default_result)
            else:
                return Result.error("生成习题失败")
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            default_result = {
                "exercises": [],
                "summary": f"生成习题时发生解析错误: {str(e)}"
            }
            return Result.success(default_result)
        except Exception as e:
            print(f"生成习题过程中发生错误: {e}")
            return Result.internal_error(f"生成习题失败: {str(e)}")
    
    # 作业标签生成
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
        try:
            answer = AiServices.get_answer(question)
            json_match = re.search(r'\{.*\}', answer, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result_data = json.loads(json_str)
                return Result.success(result_data)
            else:
                # 如果没有匹配到JSON，返回默认结构或错误信息
                default_result = {
                    "title": title,
                    "tags": {
                        "theme": [],
                        "core_points": [],  
                        "category": []
                    }
                }
                return Result.success(default_result)
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            # JSON解析失败时返回默认结构
            default_result = {
                "title": title,
                "tags": {
                    "theme": [],
                    "core_points": [],
                    "category": []
                }
            }
            return Result.success(default_result)
        except Exception as e:
            print(f"生成标签过程中发生错误: {e}")
            return Result.internal_error(f"生成标签失败: {str(e)}")
        

    # 学生知识掌握情况分析
    @staticmethod
    def analyze_student_knowledge(data: dict[str, Any]) -> Result:
        """
        根据学生的错题分析知识掌握情况和薄弱点
        输入参数格式:
        {
            "wrong_questions": [
                {
                    "id": "",
                    "title": "",
                    "description": "",
                    "score": {
                        "total_score": "",
                        "score": ""
                    },
                    "suggestion": ""
                },
                ...
            ]
        }
        """
        wrong_questions = data.get('wrong_questions', [])
        if not wrong_questions:
            return Result.error("错题列表为空")
        
        # 收集所有错题信息
        topics = []
        total_questions = len(wrong_questions)
        total_score_sum = 0
        student_score_sum = 0
        
        for question in wrong_questions:
            title = question.get('title', '')
            description = question.get('description', '')
            suggestion = question.get('suggestion', '')
            score_info = question.get('score', {})
            student_score = float(score_info.get('score', '0'))
            total_score = float(score_info.get('total_score', '10'))
            
            # 计算得分率
            score_rate = student_score / total_score if total_score > 0 else 0
            
            topics.append({
                'title': title,
                'description': description,
                'student_score': student_score,
                'total_score': total_score,
                'score_rate': score_rate,
                'suggestion': suggestion
            })
            
            total_score_sum += total_score
            student_score_sum += student_score
        
        # 计算整体平均得分率
        overall_score_rate = student_score_sum / total_score_sum if total_score_sum > 0 else 0
        
        # 构建分析提示词
        question = f'''
        你是一位经验丰富的教学分析师，请根据学生的错题信息，全面分析学生的知识掌握情况和薄弱点。
        
        学生错题信息如下（共{total_questions}题）：
        {json.dumps(topics, ensure_ascii=False, indent=2)}
        
        整体表现：
        - 题目总数：{total_questions}
        - 总分值：{total_score_sum}
        - 学生得分：{student_score_sum}
        - 平均得分率：{overall_score_rate:.2%}
        
        请进行深入分析，包括但不限于以下方面：
        1. **知识掌握总体评估**：对学生的整体学习情况进行评价
        2. **知识点分布分析**：识别题目涉及的主要知识点领域
        3. **薄弱环节识别**：找出学生最需要加强的知识点
        4. **错误类型分析**：分析学生错误的常见类型（概念理解、计算、应用等）
        5. **学习建议**：针对性地提出改进建议和学习计划
        
        输出格式（请严格按照以下JSON格式输出）：
        {{
            "overview": {{
                "total_questions": {total_questions},
                "total_score": {total_score_sum},
                "student_score": {student_score_sum},
                "average_score_rate": {overall_score_rate:.2%},
                "overall_assessment": "对学生整体学习情况的简短评价"
            }},
            "knowledge_analysis": [
                {{
                    "knowledge_area": "知识点领域名称",
                    "question_count": 该领域的题目数量,
                    "average_score_rate": "该领域的平均得分率",
                    "mastery_level": "掌握程度（优秀/良好/一般/薄弱）",
                    "common_issues": ["常见问题1", "常见问题2"]
                }},
                ...
            ],
            "weak_points": [
                {{
                    "knowledge_point": "薄弱知识点名称",
                    "severity": "薄弱程度（严重/中等/轻微）",
                    "related_questions": ["相关题目ID或标题"],
                    "suggestion": "针对该薄弱点的具体建议"
                }},
                ...
            ],
            "error_patterns": [
                {{
                    "pattern_type": "错误模式类型",
                    "description": "错误模式描述",
                    "frequency": "出现频率",
                    "example": "示例题目"
                }},
                ...
            ],
            "learning_plan": {{
                "short_term": ["短期建议1", "短期建议2"],
                "long_term": ["长期建议1", "长期建议2"],
                "priority_topics": ["优先学习主题1", "优先学习主题2"],
                "recommended_resources": ["推荐资源1", "推荐资源2"]
            }},
            "summary": "分析总结和总体建议"
        }}
        '''
        
        try:
            answer = AiServices.get_answer(question)
            if answer:
                json_match = re.search(r'\{.*\}', answer, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    result_data = json.loads(json_str)
                    
                    # 添加一些统计分析
                    result_data["statistics"] = {
                        "weak_point_count": len(result_data.get("weak_points", [])),
                        "knowledge_areas_count": len(result_data.get("knowledge_analysis", [])),
                        "error_patterns_count": len(result_data.get("error_patterns", [])),
                        "priority_levels": {
                            "high": len([w for w in result_data.get("weak_points", []) if w.get("severity") == "严重"]),
                            "medium": len([w for w in result_data.get("weak_points", []) if w.get("severity") == "中等"]),
                            "low": len([w for w in result_data.get("weak_points", []) if w.get("severity") == "轻微"])
                        }
                    }
                    
                    return Result.success(result_data)
                else:
                    # 如果没有匹配到JSON，返回默认分析结构
                    default_result = {
                        "overview": {
                            "total_questions": total_questions,
                            "total_score": total_score_sum,
                            "student_score": student_score_sum,
                            "average_score_rate": f"{overall_score_rate:.2%}",
                            "overall_assessment": "数据不足，无法进行全面分析"
                        },
                        "knowledge_analysis": [],
                        "weak_points": [],
                        "error_patterns": [],
                        "learning_plan": {
                            "short_term": ["请收集更多错题信息以获得准确分析"],
                            "long_term": ["定期复习巩固基础知识"],
                            "priority_topics": ["暂无"],
                            "recommended_resources": []
                        },
                        "summary": "需要更多数据来生成准确的分析报告"
                    }
                    return Result.success(default_result)
            else:
                return Result.error("分析学生知识掌握情况失败")
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            default_result = {
                "overview": {
                    "total_questions": total_questions,
                    "total_score": total_score_sum,
                    "student_score": student_score_sum,
                    "average_score_rate": f"{overall_score_rate:.2%}",
                    "overall_assessment": f"分析时发生解析错误: {str(e)}"
                },
                "knowledge_analysis": [],
                "weak_points": [],
                "error_patterns": [],
                "learning_plan": {
                    "short_term": ["请重试分析功能"],
                    "long_term": ["持续学习，定期检查"],
                    "priority_topics": ["基础概念"],
                    "recommended_resources": []
                },
                "summary": f"生成分析报告时发生错误: {str(e)}"
            }
            return Result.success(default_result)
        except Exception as e:
            print(f"分析学生知识过程中发生错误: {e}")
            return Result.internal_error(f"分析学生知识掌握情况失败: {str(e)}")
   
from openai import OpenAI
from typing import Any, List
from app.services.courseStudentServices import CourseStudentService
from app.models.course_students import Course_Students
from app.models.course import Course
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
            exercise_id = assignment.get('exercise_id','')
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
                'exercise_id':exercise_id,
                'question_id': question_id,
                'title': title,
                'total_score': total_score,
                'score': score,
                'comment': comment,
                'suggestion': f"建议：{comment}",
                'reference_answer': reference_answer
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
        teacher_id = data.get("teacher_id")
        course_id = data.get("course_id")

        if not teacher_id or not course_id:
            return Result.bad_request("缺少必要参数: teacher_id, course_id")

        params = {
            'student_number' : data.get('student_number'),
            'course_id' : data.get('course_id')
        }

        wrong_questions = CourseStudentService.get_student_wrong_questions_for_analysis(params)
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
        你是一位经验丰富的老师，请根据学生的错题信息，生成一份新的“练习题集”，用于巩固学生的薄弱知识点。
        
        学生错题信息如下：
        {json.dumps(topics, ensure_ascii=False, indent=2)}
        
        生成要求（必须严格遵守）：
        1. 生成 1 份练习题集（exercise）
        2. 练习题集下包含 5 道题目（questions）
        3. 每一道题目 **必须且只能选择以下四种题型之一**：
           - single_choice（单选题）
           - multiple_choice（多选题）
           - true_false（判断题）
           - short_answer（简答题）
        4. 不允许出现除上述四种以外的题型
        5. 每道题只能属于一种题型，不得混合
        6. 所有题目必须围绕学生的错误知识点
        7. 每道题必须给出正确答案
        8. 只有 single_choice 和 multiple_choice 题型可以有 options
        9. true_false 和 short_answer 题型的 options 必须为 null
        10. 每道题必须设置合理的分值（points，整数）
        
        请严格按照以下 JSON 格式输出，不要输出任何多余文本：
        
        {{
          "exercise": {{
            "title": "练习题集标题",
            "description": "本练习题集针对学生薄弱知识点的说明",
            "status": "draft"
          }},
          "questions": [
            {{
              "question_text": "题目内容",
              "question_type": "single_choice | multiple_choice | true_false | short_answer",
              "options": {{
                "A": "选项A",
                "B": "选项B",
                "C": "选项C",
                "D": "选项D"
              }},
              "correct_answer": "正确答案",
              "points": 10
            }}
          ]
        }}
        '''
     
        try:
            answer = AiServices.get_answer(question)
            if answer:
                json_match = re.search(r'\{.*\}', answer, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    result_data = json.loads(json_str)
                    exercise_id = CourseStudentService.save_generated_exercise(
                                    result_data=result_data,
                                    teacher_id=teacher_id,
                                    course_id=course_id,
                                    student_number = data.get('student_number')
                    )
                    return Result.success({"exercise_id": exercise_id})
                else:
                    # 如果没有匹配到JSON，返回默认结构
                    default_result = {
                        "summary": "未能生成习题，请重试"
                    }
                    return Result.success({"exercise_id": None,"summary": "未能生成习题，请重试"})
            else:
                return Result.error("生成习题失败")
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            default_result = {
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
    
    #错题分析(学生端)
    @staticmethod
    def analyze_student_knowledge_s(data: dict[str, Any]) -> Result:
        """
        调用AI错题分析服务（学生视角）
        输入参数格式:
        {
            "student_number": "学生学号",
            "course_id": "课程ID"
        }
        """
        student_number = data.get('student_number')
        course_id = data.get('course_id')
        
        if not student_number or not course_id:
            return Result.bad_request('缺少必要参数: student_number, course_id')
        
        # 查询学生姓名
        student_name = ""
        course_name = ""
        try:
            # 通过学号和课程ID在course_student中查询学生信息
            course_student = Course_Students.query.filter_by(
                student_number=student_number,
                course_id=course_id
            ).first()
            if course_student and hasattr(course_student, 'student_name'):
                student_name = course_student.student_name
            course = Course.query.get(course_id)
            if course:
                course_name = course.name
        except Exception as e:
            print(f"查询学生信息出错: {e}")
            # 查询出错不影响后续分析，继续执行
        
        # 使用拆分的方法获取错题数据
        wrong_questions = CourseStudentService.get_student_wrong_questions_for_analysis(data)
        
        if not wrong_questions:
            return Result.success({
                "student_number": student_number,
                "student_name": student_name,
                "course_name": course_name,
                "summary": "你目前没有错题记录，继续保持良好的学习状态！",
                "quick_stats": {
                    "wrong_question_count": 0,
                    "learning_status": "excellent",
                    "progress_level": "优秀"
                },
                "self_recommendations": [
                    "继续保持当前学习节奏",
                    "可以尝试一些拓展性练习挑战自己",
                    "定期复习已掌握知识点"
                ],
                "encouragement": "你的学习状态非常好，继续保持！"
            })
        
        # 基础统计计算
        total_questions = len(wrong_questions)
        
        # 计算得分率
        total_scores = []
        student_scores = []
        question_texts = []  # 收集题目和描述用于AI分析
        
        for question in wrong_questions:
            title = question.get('title', '')
            description = question.get('description', '')
            score_info = question.get('score', {})
            
            # 收集题目文本用于AI分析
            if title or description:
                question_texts.append(f"题目：{title}，描述：{description[:100]}")
            
            try:
                total_score = float(score_info.get('total_score', '10'))
                student_score = float(score_info.get('score', '0'))
                total_scores.append(total_score)
                student_scores.append(student_score)
            except:
                continue
            
        if total_scores:
            avg_score_rate = sum(student_scores) / sum(total_scores) if sum(total_scores) > 0 else 0
            avg_score_rate_percent = f"{avg_score_rate:.1%}"
        else:
            avg_score_rate_percent = "0%"
        
        # 根据得分率评估学习状态
        if avg_score_rate >= 0.8:
            learning_status = "good"
            progress_level = "优秀"
            encouragement = "做得很好！继续保持！"
        elif avg_score_rate >= 0.6:
            learning_status = "average"
            progress_level = "良好"
            encouragement = "有进步空间，继续加油！"
        else:
            learning_status = "needs_improvement"
            progress_level = "需加强"
            encouragement = "别灰心，发现问题就是进步的开始！"
        
        # 构建针对学生的AI分析提示
        question_text_sample = "\n".join(question_texts)
        question = f'''
        你是一位亲切的学习导师，请根据学生的错题信息，为学生提供个性化的学习分析和鼓励。
        
        学生错题概况：
        - 错题数量：{total_questions}题
        - 平均得分率：{avg_score_rate_percent}
        - 学生姓名：{student_name}
        - 课程：{course_name}
        
        错题内容：
        {question_text_sample}
        
        请用亲切、鼓励的语气（不超过150字）回答以下问题：
        1. 这位同学当前学习的主要优势和不足是什么？
        2. 建议重点提升哪些方面？
        3. 有什么具体的学习建议和方法？
        
        输出格式要求：
        请用以下格式直接回答，不要添加任何其他内容：
        [学习情况分析]|[需要提升的方面]|[学习建议和方法]
        
        示例：
        你对基础概念掌握得不错，但在应用题理解和解题步骤方面需要加强|应用题型分析、解题规范性、知识点综合运用|1.每天练习2道应用题型 2.整理错题本记录易错点 3.尝试用不同方法解同一道题
        
        注意：要用第二人称"你"来称呼学生，语气要亲切、鼓励，不要使用批评性语言。
        '''
        
        # 获取AI分析结果
        try:
            answer = AiServices.get_answer(question)
            if answer:
                # 解析AI返回的结果
                parts = answer.split("|")
                if len(parts) >= 3:
                    learning_analysis = parts[0].strip()
                    improvement_areas = parts[1].strip()
                    learning_suggestions = parts[2].strip()
                else:
                    # 如果格式不符合，使用默认值
                    learning_analysis = f"你的基础知识掌握情况一般，得分率{avg_score_rate_percent}"
                    improvement_areas = "核心概念理解和解题方法"
                    learning_suggestions = "建议加强基础练习，整理错题本"
            else:
                learning_analysis = f"你的基础知识掌握情况一般，得分率{avg_score_rate_percent}"
                improvement_areas = "核心概念理解和解题方法"
                learning_suggestions = "建议加强基础练习，整理错题本"
        except Exception as e:
            print(f"AI分析出错: {e}")
            learning_analysis = f"你完成了{total_questions}题，得分率{avg_score_rate_percent}"
            improvement_areas = "基础知识点掌握"
            learning_suggestions = "建议加强薄弱环节的练习"
        
        # 根据学习状态生成个性化鼓励语
        if learning_status == "good":
            personalized_encouragement = f"太棒了{student_name}同学！你的学习状态很好，继续保持这个势头！"
        elif learning_status == "average":
            personalized_encouragement = f"{student_name}同学，你有很好的学习基础，再努力一下会有更大进步！"
        else:
            personalized_encouragement = f"{student_name}同学，学习路上遇到困难是正常的，坚持下去就是胜利！"
        
        # 构建针对学生的返回结果
        result_data = {
            # 学生基本信息
            "student_number": student_number,
            "student_name": student_name,
            "course_name": course_name,
            
            # 学习状态概览
            "learning_overview": {
                "wrong_question_count": total_questions,
                "average_score_rate": avg_score_rate_percent,
                "learning_status": learning_status,
                "progress_level": progress_level,
                "encouragement": personalized_encouragement
            },
            
            # AI学习分析
            "learning_analysis": {
                "analysis_summary": learning_analysis,
                "improvement_areas": improvement_areas,
                "learning_suggestions": learning_suggestions
            },
            
            # 学习数据详情
            "learning_data": {
                "score_distribution": {
                    "low_score": len([i for i in range(len(student_scores)) 
                                          if total_scores[i] > 0 and student_scores[i]/total_scores[i] < 0.4]),
                    "medium_score": len([i for i in range(len(student_scores)) 
                                         if total_scores[i] > 0 and 0.4 <= student_scores[i]/total_scores[i] <= 0.7]),
                    "high_score": len([i for i in range(len(student_scores)) 
                                       if total_scores[i] > 0 and student_scores[i]/total_scores[i] > 0.7])
                },
                "performance_summary": f"共完成{len(total_scores)}题，总分{sum(total_scores)}，得分{sum(student_scores)}"
            },
            
            # 错题列表
            "wrong_questions": wrong_questions,
            
            # 个性化学习建议
            "self_recommendations": [
                f"重点提升{improvement_areas.split('、')[0] if '、' in improvement_areas else improvement_areas.split('，')[0] if '，' in improvement_areas else improvement_areas}",
                learning_suggestions,
                "每天花15分钟复习错题",
                "遇到难题及时向老师或同学请教"
            ],
            
            # 学习鼓励和激励
            "motivation": {
                "encouragement": encouragement,
                "tip_of_the_day": "每天进步一点点，坚持带来大改变！",
                "next_goal": f"目标：将得分率提升到{(avg_score_rate + 0.1):.1%}"
            }
        }
        
        # 添加一个简要的总结文本
        result_data["summary"] = f"{student_name}同学，你有{total_questions}道错题需要关注，当前得分率{avg_score_rate_percent}。{learning_analysis}"
        
        return Result.success(result_data)

    #错题分析(教师端)
    @staticmethod
    def analyze_student_knowledge(data: dict[str, Any]) -> Result:
        """
        调用AI错题分析服务
        输入参数格式:
        {
            "student_number": "学生学号",
            "course_id": "课程ID"
        }
        """
        student_number = data.get('student_number')
        course_id = data.get('course_id')
        
        if not student_number or not course_id:
            return Result.bad_request('缺少必要参数: student_number, course_id')
        
        # 查询学生姓名
        student_name = ""
        try:
            # 通过学号和课程ID在course_student中查询学生信息
            course_student = Course_Students.query.filter_by(
                student_number=student_number,
                course_id=course_id
            ).first()
            if course_student and hasattr(course_student, 'student_name'):
                student_name = course_student.student_name
            course = Course.query.get(course_id)
            if course:
                course_name = course.name
        except Exception as e:
            print(f"查询学生姓名出错: {e}")
            # 查询出错不影响后续分析，继续执行
        
        # 1. 获取学生错题数据
        wrong_questions = CourseStudentService.get_student_wrong_questions_for_analysis(data)
        if not wrong_questions:
            return Result.success({
                "student_number": student_number,
                "student_name": student_name,
                "course_name": course_name,
                "summary": "该学生暂无错题记录，学习情况良好。",
                "quick_stats": {
                    "wrong_question_count": 0,
                    "learning_status": "excellent"
                },
                "teacher_recommendations": [
                    "继续保持当前学习状态",
                    "可适当增加拓展性练习"
                ]
            })
        
        # 基础统计计算
        total_questions = len(wrong_questions)
        
        # 计算得分率
        total_scores = []
        student_scores = []
        question_texts = []  # 收集题目和描述用于AI分析
        
        for question in wrong_questions:
            title = question.get('title', '')
            description = question.get('description', '')
            score_info = question.get('score', {})
            
            # 收集题目文本用于AI分析
            if title or description:
                question_texts.append(f"题目：{title}，描述：{description[:100]}")
            
            try:
                total_score = float(score_info.get('total_score', '10'))
                student_score = float(score_info.get('score', '0'))
                total_scores.append(total_score)
                student_scores.append(student_score)
            except:
                continue
        
        if total_scores:
            avg_score_rate = sum(student_scores) / sum(total_scores) if sum(total_scores) > 0 else 0
            avg_score_rate_percent = f"{avg_score_rate:.1%}"
        else:
            avg_score_rate_percent = "0%"
        
        # 根据得分率评估学习状态
        if avg_score_rate >= 0.75:
            learning_status = "good"
        elif avg_score_rate >= 0.6:
            learning_status = "average"
        else:
            learning_status = "needs_improvement"
        
        # 构建简洁的AI分析提示
        question_text_sample = "\n".join(question_texts)
        question = f'''
        你是一位经验丰富的教师，请根据学生的错题信息，为老师提供简洁明了的学生学习情况分析。
        
        学生错题概况：
        - 错题数量：{total_questions}题
        - 平均得分率：{avg_score_rate_percent}
        
        错题内容：
        {question_text_sample}
        
        请用简洁的语言（不超过150字）回答以下问题：
        1. 该学生当前主要存在哪些学习问题？
        2. 需要重点关注哪些方面？
        3. 给老师的教学建议是什么？
        
        输出格式要求：
        请用以下格式直接回答，不要添加任何其他内容：
        [学习问题总结]|[需要关注的方面]|[教学建议]
        
        示例：
        学生对函数概念理解不深，解题步骤不完整|函数定义、参数传递、解题规范性|加强函数基础讲解，设计分步解题练习
        '''
        
        # 获取AI分析结果
        try:
            answer = AiServices.get_answer(question)
            if answer:
                # 解析AI返回的结果
                parts = answer.split("|")
                if len(parts) >= 3:
                    problem_summary = parts[0].strip()
                    focus_areas = parts[1].strip()
                    teaching_suggestions = parts[2].strip()
                else:
                    # 如果格式不符合，使用默认值
                    problem_summary = f"基础知识掌握一般，得分率{avg_score_rate_percent}"
                    focus_areas = "核心概念和解题方法"
                    teaching_suggestions = "加强基础讲解，设计针对性练习"
            else:
                problem_summary = f"基础知识掌握一般，得分率{avg_score_rate_percent}"
                focus_areas = "核心概念和解题方法"
                teaching_suggestions = "加强基础讲解，设计针对性练习"
        except Exception as e:
            print(f"AI分析出错: {e}")
            problem_summary = f"完成{total_questions}题，得分率{avg_score_rate_percent}"
            focus_areas = "基础知识点"
            teaching_suggestions = "加强薄弱环节练习"
        
        # 构建返回结果
        result_data = {
            # 学生基本信息
            "student_number": student_number,
            "student_name": student_name,
            "course_name": course_name,
            # 快速概览
            "quick_stats": {
                "wrong_question_count": total_questions,
                "average_score_rate": avg_score_rate_percent,
                "learning_status": learning_status
            },
            
            # AI分析的核心结果
            "analysis": {
                "learning_problems": problem_summary,
                "focus_areas": focus_areas,
                "teaching_suggestions": teaching_suggestions
            },
            
            # 详细数据
            "details": {
                "score_distribution": {
                    "low_score": len([i for i in range(len(student_scores)) 
                                          if total_scores[i] > 0 and student_scores[i]/total_scores[i] < 0.4]),
                    "medium_score": len([i for i in range(len(student_scores)) 
                                         if total_scores[i] > 0 and 0.4 <= student_scores[i]/total_scores[i] <= 0.7]),
                    "high_score": len([i for i in range(len(student_scores)) 
                                       if total_scores[i] > 0 and student_scores[i]/total_scores[i] > 0.7])
                },
                "overall_performance": f"共完成{len(total_scores)}题，总分{sum(total_scores)}，得分{sum(student_scores)}"
            },
            "wrong_questions":wrong_questions,
            # 给老师的直接建议
            "teacher_recommendations": [
                f"关注{focus_areas.split('、')[0] if '、' in focus_areas else focus_areas.split('，')[0] if '，' in focus_areas else focus_areas}的教学",
                teaching_suggestions,
                "定期检查学习进展，及时调整教学策略"
            ]
        }
        
        # 添加一个简要的总结文本
        result_data["summary"] = f"学生{student_name}有{total_questions}道错题，平均得分率{avg_score_rate_percent}。主要问题：{problem_summary}"
        
        return Result.success(result_data)
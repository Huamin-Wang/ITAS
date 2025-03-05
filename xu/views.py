# xu/views.py
from flask import Blueprint, request, jsonify
from .ai import get_answer  # 使用相对导入

# 创建一个 Blueprint
ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai_answer', methods=['POST'])
def ai_answer():
    # 获取用户问题
    question = request.form.get('question')
    if not question:
        return jsonify({'success': False, 'message': '问题不能为空'})

    try:
        # 调用 AI 模型获取回答
        ai_response = get_answer(question)
        return jsonify({'success': True, 'answer': ai_response})
    except Exception as e:
        return jsonify({'success': False, 'message': f"AI 服务错误：{str(e)}"})
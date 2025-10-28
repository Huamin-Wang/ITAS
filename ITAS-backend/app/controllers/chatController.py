from flask import Blueprint, request, current_app
import logging
from app.models.Result import Result

logger = logging.getLogger(__name__)

bp = Blueprint('chat', __name__)

@bp.route('/chat_handle', methods=['POST'])
def chat():
    """处理聊天消息"""
    try:
        user_message = request.json.get('message', '')
        print(user_message)
        ip_address = request.remote_addr
        
        if not user_message or not user_message.strip():
            return Result.bad_request("消息内容不能为空").to_json()
        
        # 使用应用上下文中的聊天服务
        chat_service = current_app.chat_service
        result = chat_service.process_message(user_message, ip_address)
        
        # 根据 ChatService 的返回结果构造统一的响应
        if result.get('success'):
            print(result)
            return Result.success(data=result).to_json()
        else:
            print(result)
            return Result.bad_request(result.get('error', '处理消息失败')).to_json()
        
    except Exception as e:
        logger.error(f"处理聊天消息时出错: {e}")
        return Result.internal_error("服务器内部错误").to_json()

@bp.route('/chat_stats', methods=['GET'])
def get_stats():
    """获取聊天统计信息"""
    try:
        chat_service = current_app.chat_service
        stats = chat_service.get_statistics()
        return Result.success(data=stats, message="获取统计信息成功").to_json()
    except Exception as e:
        logger.error(f"获取统计信息时出错: {e}")
        return Result.internal_error("获取统计信息失败").to_json()

@bp.route('/chat_history', methods=['GET'])
def get_conversation_history():
    """获取当前用户的对话历史"""
    try:
        ip_address = request.remote_addr
        chat_service = current_app.chat_service
        history = chat_service.get_conversation_history(ip_address)
        
        return Result.success(
            data={'conversation': history}, 
            message="获取对话历史成功"
        ).to_json()
    except Exception as e:
        logger.error(f"获取对话历史时出错: {e}")
        return Result.internal_error("获取对话历史失败").to_json()

@bp.route('/clear_history', methods=['POST'])
def clear_conversation_history():
    """清空当前用户的对话历史"""
    try:
        ip_address = request.remote_addr
        chat_service = current_app.chat_service
        success = chat_service.clear_conversation_history(ip_address)
        
        if success:
            return Result.success(message="对话历史已清空").to_json()
        else:
            return Result.success(message="没有找到对话历史").to_json()
            
    except Exception as e:
        logger.error(f"清空对话历史时出错: {e}")
        return Result.internal_error("清空对话历史失败").to_json()
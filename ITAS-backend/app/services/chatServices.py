import threading
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatService:
    """聊天服务类"""
    
    def __init__(self, spark_client, max_history_per_user: int = 20):
        self.spark_client = spark_client
        self.max_history_per_user = max_history_per_user
        self.conversation_history: Dict[str, List[dict]] = {}
        self.total_visitors = 0
        self.lock = threading.Lock()
    
    def process_message(self, user_message: str, ip_address: str) -> dict:
        """
        处理用户消息
        
        Args:
            user_message: 用户消息内容
            ip_address: 用户IP地址
            
        Returns:
            dict: 包含回复和对话历史的字典，适合作为 Result.data
        """
        # 验证输入
        if not user_message or not user_message.strip():
            return {
                "success": False,
                "error": "消息内容不能为空",
                "response": "",
                "format": "text",
                "conversation": []
            }
        
        # 更新访问统计
        self._update_user_statistics(ip_address)
        
        # 调用AI服务
        logger.info(f"IP {ip_address} 发送消息: {user_message}")
        ai_response = self.spark_client.get_response(user_message.strip())
        
        # 更新对话历史
        self._update_conversation_history(ip_address, user_message, ai_response)
        
        return {
            "success": True,
            "response": ai_response,
            "format": "markdown",
            "conversation": self.conversation_history.get(ip_address, []),
            "total_visitors": self.total_visitors
        }
    
    def _update_user_statistics(self, ip_address: str):
        """更新用户统计信息"""
        with self.lock:
            if ip_address not in self.conversation_history:
                self.total_visitors += 1
                logger.info(f"新用户访问，IP: {ip_address}，总访问人数: {self.total_visitors}")
    
    def _update_conversation_history(self, ip_address: str, user_message: str, ai_response: str):
        """更新对话历史"""
        with self.lock:
            if ip_address not in self.conversation_history:
                self.conversation_history[ip_address] = []
            
            # 添加新的对话记录
            self.conversation_history[ip_address].extend([
                {
                    "role": "user", 
                    "content": user_message, 
                    "ip_address": ip_address,
                    "timestamp": self._get_current_timestamp()
                },
                {
                    "role": "assistant", 
                    "content": ai_response, 
                    "format": "markdown", 
                    "ip_address": ip_address,
                    "timestamp": self._get_current_timestamp()
                }
            ])
            
            # 限制历史记录长度
            if len(self.conversation_history[ip_address]) > self.max_history_per_user:
                self.conversation_history[ip_address] = self.conversation_history[ip_address][-self.max_history_per_user:]
    
    def get_conversation_history(self, ip_address: str) -> List[dict]:
        """获取指定IP的对话历史"""
        return self.conversation_history.get(ip_address, [])
    
    def clear_conversation_history(self, ip_address: str) -> bool:
        """清空指定IP的对话历史"""
        with self.lock:
            if ip_address in self.conversation_history:
                del self.conversation_history[ip_address]
                logger.info(f"已清空IP {ip_address} 的对话历史")
                return True
            return False
    
    def get_statistics(self) -> dict:
        """获取服务统计信息"""
        with self.lock:
            active_conversations = len(self.conversation_history)
            total_messages = sum(len(history) for history in self.conversation_history.values())
            
            return {
                "total_visitors": self.total_visitors,
                "active_conversations": active_conversations,
                "total_messages": total_messages
            }
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        return datetime.now().isoformat()
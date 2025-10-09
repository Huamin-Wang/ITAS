# 导入所有模型，方便在其他地方导入
from app.models.Student import Student
from app.models.Account import Account
from .Result import Result
__all__ = ['Student','Account','Result']
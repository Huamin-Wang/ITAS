from flask import Blueprint, request
from app.models.Result import Result
from app.services.aiServices import AiServices

bp = Blueprint('ai', __name__)


#自动批改作业
@bp.route('/test_score', methods=['POST'])
def test_score():
    try:
        data = request.get_json()
        if not data:
            return Result.bad_request("请求数据不能为空").to_json(), 400
        result = AiServices.test_score(data)
        return result.to_json(), result.code
        
    except Exception as e:
        import traceback
        print(f"自动评分错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'自动评分过程中发生错误: {str(e)}').to_json(), 500
    
#生成作业标签
@bp.route('/generate_tags', methods=['POST'])
def generate_tags():
    try:
        data = request.get_json()
        if not data:
            return Result.bad_request("请求数据不能为空").to_json(), 400
        result = AiServices.generate_tags(data)
        return result.to_json(), result.code
        
    except Exception as e:
        import traceback
        print(f"生成标签错误详情: {traceback.format_exc()}")
        return Result.internal_error(f'生成标签过程中发生错误: {str(e)}').to_json(), 500
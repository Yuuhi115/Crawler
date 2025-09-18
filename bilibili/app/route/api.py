from flask import Blueprint
from bilibili.app.resources.db_pool import *
product_api_bp = Blueprint('product_api', __name__)
import json

@product_api_bp.route('/foodCategory', methods=['GET'])
def get_food_category():
    try:
        # 获取数据库连接池实例
        db_pool = DatabasePool()
        category_model = db_pool.get_category_model()

        # 查询所有分类
        categories = category_model.select()

        # 构建数据列表
        category_list = []
        for category in categories:
            category_list.append({
                'id': category.id,
                'identity': category.identity
            })

        # 构建返回数据
        return_dict = {
            'code': 200,
            'msg': 'success',
            'data': category_list
        }

        return return_dict

    except Exception as e:
        # 错误处理
        return {
            'code': 500,
            'msg': f'查询失败: {str(e)}',
            'data': []
        }

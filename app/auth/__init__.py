# -*- coding: utf-8 -*-
# @Time    : 18-3-14 下午4:59
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : __init__.py.py
# @Software: PyCharm

'''
TODO 创建认证蓝本
'''
# TODO 导入蓝本
from flask import Blueprint
# TODO 实例化蓝本，蓝本名称，当前app实例
auth = Blueprint('auth', __name__)
# TODO 导入 视图函数，使蓝本知道找哪个路由处理业务逻辑
from . import views
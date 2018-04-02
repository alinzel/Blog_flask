# -*- coding: utf-8 -*-
# @Time    : 18-3-27 上午9:23
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : __init__.py
# @Software: PyCharm

# TODO 定义api蓝本
from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, posts, users, comments, decorators, errors
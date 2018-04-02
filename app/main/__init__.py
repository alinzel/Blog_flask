# -*- coding: utf-8 -*-
# @Time    : 18-3-13 下午8:21
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : __init__.py
# @Software: PyCharm

from flask import Blueprint

# TODO 实例化一个蓝图，main为蓝图的名字，__name__蓝图所在的模块或者包
main = Blueprint('main', __name__)

# TODO 导入 并与蓝图关联起来，【一定在末尾导入，避免循环导入】
from . import views, errors
from ..models import Permission

# TODO 把Permission类加入模板
@main.app_context_processor
def inject_permissions():
	return dict(Permission=Permission)
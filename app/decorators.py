# -*- coding: utf-8 -*-
# @Time    : 18-3-16 上午9:12
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : decorators.py
# @Software: PyCharm

'''
TODO 检查用户权限自定义的装饰器
'''

from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if not current_user.can(permission):
				abort(403)
			return f(*args, **kwargs)
		return decorated_function
	return decorator

def admin_required(f):
	return permission_required(Permission.ADMINISTER)(f)

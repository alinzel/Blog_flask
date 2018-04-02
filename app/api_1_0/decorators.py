# -*- coding: utf-8 -*-
# @Time    : 18-3-27 上午9:24
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : decorators.py
# @Software: PyCharm
from functools import wraps

from flask import g

from app.api_1_0.errors import forbidden


def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if not g.current_user.can(permission):
				return forbidden('Insufficient permissions')
			return f(*args, **kwargs)
		return decorated_function
	return decorator
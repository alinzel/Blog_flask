# -*- coding: utf-8 -*-
# @Time    : 18-3-27 上午9:24
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : errors.py
# @Software: PyCharm
from flask import jsonify
from app.exceptions import ValidationError
from app.api_1_0 import api


# TODO 自定义错误信息

def forbidden(message):
	response = jsonify({'error': 'forbidden', 'message':'禁止'})
	response.status_code = 403
	return response

def bad_request(message):
	response = jsonify({'error': 'bad request', 'message': message})
	response.status_code = 400
	return response


def unauthorized(message):
	response = jsonify({'error': 'unauthorized', 'message': message})
	response.status_code = 401
	return response

@api.errorhandler(ValidationError)
def validation_error(e):
	return bad_request(e.args[0])
# -*- coding: utf-8 -*-
# @Time    : 18-3-13 下午9:08
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : errors.py
# @Software: PyCharm
'''
TODO 错误处理程序
'''

from flask import render_template, request, jsonify
from . import main


# TODO 注册全局的错误处理程序
@main.app_errorhandler(404)
def page_not_found(e):
	if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
		response = jsonify({'error': 'not found'})
		response.status_code = 404
		return response
	return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
	if request.accept_mimetypes.accept_json and \
			not request.accept_mimetypes.accept_html:
		response = jsonify({'error': 'internal server error'})
		response.status_code = 500
		return response
	return render_template('500.html'), 500


@main.app_errorhandler(403)
def forbidden(e):
	if request.accept_mimetypes.accept_json and \
			not request.accept_mimetypes.accept_html:
		response = jsonify({'error': 'forbidden'})
		response.status_code = 403
		return response
	return render_template('403.html'), 403
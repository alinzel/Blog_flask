# -*- coding: utf-8 -*-
# @Time    : 18-3-14 上午8:48
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : test_basics.py
# @Software: PyCharm

'''
TODO 单元测试文件
'''

import unittest
from flask import current_app
from app import create_app, db
class BasicsTestCase(unittest.TestCase):
	# TODO 测试前运行，创建一个测试环境
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()

	# TODO 测试后运行，删除数据库和上下文
	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	# TODO  test_ 开头--》测试执行函数，确保程序实例存在
	def test_app_exists(self):
		self.assertFalse(current_app is None)
	# TODO 确保程序在测试环境中运行
	def test_app_is_testing(self):
		self.assertTrue(current_app.config['TESTING'])
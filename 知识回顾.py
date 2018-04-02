# -*- coding: utf-8 -*-
# @Time    : 18-3-14 下午4:47
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : 知识回顾.py
# @Software: PyCharm
from werkzeug.security import generate_password_hash, check_password_hash
class A():
	password_hash = 'abc'

	@property
	def password(self):
		raise AttributeError('抛出错误')

	def test(self):
		# TODO 这样会更改上边变量的名称
		self.password_hash = 'asd'

	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)

	def vir_password(self,password):
		return check_password_hash(self.password_hash, password)


a = A()
# a.password = '123'
# print(a.password_hash)
# b = A()
# b.password = '123'
# print(b.password_hash)
# a.test()
# print(a.password_hash)


from random import seed

print(seed())
for i in range(100):
	print(i)



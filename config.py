# -*- coding: utf-8 -*-
# @Time    : 18-3-13 下午7:14
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : config.py
# @Software: PyCharm
'''
	TODO 配置文件，程序层次结构的配置类
'''

import os

# TODO 全局变量 当前文件的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))

# TODO 定义配置文件类--包含通用配置
class Config(object):
	# TODO 定义一些类属性
	SECRET_KEY = os.environ.get('SECKET_KEY') or 'hard to guess string'
	# 请求结束后自动刷新数据库
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	FLASKY_MAIL_SUBJECT_PREFIX = '[邮件标题前缀]'
	FLASKY_MAIL_SENDER = '显示的发件人信息<zwl18698035693@126.com>'
	FLASKY_ADMIN =  os.environ.get('FLASKY_ADMIN')
	FLASKY_POSTS_PER_PAGE = 10
	FLASKY_FOLLOWERS_PER_PAGE = 5
	FLASKY_COMMENTS_PER_PAGE = 5

	# TODO 定义一个静态方法，初始化app
	@staticmethod
	def init_app(app):
		pass


# TODO 定义开发环境中的配置--继承配置文件类
class DevelopmentConfig(Config):
	DEBUG = True  # TODO 开启调试模式
	# TODO 配置邮箱信息
	MAIL_SERVER = 'smtp.126.com'
	MAIL_PORT = 25
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	# TODO 配置数据库信息--每个生产环境，隔离数据库
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
											 'sqlite:////' + os.path.join(basedir, 'data-dev.sqlite')


# TODO 定义测试配置信息--继承配置文件类
class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TSET_DATABASE_URI') or \
											 'sqlite:////' + os.path.join(basedir, 'data-test.sqlite')


# TODO 定义生产环境中的配置
class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('TSET_DATABASE_URI') or \
											 'sqlite:////' + os.path.join(basedir, 'data-test.sqlite')

	@classmethod
	def init_app(cls, app):
		Config.init_app(app)

		# 把错误通过电子邮件发送给管理员
		import logging
		from logging.handlers import SMTPHandler
		credentials = None
		secure = None
		if getattr(cls, 'MAIL_USERNAME', None) is not None:
			credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
			if getattr(cls, 'MAIL_USE_TLS', None):
				secure = ()
			mail_handler = SMTPHandler(
				mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
				fromaddr=cls.FLASKY_MAIL_SENDER,
				toaddrs=[cls.FLASKY_ADMIN],
				subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
				credentials=credentials,
				secure=secure)
			mail_handler.setLevel(logging.ERROR)
			app.logger.addHandler(mail_handler)

# TODO 注册不同环境，字典形式
config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	'default': DevelopmentConfig
}

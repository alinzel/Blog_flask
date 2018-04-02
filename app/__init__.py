# -*- coding: utf-8 -*-
# @Time    : 18-3-14 上午9:20
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : __init__.py.py
# @Software: PyCharm

'''
	TODO 程序包构造文件，初始化扩展
'''
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
pagedown = PageDown()

# TODO 安全等级，防止回话被篡改--strong会记录电脑IP和浏览器的用户代理信息，异常会登出
login_manager.session_protection = 'string'
# TODO 设置登录页面的端点，根据次来找到视图函数
login_manager.login_view = 'auth.login'


# TODO 工厂函数--接收配置环境的名字，实现app的动态的配置
def create_app(config_name):
	app = Flask(__name__)
	# TODO 加载实际的环境
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	# TODO 拓展程序自身的方法
	bootstrap.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	pagedown.init_app(app)

	# TODO 把蓝本注册到程序上，路由能通过蓝本中的信息找到对应的app进行逻辑处理等
	from .main import main as main_blueprint
	from .auth import auth as auth_blueprint
	from .api_1_0 import api as api_1_0_blueprint
	app.register_blueprint(main_blueprint)
	# TODO url_prefix 可选参数，为此蓝本的URL添加前缀
	app.register_blueprint(auth_blueprint, url_prefix='/auth')
	app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

	return app
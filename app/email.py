# -*- coding: utf-8 -*-
# @Time    : 18-3-13 下午7:48
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : email.py
# @Software: PyCharm

'''
TODO 发送邮件
'''

from flask_mail import Message
from flask import render_template, current_app
from threading import Thread
from app import mail


# TODO 同步发送方式--定义发邮件函数，供视图函数调用
# TODO 参数信息 收件人，标题，模板信息
# def send_email(to,subject,template,**kwargs):
# 	# TODO 定义信息内容
# 	msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject, sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
# 	# TODO 渲染模板， **kwargs为user,用于前端模板中使用
# 	msg.body = render_template(template + '.txt', **kwargs)
# 	msg.html = render_template(template + '.html', **kwargs)
# 	# 发送邮件
# 	mail.send(msg)


# TODO 异步方式邮件--线程方式
def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)

# TODO 定义发送邮件信息，调用异步发送
def send_email(to, subject, template, **kwargs):
	# TODO current_app._get_current_object()多线程中获取当前程序对象
	app = current_app._get_current_object()
	msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject, sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
	msg.body = render_template(template +'.txt', **kwargs)
	msg.html = render_template(template+'.html', **kwargs)
	# TODO 创建线程
	thr = Thread(target=send_async_email, args=[app, msg])
	thr.start()
	return thr
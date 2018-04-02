# -*- coding: utf-8 -*-
# @Time    : 18-3-14 下午5:01
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : views.py
# @Software: PyCharm
'''
TODO 视图函数与路由
'''

from .import auth
from flask import render_template, redirect, request, url_for, flash
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetForm, PasswordResetRequestForm, ChangeEmailForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from app import db
from  ..email import send_email

# TODO 在请求之前过滤未确认的用户
@auth.before_app_request
def before_request():
	# TODO 当前已有用户登录，登录用户没有确认，不在蓝本认证中跳转到未确认页面
	if current_user.is_authenticated:
		if not current_user.confirmed\
				and request.endpoint \
				and request.blueprint != 'auth' \
				and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))


# TODO 未确认视图
@auth.route('/unconfirmed')
def unconfirmed():
	# TODO is_anonymous-->普通用户返回false
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirm.html')


# TODO 设置登录路由与视图函数
@auth.route('/login', methods=['GET', 'POST'])
def login():
	# TODO 实例化表单，以获取表单中的数据，及返回模板使用
	login_form = LoginForm()
	# TODO 校验表单数据有效性
	if login_form.validate_on_submit():
		# TODO 根据表单数据在数据库中查找
		user = User.query.filter_by(email=login_form.email.data).first()
		# TODO 如果有此用户并且密码正确，则加载用户的状态，返回前端使用【内置方法检查登录状态】
		if user is not None and user.verify_password(login_form.password.data):

			# TODO 内置方法-导入进来的，加载的用户登录及回话状态
			login_user(user, login_form.remember_me.data)
			# TODO 登录成功后返回主页
			return redirect(request.args.get('next') or url_for('main.index'))
		# TODO 登陆错误，放入消息队列，返还给前端显示用
		flash('用户名密码不正确')
	# TODO get请求渲染
	return render_template('auth/login.html', form=login_form)


# TODO 设置登出路由与视图
@auth.route('/logout')
@login_required
def logout():
	# TODO 每次登录成功-->更新已登录用户的访问时间
	current_user.ping()
	# TODO 加载用户状态--删除并重设用户会话
	logout_user()
	flash('你已经退出了')
	return  redirect(url_for('main.index'))


# TODO 注册函数
@auth.route('/register', methods=['GET', 'POST'])
def register():
	register_form = RegistrationForm()
	if register_form.validate_on_submit():
		# noinspection PyArgumentList
		user = User(email=register_form.email.data,
					username=register_form.username.data,
					password=register_form.password.data
					)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email,'某网站用户激活邮件',
				   'auth/email/confirm', user=user, token=token
				   )
		flash('用户激活邮件已经发送邮箱，请前往激活')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html', form=register_form)


# TODO 确认用户账户
@auth.route('/confirm/<token>')
# TODO 路由保护，用户点击确认链接时，需要先登录才能执行视图函数
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		print('11111')
		flash('你已经激活账户，开始你的表演吧')
	else:
		flash('确认链接无效或者已经失效')
	return redirect(url_for('main.index'))


# TODO 重新发送邮件-已登录但未确认会执行此视图
@auth.route('/confirm')
@login_required
def resend_confirmation():
	# TODO 生成token
	token = current_user.generate_confirmation_token()
	# TODO 给当前用户发邮件，内容，模板，用户信息及token（前端拼接的URL）
	send_email(current_user.email, '某网站确认激活的链接',
			   'auth/email/confirm', user=current_user,token=token
			   )
	flash('一个新的激活链接已经发送')
	return redirect(url_for('main.index'))


# TODO 修改密码--只有登录状态才可以修改
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
	change_pwd_form = ChangePasswordForm()
	if change_pwd_form.validate_on_submit():
		# TODO 校验当前用户数据库中存储的密码是否与输入一致
		if current_user.verify_password(change_pwd_form.old_password.data):
			# TODO 给当前用户设置新密码
			current_user.password = change_pwd_form.password.data
			db.session.add(current_user)
			db.session.commit()
			flash('你的密码已经修改')
			return redirect(url_for('main.index'))
		else :
			flash('旧密码不对')
	return render_template('auth/change_password.html', form=change_pwd_form)


# TODO 密码重设请求--网站中点击
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
	# TODO 判断当前用户是不是普通用户
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	password_reset_request_form = PasswordResetRequestForm()
	if password_reset_request_form.validate_on_submit():
		# TODO 判断邮箱是不是注册过的
		user = User.query.filter_by(email=password_reset_request_form.email.data).first()
		# TODO 存在用户-发送邮件
		if user:
			token = user.generate_reset_token()
			send_email(user.email, '重置密码的邮件',
					   'auth/email/reset_password',
					   user=user, token=token,
					   next=request.args.get('next')
					   )
			flash('一个重置密码的邮件已经发送你的邮箱')
			return redirect(url_for('auth.login'))
		# TODO 不存在用户提示
		flash('该邮箱没有被注册过')
	# TODO 请求就返回这个页面
	return render_template('auth/reset_password.html', form=password_reset_request_form)


# TODO 重置密码--邮箱中获取
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	password_reset_form = PasswordResetForm()
	if password_reset_form.validate_on_submit():
		# TODO 如果重置密码的链接通过校验，则保存到数据库
		if User.reset_password(token, password_reset_form.password.data):
			db.session.commit()
			flash('你的密码已经重置')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html', form=password_reset_form)


# TODO 修改邮件--发送邮件
@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
	change_email_form = ChangeEmailForm()
	if change_email_form.validate_on_submit():
		# TODO 密码输入正确，发送邮件
		if current_user.verify_password(change_email_form.password.data):
			new_email = change_email_form.email.data
			token = current_user.generate_email_change_token(new_email)
			send_email(new_email,'确认更改邮箱地址的邮件',
					   'auth/email/change_email',
					   user=current_user, token=token
					   )
			flash('确认更改邮箱地址的邮件已经发送')
			return redirect(url_for('main.index'))
		else:
			flash('非法的邮箱或者密码')
	return render_template('auth/change_email.html', form=change_email_form)


# TODO 修改邮件--点击邮件中链接，修改数据保存到数据库
@auth.route('/change_email/<token>')
@login_required
def change_email(token):
	# TODO 定义在module中的校验token的方法-如果确认链接成功，提交到数据库
	if current_user.change_email(token):
		db.session.commit()
		flash('你的电子邮箱地址已更新')
	else:
		flash('非法的请求')
	# TODO 登录状态下访问次路由，返回主页
	return redirect(url_for('main.index'))


# -*- coding: utf-8 -*-
# @Time    : 18-3-14 下午6:33
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : forms.py
# @Software: PyCharm
'''
TODO 登录表单
'''

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from ..models import User


# TODO 定义登录表单类
class LoginForm(FlaskForm):
	# TODO 验证邮箱长度和格式及必填，注意validators=[]格式
	email = StringField('Email', validators=[DataRequired('请输入邮箱'), Length(6,32), Email()])
	# TODO PasswordField--密码类型
	password = PasswordField('Password', validators=[DataRequired('请输入密码')])
	# TODO BooleanField--表示复选框
	remember_me = BooleanField('Keep me login in')
	submit = SubmitField('登录')


# TODO 定义注册表单
class RegistrationForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email(), Length(6,32)])
	# TODO Regexp-->限制输入内容
	username = StringField('Username', validators=[DataRequired(),
												   Length(4,10), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
																		'用户名必须有一个字母,数字,点,下划线'
																		)
											   ])
	# TODO 两个密码狂，EqualTo--验证密码是否一致，写在第一个密码字段中，参数为第二个字段
	password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='密码必须一样')])
	password2 = PasswordField('Confirm password', validators=[DataRequired()])
	submit = SubmitField('注册')

	# TODO 自定义的校验方法，validate_字段名--》与常规（字段中的验证函数）验证函数一起调用
	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('邮箱已经注册过')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('用户名已经存在')


# TODO 修改密码的表单
class ChangePasswordForm(FlaskForm):
	old_password = PasswordField('旧密码', validators=[DataRequired()])
	password = PasswordField('新密码', validators=[DataRequired(), EqualTo('password2', message='两次密码输入不一致')])
	password2 = PasswordField('确认密码', validators=[DataRequired()])
	submit = SubmitField('确认修改密码')


# TODO 重设密码请求表单-网站内点击获取的
class PasswordResetRequestForm(FlaskForm):
	email = StringField('请输入你的邮箱', validators=[DataRequired(), Email(), Length(6,32)])
	sumbit = SubmitField('确认重置密码')


# TODO 重置密码的表单--邮箱中点击获取的
class PasswordResetForm(FlaskForm):
	password = PasswordField('新密码', validators=[DataRequired(), EqualTo('password2', message='两次密码输入不一样')])
	password2 = PasswordField('确认密码', validators=[DataRequired()])
	sumbit = SubmitField('确认重置密码')


# TODO 修改邮箱的表单
class ChangeEmailForm(FlaskForm):
	email = StringField('新邮箱', validators=[DataRequired(), Length(6,32), Email()])
	password = PasswordField('密码', validators=[DataRequired()])
	submit = SubmitField('确认更新邮箱地址')

	# TODO 验证邮箱是否存在
	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('邮箱已被注册过')

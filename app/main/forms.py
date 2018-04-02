# -*- coding: utf-8 -*-
# @Time    : 18-3-13 下午9:18
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : forms.py
# @Software: PyCharm

from ..models import Role, User
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField


# TODO 用户级别的资料编辑表单
class EditProfileForm(FlaskForm):
	name = StringField('真实姓名', validators=[Length(0,64)])
	location = StringField('地址', validators=[Length(0,64)])
	about_me = TextAreaField('关于我')
	submit = SubmitField('提交')


# TODO 管理员级别的资料编辑表单
class EditProfileAdminForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email(), Length(1,64)])
	username = StringField('Username', validators=[DataRequired(), Length(1,64),
												   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters, numbers, dots or underscores')])
	confirmed = BooleanField('Confirmed')
	role = SelectField('Role', coerce=int)
	name = StringField('Real name', validators=[Length(0,64)])
	location = StringField('location', validators=[Length(0,64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('提交')

	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args,**kwargs)
		# TODO 实例化角色下拉框的内容,和用户
		self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
		self.user = user

	# TODO 验证email-->管理员在修改邮箱时候进行验证
	def validate_email(self, field):
		if field.data != self.user.email and User.query.filter_by(email=field.data).first():
			raise ValidationError('邮箱已经注册过')

	# TODO 同上
	def validate_username(self, field):
		if field.data != self.user.username and User.query.filter_by(username=field.data).first():
			raise ValidationError('用户名已经注册过')


# TODO 博客文章表单
class PostForm(FlaskForm):
	body= PageDownField('文章主题', validators=[DataRequired()])
	submit = SubmitField('提交文章')


# TODO 评论表单
class CommentForm(FlaskForm):
	body = StringField('', validators=[DataRequired()])
	submit = SubmitField('提交评论')
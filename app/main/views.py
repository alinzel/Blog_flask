# -*- coding: utf-8 -*-
# @Time    : 18-3-13 下午9:08
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : views.py
# @Software: PyCharm
'''
TODO 定义程序的路由视图
'''

from flask import render_template, abort, flash, redirect, url_for, request, current_app, make_response
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..models import User, Role, Permission, Post, Comment
from flask_login import login_required, current_user
from ..decorators import admin_required
from ..decorators import permission_required


# TODO 首页的路由
@main.route('/', methods=['GET', 'POST'])
def index():
	post_form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and post_form.validate_on_submit():
		post = Post(body=post_form.body.data, author=current_user._get_current_object())
		db.session.add(post)
		return redirect(url_for('main.index'))
	# TODO 每次都初始化show_followed--默认为显示所有用户
	show_followed = False
	# TODO 判断当前用户是否登录,并获取cookie值
	if current_user.is_authenticated:
		show_followed = bool(request.cookies.get('show_followed', ''))
	# TODO 判断show_followed,登录->从当前用户获取关注人的文章,否则,全部文章
	if show_followed:
		query = current_user.followed_posts
	else:
		query = Post.query
	# TODO 分页显示文章
	# TODO 从请求中获取要渲染的页数, 从第一页开始, type=int,当参数无法转换成整数时,返回默认值
	page = request.args.get('page', 1, type=int)
	# TODO paginate(页数,[每页显示数量,未指定默认20],[error_out->true, 超出页数,返回404,False,返回空列表])
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
		error_out=False
	)
	posts = pagination.items  # TODO 当前页的实例记录
	return render_template('Index.html', form=post_form, posts=posts, pagination=pagination, show_followed=show_followed)


# TODO 用户资料页面的路由
@main.route('/user/<username>')
def user(username):
	# TODO 查找是否有当前的用户,没有-404,有-显示用户信息页面
	user = User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	# TODO 从请求中获取要渲染的页数, 从第一页开始, type=int,当参数无法转换成整数时,返回默认值
	page = request.args.get('page', 1, type=int)
	# TODO paginate(页数,[每页显示数量,未指定默认20],[error_out->true, 超出页数,返回404,False,返回空列表])
	pagination = Post.query.filter_by(author=user).paginate(
		page, per_page=5 ,
		error_out=False
		)
	posts = pagination.items  # TODO 当前页的实例记录--列表

	return render_template('user.html', user=user, posts=posts, pagination=pagination)


# TODO 用户--编辑资料页面的路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	# TODO 实例化编辑个人信息表单
	edit_form = EditProfileForm()
	# TODO 判断是否有效提交,有效内容更新到数据库,并跳转到个人信息页面
	if edit_form.validate_on_submit():
		current_user.name = edit_form.name.data
		current_user.location = edit_form.location.data
		current_user.about_me = edit_form.about_me.data
		db.session.add(current_user)
		flash('你的个人资料已经更新')
		return redirect(url_for('main.user', username=current_user.username))
	# TODO 无效提交,内容不变,还在当前编辑页面
	edit_form.name.data = current_user.name
	edit_form.location.data = current_user.location
	edit_form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=edit_form)


# TODO 管理员--编辑资料页面的路由
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required  # TODO 判断是不是管理员的权限
def edit_profile_admin(id):
	# TODO 通过id查找,没有则抛出404错误,而不是none
	user = User.query.get_or_404(id)
	# TODO 实例化表单,并传入User
	admin_form = EditProfileAdminForm(user=user)
	print(admin_form)
	# TODO 如果是有效的提交,更新数据库信息,并返回用户资料页面
	if admin_form.validate_on_submit():
		user.name = admin_form.name.data
		user.email = admin_form.email.data
		user.username = admin_form.username.data
		user.confirmed = admin_form.confirmed.data
		user.role = Role.query.get(admin_form.role.data)
		user.location = admin_form.location.data
		user.about_me = admin_form.about_me.data
		db.session.add(user)
		flash('资料已经更新')
		return redirect(url_for('main.user', username=user.username))
	# TODO 无效提交,返回到编辑资料页面
	admin_form.email.data = user.email
	admin_form.username.data = user.username
	admin_form.confirmed.data = user.confirmed
	admin_form.role.data = user.role_id
	admin_form.name.data = user.name
	admin_form.location.data = user.location
	admin_form.about_me.data = user.about_me
	return render_template('edit_profile.html', form=admin_form, user=user)


# TODO 支持文章固定连接 + 提交评论功能
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
	# TODO 根据id查找,不存在则抛出404
	post = Post.query.get_or_404(id)
	comment_form = CommentForm()
	# TODO 判断是否有效输入,并获取数据插入数据库
	if comment_form.validate_on_submit():
		comment = Comment(body=comment_form.body.data, post=post, author=current_user._get_current_object())
		db.session.add(comment)
		db.session.commit()
		flash('你的评论已经发布')
		# TODO 提交成功后重定向至本业
		return redirect(url_for('main.post', id=post.id))
		# return redirect(url_for('main.post', id=post.id, page=-1))  # TODO 指定page=-1,提交会提交至最后一页
	page = request.args.get('page', 1, type=int)
	# TODO 如果提交只最后一页,则设置 page = -1[此条件,重新复制,使其从处理过的page值开始分页]
	# if page == -1:
	# 	page = (post.comments.count() - 1) // current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
	pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
		error_out = False
	)
	comments = pagination.items
	return render_template('post.html', posts=[post], form=comment_form, comments=comments, pagination=pagination)


# TODO 编辑文章的路由与视图逻辑
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		flash('文章已经更新')
		# TODO 重定向到文章信息页面
		return redirect(url_for('main.post', id=post.id))
	# TODO 从数据库中取出文章显示在表单
	form.body.data = post.body
	return render_template('edit_post.html', form=form)


# TODO 关注其他用户逻辑处理
@main.route('/follow/<username>')
# TODO 验证是否登录与权限
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	# TODO 在数据库中查找用户
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在')
		return redirect(url_for('main.index'))
	if current_user.is_following(user):
		flash('你已经关注过该用户')
		return redirect(url_for('main.user', username=username))
	current_user.follow(user)
	flash('你已经关注%s'% username)
	return redirect(url_for('main.user', username=username))


# TODO 取消关注的业务逻辑
'''
	查找user用户,不存在,返回首页
	验证是否关注,没有关注,提示未关注
	其他,取消关注,调用unfollow方法,从数据库删除
'''
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash('你没有关注此用户.')
		return redirect(url_for('.user', username=username))
	current_user.unfollow(user)
	flash('你已经取消关注%s' % username)
	return redirect(url_for('.user', username=username))


# TODO 查看粉丝的路由与业务逻辑
@main.route('/followers/<username>')
def followers(username):
	# TODO 查找当前用户,如果用户不存在,返回首页
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('非法的用户')
		return redirect(url_for('main.index'))
	page = request.args.get('page', 1, type=int)
	# TODO 对用户下的followers粉丝进行分页
	pagination = user.followers.paginate(
		page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
		error_out = False
	)
	# TODO 获取每一个分页实例的用户,跟关注时间--列表形式[{},{}]
	follows = [{'user':item.follower, 'timestamp' : item.timestamp }for item in pagination.items]
	for follow in follows:
		print(follow)
		print(type(follow))
	return render_template('followers.html', user=user, title="的粉丝",
						   endpoint='main.followers', pagination=pagination,
						   follows=follows
						   )


# TODO 查看关注了谁的业务逻辑--与查看粉丝逻辑一样
@main.route('/followed-by/<username>')
def followed_by(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	pagination = user.followed.paginate(
		page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
		error_out=False)
	follows = [{'user': item.followed, 'timestamp': item.timestamp}
			   for item in pagination.items]
	return render_template('followers.html', user=user, title="Followed by",
						   endpoint='.followed_by', pagination=pagination,
						   follows=follows)


# TODO 设置cookie,查看全部文章的时候,show_followed设为空
@main.route('/all')
@login_required
def show_all():
	resp = make_response(redirect(url_for('main.index')))
	resp.set_cookie('show_followed', '', max_age=30*24*60*60)
	return resp


# TODO 设置查看关注文章的cookie
@main.route('/followed')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('main.index')))
	resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
	return resp


# TODO 展示所有评论的路由
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	# TODO 对所有评论进行分页,并渲染管理员可见的评论页面
	page = request.args.get('page', 1, type=int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
		error_out=False
	)
	comments = pagination.items
	return render_template('moderate.html', comments=comments, pagination=pagination, page=page)


# TODO 评论管理,设置评论可用
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	# TODO 查找评论,将其设置为可用,并添加到数据库
	comment = Comment.query.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	db.session.commit()
	return redirect(url_for('main.moderate', page=request.args.get('page', 1, type=int)))


# TODO 管理评论,设置评论不可用
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	db.session.commit()
	return redirect(url_for('main.moderate', page=request.args.get('page', 1, type=int)))

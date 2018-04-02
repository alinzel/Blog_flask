# -*- coding: utf-8 -*-
# @Time    : 18-3-13 下午7:48
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : models.py
# @Software: PyCharm

'''
TODO 模型
'''

# TODO 两个加盐加密的方法uth 9449
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from datetime import datetime
import hashlib
from sqlalchemy.exc import IntegrityError
from random import seed, randint
import forgery_py
from markdown import markdown
import bleach
from app.exceptions import ValidationError


# TODO 权限常亮--》用来组织用户角色 或的关系
class Permission:
	# 关注他人
	FOLLOW = 0x01
	# 他人文章中写评论
	COMMENT = 0x02
	# 写文章
	WRITE_ARTICLES = 0x04
	# 管理他人发表的评论
	MODERATE_COMMENTS = 0x08
	# 管理员
	ADMINISTER = 0x80


# TODO 关注的关联表的模型
class Follow(db.Model):
	# TODO 表名字
	__tablename = 'follows'
	# TODO 关注者
	follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	# TODO 被关注者
	followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# TODO 定义模型类
class Role(db.Model):
	# TODO 定义表
	__tablename__ = 'roles'
	# TODO db.Column-->定义字段的实例，第一个参数为数据类型
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer)
	# TODO 添加users属性，定义与哪个模型间的关系，backref,向关系模型中添加一个属性，这个属性可以代替外建访问关系模型
	users = db.relationship('User', backref='role', lazy='dynamic')  # 禁止自动查询

	# TODO 往数据库中添加角色
	@staticmethod
	def insert_roles():
		# TODO 定义角色类型
		roles = {
			'User': (Permission.FOLLOW |
					Permission.COMMENT |
					Permission.WRITE_ARTICLES, True
					),
			'Moderator': (Permission.FOLLOW |
						  Permission.COMMENT |
						  Permission.WRITE_ARTICLES |
						  Permission.MODERATE_COMMENTS, False
						),
			'Administrator': (0xff, False)
		}
		# TODO 遍历每一个角色
		for r in roles:
			# TODO 查找是否有此角色,没有添加到数据库
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			# TODO 设置权限和默认角色,User,True
			role.permissions = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)
		db.session.commit()

	# TODO 可选， 告诉Python如何打印class对象，返回一个可读性字符串，方便调试使用
	def __repr__(self):
		return '<Role %r>' % self.name


class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(), unique=True, index=True)
	password_hash = db.Column(db.String(128))
	# TODO 用户信息字段
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	# TODO 头像缓存hash
	avatar_hash = db.Column(db.String(32))
	# TODO 注册日期
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	# TODO 上次登录时间
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
	# TODO 标记用户是否确认链接的字段,默认没有确定
	confirmed = db.Column(db.Boolean, default=False)
	# TODO 添加外建字段，roles.id指某一张表的某个字段
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	# TODO 关注者与被关注者之间的关系
	followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
								backref=db.backref('followed', lazy='joined'),
								lazy='dynamic',
								cascade='all, delete-orphan'
								)
	followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
							   backref=db.backref('follower', lazy='joined'),
							   lazy='dynamic',
							   # TODO 级联关系-添加与删除
							   cascade='all, delete-orphan'
							   )
	comments = db.relationship('Comment', backref='author', lazy='dynamic')

	# TODO 把用户转化为JSON格式的序列化字典
	def to_json(self):
		json_user = {
			'url': url_for('api.get_post', id=self.id, _external=True),
			'username': self.username,
			'member_since': self.member_since,
			'last_seen': self.last_seen,
			'posts': url_for('api.get_user_posts', id=self.id, _external=True),
			'followed_posts': url_for('api.get_user_followed_posts', id=self.id, _external=True),
			'post_count': self.posts.count()
		}
		return json_user

	# TODO 基于令牌的认证
	def generate_auth_token(self, expiration):
		s = Serializer(current_app.config['SECRET_KEY'],
					   expires_in=expiration)
		return s.dumps({'id': self.id}).decode('utf-8')

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return None
		return User.query.get(data['id'])

	# TODO 把用户设为自己的关注者的方法
	@staticmethod
	def add_self_follows():
		# TODO 查询所有的用户,判断是否关注自己,进行逻辑处理
		for user in User.query.all():
			if not user.is_following(user):
				user.follow(user)
				db.session.add(user)
				db.session.commit()


	# TODO 获取关注用户的文章
	@property
	def followed_posts(self):
		# TODO 联表查询-查询对象.query.join(联结的表,条件).过滤条件(条件)
		return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

	# TODO 将关注实例写入数据库
	def follow(self, user):
		if not self.is_following(user):
			f = Follow(follower = self, followed = user)
			db.session.add(f)

	# TODO 取消关注 查找指定用户,如果找到-删除,
	def unfollow(self, user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)

	# TODO 进行关注的方法-->根据follow的关联关系,查找到是否可以查询到指定用户,查看是否已经关注
	def is_following(self, user):
		return self.followed.filter_by(followed_id=user.id).first() is not None

	# TODO 查看被谁关注
	def is_followed_by(self,user):
		return self.followers.filter_by(follower_id=user.id).first() is not None

	# TODO 静态方法--生成虚拟用户
	@staticmethod
	def generate_fake(count=100):
		# TODO why?
		seed()
		for i in range(count):
			# TODO orgery_py-->生成相应信息
			u = User(email=forgery_py.internet.email_address(),
					 username=forgery_py.internet.user_name(True),
					 password=forgery_py.lorem_ipsum.word(),
					 confirmed=True,
					 name=forgery_py.name.full_name(),
					 location=forgery_py.address.city(),
					 about_me=forgery_py.lorem_ipsum.sentence(),
					 member_since=forgery_py.date.date(True)
					 )
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()

	# TODO 生成头像url的方法
	def gravatar(self, size=100, default='monsterid', rating='g'):
		if request.is_secure:
			url = 'https://secure.gravatar.com/avatar'
		else:
			url = 'http://www.gravatar.com/avatar'
		hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
			url=url, hash=hash, size=size, default=default, rating=rating
		)

	# TODO 刷新用户最后的访问时间
	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)

	# TODO 注册时候判断用户应赋予的角色
	def __init__(self, **kwargs):
		# TODO 调用父类方法,实例基类对象后还没有角色,则进行下边逻辑
		super(User, self).__init__(**kwargs)
		# TODO 如果role属性为none
		if self.role is None:
			# TODO 判断邮箱是不是跟环境变量中的管理员邮箱一致
			if self.email == current_app.config['FLASKY_ADMIN']:
				# TODO 一致则查找权限为超管附给角色
				self.role = Role.query.filter_by(permissions=0xff).first()
			# TODO 如果不是超管则为普通用户
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()

		# TODO 初始化头像hash,如果存在email,但是头像url为空,则生成url
		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

		# TODO 注册用户的时候关注自己
		self.follow(self)

	# TODO 用户角色验证
	def can(self, permissions):
		# TODO 判断是否允许用户执行此操作
		return self.role is not None and (self.role.permissions & permissions) == permissions

	# TODO 判断是否是管理员
	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

	# TODO 此装饰器作用是将方法作为属性使用
	@property
	def password(self):
		raise AttributeError('密码不是一个可读的属性')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		# TODO 检查两个值，正确返回True
		return check_password_hash(self.password_hash, password)

	# TODO 生成确认令牌
	def generate_confirmation_token(self, expiration=3600):
		# TODO 实例化序列对象
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		# TODO 返回序列化后的数据与签名--》即token
		return s.dumps({'confirm':self.id}).decode('utf-8')

	# TODO 校验是否已确认
	def confirm(self, token):
		# TODO 实例化序列对象，因为解密，所以序列化的要为一个秘钥
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			# TODO 对生成的令牌反序列化
			data = s.loads(token.encode('utf-8'))
		except:
			# TODO 反序列化失败返回false
			return False
		# TODO 反序列化成功，但用户ID不对，返回Flase
		if data.get('confirm') != self.id:
			return False
		# TODO 反序列化与id都对，更改数据库的用户确认字段
		self.confirmed = True
		db.session.add(self)
		return True

	# TODO 生成重置密码的token
	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id}).decode('utf-8')

	# TODO 校验是否一点过链接重置密码
	@staticmethod
	def reset_password(token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
			print()
		except:
			return False
		user = User.query.get(data.get('reset'))
		if user is None:
			return False
		# TODO 有当前用户则进行次修改
		user.password = new_password
		db.session.add(user)
		return True

	# TODO 修改邮箱的两个序列化处理方法
	def generate_email_change_token(self, new_email, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps(
			{'change_email': self.id, 'new_email': new_email}).decode('utf-8')

	def change_email(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return False
		# TODO 判断用户ID是否相符
		if data.get('change_email') != self.id:
			return False
		new_email = data.get('new_email')
		if new_email is None:
			return False
		if self.query.filter_by(email=new_email).first() is not None:
			return False
		self.email = new_email
		# TODO 将新改的email生成头像
		self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
		db.session.add(self)
		return True

	def __repr__(self):
		return 'User %r' % self.username


# TODO 文章模型
class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	# TODO makedown转换后的html文本
	body_html = db.Column(db.Text)
	comments = db.relationship('Comment', backref='post', lazy='dynamic')

	# TODO  利用/JSON格式创建文章
	@staticmethod
	def from_json(json_post):
		body = json_post.get('body')
		if body is None or body == '':
			raise ValidationError('文章没有内容')
		return Post(body=body)

	# TODO 把文章转换成JSON格式的序列化字典
	def to_json(self):
		json_post = {
			'url': url_for('api.get_post', id = self.id, _external=True),
			'body': self.body,
			'body_html': self.body_html,
			'timestamp': self.timestamp,
			'author': url_for('api.get_user', id=self.id, _external=True),
			'comments': url_for('api.get_post_comments', id=self.id, _external=True),
			'comment_count': self.comments.count()
		}
		return json_post

	# TODO markdown到html文本的转换
	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator ):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
		# TODO markdown先把value(Markdow)文本,转换成html,并传clean
		# TODO clean进行清洗,删除不在允许的标签
		# TODO linkify,组织链接,加上a标签
		target.body_html =bleach.linkify(bleach.clean(
			markdown(value, output_format='html'),
			tags=allowed_tags, strip=True
		))

	@staticmethod
	def generate_fake(count=100):
		seed()
		user_count = User.query.count()
		for i in range(count):
			# TODO 为每篇文章指定一个用户
			u = User.query.offset(randint(0, user_count-1)).first()
			p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),
					 timestamp=forgery_py.date.date(True),
					 author=u
					 )
			db.session.add(p)
			db.session.commit()


# TODO 评论的模型
class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	# TODO 评论管理员可以禁用不当评论
	disabled = db.Column(db.Boolean)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

	# TODO 将markdown转换为HTML
	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
		target.body_html = bleach.linkify(bleach.clean(
			markdown(value, output_format='html'),
			tags=allowed_tags, strip=True))


# TODO 加载用户的回调函数--找到用户返回用户，未找到返回None
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


# TODO 允许用户未登录 也能调用current_User
class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False

	def is_administrator(self):
		return False

login_manager.anonymous_user = AnonymousUser
# TODO 监听body字段,只要body有新值,会自动调用转换函数,进行markdown到html的转换
db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Comment.body, 'set', Comment.on_changed_body)




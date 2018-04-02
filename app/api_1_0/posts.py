# -*- coding: utf-8 -*-
# @Time    : 18-3-27 上午9:24
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : posts.py
# @Software: PyCharm

from flask import jsonify, request, g, url_for, current_app

from app import db
from app.api_1_0 import api
from app.api_1_0.authentication import auth
from app.api_1_0.errors import forbidden
from .decorators import permission_required
from app.models import Post, Permission

# TODO 所有文章资源get请求处理
@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


# TODO 单个文章
@api.route('/posts/<int:id>')
def get_post(id):
	post = Post.query.get_or_404(id)
	return jsonify(post.to_json())


# TODO 添加文章资源post请求处理
@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
	print('添加文章视图进来了')
	post = Post.from_json(request.json)
	print(post.id)
	post.author = g.current_user
	db.session.add(post)
	db.session.commit()
	return jsonify(post.to_json()), 201, \
		{'Location': url_for('api.get_post', id=post.id)}


# TODO 修改文章资源PUT请求处理
@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())
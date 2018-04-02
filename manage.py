# -*- coding: utf-8 -*-
# @Time    : 18-3-13 下午11:33
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : manage.py
# @Software: PyCharm

'''
TODO 启动脚本
'''
import os
from app import create_app, db
from app.models import User, Role, Post
from flask_script import Manager,Shell
from flask_migrate import Migrate, MigrateCommand


# TODO 创建app,从系统环境中获取变量
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
# TODO 初始化迁移脚本仓库
migrate = Migrate(app, db)


# TODO 集成shell命令
def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role, Post=Post)


# TODO 启动单元测试的命令
@manager.command
def test():
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)

# TODO 部署命令
@manager.command
def deploy():
	''' 部署任务 '''
	from flask_migrate import upgrade
	from app.models import Role, User

	# 把数据库迁移到最新修订版本
	upgrade()

	# 创建用户角色
	Role.insert_roles()

	# 关注你自己
	User.add_self_follows()

manager.add_command("shell", Shell(make_context=make_shell_context))
# TODO 添加数据库迁移命令
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
	manager.run()
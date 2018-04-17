# coding:utf-8
# 程序入口


from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# from iHome import app, db
from iHome import get_app, db

app = get_app('dev')

manager = Manager(app)

Migrate(app, db)

manager.add_command('db', MigrateCommand)


# @app.route('/', methods=['GET', 'POST'])
# def hello_world():
#     return 'Hello World!'


if __name__ == '__main__':
    manager.run()
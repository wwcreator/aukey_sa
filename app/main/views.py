import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import time
import math
import hashlib
# from datetime import timedelta
# from flask_login import login_manager
from forms import LoginForm
from flask import (render_template,
                   g,
                   request,
                   abort,
                   session,
                   redirect,
                   url_for,
                   flash)


import MySQLdb as mdb

from config import config
from . import main
# import bleach
from markdown import markdown, Markdown

# try:
#     conn = mdb.connect(**config.db_config)
#     cursor = conn.cursor()
# except Exception, e:
#     print e
#     sys.exit()


@main.before_request
def before_request():
    g.db = mdb.connect(**config.db_config)


# @main.teardown_request
# def teardown_request():
#     if hasattr(g, 'db'):
#         g.db.close()


def verify_user(username):
    c = g.db.cursor()
    c.execute("SELECT username FROM users WHERE username='%s'" % username)
    if c.fetchone() is None:
        return False
    else:
        return True


def verify_password(username, password):
    c = g.db.cursor()
    c.execute("SELECT username FROM users WHERE username='%s' AND password='%s' " % (username, password))
    if c.fetchone() is None:
        return False
    else:
        return True


def get_salt(username):
    c = g.db.cursor()
    c.execute("SELECT salt FROM users WHERE username='%s'" % username)
    salt = c.fetchone()
    if salt is not None:
        return salt[0].encode('utf8')
    else:
        return ''


def get_userid(username):
    c = g.db.cursor()
    c.execute("SELECT user_id FROM users WHERE username='%s'" % username)
    userid = c.fetchone()
    if userid is not None:
        return userid[0]


def get_username(userid):
    c = g.db.cursor()
    c.execute("SELECT username FROM users WHERE user_id='%s'" % userid)
    username = c.fetchone()
    if username is not None:
        return username[0].encode('utf8')


def get_reccount(table_name, where):
    query = "SELECT COUNT(1) FROM %s WHERE %s" % (table_name, where)
    c = g.db.cursor()
    c.execute(query)
    rec_count = c.fetchone()
    return int(rec_count[0])


# def paginate(table_name, where, page):
#     pagination = {}
#     pagecount = int(math.floor(get_reccount(table_name, where)/config.POSTS_PER_PAGE) + 1)
#     pagination['pagecount'] = pagecount
#     pagination['page'] = page
#     if page == 1 & page != pagecount:
#         pagination['has_prev'] = False
#         pagination['has_next'] = True
#         pagination['prev_num'] = page
#         pagination['next_num'] = page + 1
#     elif page != 1 & page == pagecount:
#         pagination['has_next'] = False
#         pagination['has_prev'] = True
#         pagination['prev_num'] = page - 1
#         pagination['next_num'] = page
#     elif page == pagecount & page == 1:
#         pagination['has_next'] = False
#         pagination['has_prev'] = False
#         pagination['prev_num'] = page
#         pagination['next_num'] = page
#     else:
#         pagination['has_prev'] = True
#         pagination['has_next'] = True
#         pagination['prev_num'] = page - 1
#         pagination['next_num'] = page + 1
#     return pagination


# @main.route('/', methods=['GET', 'POST'])
# def index():
#     page = request.args.get('page', 1, type=int)
#     query = """SELECT title, concat(LEFT(content, 200),' ...'), username , from_unixtime(create_at)create_at, post_id
#                FROM posts
#                INNER JOIN users
#                ON users.user_id = posts.user_id
#                WHERE status = 1
#                ORDER BY create_at DESC
#                LIMIT %s OFFSET %s
#                """ % (config.POSTS_PER_PAGE, config.POSTS_PER_PAGE*(page - 1))
#     c = g.db.cursor()
#     c.execute(query)
#     posts = [dict(title=row[0], content=row[1], username=row[2], create_at=row[3], post_id=row[4]) for row in c.fetchall()]
#     pagination = paginate('posts', 'status = 1', page)
#     return render_template('index.html', endpoint='main.index', posts=posts, pagination=pagination)
@main.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('login.html', form=form, name=name)


# @main.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         form_password = form.password.data
#         username = form.username.data
#         # remember_me = form.remember_me.data
#         salt = get_salt(username)
#         password = hashlib.md5(hashlib.md5(form_password + salt).hexdigest()).hexdigest()
#         if not verify_user(username):
#             flash('Invalid username.')
#         elif not verify_password(username, password):
#             flash('Invalid password.')
#         else:
#             session['logged_in'] = True
#             session['username'] = username
#             # flash('You were logged in.')
#             return render_template('main.html')
#     return render_template('login.html', form=form)


@main.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('logged_in', None)
    flash('You have been logged out.')
    # return render_template('login.html')
    return redirect(url_for('main.index'))










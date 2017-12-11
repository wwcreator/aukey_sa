# -*- coding: utf8 -*-

import time
import math
import paramiko
import hashlib
from forms import LoginForm, AddServerForm
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




@main.before_request
def before_request():
    g.db = mdb.connect(**config.db_config)


def sshclient_execmd(hostname, port, username, password, execmd):
    paramiko.util.log_to_file("paramiko.log")

    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    s.connect(hostname=hostname, port=port, username=username, password=password)
    stdin, stdout, stderr = s.exec_command(execmd)
    stdin.write("Y")  # Generally speaking, the first connection, need a simple interaction.

    print stdout.read()

    s.close()


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


def paginate(table_name, where, page):
    pagination = {}
    pagecount = int(math.floor(get_reccount(table_name, where) / config.POSTS_PER_PAGE) + 1)
    pagination['pagecount'] = pagecount
    pagination['page'] = page
    if page == 1 & page != pagecount:
        pagination['has_prev'] = False
        pagination['has_next'] = True
        pagination['prev_num'] = page
        pagination['next_num'] = page + 1
    elif page != 1 & page == pagecount:
        pagination['has_next'] = False
        pagination['has_prev'] = True
        pagination['prev_num'] = page - 1
        pagination['next_num'] = page
    elif page == pagecount & page == 1:
        pagination['has_next'] = False
        pagination['has_prev'] = False
        pagination['prev_num'] = page
        pagination['next_num'] = page
    else:
        pagination['has_prev'] = True
        pagination['has_next'] = True
        pagination['prev_num'] = page - 1
        pagination['next_num'] = page + 1
    return pagination


def is_connect(ip, user, port, password):
	ip = ip
	user = user
	password = password
	port = port
	ssh = paramiko.SSHClient()
	# 这行代码的作用是允许连接不在know_hosts文件中的主机
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try :
		ssh.connect(ip, port, user, password)
		ssh.close()
		return True
	except :
		return False


def collect_info(ip, user, port, password):
	info = {}
	ip = ip
	user = user
	password = password
	port = port
	ssh = paramiko.SSHClient()
	# 这行代码的作用是允许连接不在know_hosts文件中的主机
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ip, port, user, password)
	(stdin, stdout, stderr) = ssh.exec_command('cat /proc/cpuinfo |grep "processor"|wc -l')
	cpuinfo = stdout.read()
	(stdin, stdout, stderr) = ssh.exec_command("free -m|grep 'Mem:'|awk '{print $2}'")
	meminfo = stdout.read()
	(stdin, stdout, stderr) = ssh.exec_command("df -kl|awk '{print $2,$3}'|sed '1d'|awk '{sum += $2};END {print sum}'")
	used_disk = stdout.read()
	(stdin, stdout, stderr) = ssh.exec_command("df -kl|awk '{print $2,$3}'|sed '1d'|awk '{sum += $1};END {print sum}'")
	all_disk = stdout.read()
	(stdin, stdout, stderr) = ssh.exec_command("""cat /proc/uptime| awk -F. '{run_days=$1 / 86400;run_hour=($1 % 86400)/3600;run_minute=($1 % 3600)/60;run_second=$1 % 60;printf("%d Day %d:%d:%d \n",run_days,run_hour,run_minute,run_second)}'""")
	uptime = stdout.read()
	(stdin, stdout, stderr) = ssh.exec_command("uname -a")
	release = stdout.read()
	ssh.close()
	info['cpuinfo'] = cpuinfo
	info['meminfo'] = meminfo
	info['free_disk'] = all_disk - used_disk
	info['all_disk'] = all_disk
	info['uptime'] = uptime
	info['release'] = release
	return info


@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        form_password = form.password.data
        username = form.username.data
        # remember_me = form.remember_me.data
        salt = get_salt(username)
        password = hashlib.md5(hashlib.md5(form_password + salt).hexdigest()).hexdigest()
        if not verify_user(username):
            flash('Invalid username.')
        elif not verify_password(username, password):
            flash('Invalid password.')
        else:
            session['logged_in'] = True
            session['username'] = username
            # flash('You were logged in.')
            return redirect(url_for('main.portal'))
    return render_template('login.html', form=form)


@main.route('/portal', methods=['GET', 'POST'])
def portal():
    return render_template('main.html')


@main.route('/server/<env>', methods=['GET', 'POST'])
def server(env):
	if env == 'production':
		server_env = 1
	elif env == 'test':
		server_env = 2
	elif env == 'dev':
		server_env = 3
	else:
		server_env = 4

	page = request.args.get('page', 1, type=int)
	query = """ SELECT * FROM infra_server WHERE server_env = '%s' AND is_delete=0 LIMIT %s OFFSET %s """ % (
	server_env, config.POSTS_PER_PAGE, config.POSTS_PER_PAGE * (page - 1))
	c = g.db.cursor()
	c.execute(query)
	servers = [dict(id=row[0], server_hostname=row[1], server_ip=row[2], server_env=row[3], post_id=row[4]) for row in
			   c.fetchall()]
	pagination = paginate('infra_server', 'server_env = ' + str(server_env) + ' AND is_delete = 0', page)

	return render_template('server.html', endpoint='main.server', servers=servers, pagination=pagination)


@main.route('/server/add', methods=['GET', 'POST'])
def add_server():
	form = AddServerForm()
	if form.validate_on_submit():
		server_name = form.server_name.data
		server_ip = form.server_ip.data
		server_username = form.server_username.data
		server_password = form.server_password.data
		server_env = form.server_env.data
		server_tag = form.server_tag.data
		server_type = form.server_type.data
		server_loc = form.server_loc.data
		if is_connect(server_ip, server_username, 22, server_password):
			server_info = collect_info(server_ip, server_username, 22, server_password)
			query = """INSERT INTO infra_server(server_name,server_ip,server_username,server_password,server_env,server_tag,server_type,server_loc)
					  VALUES('%s','%s','%s','%s','%s','%s','%s','%s')		  
			""" %(server_name, server_ip, server_username, server_password, server_env, server_tag, server_type, server_loc)
			c = g.db.cursor()
			c.execute(query)
			g.db.commit()
		else:
			flash('服务器连接失败，请您确认用户名，密码，端口是否正确！')
		return redirect(url_for('main.server', env=server_env))
	return render_template('add_server.html', form=form)


# @main.route('/server/<server_name>/edit', methods=['GET', 'POST'])
# def modify_server(server_name):
#     page = request.args.get('page', 1, type=int)
#     query = """ SELECT * FROM infra_server WHERE server_name = %s AND is_delete=0 LIMIT %s OFFSET %s """ % (server_name, config.POSTS_PER_PAGE, config.POSTS_PER_PAGE * (page - 1))
#     c = g.db.cursor()
#     c.execute(query)
#     servers = [dict(id=row[0], server_hostname=row[1], server_ip=row[2], server_env=row[3], post_id=row[4]) for row in c.fetchall()]
#     pagination = paginate('posts', 'is_delete = 0', page)
#     return render_template('modify_server.html', endpoint='main.server', servers=servers, pagination=pagination)



@main.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('logged_in', None)
    flash('You have been logged out.')
    # return render_template('login.html')
    return redirect(url_for('main.login'))


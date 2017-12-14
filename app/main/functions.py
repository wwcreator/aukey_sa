import paramiko
import math
from config import config
import MySQLdb as mdb
from flask import (render_template,
				   g,
				   request,
				   abort,
				   session,
				   redirect,
				   url_for,
				   flash)


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


def get_serverip(server_id):
	c = g.db.cursor()
	c.execute("SELECT inet_ntoa(server_ip) FROM infra_server WHERE id='%s'" % server_id)
	server_ip = c.fetchone()
	if server_ip is not None:
		return server_ip[0].encode('utf8')
	else:
		return ''


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


def is_connect_server(ip, user, port, password):
	ip = ip
	user = user
	password = password
	port = port
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		ssh.connect(ip, port, user, password)
		return True
	except:
		ssh.close()
		print 'connect failed!'
		return False



def collect_info(ip, user, port, password):
	info = {}
	ip = ip
	user = user
	password = password
	port = port
	print "start SSHClient:"
	ssh = paramiko.SSHClient()
	print "start SSHClient choice:"
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print "start SSH connect:"
	ssh.connect(ip, port, user, password)
	print "start exec hostname:"
	(stdin, stdout, stderr) = ssh.exec_command('hostname')
	hostname = stdout.read()
	print "start execcpuinfo:"
	(stdin, stdout, stderr) = ssh.exec_command('cat /proc/cpuinfo |grep "processor"|wc -l')
	cpuinfo = stdout.read()
	(stdin, stdout, stderr) = ssh.exec_command("free -g|grep 'Mem:'|awk '{print $2}'")
	meminfo = stdout.read()
	# (stdin, stdout, stderr) = ssh.exec_command("df -kl|awk '{print $2,$3}'|sed '1d'|awk '{sum += $2};END {print sum}'")
	# used_disk = stdout.read()
	(stdin, stdout, stderr) = ssh.exec_command("df -kl|awk '{print $2,$3}'|sed '1d'|awk '{sum += $1};END {print sum}'")
	diskinfo = stdout.read()
	# (stdin, stdout, stderr) = ssh.exec_command("""cat /proc/uptime| awk -F. '{run_days=$1 / 86400;run_hour=($1 % 86400)/3600;run_minute=($1 % 3600)/60;run_second=$1 % 60;printf("%d Day %d:%d:%d \n",run_days,run_hour,run_minute,run_second)}'""")
	# uptime = stdout.read()
	(stdin, stdout, stderr) = ssh.exec_command("cat /etc/issue")
	release = stdout.read()
	ssh.close()
	info['hostname'] = hostname
	info['cpuinfo'] = cpuinfo
	info['meminfo'] = meminfo
	info['diskinfo'] = diskinfo
	info['release'] = release
	return info


def is_connect_mysql(server_ip, instance_username,instance_password, instance_port):
	try:
		mdb.connect(hostname=server_ip, username=instance_username,password=instance_password, port=instance_port, charset='utf8')
		return True
	except:
		return False



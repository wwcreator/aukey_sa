import sys
reload(sys)
sys.setdefaultencoding("utf-8")


import ipaddress
import hashlib
from forms import LoginForm, AddServerForm, UpdateServerForm, AddInstanceForm
from flask import (render_template,
				   g,
				   request,
				   abort,
				   session,
				   redirect,
				   url_for,
				   flash)

import MySQLdb as mdb

import functions as func
from config import config
from . import main


@main.before_request
def before_request():
	g.db = mdb.connect(**config.db_config)


@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		form_password = form.password.data
		username = form.username.data
		# remember_me = form.remember_me.data
		salt = func.get_salt(username)
		password = hashlib.md5(hashlib.md5(form_password + salt).hexdigest()).hexdigest()
		if not func.verify_user(username):
			flash('Invalid username.')
		elif not func.verify_password(username, password):
			flash('Invalid password.')
		else:
			session['logged_in'] = True
			session['username'] = username
			return redirect(url_for('main.portal'))
	return render_template('login.html', form=form)


@main.route('/logout')
def logout():
	# remove the username from the session if it's there
	session.pop('username', None)
	session.pop('logged_in', None)
	flash('You have been logged out.')
	return redirect(url_for('main.login'))


@main.route('/portal', methods=['GET', 'POST'])
def portal():
	return render_template('main.html')


@main.route('/server/<int:server_env>', methods=['GET', 'POST'])
def server(server_env):
	page = request.args.get('page', 1, type=int)
	query = """ SELECT id,server_hostname, inet_ntoa(server_ip),server_env,server_tag,server_os,
  				server_version,server_cpu,server_mem,server_disk,server_type,server_loc 
  				FROM infra_server WHERE server_env = '%s' AND is_delete=0 LIMIT %s OFFSET %s """ % (
		server_env, config.POSTS_PER_PAGE, config.POSTS_PER_PAGE * (page - 1))
	c = g.db.cursor()
	c.execute(query)
	servers = [dict(id=row[0], server_hostname=row[1], server_ip=row[2], server_env=row[3], server_tag=row[4],
				server_os=row[5], server_version=row[6], server_cpu=row[7], server_mem=row[8], server_disk=row[9],
				server_type=row[10], server_loc=row[11]) for row in c.fetchall()]
	pagination = func.paginate('infra_server', 'server_env = ' + str(server_env) + ' AND is_delete = 0', page)

	return render_template('server.html', endpoint='main.server', server_env=server_env, servers=servers,pagination=pagination)


@main.route('/server/add', methods=['GET', 'POST'])
def add_server():
	form = AddServerForm()
	if form.validate_on_submit():
		server_ip = form.server_ip.data
		server_username = form.server_username.data
		server_password = form.server_password.data
		server_port = form.server_port.data
		server_env = form.server_env.data
		server_tag = form.server_tag.data
		server_os = form.server_os.data
		server_type = form.server_type.data
		server_loc = form.server_loc.data
		if func.is_connect_server(server_ip, server_username, server_port, server_password):
			server_info = func.collect_info(server_ip, server_username, server_port, server_password)
			query = """INSERT INTO infra_server(server_hostname,server_ip,server_username,server_password, server_port, server_env,server_tag,
						server_os,server_version,server_cpu, server_mem,server_disk,server_type,server_loc)
					  VALUES('%s','%s','%s','%s',%s,%s,'%s','%s','%s', %s, %s, %s,%s,'%s')		  
			""" % (
				server_info['hostname'], int(ipaddress.ip_address(server_ip)), server_username, server_password, server_port, server_env, server_tag, server_os,
				server_info['release'],
				int(server_info['cpuinfo']), int(server_info['meminfo']), int(server_info['diskinfo'])/1024/1024, server_type, server_loc)
			c = g.db.cursor()
			c.execute(query)
			g.db.commit()
			return redirect(url_for('main.server', server_env=server_env))
		else:
			flash(u'connect failed, invalid username or password!')
	return render_template('add_server.html', form=form)


@main.route('/server/<int:server_id>', methods=['GET', 'POST'])
def get_serverinfo(server_id):
	query = """SELECT id,server_hostname, inet_ntoa(server_ip),server_env,server_tag,server_os,
  				server_version,server_cpu,server_mem,server_disk,server_type,server_loc 
  				FROM infra_server WHERE id=%s """ %(server_id)
	c = g.db.cursor()
	c.execute(query)
	servers = [dict(id=row[0], server_hostname=row[1], server_ip=row[2], server_env=row[3], server_tag=row[4],
					server_os=row[5], server_version=row[6], server_cpu=row[7], server_mem=row[8], server_disk=row[9],
					server_type=row[10], server_loc=row[11]) for row in c.fetchall()]
	return render_template('server.html', servers=servers)

@main.route('/server/<int:server_id>/edit', methods=['GET', 'POST'])
def update_server(server_id):
	if not session.get('logged_in'):
		abort(401)
	form = UpdateServerForm()
	if form.validate_on_submit():
		server_port = form.server_port.data
		server_env = form.server_env.data
		server_tag = form.server_tag.data
		server_type = form.server_type.data
		server_loc = form.server_loc.data
		update_server = """ UPDATE infra_server 
 							SET server_port=%s, server_env=%s, server_tag='%s', server_type=%s,server_loc='%s'
 							WHERE id= %s """ % (server_port, server_env, server_tag, server_type, server_loc, server_id)
		c = g.db.cursor()
		c.execute(update_server)
		g.db.commit()
		flash('server has been updated successfully.')
		return redirect(url_for('main.server', server_env=server_env))
	form.server_ip.data = func.get_serverip(server_id)
	return render_template('update_server.html', form=form)


@main.route('/server/<int:server_env>/<int:server_id>/delete', methods=['GET', 'POST'])
def delete_server(server_env, server_id):
	if not session.get('logged_in'):
		abort(401)
	delete_server = "UPDATE infra_server SET is_delete = 1 WHERE id = %s" % server_id
	c = g.db.cursor()
	c.execute(delete_server)
	g.db.commit()

	flash('server has been deleted successfully.')
	return redirect(url_for('main.server', server_env=server_env))


@main.route('/instance/<int:instance_type>', methods=['GET', 'POST'])
def instance(instance_type):
	page = request.args.get('page', 1, type=int)
	query = """SELECT id, inet_ntoa(server_ip), instance_name, instance_port, instance_type FROM infra_instance WHERE instance_type=%s AND is_delete = 0 LIMIT %s OFFSET %s """ \
			% (instance_type, config.POSTS_PER_PAGE, config.POSTS_PER_PAGE * (page - 1))
	c = g.db.cursor()
	c.execute(query)
	instances = [dict(id=row[0], server_ip=row[1], instance_name=row[2], instance_port=row[3], instance_type=row[4]) for row in c.fetchall()]
	pagination = func.paginate('infra_instance', 'instance_type = ' + str(instance_type) + ' AND is_delete = 0', page)
	return render_template('instance.html', endpoint='main.instance', instance_type=instance_type, instances=instances, pagination=pagination)


@main.route('/instance/<int:instance_type>/add', methods=['GET', 'POST'])
def add_instance(instance_type):
	if not session.get('logged_in'):
		abort(401)
	form = AddInstanceForm()
	if form.validate_on_submit():
		server_ip = form.server_ip.data
		instance_name = form.instance_name.data
		instance_username = form.instance_username.data
		instance_password = form.instance_password.data
		instance_port = form.instance_port.data
		if func.is_connect_mysql(server_ip, instance_username, instance_password, instance_port) :
			add_instance = """INSERT INTO infra_instance(server_ip, instance_name, instance_type, instance_username, instance_password, instance_port)
						VALUES(%s,'%s', %s, '%s','%s', %s) """ %(int(ipaddress.ip_address(server_ip)), instance_name, instance_type, instance_username, instance_password, instance_port)
			c = g.db.cursor()
			c.execute(add_instance)
			g.db.commit()
			return redirect(url_for('main.instance', instance_type=instance_type))
		else:
			flash(u"connect failed, invalid username or password!")
	return render_template('add_instance.html', form=form)


@main.route('/instance/<int:instance_type>/<int:instance_id>/delete', methods=['GET', 'POST'])
def delete_instance(instance_type, instance_id):
	if not session.get('logged_in'):
		abort(401)
	delete_instance = """UPDATE infra_instance SET is_delete = 1 WHERE id = %s""" %(instance_id)
	c = g.db.cursor()
	c.execute(delete_instance)
	g.db.commit()
	return redirect(url_for('main.instance', instance_type=instance_type))


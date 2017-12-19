# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField(u'用户名', validators=[DataRequired()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    # remember_me = BooleanField('Keep me logged in')
    submit = SubmitField(u'登录')


class AddServerForm(FlaskForm):
    # server_name = StringField(u'服务器名称', validators=[DataRequired()])
    server_ip = StringField(u'服务器 IP', validators=[DataRequired()])
    server_username = StringField(u'服务器用户名', validators=[DataRequired()])
    server_password = PasswordField(u'服务器密码', validators=[DataRequired()])
    server_port = StringField(u'服务器端口', validators=[DataRequired()], default=22)
    server_env = SelectField(u'所属环境', choices=[('1', 'production'),('2', 'test'), ('3', 'dev')], default=1)
    server_tag = StringField(u'标签', validators=[DataRequired()])
    server_os = SelectField(u'系统类型', choices=[('1', u'Linux'), ('2', u'Windows')], default=1)
    server_type = SelectField(u'服务器类型', choices=[('1', u'物理机'),('2', u'虚拟机')], default=1)
    server_loc = StringField(u'机房机架号')
    submit = SubmitField(u'添加')



class UpdateServerForm(FlaskForm):
    # server_username = StringField(u'服务器用户名', validators=[DataRequired()])
    # server_password = PasswordField(u'服务器密码', validators=[DataRequired()])
    server_ip = StringField(u'服务器 IP', render_kw={'readonly': True})
    server_port = StringField(u'服务器端口', validators=[DataRequired()], default=22)
    server_env = SelectField(u'所属环境', choices=[('1', 'production'),('2', 'test'), ('3', 'dev')], default=1)
    server_tag = StringField(u'标签', validators=[DataRequired()])
    server_type = SelectField(u'服务器类型', choices=[('1', u'物理机'),('2', u'虚拟机')], default=1)
    server_loc = StringField(u'机房机架号')
    submit = SubmitField(u'修改')


class AddInstanceForm(FlaskForm):
    server_ip = StringField(u'服务器 IP', validators=[DataRequired()])
    instance_name = StringField(u'实例名', validators=[DataRequired()])
    instance_username = StringField(u'实例用户名', validators=[DataRequired()])
    instance_password = PasswordField(u'实例密码', validators=[DataRequired()])
    instance_type = SelectField(u'实例类型', choices=[('1', 'MySQL'),('2', 'SQL SERVER')], default=1)
    instance_port = StringField(u'实例端口', validators=[DataRequired()])
    submit = SubmitField(u'添加')


class NewInstanceForm(FlaskForm):
    server_ip = StringField(u'服务器 IP', validators=[DataRequired()])
    instance_name = StringField(u'实例名', validators=[DataRequired()])
    instance_mem = StringField(u'分配内存', validators=[DataRequired()])
    instance_disk = StringField(u'预估空间', validators=[DataRequired()])
    instance_type = SelectField(u'实例类型', choices=[('1', 'MySQL')], default=1)
    instance_port = StringField(u'实例端口', validators=[DataRequired()])
    submit = SubmitField(u'新建')

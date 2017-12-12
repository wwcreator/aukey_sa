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
    server_env = SelectField(u'所属环境', choices=[('1', 'production'),('2', 'test'), ('3', 'dev')], default=1)
    server_tag = StringField(u'标签', validators=[DataRequired()])
    server_os = SelectField(u'系统类型', choices=[('1', u'Linux'), ('2', u'Windows')], default=1)
    server_type = SelectField(u'服务器类型', choices=[('1', u'物理机'),('2', u'虚拟机')], default=1)
    server_loc = StringField(u'机房机架号')
    submit = SubmitField(u'添加')
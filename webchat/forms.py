from wtforms import StringField, PasswordField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email
from flask_wtf import Form
from wtforms.widgets.core import HiddenInput


class RegisterForm(Form):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class LoginForm(Form):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class SubscribeForm(Form):
    channel_id = IntegerField('channel_id', validators=[DataRequired()],
                              widget=HiddenInput())


class UnsubscribeForm(Form):
    channel_id = IntegerField('channel_id', validators=[DataRequired()],
                              widget=HiddenInput())
    return_to = StringField('return_to', validators=[DataRequired()],
                            widget=HiddenInput())


class SendForm(Form):
    text = TextAreaField('text', validators=[DataRequired()])

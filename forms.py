from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerRangeField, IntegerField, \
    SelectField, RadioField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired


# DV1, DV2, DV4
# Server Side form validation configurations
class RegistrationForm(Form):
    uid = StringField('Username',
                      [validators.Length(min=4, max=25), validators.input_required()])
    fname = StringField('First Name', [validators.input_required()])
    lname = StringField('Last Name', [validators.input_required()])
    email = StringField('Email Address', [validators.Email(),
                                          validators.input_required()])
    address = StringField('Address', [validators.input_required()])


class LoginForm(Form):
    uid = StringField('Username',
                      [validators.Length(min=4), validators.input_required()])
    passw = PasswordField('Password', [validators.input_required()])


class ForgotForm(Form):
    email = StringField('Email Address', [validators.Email(),
                                          validators.input_required()])


class ProfileForm(Form):
    uid = StringField('Username')
    fname = StringField('First Name', [validators.input_required()])
    lname = StringField('Last Name', [validators.input_required()])
    email = StringField('Email Address')
    address = StringField('Address', [validators.input_required()])


class PasswordForm(Form):
    appname = StringField('App Name', [validators.input_required()])
    letters = BooleanField('Letters', [validators.input_required()])
    digits = BooleanField('Digits')
    special = BooleanField('Special Chars')
    length = IntegerRangeField('Length', [validators.input_required(), validators.NumberRange(min=6, max=25)])


class AppForm(Form):
    appname = StringField('App Name')
    letters = BooleanField('Letters', [validators.input_required()])
    digits = BooleanField('Digits')
    special = BooleanField('Special Chars')
    length = IntegerRangeField('Length', [validators.input_required(), validators.NumberRange(min=6, max=25)])


class PolicyForm(Form):
    length = IntegerField('Password Length(6-30)', [validators.input_required(),
                                                    validators.NumberRange(min=6, max=30)])
    upper = IntegerField('Uppercase Letters(Min 1)', [validators.input_required(),
                                                      validators.NumberRange(min=1)])
    lower = IntegerField('Lowercase Letters(Min 1)', [validators.input_required(),
                                                      validators.NumberRange(min=1)])
    digits = IntegerField('Digits(Min 1)', [validators.input_required(),
                                            validators.NumberRange(min=1)])
    special = IntegerField('Special Chars(Min 1)', [validators.input_required(),
                                                    validators.NumberRange(min=1)])
    age = IntegerField('Password Retention Period(10-60)', [validators.input_required(),
                                                            validators.NumberRange(min=10, max=60)])


class UploadForm(FlaskForm):
    file = FileField('Upload JSON', validators=[FileAllowed(['json', 'JSON']), FileRequired()])


class ShareForm(Form):
    uid = SelectField('User', coerce=int)
    perms1 = SelectField('Permission', choices=[('v', 'viewer'), ('e', 'editor')])
    perms2 = SelectField('Permission', choices=[('o', 'owner'), ('v', 'viewer'), ('e', 'editor')])
    role = RadioField(choices=[('user', 'user'), ('admin', 'admin')])

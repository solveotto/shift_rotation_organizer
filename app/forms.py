from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField, FloatField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, EqualTo, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CalculationForm(FlaskForm):
    helgetimer = SelectField('Helgetimer', choices=[('0', '0p'), ('0.5', '0.5p'), ('1', '1.0p'), ('1.5', '1.5p')], validators=[DataRequired()])
    helgetimer_dagtid = SelectField('Helgetimer Dagtid', choices=[('0', '0p'), ('0.5', '0.5p'), ('1', '1.0p'), ('1.5', '1.5p')], validators=[DataRequired()])
    natt_helg = SelectField('Natt Helg', choices=[(str(i), f'> {i} vakter') for i in range(0, 11)], validators=[DataRequired()])
    tidlig = SelectField('Tidlig', choices=[(str(i), f'> {i} vakter') for i in range(0, 11)], validators=[DataRequired()])
    before_6 = SelectField('Before 6', choices=[('0', '0p'), ('0.5', '0.5p'), ('1', '1.0p'), ('1.5', '1.5p')], validators=[DataRequired()])
    ettermiddager = SelectField('Ettermiddager', choices=[(str(i), f'> {i} vakter') for i in range(0, 22, 2)], validators=[DataRequired()])
    slutt_for_20 = SelectField('Slutt For 20',  choices=[(str(i), f'> {i} vakter') for i in range(0, 11)], validators=[DataRequired()])
    nights = SelectField('Nights', choices=[(str(i), f'> {i} vakter') for i in range(0, 22, 2)], validators=[DataRequired()])
    submit = SubmitField('Calculate')

# Admin Forms
class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_auth = BooleanField('Admin rights')
    submit = SubmitField('Create User')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('New Password (leave blank to keep current)')
    confirm_password = PasswordField('Confirm New Password')
    is_auth = BooleanField('Admin rights')
    submit = SubmitField('Update User')

    def validate_confirm_password(self, field):
        if self.password.data and not field.data:
            raise ValidationError('Please confirm your new password.')
        if self.password.data and field.data and self.password.data != field.data:
            raise ValidationError('Passwords must match.')


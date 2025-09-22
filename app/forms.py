from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField, FloatField, IntegerField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, NumberRange, EqualTo, ValidationError
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
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

# Turnus Set Management Forms
class CreateTurnusSetForm(FlaskForm):
    name = StringField('Turnus Set Name', 
                      validators=[DataRequired(), Length(min=3, max=100)],
                      render_kw={"placeholder": "e.g., OSL Train Shifts 2025"})
    year_identifier = StringField('Year Identifier', 
                                 validators=[DataRequired(), Length(min=2, max=10)],
                                 render_kw={"placeholder": "e.g., R25, R26"})
    is_active = BooleanField('Set as active turnus set')
    turnus_file = FileField('Turnus JSON File (optional)', 
                           validators=[FileAllowed(['json'], 'JSON files only!')])
    df_file = FileField('DataFrame JSON File (optional)', 
                       validators=[FileAllowed(['json'], 'JSON files only!')])
    submit = SubmitField('Create Turnus Set')

class SelectTurnusSetForm(FlaskForm):
    turnus_set = SelectField('Select Turnus Set', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Switch to Selected Set')
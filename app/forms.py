from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField, FloatField, IntegerField, BooleanField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, EqualTo, ValidationError, Email
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=255)])
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
    email = StringField('Email Address', validators=[Email(message='Please enter a valid email address'), Length(max=255)])
    rullenummer = StringField('Rullenummer (Work ID)', validators=[Length(max=50)])
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
    
    # File handling options
    use_existing_files = BooleanField('Use existing files from turnusfiler directory', 
                                    default=True,
                                    render_kw={"onchange": "toggleFileUploads()"})
    
    # PDF upload option
    pdf_file = FileField('Upload PDF File (to scrape and generate JSON)', 
                        validators=[FileAllowed(['pdf'], 'PDF files only!')])
    
    submit = SubmitField('Create Turnus Set')

class SelectTurnusSetForm(FlaskForm):
    turnus_set = SelectField('Select Turnus Set', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Switch to Selected Set')

# User Profile Forms
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

# Registration Forms
class RegisterForm(FlaskForm):
    """User self-registration form"""
    username = StringField('Username (Display Name)', validators=[
        DataRequired(),
        Length(min=2, max=255, message='Username must be between 2 and 255 characters')
    ])

    rullenummer = StringField('Rullenummer (Work ID)', validators=[
        DataRequired(),
        Length(min=1, max=50, message='Rullenummer is required')
    ])

    email = StringField('Email Address', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address'),
        Length(max=255)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_email(self, field):
        """Custom email validation"""
        email = field.data.lower()
        # Prevent obviously fake emails
        if email.endswith('.test') or email.endswith('.invalid'):
            raise ValidationError('Please use a valid email address.')

class ResendVerificationForm(FlaskForm):
    """Form to resend verification email"""
    email = StringField('Email Address', validators=[
        DataRequired(),
        Email()
    ])
    submit = SubmitField('Resend Verification Email')


class UploadStreklisteForm(FlaskForm):
    """Form for uploading strekliste PDF"""
    pdf_file = FileField('Strekliste PDF', validators=[
        DataRequired(),
        FileAllowed(['pdf'], 'PDF files only!')
    ])
    submit = SubmitField('Upload')


class ForgotPasswordForm(FlaskForm):
    """Form to request password reset email"""
    email = StringField('Email Address', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):
    """Form to set a new password"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
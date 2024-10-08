from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CalculationForm(FlaskForm):
    helgetimer = SelectField('Helgetimer', choices=[('0', '0p'), ('0.5', '0.5p'), ('1', '1.0p'), ('1.5', '1.5p')], validators=[DataRequired()])
    helgetimer_dagtid = SelectField('Helgetimer Dagtid', choices=[('0', '0p'), ('0.5', '0.5p'), ('1', '1.0p'), ('1.5', '1.5p')], validators=[DataRequired()])
    natt_helg = SelectField('Natt Helg', choices=[(str(i), f'> {i} vakter') for i in range(0, 11)], validators=[DataRequired()])
    tidlig = SelectField('Tidlig', choices=[(str(i), f'> {i} vakter') for i in range(0, 11)], validators=[DataRequired()])
    tidlig_poeng = SelectField('Tidlig Poeng', choices=[(str(i), f'{i}p') for i in range(0, 11)], validators=[DataRequired()])
    before_6 = SelectField('Before 6', choices=[('0', '0p'), ('0.5', '0.5p'), ('1', '1.0p'), ('1.5', '1.5p')], validators=[DataRequired()])
    ettermiddager = SelectField('Ettermiddager', choices=[(str(i), f'> {i} vakter') for i in range(0, 22, 2)], validators=[DataRequired()])
    ettermiddager_poeng = SelectField('Ettermiddager Poeng', choices=[(str(i), f'{i}p') for i in range(0, 55, 5)], validators=[DataRequired()])
    slutt_for_20 = SelectField('Slutt For 20',  choices=[(str(i), f'> {i} vakter') for i in range(0, 11)], validators=[DataRequired()])
    nights = SelectField('Nights', choices=[(str(i), f'> {i} vakter') for i in range(0, 22, 2)], validators=[DataRequired()])
    nights_pts = SelectField('Nights Points', choices=[(str(i), f'{i}p') for i in range(0, 55, 5)], validators=[DataRequired()])
    submit = SubmitField('Calculate')


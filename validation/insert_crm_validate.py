from validation import FlaskForm,StringField,IntegerField,DataRequired,NumberRange,Length

class InsertCrmForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(max=25)])
    email = StringField('email', validators=[DataRequired(), Length(max=25)])
    subject = StringField('subject', validators=[DataRequired(), Length(max=25)])
    department = StringField('department', validators=[ Length(max=25)])
    # department = StringField('department', validators=[DataRequired(), Length(max=25)])
    priority = IntegerField('priority', validators=[DataRequired(), NumberRange(min=0, max=3)])
    message = StringField('message', validators=[DataRequired(), Length(max=100)])

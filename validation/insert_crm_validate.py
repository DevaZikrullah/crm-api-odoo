from validation import FlaskForm,StringField,IntegerField,DataRequired,NumberRange,Length

class InsertCrmForm(FlaskForm):
    firstname = StringField('firstname', validators=[DataRequired(), Length(max=255)])
    lastname = StringField('lastname', validators=[DataRequired(), Length(max=255)])
    email = StringField('email', validators=[DataRequired(), Length(max=255)])
    country = StringField('country', validators=[DataRequired(), Length(max=255)])
    phone = StringField('phone', validators=[ Length(max=255)])
    request = StringField('request', validators=[DataRequired(), Length(max=25)])
    priority = IntegerField('priority', validators=[DataRequired(), NumberRange(min=0, max=3)])
    product = StringField('product', validators=[DataRequired(), Length(max=255)])

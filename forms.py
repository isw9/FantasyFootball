from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

seasons=[(2018, 2018), (2017, 2017), (2016, 2016), (2015, 2015), (2014, 2014), (2013, 2013),
        (2012, 2012), (2011, 2011), (2010, 2010)]
all_seasons=[(2019, 2019), (2018, 2018), (2017, 2017), (2016, 2016), (2015, 2015), (2014, 2014), (2013, 2013),
        (2012, 2012), (2011, 2011), (2010, 2010)]
weeks=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9),
        (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17)]
numberResultsChoices = [(5, 5), (10, 10), (20, 20), (50, 50)]

class PlayerProjectionForm(FlaskForm):
    playerName = StringField('Player Name', validators=[DataRequired()])
    season = SelectField('Season', choices=all_seasons, coerce=int, validators=[DataRequired()])
    week = SelectField('Week Number', choices=weeks, coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

class PlayerComparisonForm(FlaskForm):
    playerNameOne = StringField('Player Name', validators=[DataRequired()])
    playerNameTwo = StringField('Player Name', validators=[DataRequired()])
    season = SelectField('Season', choices=all_seasons, coerce=int, validators=[DataRequired()])
    week = SelectField('Week Number', choices=weeks, coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

class LeadersForm(FlaskForm):
    season = SelectField('Season', choices=seasons, coerce=int, validators=[DataRequired()])
    numberResults = SelectField('Number Results', choices=numberResultsChoices, coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

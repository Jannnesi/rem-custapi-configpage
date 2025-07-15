# app/customers/forms.py   (or a separate base_column_forms.py)
from flask_wtf import FlaskForm
from wtforms import (
    EmailField,
    FieldList,
    FormField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional


# app/customers/forms.py
class BaseColumnForm(FlaskForm):
    order = IntegerField("Row order", validators=[DataRequired(), NumberRange(min=1, max=999)])
    key = StringField("Column key", validators=[DataRequired(), Length(max=100)])
    name = StringField("Display name", validators=[DataRequired(), Length(max=255)])
    dtype = SelectField(
        "Data type",
        choices=[("string", "string"), ("float", "float"), ("int", "int")],
        validators=[DataRequired()],
    )
    length = IntegerField("Length", validators=[Optional(), NumberRange(min=1, max=4000)])
    decimals = IntegerField("Decimals", validators=[Optional(), NumberRange(min=0, max=10)])


class BaseColumnListForm(FlaskForm):
    columns = FieldList(FormField(BaseColumnForm), min_entries=0)


class EmailEntryForm(FlaskForm):
    address = EmailField("Sähköposti", validators=[DataRequired(), Email(), Length(max=255)])
    display_name = StringField("Näyttönimi", validators=[DataRequired(), Length(max=100)])


class GeneralSettingsForm(FlaskForm):
    retry_attempts = IntegerField(
        "Uudelleenyritysten määrä", validators=[DataRequired(), NumberRange(min=0)]
    )
    retry_delay = IntegerField(
        "Uudelleenyritysten väli (sekunteina)", validators=[DataRequired(), NumberRange(min=0)]
    )
    emails = FieldList(FormField(EmailEntryForm), min_entries=1)
    submit = SubmitField("Tallenna")

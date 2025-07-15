from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FieldList,
    FormField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, Optional


class ExtraColumnForm(FlaskForm):
    key = StringField("Column key", validators=[Optional(), Length(max=100)])
    name = StringField("Display name", validators=[Optional(), Length(max=100)])
    dtype = StringField("Data type", validators=[Optional(), Length(max=50)])


def parse_int_list(value):
    """
    Turn "2208, 1234"  ➜ [2208, 1234]
         ["2208","1234"] ➜ [2208, 1234]   (already a list)
         None           ➜ []
    """
    if value is None:
        return []

    # If we've been passed a list/tuple (e.g. obj=customer on GET)
    if isinstance(value, (list | tuple)):
        iterable = value
    else:
        iterable = value.split(",")

    out: list[int] = []
    for item in iterable:
        s = str(item).strip()
        if not s:
            continue
        try:
            out.append(int(s))
        except ValueError:
            # Skip or raise depending on how strict you want to be
            continue
    return out


class CustomerForm(FlaskForm):
    name = StringField("Customer Name", validators=[DataRequired(), Length(max=100)])
    konserni = StringField(
        "Konserni IDs",
        validators=[DataRequired(), Length(max=100)],
        filters=[parse_int_list],
        description="Comma-separated list of integer IDs, e.g. 2208,1234",
    )
    source_container = StringField("Source Container", validators=[DataRequired(), Length(max=100)])
    destination_container = StringField(
        "Destination Container", validators=[DataRequired(), Length(max=100)]
    )
    file_format = SelectField(
        "File Format", choices=[("csv", "CSV"), ("json", "JSON")], validators=[DataRequired()]
    )
    file_encoding = SelectField(
        "File Encoding",
        choices=[
            ("utf-8", "UTF-8"),
            ("iso-8859-1", "ISO-8859-1"),
            ("windows-1252", "Windows-1252"),
        ],
        validators=[DataRequired()],
    )
    extra_columns = FieldList(
        FormField(ExtraColumnForm), min_entries=0, label="Extra Columns", validators=[Optional()]
    )
    exclude_columns = FieldList(
        StringField("Column to Exclude", validators=[Optional(), Length(max=100)]),
        min_entries=0,
        label="Exclude Columns",
        validators=[Optional()],
    )
    enabled = BooleanField("Enabled")
    submit = SubmitField("Save")

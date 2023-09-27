from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, ValidationError, URL
from flask_ckeditor import CKEditorField
import json

# Load the JSON data from the file
with open('templates/baguio_city_barangays.json', 'r') as json_file:
    barangay_choices = json.load(json_file)

# Extract the "BARANGAY" values from the JSON data
all_barangay_choices = [entry["BARANGAY"] for entry in barangay_choices]

def no_spaces_only(form, field):
    if field.data.strip() == "":
        raise ValidationError("Field cannot contain spaces only")

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class RegisterForm(FlaskForm):

    fname = StringField("First Name", validators=[DataRequired(), no_spaces_only])
    mname = StringField("Middle Name", validators=[DataRequired(), no_spaces_only])
    lname = StringField("Last Name", validators=[DataRequired(), no_spaces_only])
    username = StringField("Username", validators=[DataRequired(), no_spaces_only])
    password = PasswordField("Password", validators=[DataRequired(), no_spaces_only])
    submit = SubmitField("Sign Me Up!")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class AddCase(FlaskForm):
    case_no = StringField("Case Number", validators=[DataRequired(), no_spaces_only])
    case_title = TextAreaField("Case Title", validators=[DataRequired(), no_spaces_only])
    complainant_name = TextAreaField("Name of Complainant", validators=[DataRequired(), no_spaces_only])
    contact_complainant = StringField("Contact Information", validators=[DataRequired(), no_spaces_only])
    address_complainant = StringField("Address of Complainant", validators=[DataRequired(), no_spaces_only])
    respondent_name = TextAreaField("Name of Respondent", validators=[DataRequired(), no_spaces_only])
    contact_respondent = StringField("Contact Information", validators=[DataRequired(), no_spaces_only])
    address_respondent = StringField("Address of Respondent", validators=[DataRequired(), no_spaces_only])
    location_of_structure = StringField("Location of Subject Structure", validators=[DataRequired(), no_spaces_only])
    barangay = SelectField("Barangay", validators=[DataRequired()], choices=[(choice, choice) for choice in all_barangay_choices])
    inves_report = FileField("Investigation Report", validators=[DataRequired()])

class EditCase(FlaskForm):
    case_no = StringField("Case Number")
    case_title = TextAreaField("Case Title", validators=[DataRequired(), no_spaces_only])
    complainant_name = TextAreaField("Name of Complainant", validators=[DataRequired(), no_spaces_only])
    contact_complainant = StringField("Contact Information", validators=[DataRequired(), no_spaces_only])
    address_complainant = StringField("Address of Complainant", validators=[DataRequired(), no_spaces_only])
    respondent_name = TextAreaField("Name of Respondent", validators=[DataRequired(), no_spaces_only])
    contact_respondent = StringField("Contact Information", validators=[DataRequired(), no_spaces_only])
    address_respondent = StringField("Address of Respondent", validators=[DataRequired(), no_spaces_only])
    location_of_structure = StringField("Location of Subject Structure", validators=[DataRequired(), no_spaces_only])
    barangay = SelectField("Barangay", validators=[DataRequired()], choices=[(choice, choice) for choice in all_barangay_choices])

class AddFile(FlaskForm):
    file_type = SelectField("", validators=[DataRequired()], choices=[
        ('Investigation Report', 'Investigation Report'),
        ('Resolution', 'Resolution'),
        ('Minutes of Meeting', 'Minutes of Meeting'),
        ('Audio File', 'Audio File'),
        ('Position Paper - Complainant', 'Position Paper - Complainant'),
        ('Position Paper - Respondent', 'Position Paper - Respondent'),
        ('Post Demolition Report', 'Post Demolition Report'),
        ('Notice of Meeting', 'Notice of Meeting'),
        ('Others', 'Others')
        # Add more options as needed
    ])
    files = FileField("File Upload", validators=[DataRequired()])

class Schedule(FlaskForm):
    schedule = DateField('Date', validators=[DataRequired()])



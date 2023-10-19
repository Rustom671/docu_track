from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, ValidationError, URL
from flask_ckeditor import CKEditorField
import json

# Load the JSON data from the file
with open('templates/baguio_city_barangays.json', 'r') as json_file:
    barangay_choices = json.load(json_file)

# Extract the "BARANGAY" values from the JSON data
all_barangay_choices = [(entry["ID"], entry["BARANGAY"]) for entry in barangay_choices]

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
    office = StringField("Office", validators=[DataRequired(), no_spaces_only])
    contact = StringField("Contact Number", validators=[DataRequired(), no_spaces_only])
    user_type = SelectField("User Type", validators=[DataRequired()], choices=[
        ('', 'Select User Type'),
        ('1', 'Admin'),
        ('2', 'Secretariat'),
        ('3', 'Member')
        # Add more options as needed
    ])
    coerce = str,  # Coerce values to strings
    default = ''  # Set the default value to the empty string
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
    barangay = SelectField("Barangay", validators=[DataRequired()], choices=all_barangay_choices)
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
    barangay = SelectField("Barangay", validators=[DataRequired()], choices=all_barangay_choices)

class AddFile(FlaskForm):
    file_type = SelectField("", validators=[DataRequired()], choices=[
        ('1', 'Investigation Report'),
        ('2', 'Resolution'),
        ('3', 'Minutes of Meeting'),
        ('4', 'Audio File'),
        ('5', 'Position Paper - Complainant'),
        ('6', 'Position Paper - Respondent'),
        ('7', 'Post Demolition Report'),
        ('8', 'Notice of Meeting'),
        ('9', 'Notice for Position Paper'),
        ('10', 'Others')
        # Add more options as needed
    ])
    files = FileField("File Upload", validators=[DataRequired()])

class EditStatus(FlaskForm):
    status = SelectField("", validators=[DataRequired()], choices=[
        ('1', 'Pending'),
        ('2', 'Archived'),
        ('3', 'Dismissed'),
        ('4', 'For Demolition'),
        ('5', 'Structure Demolished')
        # Add more options as needed
    ])
    remarks = TextAreaField("Remarks", validators=[DataRequired()])

class Schedule(FlaskForm):
    schedule = DateField('Date', validators=[DataRequired()])
    remarks =  TextAreaField("Remarks", validators=[DataRequired(), no_spaces_only])



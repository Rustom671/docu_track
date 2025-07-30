from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, ValidationError, URL
from flask_ckeditor import CKEditorField
import json

# Load the JSON data from the file
with open('templates/baguio_city_barangays.json', 'r') as json_file:
    barangay_choices = json.load(json_file)

# Load the JSON data from the file
with open('templates/employee.json', 'r') as json_file:
    employees = json.load(json_file)

# Load the JSON data from the file
with open('templates/products.json', 'r') as json_file:
    products = json.load(json_file)

# Load the JSON data from the file
with open('templates/position.json', 'r') as json_file:
    position = json.load(json_file)

# Extract the "BARANGAY" values from the JSON data
all_barangay_choices = [(entry["ID"], entry["BARANGAY"]) for entry in barangay_choices]
# Extract the "Name" values from the JSON data
all_employees = [(entry["ID"], entry["Name"]) for entry in employees]
# Extract the "Product" values from the JSON data
all_products = [(entry["ID"], f"{entry['Product']} - ( {entry['Quantity']} )") for entry in products]
# Extract the "Position" values from the JSON data
all_position = [(entry["ID"], f"{entry['Position']}") for entry in position]

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
    division = StringField("Division", validators=[DataRequired(), no_spaces_only])
    contact = StringField("Contact Number", validators=[DataRequired(), no_spaces_only])
    user_type = SelectField("User Type", validators=[DataRequired()], choices=[
        ('', 'Select User Type'),
        ('1', 'Administrator'),
        ('2', 'Supply Officer'),
        ('3', 'Employee')
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

class AddNewEmployee(FlaskForm):
    emp_lname = TextAreaField("Last Name", validators=[DataRequired(), no_spaces_only])
    emp_fname = TextAreaField("First Name", validators=[DataRequired(), no_spaces_only])
    emp_mname = TextAreaField("Middle Initial", validators=[DataRequired(), no_spaces_only])
    emp_position = SelectField("Position", validators=[DataRequired()], choices=all_position)
    emp_division = SelectField("Division", validators=[DataRequired()], choices=[
        ('1', 'Administrative Division'),
        ('2', 'Market Division'),
        ('3', 'Real Property Tax Division'),
        ('4', 'Business Taxes and Fees Division'),
        ('5', 'Campaign and Investigation Division'),
        ('6', 'Cash Division'),
        ('7', 'Treasury Operations Review Unit')

        # Add more options as needed
    ])
    emp_gender = SelectField("Gender", validators=[DataRequired()], choices=[
        ('1', 'Male'),
        ('2', 'Female')
        # Add more options as needed
    ])

class EditCase(FlaskForm):
    case_no = StringField("Case Number")
    case_title = TextAreaField("Case Title", validators=[DataRequired(), no_spaces_only])
    case_category = SelectField("", validators=[DataRequired()], choices=[
        ('1', 'Registered Land'),
        ('2', 'Unregistered Land'),
        ('3', 'Road Right-of-Way (RROW)'),
        ('4', 'Forest Reservation and Greenbelt Area'),
        ('5', 'Watershed'),
        ('6', 'Esteros and Waterway'),
        ('7', 'Military Reservation'),
        ('8', 'Government Reservation'),
        ('9', 'City / Barangay Needs'),
        ('10', 'Others')
        # Add more options as needed
    ])
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
        ('1', 'IT Equipment - Computer Set'),
        ('2', 'IT Equipment - Laptop'),
        ('3', 'IT Equipment - Keyboard'),
        ('4', 'IT Equipment - Mouse'),
        ('5', 'IT Equipment - AVR'),
        ('6', 'IT Equipment - Power Supply'),
        ('7', 'Furniture - Table'),
        ('8', 'Furniture - Chair'),
        ('9', 'Furniture - Cabinet'),
        ('10', 'Stapler'),
        ('11', 'Others')
        # Add more options as needed
    ])
    files = FileField("File Upload", validators=[DataRequired()])

class EditStatus(FlaskForm):
    status = SelectField("", validators=[DataRequired()], choices=[
        ('1', 'Pending'),
        ('2', 'Archived'),
        ('3', 'Dismissed'),
        ('4', 'For Demolition'),
        ('5', 'Structure Demolished'),
        ('6', 'Defer'),
        ('7', 'For Resolution')

        # Add more options as needed
    ])
    remarks = TextAreaField("Remarks")

class RequestItem(FlaskForm):
    employee = SelectField("Recipient", validators=[DataRequired()], choices=all_employees)
    item = SelectField("Item", validators=[DataRequired()], choices=all_products)
    quantity = StringField("Quantity", validators=[DataRequired(), no_spaces_only])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item.choices = get_products()  # Load choices dynamically
        self.employee.choices = get_employees()

class IssueItem(FlaskForm):
    employee = SelectField("Recipient", validators=[DataRequired()], choices=all_employees)
    item = SelectField("Item", validators=[DataRequired()], choices=all_products)
    quantity = StringField("Quantity", validators=[DataRequired(), no_spaces_only])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item.choices = get_products()  # Load choices dynamically
        self.employee.choices = get_employees()

def get_products():
    """Load products from JSON file dynamically."""
    # Load products from JSON file dynamically
    with open('templates/products.json', 'r') as json_file:
        product_list = json.load(json_file)

    # Sort products alphabetically by Product name
    sorted_products = sorted(product_list, key=lambda x: x['Product'].lower())

    # Format choices as (ID, "Product - (Quantity)")
    return [(entry["ID"], f"{entry['Product']}  ( {entry['Quantity']} )") for entry in sorted_products]

def get_employees():
    """Load products from JSON file dynamically."""
    # Load products from JSON file dynamically
    with open('templates/employee.json', 'r') as json_file:
        employees_list = json.load(json_file)

    # Sort names alphabetically by Name
    sorted_employees = sorted(employees_list, key=lambda x: x['Name'].lower())

    # Format choices as ("Name")
    return [(entry["ID"], f"{entry['Name']}") for entry in sorted_employees]

class AddExistingItem(FlaskForm):
    item = SelectField("Item", validators=[DataRequired()], choices=all_products)
    quantity = StringField("Quantity", validators=[DataRequired(), no_spaces_only])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item.choices = get_products()  # Load choices dynamically

class AddNewItem(FlaskForm):
    item = StringField("Item", validators=[DataRequired(), no_spaces_only])
    quantity = StringField("Quantity", validators=[DataRequired(), no_spaces_only])

class ReplaceFile(FlaskForm):
    files = FileField("File Upload", validators=[DataRequired()])

# class Schedule(FlaskForm):
#     schedule = DateField('Date', validators=[DataRequired()])
#     sched_remarks = TextAreaField("Remarks", validators=[DataRequired(), no_spaces_only])



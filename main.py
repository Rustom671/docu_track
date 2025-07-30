from flask import Flask, render_template, redirect, url_for, flash
from sqlalchemy import text, distinct, or_, func, event
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm, LoginForm, AddFile, EditCase, EditStatus, ReplaceFile, IssueItem, AddNewItem, AddExistingItem, RequestItem
from flask_wtf.csrf import generate_csrf
from flask import request
import os
import json
from AddExistingItem import addexistingitem
from AddNewItem import addnewitem
from IssueItem import issueitem
from AddEmployee import addnewemployee
from models import db, User, Document, IssuedItems, Notes, ckeditor
from collections import defaultdict


app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:baguioCAISC2023**@localhost/document_track'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/document_track'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'


db.init_app(app)
migrate = Migrate(app, db)
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)


# Define the upload folder where files will be saved
UPLOAD_FOLDER = 'static/documents'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'jpg', 'png', 'gif', 'bmp', 'jpeg', 'mp3', 'wav', 'ogg', 'flac'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define the path to your JSON file
JSON_FILE_PATH_PRODUCTS = 'templates/products.json'


# Function to create a default administrator user
def create_default_admin_user(*args, **kwargs):

    # Check if the admin user already exists
    admin_exists = User.query.filter_by(username='admin').first()

    if admin_exists:
        print("Admin user already exists. No new admin will be created.")
        return  # Exit the function early if admin already exists

    # Admin user doesn't exist, create a new one
    default_password = "admin"
    hash_and_salted_password = generate_password_hash(
        default_password,
        method='pbkdf2:sha256',
        salt_length=8
    )

    admin_user = User(
        user_lname='Admin',
        user_fname='Administrator',
        username='admin',
        password=hash_and_salted_password,
        type='1',
        division='Administrative',
        contact='09664335610'
    )
    db.session.add(admin_user)
    db.session.commit()
    print("Admin user created!")


with app.app_context():
    create_default_admin_user()  # ✅ Run this safely
    print("success DB")



@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def get_all_posts():
    form = RequestItem()
    return render_template("index.html", form=form)


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    csrf_token = generate_csrf()
    if form.validate_on_submit():

        # Execute the query
        query = text("SELECT * FROM user WHERE username = :username")
        user_name = request.form.get('username')
        # Fetch the result
        result = db.session.execute(query, {'username': user_name}).fetchone()

        # Return True if the username exists, False otherwise
        if result:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        else:
            try:
                hash_and_salted_password = generate_password_hash(
                    request.form.get('password'),
                    method='pbkdf2:sha256',
                    salt_length=8
                )
                # Execute the query to insert the user
                query = text("INSERT INTO user (user_lname, user_fname, user_mname, division, contact, status, type, date_created, username, password) "
                             "VALUES (:lname, :fname, :mname, :division, :contact, :status, :user_type, :today, :username, :password)")

                last_name = request.form.get('lname')
                first_name = request.form.get('fname')
                middle_name = request.form.get('mname')
                division_add = request.form.get('division')
                contact_num = request.form.get('contact')
                stat = "1"
                usertype = request.form.get('user_type')
                today = date.today()

                values = {
                    'lname': last_name,
                    'fname': first_name,
                    'mname': middle_name,
                    'division': division_add,
                    'contact': contact_num,
                    'status': stat,
                    'user_type': usertype,
                    'today': today,
                    'username': user_name,
                    'password': hash_and_salted_password
                }

                db.session.execute(query, values)

                # Commit the changes and close the database connection
                db.session.commit()


                print("User registered successfully!")
                flash("User registered successfully!")
                return redirect(url_for("login"))
            except Exception as e:
                flash(f"An error occurred while registering user: {str(e)}")
                db.session.rollback()

    return render_template("register.html", current_user=current_user, form=form, csrf_token=csrf_token)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    csrf_token = generate_csrf()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data

        # Find user by username entered.
        user = User.query.filter_by(username = user_name).first()
        if not user:
            flash("That username does not exist, please try again.")
            return redirect(url_for('login'))
            # Password incorrect
        if not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        # Email exists and password correct
        if user.status == "1":
            flash('This account is inactive. Please contact administrator for activation.')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=True)

            return redirect(url_for("user_dashboard"))

    return render_template("login.html", current_user=current_user, form=form, csrf_token=csrf_token)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def custom_pagination(current_page, total_pages, max_display):
    half_max = (max_display - 1) // 2
    start = max(current_page - half_max, 1)
    end = min(start + max_display - 1, total_pages)
    return range(start, end + 1)

def load_employees_from_json():
    """Load employees from a JSON file."""
    with open("templates/employee.json", "r", encoding="utf-8") as file:
        return json.load(file)

def load_products_from_json():
    """Load employees from a JSON file."""
    with open("templates/products.json", "r", encoding="utf-8") as file:
        return json.load(file)

def load_position_from_json():
    """Load employees from a JSON file."""
    with open("templates/position.json", "r", encoding="utf-8") as file:
        return json.load(file)

def save_employees_to_json(employees):
    """Save employees to a JSON file."""
    with open("templates/employee.json", "w", encoding="utf-8") as file:
        json.dump(employees, file, indent=4)

def paginate_items(items, page, per_page):
    """Manually paginate a list of items."""
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = items[start:end]
    total_pages = -(-len(items) // per_page)  # Equivalent to math.ceil(len(items) / per_page)
    return paginated_items, total_pages

@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def user_dashboard():
    form = IssueItem()
    form1 = AddExistingItem()
    form2 = AddNewItem()

    csrf_token = generate_csrf()
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of employees per page

    # Get the search term from the query parameters
    search_term = request.args.get('search', '').lower()
    all_employees = load_employees_from_json()

    # Filter employees based on search term
    if search_term:
        employees = [emp for emp in all_employees if search_term in emp.get("Name", "").lower()]
    else:
        employees = all_employees

    # Paginate the filtered employees
    employees_paginated, total_pages = paginate_items(employees, page, per_page)

    # Generate pagination range
    max_display_pages = 3
    pagination_range = custom_pagination(page, total_pages, max_display_pages)

    # Generate a URL for resetting the search
    reset_search_url = url_for('user_dashboard', page=1)

    return render_template("user_dashboard.html",
                           current_user=current_user,
                           current_page=page,
                           total_pages=total_pages,
                           employees_paginated=employees_paginated,
                           pagination_range=pagination_range,
                           search_term=search_term,
                           reset_search_url=reset_search_url,
                           form=form, form1=form1, form2=form2, csrf_token=csrf_token)


def save_documents(emp_number):
    # Logic to save documents associated with the given case number
    # Upload file and file path
    form = AddFile()
    uploaded_file = form.files.data
    if uploaded_file.filename != '' and allowed_file(uploaded_file.filename):
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = secure_filename(uploaded_file.filename)
        unique_filename = f"{current_time}_{filename}"

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        uploaded_file.save(file_path)

        new_document = Document(file_path=file_path)

        # Execute the query to insert the document
        query2 = text("INSERT INTO documents (emp_id, user_id, document_type, file_path, upload_date) "
                      "VALUES (:emp_id, :user_id, :docu_type, :path_file, :date_of_upload)")
        #
        user_id = current_user.id
        doc_type = "1"
        path = new_document.file_path  # Get the file path from the new_document object
        date_upload = datetime.today()

        values2 = {
            'user_id': user_id,
            'emp_id': emp_number,
            'docu_type': doc_type,
            'path_file': path,
            'date_of_upload': date_upload,
        }

        result = db.session.execute(query2, values2)


        # new_action = AuditTrail(user_id=current_user.id, case_id=emp_number, action_id=1, action=path,
        #                         action_date=date_upload)
        db.session.add(result)
        # db.session.add(new_action)
        # Commit the changes and close the database connection
        db.session.commit()
    else:
        flash("File extension not valid")
        return redirect(url_for('employee'))



# @app.route('/EditCase', methods=["GET", "POST"])
# @login_required
# def edit_case():
#     form = EditCase()
#     replace = ReplaceFile()
#     csrf_token = generate_csrf()
#     case_number = request.args.get('case_no')
#     case = Cases.query.filter_by(id=case_number).first()  # Fetch the case based on case_no
#     documents = Document.query.filter_by(case_id=case_number).all()
#     today = datetime.today()
#     # Fetch all user
#     users = User.query.all()
#
#     if form.validate_on_submit():
#         try:
#             if case:
#                 # Update the existing case
#
#                 case.case_title = request.form.get('case_title').strip()
#                 case.case_complainant = request.form.get('complainant_name').strip()
#                 case.category = request.form.get('case_category')
#                 case.address_complainant = request.form.get('address_complainant').strip()
#                 case.contact_complainant = request.form.get('contact_complainant').strip()
#                 case.case_respondent = request.form.get('respondent_name').strip()
#                 case.address_respondent = request.form.get('address_respondent').strip()
#                 case.contact_respondent = request.form.get('contact_respondent').strip()
#                 case.location = request.form.get('location_of_structure').strip()
#                 case.barangay = request.form.get('barangay')
#                 case_id = case.id
#                 #
#                 new_action = AuditTrail(user_id=current_user.id, case_id=case_id, action_id=2,
#                                         action_date=today)
#                 db.session.add(new_action)
#
#                 db.session.commit()
#                 #
#                 #
#                 flash("Case saved!")
#                 return redirect(url_for("case", case_no=case_number))
#             else:
#                 flash("This case does not exist. Please provide a unique number.")
#                 return redirect(url_for('add_case'))
#         except Exception as e:
#             flash(f"An error occurred editing the case: {str(e)}")
#             db.session.rollback()  # Rollback the transaction if an exception occurs
#
#     return render_template("edit_case.html", current_user=current_user, form=form, case=case, csrf_token=csrf_token, case_no=case_number, docu=documents, user=users, replace_form=replace)

def get_employee_data_by_id(employee_id):
    """Search for an employee by ID and return all their details as a dictionary."""
    employees = load_employees_from_json()
    employee = next((emp for emp in employees if str(emp.get("ID")) == str(employee_id)), None)
    return employee if employee else None  # Return the full employee details if found, else None

def format_date(value):
    if isinstance(value, str):  # Convert string to date
        value = datetime.strptime(value, "%Y-%m-%d").date()
    return value.strftime("%B %d, %Y")  # Format correctly

app.jinja_env.filters["format_date"] = format_date

@app.route('/employee', methods=["GET", "POST"])
@login_required
def employee():
    form = AddFile()
    form1 = EditStatus()
    # form2 = Schedule()
    csrf_token = generate_csrf()
    employee_no = request.args.get('emp_no')
    all_products = load_products_from_json()
    all_position = load_position_from_json()

    if employee_no:  # Ensure employee_no is not None
        emp_data = get_employee_data_by_id(employee_no)
        if not emp_data:
            emp_error = "Employee Not Found"
    else:
        emp_error = "Invalid Employee ID"

    # Fetch all documents for the specified case
    documents = Document.query.filter_by(emp_id=employee_no).all()
    history_raw =  IssuedItems.query.filter_by(emp_id=employee_no).all()
    #reverse the order
    history = history_raw[::-1][:10]

    #top 5
    # Query data from the database
    history_raw = IssuedItems.query.filter_by(emp_id=employee_no).all()

    # Dictionary to store total quantity per item_id
    item_quantity = defaultdict(int)

    # Loop through history_raw and sum quantities for the same item_id
    for item in history_raw:
        item_quantity[item.item_id] += item.q_issued

    # Sort items by total quantity in descending order and get the top 5
    top_items = sorted(item_quantity.items(), key=lambda x: x[1], reverse=True)[:5]

    # Convert to a dictionary for easy access
    top_items_dict = {f"item_{i + 1}": {"item_id": item_id, "quantity": quantity} for i, (item_id, quantity) in
                      enumerate(top_items)}
    #end of top 5

    existing_note = Notes.query.filter(
        (Notes.emp_id == employee_no) &
        (Notes.user_id == current_user.id)
    ).first()

    # existing_summary = Summary.query.filter(
    #     Summary.case_id == employee_no).first()

    if form.validate_on_submit():
        try:
            # Upload file and file path
            uploaded_file = form.files.data
            docum_type = form.file_type.data

            if uploaded_file.filename != '' and allowed_file(uploaded_file.filename):
                current_time = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = secure_filename(uploaded_file.filename)
                unique_filename = f"{current_time}_{filename}"

                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                uploaded_file.save(file_path)

                new_document = Document(file_path=file_path)

                # Execute the query to insert the document
                query2 = text("INSERT INTO documents (emp_id, user_id, document_type, file_path, upload_date) "
                              "VALUES (:case_id, :user_id, :docu_type, :path_file, :date_of_upload)")
                #
                user_id = current_user.id
                doc_type = docum_type
                path = new_document.file_path  # Get the file path from the new_document object
                date_upload = datetime.today()

                values2 = {
                    'case_id': employee_no,
                    'user_id': user_id,
                    'docu_type': doc_type,
                    'path_file': path,
                    'date_of_upload': date_upload,
                }

                db.session.execute(query2, values2)
                # new_action = AuditTrail(user_id=current_user.id, case_id=employee_no, action_id=3, action=path,
                #                         action_date=date_upload)
                # db.session.add(new_action)

                # Commit the changes to the database
                db.session.commit()

                flash("File saved successfully!")  # Flash a success message
                return redirect(url_for('employee', emp_no=employee_no))  # Redirect back to the page with the updated content
            else:
                flash("File extension not valid")
                return redirect(url_for('employee', emp_no=employee_no))


        except Exception as e:
            db.session.rollback()  # Rollback the transaction
            error_message = str(e)  # Convert exception to string
            flash(f"Error saving file: {error_message}", "danger")  # Display the specific error
            print(f"File Upload Error: {error_message}")  # Print error to console (for debugging)
            return redirect(url_for('employee', emp_no=employee_no))

    return render_template("employee.html",
                           employee_no=employee_no,
                           emp_data=emp_data,
                           docu=documents,
                           hist=history,
                           product=all_products,
                           position=all_position,
                           form=form,
                           form1=form1,
                           csrf_token=csrf_token,
                           notes=existing_note,
                           summary="summary",
                           top_items=top_items_dict
                           )

@app.route('/schedule', methods=["GET", "POST"])
@login_required
def schedule():

    case_number = request.args.get('case_no')
    case = Cases.query.filter_by(id=case_number).first()  # Fetch the case based on case_no
    time_changed = datetime.today()
    today = datetime.today()

    if request.method == 'POST':
        try:
            schedule_date = request.form.get('schedule')  # Access the date picker value from the form data
            remarks = request.form.get('remarks')
            schedule_date_obj = datetime.strptime(schedule_date, '%m/%d/%Y')
            formatted_schedule_date = schedule_date_obj.strftime('%Y-%m-%d')

            existing_schedule = Schedule.query.filter_by(case_id=case_number).first()
            update_status = Cases.query.filter_by(id=case_number).first()

            if existing_schedule:
                # Case with the same case number already exists, update the schedule
                existing_schedule.schedule = formatted_schedule_date
                existing_schedule.remarks = remarks
                #existing_schedule.case_title = update_status.case_title
                update_status.status = "8"
                new_status = Status(case_id=case_number, remarks=remarks, status_date=time_changed, status="8")
                db.session.add(new_status)
            else:
                # Case with the case number doesn't exist, add a new row
                new_schedule = Schedule(case_id=case_number, schedule=formatted_schedule_date, remarks=remarks)
                update_status.status = "8"
                db.session.add(new_schedule)
                new_status = Status(case_id=case.id, remarks=remarks, status_date=time_changed, status="8")
                db.session.add(new_status)

            new_action = AuditTrail(user_id=current_user.id, case_id=case_number, action_id=4, action=formatted_schedule_date,
                                    action_date=today)
            db.session.add(new_action)

            db.session.commit()
            flash("Schedule successfully updated!")

            # Debugging statements
            # print(f"Debug: Case number - {case_number}")
            # print(f"Debug: Existing Schedule - { schedule_date }")
            # print(f"Debug: Updated Status - {update_status.status}")

            flash("Schedule successfully updated!")

        except Exception as e:
            # Handle any exceptions that may occur during the database operation
            db.session.rollback()  # Rollback the transaction
            flash(f"An error occurred while saving the schedule: {str(e)}")# Flash an error message

        return redirect(url_for('case', case_no=case_number))


@app.route('/scheduled', methods=["GET", "POST"])
@login_required
def scheduled():

    # all schedule
    all_schedule = db.session.query(Schedule).all()
    #all cases
    query = text("SELECT * FROM cases WHERE status = 8")
    result_set = db.session.execute(query)

    # Fetch all rows from the result set
    all_case = result_set.fetchall()

    # Query for unique case_id values
    unique_schedule = db.session.query(distinct(Schedule.schedule)).all()

    # Extract the unique case_id values from the result
    unique_schedule = [schedule[0] for schedule in unique_schedule]

    # Sort the dates directly
    unique_schedule = sorted(unique_schedule)


    return render_template("scheduled.html",
                           schedule_date=unique_schedule,
                           all_schedule = all_schedule,
                           all_case = all_case,
                           get_title=get_title,
                           get_number=get_number)

def get_barangay_name(id):
    # Load the JSON data from the file
    with open('templates/baguio_city_barangays.json', 'r') as json_file:
        barangay_choices = json.load(json_file)

    # Find the entry with the matching ID and return its BARANGAY
    for entry in barangay_choices:
        if entry["ID"] == id:
            return entry["BARANGAY"]

    # If no match is found, return a default value or handle the case as needed
    return "Unknown Barangay"  # You can customize this default value


@app.route('/accounts', methods=["GET", "POST"])
@login_required
def accounts():
    page = request.args.get('page', 1, type=int)
    page = max(1, page)  # Ensure the page is not less than 1
    per_page = 10  # Number of accounts per page
    today = datetime.now()
    # Get the search term from the query parameters with a default value of an empty string
    search_term = request.args.get('searchUser', '')

    # Your SQL query here
    if search_term:
        users_query = db.session.query(User).filter(
            User.status.isnot(None),
            or_(
                User.user_fname.ilike(f'%{search_term}%'),
                User.user_lname.ilike(f'%{search_term}%'),
                User.user_mname.ilike(f'%{search_term}%'),
                User.office.ilike(f'%{search_term}%'),
                User.status.ilike(f'%{search_term}%'),
                User.type.ilike(f'%{search_term}%')
            )
        )
    else:
        # If no search term is provided, retrieve all cases
        users_query = User.query
    if request.method == 'POST':
        user_id = request.args.get('user_id')  # Retrieve user ID from the form
        user = User.query.filter_by(id=user_id).first()
        print(user_id)
        try:
            if user.status == "1":
                user.status = "2"
                flash("User activated successfully!")
                # new_action = AuditTrail(user_id=current_user.id, action_id=6, action=2,
                #                         action_date=today)
                # db.session.add(new_action)
            elif user.status == "2":
                user.status = "1"
                # new_action = AuditTrail(user_id=current_user.id, action_id=6, action=1,
                #                         action_date=today)
                # db.session.add(new_action)
                flash("User deactivated successfully!")


            db.session.commit()

        except Exception as e:
            # Handle any exceptions that may occur during the database operation
            db.session.rollback()  # Rollback the transaction
            flash(f"An error occurred while changing user status: {str(e)}")  # Flash an error message

        return redirect(url_for('accounts'))

    users_paginated = users_query.paginate(page=page, per_page=per_page, error_out=False)

    max_display_pages = 3
    pagination_range = custom_pagination(users_paginated.page, users_paginated.pages, max_display_pages)

    # Generate a URL for the current endpoint with an empty search parameter
    reset_search_url = url_for('user_dashboard', page=page)

    return render_template("accounts.html",
                           users=users_paginated.items,
                           users_paginated=users_paginated,
                           pagination_range=pagination_range,
                           search_term=search_term,
                           reset_search_url=reset_search_url)




@app.route('/note', methods=["GET", "POST"])
def note():
    case_number = request.args.get('emp_no')
    time_note = datetime.now()
    note_content = request.form.get('notes')
    # case = Cases.query.filter_by(id=case_number).first()  # Fetch the case based on case_no

    if request.method == 'POST':
        existing_note = Notes.query.filter(
            (Notes.emp_id == case_number) &
            (Notes.user_id == current_user.id)
        ).first()
        try:
            if existing_note:
                # Case with the same case number already exists, update the note
                existing_note.note = note_content
                existing_note.note_date = time_note
            else:
                # Case with the case number doesn't exist, add a new note
                new_note = Notes(user_id=current_user.id, emp_id=case_number, note=note_content, note_date=time_note)
                db.session.add(new_note)

            # new_action = AuditTrail(user_id=current_user.id, case_id=case_number, action_id=7, action=note_content,
            #                         action_date=time_note)
            # db.session.add(new_action)

            db.session.commit()
            flash("Note successfully updated!")

        except Exception as e:
            # Handle any exceptions that may occur during the database operation
            db.session.rollback()  # Rollback the transaction
            flash(f"An error occurred while saving the note: {str(e)}")

        return redirect(url_for('employee', emp_no=case_number))

    return redirect(url_for('employee', emp_no=case_number))  # Add the appropriate template for rendering the form

@app.route('/summary', methods=["GET", "POST"])
def summary():
    case_number = request.args.get('emp_no')
    time_summary = datetime.now()
    summary_content = request.form.get('summary')
    # case = Cases.query.filter_by(id=case_number).first()  # Fetch the case based on case_no

    if request.method == 'POST':
        existing_summary = Summary.query.filter(
            Summary.case_id == case_number).first()
        try:
            if existing_summary:
                # Case with the same case number already exists, update the note
                existing_summary.summary = summary_content
                existing_summary.summary_date = time_summary
            else:
                # Case with the case number doesn't exist, add a new note
                new_summary = Summary(user_id=current_user.id, case_id=case_number, summary=summary_content, summary_date=time_summary)
                db.session.add(new_summary)

            new_action = AuditTrail(user_id=current_user.id, case_id=case_number, action_id=8, action=summary_content,
                                    action_date=time_summary)
            db.session.add(new_action)
            db.session.commit()
            flash("Executive summary successfully updated!")

        except Exception as e:
            # Handle any exceptions that may occur during the database operation
            db.session.rollback()  # Rollback the transaction
            flash(f"An error occurred while saving the Executive Summary: {str(e)}")

        return redirect(url_for('employee', emp_no=case_number))

    return redirect(url_for('employee', emp_no=case_number))  # Add the appropriate template for rendering the form


@app.route('/replace-doc', methods=["GET", "POST"])
def replace_doc():
    form = EditCase()
    csrf_token = generate_csrf()
    replace_form = ReplaceFile()
    case_number = request.args.get('case_no')
    case = Cases.query.filter_by(case_no=case_number).first()  # Fetch the case based on case_no
    doc_id = request.form.get('docid')
    documents = Document.query.filter_by(case_id=case_number).all()
    change_doc = Document.query.filter_by(id=doc_id).first()
    users = User.query.all()

    if replace_form.validate_on_submit():
        try:
            if documents and change_doc:
                # Upload file and file path
                today = datetime.today()
                formatted_date = today.strftime('%Y-%m-%dT%H:%M:%S')
                user_id = current_user.id
                uploaded_file = replace_form.files.data
                if uploaded_file.filename != '' and allowed_file(uploaded_file.filename):
                    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = secure_filename(uploaded_file.filename)
                    unique_filename = f"{current_time}_{filename}"

                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    uploaded_file.save(file_path)

                    new_document = Document(file_path=file_path)

                # Update the file_path attribute in the database
                change_doc.file_path = new_document.file_path
                change_doc.upload_date = formatted_date
                change_doc.user_id = user_id

                new_action = AuditTrail(user_id=current_user.id, case_id=case.id, action_id=9, action=file_path,
                                        action_date=formatted_date)
                db.session.add(new_action)

                db.session.commit()

                flash("File replaced!")
                return redirect(url_for("case", case_no=case_number))
            else:
                flash("This case or document does not exist.")
                return redirect(url_for("case", case_no=case_number))
        except Exception as e:
            flash(f"An error occurred editing the case: {str(e)}")
            db.session.rollback()  # Rollback the transaction if an exception occurs

    return render_template("edit_case.html", current_user=current_user, form=form, case=case, csrf_token=csrf_token,
                           case_no=case_number, docu=documents, user=users, replace=replace_form)

@app.route('/delete-doc', methods=["GET", "POST"])
def delete_doc():
    csrf_token = generate_csrf()
    case_number = request.args.get('case_no')
    case = Cases.query.filter_by(case_no=case_number).first()  # Fetch the case based on case_no
    doc_id = request.form.get('dociddelete')
    documents = Document.query.filter_by(case_id=case.id).all()
    change_doc = Document.query.filter_by(id=doc_id).first()
    users = User.query.all()
    today = datetime.today()
    path = change_doc.file_path


    try:
        if documents and change_doc:
            # Update the file_path attribute in the database
            db.session.delete(change_doc)


            new_action = AuditTrail(user_id=current_user.id, case_id=case.id, action_id=10, action=path,
                                    action_date=today)
            db.session.add(new_action)
            db.session.commit()
            flash("File deleted!")
            return redirect(url_for("case", case_no=case_number))
        else:
            flash("This case or document does not exist.")
            return redirect(url_for("case", case_no=case_number))
    except Exception as e:
        flash(f"An error occurred while deleting the case: {str(e)}")
        db.session.rollback()  # Rollback the transaction if an exception occurs

    return render_template("edit_case.html", current_user=current_user, case=case, csrf_token=csrf_token,
                           case_no=case_number, docu=documents, user=users)

@app.route('/add-to-existing-items', methods=["GET", "POST"])
def add_existing_item():
    return addexistingitem()

@app.route('/add-new-items', methods=["GET", "POST"])
def add_new_item():
    return addnewitem()

@app.route('/add-employee', methods=["GET", "POST"])
def add_new_employee():
    return addnewemployee()

@app.route('/issue-items', methods=["GET", "POST"])
def issue_item():
    return issueitem()

@app.route('/request-items', methods=["GET", "POST"])
def request_item():
    return issueitem()

def reset_password():
    pass
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

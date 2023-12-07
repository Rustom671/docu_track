from flask import Flask, render_template, redirect, url_for, flash, request, get_flashed_messages, Blueprint
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, distinct, or_, func
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, AddCase, AddFile, EditCase, EditStatus, ReplaceFile
from flask_wtf.csrf import generate_csrf
from flask import request
import os
import json

app = Flask(__name__)
app.register_blueprint
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)


# app.config['SQLALCHEMY_DATABASE_URI'] = mysql.connector.connect(
#     host='localhost',
#     user='root',
#     password='root',
#     port='3306',
#     database='docu_track'
# )
#mysql_db_cursor = db.cursor()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/document_track'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the upload folder where files will be saved
UPLOAD_FOLDER = 'static/documents'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'jpg', 'png', 'gif', 'bmp', 'jpeg', 'mp3', 'wav', 'ogg', 'flac'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

##CREATE TABLE IN USER DB
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    user_lname = db.Column(db.String(100))
    user_fname = db.Column(db.String(100))
    user_mname = db.Column(db.String(100))
    date_created = db.Column(db.Date)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    status = db.Column(db.String(20))
    type = db.Column(db.String(20))
    office = db.Column(db.String(100))
    contact = db.Column(db.String(100))

    def get_id(self):
        return str(self.id)


##CREATE TABLE IN cases DB
class Cases(UserMixin, db.Model):
    __tablename__ = "cases"
    id = db.Column(db.Integer, primary_key=True)
    case_no = db.Column(db.String(20))
    case_title = db.Column(db.String(200))
    case_complainant = db.Column(db.String(100))
    address_complainant = db.Column(db.String(150))
    contact_complainant = db.Column(db.String(100))
    case_respondent = db.Column(db.String(100))
    address_respondent = db.Column(db.String(150))
    contact_respondent = db.Column(db.String(100))
    location = db.Column(db.String(100))
    barangay = db.Column(db.String(10))
    date_created = db.Column(db.DateTime)
    status = db.Column(db.String(10))
    category = db.Column(db.String(10))
    documents = db.relationship("Document", backref="case", lazy=True)

    def get_id(self):
        return str(self.id)


class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id', onupdate='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    document_type = db.Column(db.String(50))  # e.g., 'investigation_report', 'position_paper', etc.
    file_path = db.Column(db.String(250))
    upload_date = db.Column(db.DateTime)

    def __repr__(self):
        return f"Document(id={self.id}, case_id={self.case_id}, user_id={self.user_id})"


class Schedule(db.Model):
    __tablename__ = "schedule"
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id', onupdate='CASCADE'))
    schedule = db.Column(db.Date)
    remarks = db.Column(db.String(1000))

    def __repr__(self):
        return f"Document(id={self.id}, case_id={self.case_id})"


class DemolitionSchedule(db.Model):
    __tablename__ = "demolitionschedule"
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id', onupdate='CASCADE'))
    schedule = db.Column(db.Date)
    remarks = db.Column(db.String(1000))

    def __repr__(self):
        return f"Document(id={self.id}, case_id={self.case_id})"


class Status(db.Model):
    __tablename__ = "status"
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id', onupdate='CASCADE'), index=True)
    remarks = db.Column(db.String(100))
    status = db.Column(db.String(100))
    status_date = db.Column(db.Date)

    def __repr__(self):
        return f"Document(id={self.id}, case_id={self.case_id})"

class AuditTrail(db.Model):
    __tablename__ = "audittrail"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id', onupdate='CASCADE'), index=True)
    action_id = db.Column(db.Integer)  # Change the type to db.Integer
    action = db.Column(db.String(200))
    action_date = db.Column(db.DateTime)

    def __repr__(self):
        return f"AuditTrail(id={self.id}, case_id={self.case_id})"
    # 1 - add case
    # 2 - edit case
    # 3 - add document
    # 4 - schedule
    # 5 - change status
    # 6 - activate / deactivate account
    # 7 - note
    # 8 - summary
    # 9 - replace doc




class Notes(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id', onupdate='CASCADE'), index=True)
    note = db.Column(db.String(1000))
    note_date = db.Column(db.DateTime)

class Summary(db.Model):
    __tablename__ = "summary"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id', onupdate='CASCADE'), index=True)
    summary = db.Column(db.String(1000))
    summary_date = db.Column(db.DateTime)

with app.app_context():
    db.create_all()
    print("success DB")

#--reference on retrieving documents for a specific case
#case = Cases.query.get(case_id)
#documents = case.documents

# Example of uploading an investigation report
# new_document = Document(
#     case_id=case_id,  # The ID of the case
#     user_id=current_user.id,  # The ID of the uploading user
#     document_type="investigation_report",  # Specify the type of document
#     file_path="path_to_uploaded_file",  # Set the file path
#     upload_date=datetime.now()  # Set the upload date
# )
# db.session.add(new_document)
# db.session.commit()
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def get_all_posts():
    return render_template("index.html")


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
                query = text("INSERT INTO user (user_lname, user_fname, user_mname, office, contact, status, type, date_created, username, password) "
                             "VALUES (:lname, :fname, :mname, :office, :contact, :status, :user_type, :today, :username, :password)")

                last_name = request.form.get('lname')
                first_name = request.form.get('fname')
                middle_name = request.form.get('mname')
                office_add = request.form.get('office')
                contact_num = request.form.get('contact')
                stat = "1"
                usertype = request.form.get('user_type')
                today = date.today()

                values = {
                    'lname': last_name,
                    'fname': first_name,
                    'mname': middle_name,
                    'office': office_add,
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

@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def user_dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of cases per page

    # Get the search term from the query parameters with a default value of an empty string
    search_term = request.args.get('search', '')

    # Your SQL query here
    if search_term:
        # If a search term is provided, filter based on the search term
        cases_query = db.session.query(Cases).filter(
            Cases.status.isnot(None),
            or_(
                Cases.case_no.ilike(f'%{search_term}%'),
                Cases.case_title.ilike(f'%{search_term}%'),
                Cases.case_complainant.ilike(f'%{search_term}%'),
                Cases.address_complainant.ilike(f'%{search_term}%'),
                Cases.case_respondent.ilike(f'%{search_term}%'),
                Cases.address_respondent.ilike(f'%{search_term}%'),
                Cases.location.ilike(f'%{search_term}%'),
                Cases.barangay.ilike(f'%{search_term}%')
            )
        )
    else:
        # If no search term is provided, retrieve all cases
        cases_query = db.session.query(Cases).filter(Cases.status.isnot(None))

    cases_paginated = cases_query.paginate(page=page, per_page=per_page, error_out=False)

    max_display_pages = 3
    pagination_range = custom_pagination(cases_paginated.page, cases_paginated.pages, max_display_pages)

    for_deliberation = db.session.query(Cases).filter(Cases.status == 1)

    # Generate a URL for the current endpoint with an empty search parameter
    reset_search_url = url_for('user_dashboard', page=page)

    # count statuses
    pending = db.session.query(func.count()).filter(or_(Cases.status == "1", Cases.status == "8")).scalar()
    archived = db.session.query(func.count()).filter(Cases.status == "2").scalar()
    dismissed = db.session.query(func.count()).filter(Cases.status == "3").scalar()
    for_demolition = db.session.query(func.count()).filter(Cases.status == "4").scalar()
    demolished = db.session.query(func.count()).filter(Cases.status == "5").scalar()
    deferred = db.session.query(func.count()).filter(Cases.status == "6").scalar()
    for_resolution = db.session.query(func.count()).filter(Cases.status == "7").scalar()

    return render_template("user_dashboard.html", current_user=current_user, cases_paginated=cases_paginated,
                           pagination_range=pagination_range, for_deliberation=for_deliberation,
                           search_term=search_term, reset_search_url=reset_search_url, get_barangay_name=get_barangay_name,
                           pending=pending, archived=archived, dismissed=dismissed, for_demolition=for_demolition, demolished=demolished,
                           deferred=deferred, for_resolution=for_resolution)


@app.route('/AddCase', methods=["GET", "POST"])
@login_required
def add_case():
    form = AddCase()
    csrf_token = generate_csrf()

    if form.validate_on_submit():

        # Execute the query
        query = text("SELECT * FROM cases WHERE case_no = :case_num")
        case_num = request.form.get('case_no')
        # Fetch the result
        result = db.session.execute(query, {'case_num': case_num}).fetchone()

        # Return True if the username exists, False otherwise
        if result:
            flash("This case number already exists. Please provide a unique number.")
            return redirect(url_for('add_case'))
        else:
            try:
                # Execute the query to insert the case
                query1 = text(
                    "INSERT INTO cases (case_no, case_title, case_complainant, address_complainant, contact_complainant, case_respondent, address_respondent, contact_respondent, location, barangay, date_created, status, category) " \
                    "VALUES (:case_numb, :case_tit, :comp_name, :address_com, :con_complainant, :resp_name, :address_res, :con_respondent, :loc_struct, :barangay_struct, :today, :status, :category)")
                #
                case_number = request.form.get('case_no').strip()
                title = request.form.get('case_title').strip()
                com_name = request.form.get('complainant_name').strip()
                add_comp = request.form.get('address_complainant').strip()
                con_comp = request.form.get('contact_complainant').strip()
                res_name = request.form.get('respondent_name').strip()
                add_res = request.form.get('address_respondent').strip()
                con_res = request.form.get('contact_respondent').strip()
                struct_loc = request.form.get('location_of_structure').strip()
                brgy = form.barangay.data
                categ = form.case_category.data
                today = datetime.today()
                formatted_date = today.strftime('%Y-%m-%dT%H:%M:%S')
                case_stat = "1"

                values = {
                    'case_numb': case_number,
                    'case_tit': title,
                    'comp_name': com_name,
                    'address_com': add_comp,
                    'con_complainant': con_comp,
                    'resp_name': res_name,
                    'address_res': add_res,
                    'con_respondent': con_res,
                    'loc_struct': struct_loc,
                    'barangay_struct': brgy,
                    'today': formatted_date,
                    'status': case_stat,
                    'category': categ
                }
                db.session.execute(query1, values)
                # Commit the changes and close the database connection
                db.session.commit()

                # Upload file and file path
                uploaded_file = form.inves_report.data
                if uploaded_file.filename != '' and allowed_file(uploaded_file.filename):
                    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = secure_filename(uploaded_file.filename)
                    unique_filename = f"{current_time}_{filename}"

                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    uploaded_file.save(file_path)

                    new_document = Document(file_path=file_path)

                    # Execute the query to insert the document
                    query2 = text("INSERT INTO documents (case_id, user_id, document_type, file_path, upload_date) " \
                                  "VALUES (:case_id, :user_id, :docu_type, :path_file, :date_of_upload)")
                    #
                    case_id = case_number
                    user_id = current_user.id
                    doc_type = "1"
                    path = new_document.file_path  # Get the file path from the new_document object
                    date_upload = datetime.today()

                    values2 = {
                        'case_id': case_id,
                        'user_id': user_id,
                        'docu_type': doc_type,
                        'path_file': path,
                        'date_of_upload': date_upload,
                    }

                    db.session.execute(query2, values2)

                    new_action = AuditTrail(user_id=current_user.id, case_id=case_number, action_id=1, action=path,
                                            action_date=date_upload)
                    db.session.add(new_action)
                    # Commit the changes and close the database connection
                    db.session.commit()
                else:
                    flash("File extension not valid")
                    return redirect(url_for('add_case'))
                    db.session.rollback()  # Rollback the transaction
            except Exception as e:
                flash(f"An error occurred while saving the case and document: {str(e)}")
                db.session.rollback()   # Rollback the transaction if an exception occurs

        flash("Case saved!")
        return redirect(url_for('add_case'))

    return render_template("add_case.html", current_user=current_user, form=form, csrf_token=csrf_token)

@app.route('/EditCase', methods=["GET", "POST"])
@login_required
def edit_case():
    form = EditCase()
    replace = ReplaceFile()
    csrf_token = generate_csrf()
    case_number = request.args.get('case_no')
    case = Cases.query.filter_by(case_no=case_number).first()  # Fetch the case based on case_no
    documents = Document.query.filter_by(case_id=case_number).all()
    today = datetime.today()
    # Fetch all user
    users = User.query.all()

    if form.validate_on_submit():
        try:
            if case:
                # Update the existing case

                case.case_title = request.form.get('case_title').strip()
                case.case_complainant = request.form.get('complainant_name').strip()
                case.category = request.form.get('case_category')
                case.address_complainant = request.form.get('address_complainant').strip()
                case.contact_complainant = request.form.get('contact_complainant').strip()
                case.case_respondent = request.form.get('respondent_name').strip()
                case.address_respondent = request.form.get('address_respondent').strip()
                case.contact_respondent = request.form.get('contact_respondent').strip()
                case.location = request.form.get('location_of_structure').strip()
                case.barangay = request.form.get('barangay')

                #
                new_action = AuditTrail(user_id=current_user.id, case_id=case_number, action_id=2,
                                        action_date=today)
                db.session.add(new_action)

                db.session.commit()
                #
                #
                flash("Case saved!")
                return redirect(url_for("case", case_no=case_number))
            else:
                flash("This case does not exist. Please provide a unique number.")
                return redirect(url_for('add_case'))
        except Exception as e:
            flash(f"An error occurred editing the case: {str(e)}")
            db.session.rollback()  # Rollback the transaction if an exception occurs

    return render_template("edit_case.html", current_user=current_user, form=form, case=case, csrf_token=csrf_token, case_no=case_number, docu=documents, user=users, replace_form=replace)


@app.route('/case', methods=["GET", "POST"])
@login_required
def case():
    form = AddFile()
    form1 = EditStatus()
    # form2 = Schedule()
    csrf_token = generate_csrf()
    case_number = request.args.get('case_no')
    case = Cases.query.filter_by(case_no=case_number).first()  # Fetch the case based on case_no
    # Fetch all documents for the specified case
    documents = Document.query.filter_by(case_id=case_number).all()
    # Fetch all user
    users = User.query.all()
    # Fetch schedule
    sched = Schedule.query.filter_by(case_id=case_number).first()
    barangay_name = get_barangay_name(case.barangay)

    existing_note = Notes.query.filter(
        (Notes.case_id == case_number) &
        (Notes.user_id == current_user.id)
    ).first()

    existing_summary = Summary.query.filter(
        (Summary.case_id == case_number) &
        (Summary.user_id == current_user.id)
    ).first()

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
                query2 = text("INSERT INTO documents (case_id, user_id, document_type, file_path, upload_date) "
                              "VALUES (:case_id, :user_id, :docu_type, :path_file, :date_of_upload)")
                #
                case_id = case_number
                user_id = current_user.id
                doc_type = docum_type
                path = new_document.file_path  # Get the file path from the new_document object
                date_upload = datetime.today()

                values2 = {
                    'case_id': case_id,
                    'user_id': user_id,
                    'docu_type': doc_type,
                    'path_file': path,
                    'date_of_upload': date_upload,
                }

                db.session.execute(query2, values2)
                new_action = AuditTrail(user_id=current_user.id, case_id=case_number, action_id=3, action=path,
                                        action_date=date_upload)
                db.session.add(new_action)

                # Commit the changes to the database
                db.session.commit()

                flash("File saved successfully!")  # Flash a success message
                return redirect(url_for('case', case_no=case_number))  # Redirect back to the page with the updated content
            else:
                flash("File extension not valid")
                return redirect(url_for('case', case_no=case_number))

        except Exception as e:
            # An exception occurred during the commit
            db.session.rollback()  # Rollback the transaction
            flash("Error saving file. Please try again later.")  # Flash an error message
            return redirect(url_for('case', case_no=case_number))
    return render_template("case.html",
                           case=case,
                           docu=documents,
                           form=form,
                           form1=form1,
                           csrf_token=csrf_token,
                           user=users,
                           sched=sched,
                           barangay_name=barangay_name,
                           notes=existing_note,
                           summary=existing_summary)

@app.route('/schedule', methods=["GET", "POST"])
@login_required
def schedule():

    case_number = request.args.get('case_no')
    time_changed = datetime.today()
    today = datetime.today()

    if request.method == 'POST':
        try:
            schedule_date = request.form.get('schedule')  # Access the date picker value from the form data
            remarks = request.form.get('remarks')
            schedule_date_obj = datetime.strptime(schedule_date, '%m/%d/%Y')
            formatted_schedule_date = schedule_date_obj.strftime('%Y-%m-%d')

            existing_schedule = Schedule.query.filter_by(case_id=case_number).first()
            update_status = Cases.query.filter_by(case_no=case_number).first()

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
                new_status = Status(case_id=case_number, remarks=remarks, status_date=time_changed, status="8")
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
                           get_title=get_title)

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

def get_title(id):
    case_number = id
    case = Cases.query.filter_by(case_no=case_number).first()  # Fetch the case based on case_no
    case_title = case.case_title

    return case_title

@app.route('/change_status', methods=["GET", "POST"])
@login_required
def status():

    case_number = request.args.get('case_no')

    if request.method == 'POST':
        status = request.form['status']  # Access the date picker value from the form data
        remarks = request.form['remarks']
        time_changed = datetime.today()
        try:
            case = Cases.query.filter_by(case_no=case_number).first()
            if case.status == "8":
                delete_case = Schedule.query.filter_by(case_id=case_number).first()
                db.session.delete(delete_case)
                case.status = status
                new_status = Status(case_id=case_number, remarks=remarks, status_date=time_changed, status=status)
                db.session.add(new_status)
            else:
                case.status = status
                new_status = Status(case_id=case_number, remarks=remarks, status_date=time_changed, status=status)
                db.session.add(new_status)

            new_action = AuditTrail(user_id=current_user.id, case_id=case_number, action_id=5, action=status,
                                    action_date=time_changed)
            db.session.add(new_action)

            db.session.commit()
            flash("Status successfully updated!")

        except Exception as e:
            # Handle any exceptions that may occur during the database operation
            db.session.rollback()  # Rollback the transaction
            flash(f"An error occurred while saving the case and document: {str(e)}")# Flash an error message

    return redirect(url_for('case', case_no=case_number))

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
                new_action = AuditTrail(user_id=current_user.id, action_id=6, action=2,
                                        action_date=today)
                db.session.add(new_action)
            elif user.status == "2":
                user.status = "1"
                new_action = AuditTrail(user_id=current_user.id, action_id=6, action=1,
                                        action_date=today)
                db.session.add(new_action)
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


@app.route('/ForScheduling', methods=["GET", "POST"])
@login_required
def for_scheduling():
    result = db.session.query(
        Cases.case_no,
        Cases.case_title,
        Cases.location,
        Cases.barangay
    ).join(Document). \
        filter(Document.document_type.in_([5, 6])). \
        filter(Cases.status == 1).group_by(
            Cases.case_no,
            Cases.case_title,
            Cases.location,
            Cases.barangay
        ). \
        having(func.count(Document.document_type.distinct()) == 2).all()

    return render_template("for_scheduling.html", case=result, get_barangay_name=get_barangay_name)


@app.route('/note', methods=["GET", "POST"])
def note():
    case_number = request.args.get('case_no')
    time_note = datetime.now()
    note_content = request.form.get('notes')

    if request.method == 'POST':
        existing_note = Notes.query.filter(
            (Notes.case_id == case_number) &
            (Notes.user_id == current_user.id)
        ).first()
        try:
            if existing_note:
                # Case with the same case number already exists, update the note
                existing_note.note = note_content
                existing_note.note_date = time_note
            else:
                # Case with the case number doesn't exist, add a new note
                new_note = Notes(user_id=current_user.id, case_id=case_number, note=note_content, note_date=time_note)
                db.session.add(new_note)

            new_action = AuditTrail(user_id=current_user.id, case_id=case_number, action_id=7, action=note_content,
                                    action_date=time_note)
            db.session.add(new_action)

            db.session.commit()
            flash("Note successfully updated!")

        except Exception as e:
            # Handle any exceptions that may occur during the database operation
            db.session.rollback()  # Rollback the transaction
            flash(f"An error occurred while saving the note: {str(e)}")

        return redirect(url_for('case', case_no=case_number))

    return redirect(url_for('case', case_no=case_number))  # Add the appropriate template for rendering the form

@app.route('/summary', methods=["GET", "POST"])
def summary():
    case_number = request.args.get('case_no')
    time_summary = datetime.now()
    summary_content = request.form.get('summary')

    if request.method == 'POST':
        existing_summary = Summary.query.filter(
            (Summary.case_id == case_number) &
            (Summary.user_id == current_user.id)
        ).first()
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

        return redirect(url_for('case', case_no=case_number))

    return redirect(url_for('case', case_no=case_number))  # Add the appropriate template for rendering the form

app.route('/demolition_schedule', methods=["GET", "POST"])
@login_required
def demolition_schedule():

    case_number = request.args.get('case_no')
    time_changed = datetime.today()

    if request.method == 'POST':
        try:
            schedule_date = request.form.get('schedule')  # Access the date picker value from the form data
            remarks = request.form.get('remarks')
            schedule_date_obj = datetime.strptime(schedule_date, '%m/%d/%Y')
            formatted_schedule_date = schedule_date_obj.strftime('%Y-%m-%d')

            existing_schedule = Schedule.query.filter_by(case_id=case_number).first()
            update_status = Cases.query.filter_by(case_no=case_number).first()

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
                new_status = Status(case_id=case_number, remarks=remarks, status_date=time_changed, status="8")
                db.session.add(new_status)

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

                new_action = AuditTrail(user_id=current_user.id, case_id=case_number, action_id=9, action=file_path,
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
    documents = Document.query.filter_by(case_id=case_number).all()
    change_doc = Document.query.filter_by(id=doc_id).first()
    users = User.query.all()
    today = datetime.today()
    path = change_doc.file_path


    try:
        if documents and change_doc:
            # Update the file_path attribute in the database
            db.session.delete(change_doc)


            new_action = AuditTrail(user_id=current_user.id, case_id=case_number, action_id=10, action=path,
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


if __name__ == "__main__":
    app.run(debug=True)

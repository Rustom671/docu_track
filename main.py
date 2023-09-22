from flask import Flask, render_template, redirect, url_for, flash, request, get_flashed_messages
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, AddCase, AddFile, EditCase
from flask_wtf.csrf import generate_csrf
from flask import request
import os

app = Flask(__name__)
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/docu_track'
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

    def get_id(self):
        return str(self.id)

    # # This will act like a List of BlogPost objects attached to each User.
    # # The "author" refers to the author property in the BlogPost class.
    # posts = relationship("BlogPost", back_populates="author")
    #
    # # *******Add parent relationship*******#
    # # "comment_author" refers to the comment_author property in the Comment class.
    # comments = relationship("Comment", back_populates="comment_author")

##CREATE TABLE IN cases DB
class Cases(UserMixin, db.Model):
    __tablename__ = "cases"
    id = db.Column(db.Integer, primary_key=True)
    case_no = db.Column(db.String(45))
    case_title = db.Column(db.String(250))
    case_complainant = db.Column(db.String(500))
    address_complainant = db.Column(db.String(500))
    contact_complainant = db.Column(db.String(500))
    case_respondent = db.Column(db.String(500))
    address_respondent = db.Column(db.String(500))
    contact_respondent = db.Column(db.String(500))
    location = db.Column(db.String(500))
    barangay = db.Column(db.String(500))
    date_created = db.Column(db.DateTime)
    status = db.Column(db.String(20))
    documents = db.relationship("Document", backref="case", lazy=True)

    def get_id(self):
        return str(self.id)

class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    document_type = db.Column(db.String(50))  # e.g., 'investigation_report', 'position_paper', etc.
    file_path = db.Column(db.String(250))
    upload_date = db.Column(db.DateTime)

    def __repr__(self):
        return f"Document(id={self.id}, case_id={self.case_id}, user_id={self.user_id})"

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

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        # Execute the query to insert the user
        query = text("INSERT INTO user (user_lname, user_fname, user_mname, date_created, username, password) " \
                     "VALUES (:lname, :fname, :mname, :today, :username, :password)")

        last_name = request.form.get('lname')
        first_name = request.form.get('fname')
        middle_name = request.form.get('mname')
        today = date.today()

        values = {
            'lname': last_name,
            'fname': first_name,
            'mname': middle_name,
            'today': today,
            'username': user_name,
            'password': hash_and_salted_password
        }

        db.session.execute(query, values)

        # Commit the changes and close the database connection
        db.session.commit()


        print("User registered successfully!")


        return redirect(url_for("get_all_posts"))
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

    # Your SQL query here
    cases_query = db.session.query(Cases).filter(Cases.status == "Pending")  # Assuming `Case` is your SQLAlchemy model for cases
    cases_paginated = cases_query.paginate(page=page, per_page=per_page, error_out=False)

    max_display_pages = 3
    pagination_range = custom_pagination(cases_paginated.page, cases_paginated.pages, max_display_pages)

    for_deliberation = db.session.query(Cases).filter(Cases.status == 1)

    return render_template("user_dashboard.html", current_user=current_user, cases_paginated=cases_paginated,
                           pagination_range=pagination_range, for_deliberation=for_deliberation)


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
                    "INSERT INTO cases (case_no, case_title, case_complainant, address_complainant, contact_complainant, case_respondent, address_respondent, contact_respondent, location, barangay, date_created, status) " \
                    "VALUES (:case_numb, :case_tit, :comp_name, :address_com, :con_complainant, :resp_name, :address_res, :con_respondent, :loc_struct, :barangay_struct, :today, :status)")
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
                brgy = request.form.get('barangay')
                today = datetime.today()
                formatted_date = today.strftime('%Y-%m-%dT%H:%M:%S')
                case_stat = "Pending"

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
                    doc_type = "Investigation Report"
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
    csrf_token = generate_csrf()
    case_number = request.args.get('case_no')
    case = Cases.query.filter_by(case_no=case_number).first()  # Fetch the case based on case_no

    if form.validate_on_submit():
        try:
            if case:
                # Update the existing case
                case.case_title = request.form.get('case_title').strip()
                case.case_complainant = request.form.get('complainant_name').strip()
                case.address_complainant = request.form.get('address_complainant').strip()
                case.contact_complainant = request.form.get('contact_complainant').strip()
                case.case_respondent = request.form.get('respondent_name').strip()
                case.address_respondent = request.form.get('address_respondent').strip()
                case.contact_respondent = request.form.get('contact_respondent').strip()
                case.location = request.form.get('location_of_structure').strip()
                case.barangay = request.form.get('barangay')

                db.session.commit()

                flash("Case saved!")
                return redirect(url_for('edit_case', case_no=case_number))
            else:
                flash("This case does not exist. Please provide a unique number.")
                return redirect(url_for('add_case'))
        except Exception as e:
            flash(f"An error occurred while saving the case and document: {str(e)}")
            db.session.rollback()  # Rollback the transaction if an exception occurs

    return render_template("edit_case.html", current_user=current_user, form=form, case=case, csrf_token=csrf_token)


@app.route('/case', methods=["GET", "POST"])
@login_required
def case():
    form = AddFile()
    csrf_token = generate_csrf()
    case_number = request.args.get('case_no')
    case = Cases.query.filter_by(case_no=case_number).first()  # Fetch the case based on case_no
    # Fetch all documents for the specified case
    documents = Document.query.filter_by(case_id=case_number).all()


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
                query2 = text("INSERT INTO documents (case_id, user_id, document_type, file_path, upload_date) " \
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
    return render_template("case.html", case=case, docu=documents, form=form, csrf_token=csrf_token)



if __name__ == "__main__":
    app.run(debug=True)

from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_login import UserMixin

db = SQLAlchemy()  # ⚠️ NO `app` here
ckeditor = CKEditor()


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
    division = db.Column(db.String(100))
    contact = db.Column(db.String(100))

    def get_id(self):
        return str(self.id)


#CREATE TABLE IN cases DB
# class Employees(UserMixin, db.Model):
#     __tablename__ = "employees"
#     id = db.Column(db.Integer, primary_key=True)
#     emp_no = db.Column(db.String(20))
#     emp_name = db.Column(db.String(200))
#     emp_position = db.Column(db.String(100))
#     emp_div = db.Column(db.String(20))
#     date_created = db.Column(db.DateTime)
#     status = db.Column(db.String(10))
#     emp_gender = db.Column(db.String(10))
#     extra_1 = db.Column(db.String(200))
#     extra_2 = db.Column(db.String(200))
#
#     def get_id(self):
#         return str(self.id)


class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    document_type = db.Column(db.String(50))  # e.g., 'investigation_report', 'position_paper', etc.
    file_path = db.Column(db.String(250))
    upload_date = db.Column(db.DateTime)
    status = db.Column(db.String(50))

    def __repr__(self):
        return f"Document(id={self.id}, Employee={self.emp_id}, User={self.user_id})"

class IssuedItems(db.Model):
    __tablename__ = "issueditems"
    id = db.Column(db.Integer, primary_key=True)
    issued_by = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    item_id = db.Column(db.Integer, index=True)
    emp_id = db.Column(db.Integer, index=True)
    q_issued = db.Column(db.Integer)
    date_issued = db.Column(db.DateTime)

    def __repr__(self):
        return f"Issued Item: (id={self.id}, item={self.item_id}, employee={self.emp_id} )"

class RequestedItems(db.Model):
    __tablename__ = "requesteditems"
    id = db.Column(db.Integer, primary_key=True)
    requested_by = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    item_id = db.Column(db.Integer, index=True)
    q_issued = db.Column(db.Integer)
    date_issued = db.Column(db.DateTime)
    status = db.Column(db.Integer)
    date_status = db.Column(db.DateTime)
    details = db.Column(db.String(150))

    def __repr__(self):
        return f"Issued Item: (id={self.id}, item={self.item_id}, employee={self.emp_id} )"

class AddExistingItems(db.Model):
    __tablename__ = "addexistingitems"
    id = db.Column(db.Integer, primary_key=True)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    item_id = db.Column(db.Integer, index=True)
    emp_id = db.Column(db.Integer, index=True)
    q_added = db.Column(db.Integer)
    date_issued = db.Column(db.DateTime)

    def __repr__(self):
        return f"Added Item: (id={self.id}, item={self.item_id}, employee={self.emp_id} )"

class AddItems(db.Model):
    __tablename__ = "additems"
    id = db.Column(db.Integer, primary_key=True)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    item_id = db.Column(db.Integer, index=True)
    emp_id = db.Column(db.Integer, index=True)
    q_added = db.Column(db.Integer)
    date_issued = db.Column(db.DateTime)

    def __repr__(self):
        return f"Added Item: (id={self.id}, item={self.item_id}, employee={self.emp_id} )"

class AddEmployee(db.Model):
    __tablename__ = "addemployee"
    id = db.Column(db.Integer, primary_key=True)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    emp_id = db.Column(db.Integer, index=True)
    date_added = db.Column(db.DateTime)

    def __repr__(self):
        return f"Added Employee: (id={self.id}, employee={self.emp_id} )"

class ForDisposal(db.Model):
    __tablename__ = "fordisposal"
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    document_type = db.Column(db.String(50))  # e.g., 'investigation_report', 'position_paper', etc.
    file_path = db.Column(db.String(250))
    upload_date = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    extra_1 = db.Column(db.String(100))
    extra_2 = db.Column(db.String(100))

class Notes(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    emp_id = db.Column(db.Integer, index=True)
    note = db.Column(db.String(1000))
    note_date = db.Column(db.DateTime)


class History(db.Model):
    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key=True)
    transferred_by = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    doc_id = db.Column(db.Integer, db.ForeignKey('documents.id', onupdate='CASCADE'))
    source_id = db.Column(db.Integer)
    destination_id = db.Column(db.Integer)
    history_date = db.Column(db.DateTime)
    extra_1 = db.Column(db.String(100))
    extra_2 = db.Column(db.String(100))


class Records(db.Model):
    __tablename__ = "records"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'))
    doc_id = db.Column(db.Integer)
    folder_id = db.Column(db.Integer, index=True)
    description = db.Column(db.String(500))
    file_path = db.Column(db.String(250))
    upload_date = db.Column(db.DateTime)
    extra_1 = db.Column(db.String(100))
    extra_2 = db.Column(db.String(100))
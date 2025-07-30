from flask import Flask, render_template, redirect, url_for, flash
from flask_login import current_user
from forms import  AddNewEmployee
from flask_wtf.csrf import generate_csrf
from flask import request
from datetime import date, datetime
import json
from models import db, AddEmployee


# Load items from JSON
def load_json():
    """Load employees from JSON file without caching."""
    try:
        with open("templates/employee.json", "r", encoding="utf-8") as file:
            return json.loads(file.read())  # Force fresh read instead of caching
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Return an empty list if the file doesn't exist or is invalid

# Save items to JSON (Append instead of Overwrite)
def save_json(new_employee):
    try:
        employees = load_json()  # Load updated data
        employees.append(new_employee)  # Append new employee

        with open("templates/employee.json", "w", encoding="utf-8") as file:
            json.dump(employees, file, indent=4)  # Overwrite with updated data

    except Exception as e:
        print(f"Error saving JSON: {e}")


def addnewemployee():
    csrf_token = generate_csrf()
    form = AddNewEmployee()
    time_note = datetime.now()

    if request.method == 'POST' and form.validate_on_submit():
        full_name = f"{form.emp_lname.data.upper()}, {form.emp_fname.data.upper()} {form.emp_mname.data[:1].upper()}."

        position = form.emp_position.data
        division = form.emp_division.data
        gender = form.emp_gender.data

        employees = load_json()

        # Check for duplicate full_name
        if any(emp["Name"] == full_name for emp in employees):
            flash(f"Employee '{full_name}' already exists in JSON.", "error")
            return redirect(url_for("add_new_employee"))

        last_item_id = int(employees[-1]['ID']) if employees else 0
        new_id = str(last_item_id + 1)

        # Check for duplicate in database
        existing_employee = AddEmployee.query.filter_by(emp_id=new_id).first()
        if existing_employee:
            flash(f"Employee '{full_name}' already exists in the database.", "error")
            return redirect(url_for("add_new_employee"))


        new_employee = {
            "ID": new_id,
            "Name": full_name,
            "Position": position,
            "Division": division,
            "Gender": gender,
            "Date Added": time_note.strftime("%Y-%m-%d %H:%M:%S"),
            "Status": "1"
        }

        add_employee = AddEmployee(
            added_by=current_user.id,
            emp_id=new_id,
            date_added=time_note
        )

        try:
            db.session.add(add_employee)
            db.session.flush()  # Catch errors before committing

            # Append and save to JSON
            save_json(new_employee)

            db.session.commit()
            flash(f"New employee '{full_name}' added successfully.", "success")
            return redirect(url_for("add_new_employee"))

        except Exception as e:
            db.session.rollback()
            flash(f"Failed to save employee: {str(e)}", "error")
            return redirect(url_for("add_new_employee"))

    return render_template("add_employee.html", current_user=current_user, csrf_token=csrf_token, form=form)
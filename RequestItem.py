from flask import Flask, render_template, redirect, url_for, flash
from flask_login import current_user
from forms import RequestItem
from flask_wtf.csrf import generate_csrf
from flask import request
from datetime import date, datetime
import json
from models import db, IssuedItems

#Load items from JSON
def load_json_item():
    with open('templates/products.json', 'r') as file:
        return json.load(file)

# Save items to JSON
def save_json(items):
    with open('templates/products.json', 'w') as file:
        json.dump(items, file, indent=4)

def get_products():
    #Load products from JSON file dynamically.#
    with open('templates/products.json', 'r') as json_file:
        products = json.load(json_file)
    return [(p, p) for p in products]  # Ensure choices are in (value, label) format

def requestitem():
    csrf_token = generate_csrf()
    form = RequestItem()
    time_note = datetime.now()

    if request.method == 'POST' and form.validate_on_submit():
        item_name = form.item.data
        emp_name = form.employee.data
        quantity_to_subtract = int(form.quantity.data)

        items = load_json_item()
        try:
            item_found = False
            for item in items:
                if item['ID'] == item_name:
                    current_stock = int(item['Quantity'])

                    if quantity_to_subtract > current_stock:
                        flash(f"Error: Requested quantity ({quantity_to_subtract}) exceeds available stock ({current_stock}).", "danger")
                        return redirect(url_for("user_dashboard"))

                    # First, create the issued item record (but don't commit yet)
                    issued_item = IssuedItems(
                        issued_by=current_user.id,
                        item_id=item['ID'],  # No need to access .id since 'ID' is already an identifier
                        emp_id=emp_name,
                        q_issued=quantity_to_subtract,
                        date_issued=time_note
                    )
                    db.session.add(issued_item)

                    # Flush to check for DB errors before committing
                    db.session.flush()

                    # If successful, then update the JSON file
                    item['Quantity'] = str(current_stock - quantity_to_subtract)

                    # Now commit the database transaction
                    db.session.commit()

                    # Save JSON only after successful DB commit
                    save_json(items)

                    flash("Item issued successfully.", "success")
                    return redirect(url_for("user_dashboard"))

            if not item_found:
                flash(f"This item does not exist: {item_name}", "error")
                return redirect(url_for("user_dashboard"))

        except Exception as e:
            db.session.rollback()  # Rollback DB changes if any error occurs
            flash(f"An error occurred: {str(e)}", "danger")

    return redirect(url_for("user_dashboard"))
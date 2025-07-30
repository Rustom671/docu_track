from flask import Flask, render_template, redirect, url_for, flash
from flask_login import current_user
from forms import  AddExistingItem
from flask_wtf.csrf import generate_csrf
from flask import request
from datetime import date, datetime
import json
from models import db, AddExistingItems



 #Load items from JSON
def load_json():
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

def addexistingitem():
    csrf_token = generate_csrf()
    form = AddExistingItem()
    time_note = datetime.now()

    if request.method == 'POST' and form.validate_on_submit():
        # Get values from the form using form's attribute data
        item_name = form.item.data
        quantity_to_add = int(form.quantity.data)  # Convert quantity to int

        # Load the existing items from the JSON file
        items = load_json()

        # Find the item in the JSON data
        item_found = False
        for item in items:
            if str(item['ID']) == str(item_name):   # Ensure item_name is an integer
                try:
                    existing_item = AddExistingItems(
                        added_by=current_user.id,
                        item_id=item['ID'],
                        emp_id=current_user.id,
                        q_added=quantity_to_add,
                        date_issued=time_note
                    )
                    db.session.add(existing_item)
                    db.session.commit()  # Commit the transaction to save to DB

                    # Successfully added to DB, now update the quantity in JSON
                    item['Quantity'] = str(int(item['Quantity']) + quantity_to_add)
                    save_json(items)  # Save the updated JSON file

                    item_found = True
                    flash("Item quantity updated successfully.")
                    return redirect(url_for("user_dashboard"))

                except Exception as e:
                    db.session.rollback()  # Rollback the transaction if there's an error
                    flash(f"Failed to save to database: {str(e)}", "error")
                    return redirect(url_for("user_dashboard"))

        if not item_found:
            flash(f"This item does not exist: {item_name}", "error")
            return redirect(url_for("user_dashboard"))

    return render_template("user_dashboard.html", current_user=current_user, csrf_token=csrf_token, form1=form)
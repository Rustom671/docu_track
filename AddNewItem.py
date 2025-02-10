from flask import render_template, redirect, url_for, flash
from flask_login import current_user
from forms import AddNewItem, AddExistingItem
from flask_wtf.csrf import generate_csrf
from flask import request
import json

# Load items from JSON
def load_json():
    with open('templates/products.json', 'r') as file:
        return json.load(file)

# Save items to JSON
def save_json(items):
    with open('templates/products.json', 'w') as file:
        json.dump(items, file, indent=4)

def get_products():
    # Load products from JSON file dynamically
    with open('templates/products.json', 'r') as json_file:
        products = json.load(json_file)
    return [(p['Product'], p['Product']) for p in products]  # Ensure choices are in (value, label) format

def addnewitem():
    csrf_token = generate_csrf()
    form = AddNewItem()
    form_existing = AddExistingItem()  # Reload the form to get updated choices

    if request.method == 'POST' and form.validate_on_submit():
        # Get values from the form using form's attribute data
        item_name = form.item.data
        quantity_to_add = int(form.quantity.data)  # Convert quantity to int

        # Load the existing items from the JSON file
        items = load_json()

        # Check if the item already exists (case-insensitive comparison)
        for item in items:
            if item['Product'].lower() == item_name.lower():  # Case-insensitive search
                flash("Item already exists.")
                return redirect(url_for("user_dashboard"))

        # If not found, add the new item
        last_item_id = int(items[-1]['ID']) if items else 0  # Get the last item ID, or 0 if empty
        new_id = str(last_item_id + 1)

        # Add the new item with a unique ID
        new_item = {
            "ID": new_id,
            "Product": item_name,
            "Quantity": str(quantity_to_add)
        }
        items.append(new_item)

        # Save the updated items back to the JSON file
        save_json(items)  # Use the save_json function to update the file

        flash(f"New item '{item_name}' added successfully with quantity {quantity_to_add}.", "success")

        # After adding the new item, reload the product list

        return redirect(url_for("user_dashboard"))

    # Ensure `form_existing` has updated choices
    form_existing.item.choices = get_products()
    return render_template("user_dashboard.html", current_user=current_user, csrf_token=csrf_token, form2=form, form1=form_existing)

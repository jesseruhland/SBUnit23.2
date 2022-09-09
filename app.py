"""Blogly application."""

from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secretkey'

debug = DebugToolbarExtension(app)

connect_db(app)
#db.create_all()

@app.route("/")
def redirect_for_now():
    """as directed by the assignment, this currently redirects to /users"""
    return redirect ('/users')


@app.route("/users")
def list_users():
    """List users and show "add user" button."""
    users = User.query.all()
    return render_template('user-list.html', users=users)

@app.route("/users/new", methods=['POST', 'GET'])
def add_user():
    """handle new user entry,
    on GET request, display new user entry form,
    on POST request, save new user from form to db and display updated user list
    """
    method = request.method
    if method == 'GET':
        return render_template('new-user.html')
    
    if method == 'POST':
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        image_url = request.form['image-url']

        if image_url == "":
            new_user = User(first_name=first_name, last_name=last_name)
        else:
            new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()

        flash(f"{first_name} {last_name} has been added successfully!")
        return redirect('/users')


@app.route("/users/<int:user_id>")
def show_user_details(user_id):
    """display user detail page from db"""
    user = User.query.get_or_404(user_id)
    return render_template('user-detail.html', user=user)

@app.route("/users/<int:user_id>/edit", methods=['POST', 'GET'])
def edit_user(user_id):
    """handle edit entry,
    on GET request, display edit user form,
    on POST request, save updated user from form to db and display updated user list
    """
    method = request.method
    if method == 'GET':
        user = User.query.get(user_id)
        return render_template('edit-user.html', user=user)

    if method == 'POST':
        user = User.query.get(user_id)
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        image_url = request.form['image-url']

        user.first_name = first_name
        user.last_name = last_name
        if image_url != '':
            user.image_url = image_url
        
        db.session.add(user)
        db.session.commit()

        flash(f"{first_name} {last_name} has been successfully updated!")
        return redirect('/users')

@app.route("/users/<int:user_id>/delete", methods=['POST'])
def delete_user(user_id):
    """delete user details from db"""
    user = User.query.get(user_id)

    User.query.filter_by(id=user_id).delete()
    db.session.commit()

    flash(f"{user.first_name} {user.last_name} has been successfully deleted!")
    return redirect('/users')
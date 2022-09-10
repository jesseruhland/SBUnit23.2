"""Blogly application."""

from flask import Flask, request, redirect, render_template, flash
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secretkey'

# debug = DebugToolbarExtension(app)

connect_db(app)
#db.create_all()

@app.route("/")
def display_home():
    """display homepage with 5 recent posts"""
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('homepage.html', posts=posts)


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

@app.route("/users/<int:user_id>/posts/new", methods=['GET', 'POST'])
def add_new_post(user_id):
    """ on GET request - Show form to add a post for that user.
    on POST request - Handle add form; add post and redirect to the user detail page.
    """
    user = User.query.get(user_id)
    method = request.method
    if method == 'GET':
        return render_template('new-post.html', user=user)
    
    if method == 'POST':
        title = request.form['title']
        content = request.form['content']

        new_post = Post(title=title, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        flash(f"{title} has been added successfully!")
        return redirect(f'/users/{user_id}')

@app.route("/posts/<int:post_id>")
def show_post(post_id):
    """show post and available options"""
    
    post = Post.query.get_or_404(post_id)
    return render_template('post-detail.html', post=post)


@app.route("/posts/<int:post_id>/edit", methods=['GET', 'POST'])
def edit_post(post_id):
    """on GET request - Show form to edit a post, and to cancel (back to user page).
    on POST request - Handle editing of a post. Redirect back to the post view.
    """
    post = Post.query.get(post_id)
    method = request.method
    if method == 'GET':
        return render_template('edit-post.html', post=post)
    
    if method == 'POST':
        title = request.form['title']
        content = request.form['content']

        post.title = title
        post.content= content
        db.session.add(post)
        db.session.commit()

        flash(f"{title} has been updated successfully!")
        return redirect(f'/users/{post.user_id}')

@app.route("/posts/<int:post_id>/delete", methods=['POST'])
def delete_post(post_id):
    """delete the post"""

    post = Post.query.get(post_id)

    Post.query.filter_by(id=post_id).delete()
    db.session.commit()

    flash(f"{post.title} has been successfully deleted!")
    return redirect(f'/users/{post.user_id}')
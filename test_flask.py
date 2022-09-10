from unittest import TestCase

from app import app
from models import db, User, Post

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class ViewsTestCase(TestCase):
    """Tests for views for Users"""

    def setUp(self):
        """Add sample user"""

        User.query.delete()

        test_user = User(first_name='John', last_name='Doe')
        db.session.add(test_user)
        db.session.commit()

        test_post = Post(title='Post for Testing With', content='This is a paragraph of text for the test.', user_id=test_user.id)
        db.session.add(test_post)
        db.session.commit()

        self.user_id = test_user.id
        self.post_id = test_post.id

    def tearDown(self):
        """Clean up any fouled transactions"""

        db.session.rollback()

    def test_root_route(self):
        """test redirect set up per assignment requirements"""
        with app.test_client() as client:
            resp = client.get('/')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "http://localhost/users")
    
    def test_user_list(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("John Doe", html)

    def test_new_user_form(self):
        with app.test_client() as client:
            resp = client.get('/users/new')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Create A User</h1>', html)
    
    def test_new_user_submission(self):
        with app.test_client() as client:
            d = {"first-name": "Betty", "last-name": "White", "image-url": "www.google.com"}
            resp = client.post("/users/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Betty White", html)

    def test_user_details(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>John Doe</h1>', html)
            self.assertIn('Post for Testing With', html)
    
    def test_edit_user_form(self):
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}/edit')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Edit A User</h1>', html)
            self.assertIn('John', html)
    
    def test_edit_user_submission(self):
        with app.test_client() as client:
            d = {"first-name": "Betty", "last-name": "White", "image-url": "www.google.com"}
            resp = client.post(f"/users/{self.user_id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Betty White", html)

    def test_delete_user(self):
        with app.test_client() as client:
            resp = client.post(f"/users/{self.user_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("John Doe has been successfully deleted!", html)

    def test_new_post_form(self):
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}/posts/new')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>New Post for John Doe</h1>', html)

    def test_new_post_submission(self):
        with app.test_client() as client:
            d = {"title": "Post Title", "content": "Post Content"}
            resp = client.post(f'/users/{self.user_id}/posts/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Post Title", html)

    def test_post_details(self):
        with app.test_client() as client:
            resp = client.get(f"/posts/{self.post_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Post for Testing With</h1>', html)

    def test_edit_post_form(self):
        with app.test_client() as client:
            resp = client.get(f'/posts/{self.post_id}/edit')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Edit Post</h1>', html)
            self.assertIn('<button>Save</button>', html)

    def test_edit_post_submission(self):
        with app.test_client() as client:
            d = {"title": "Betty White Article", "content": "Betty White's content"}
            resp = client.post(f"/posts/{self.post_id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Betty White Article has been updated successfully!", html)

    def test_delete_post(self):
        with app.test_client() as client:
            resp = client.post(f"/posts/{self.post_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Post for Testing With has been successfully deleted!", html)       
"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()


    def test_user_view_profile(self):
            """Can a user view their profile"""

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id


                resp = c.get(f"/users/{self.testuser.id}")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('testuser', html)

    def test_user_view_followers__logged_in(self):
            """Can a user add a follower view another user's following page when logged in?"""

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id

                testuser2 = User.signup(username="testuser2",
                                        email="test2@test.com",
                                        password="testuser",
                                        image_url=None)
                
                db.session.add(testuser2)
                db.session.commit()

                follow_resp = c.post(f"/users/follow/{testuser2.id}")

                resp = c.get(f"/users/{self.testuser.id}/following")
                html = resp.get_data(as_text=True)

                self.assertEqual(follow_resp.status_code, 302)
                self.assertEqual(len(Follows.query.all()), 1)
                self.assertEqual(resp.status_code, 200)
                self.assertIn('testuser2', html)


    def test_user_view_followers_not_logged_in(self):
                """Can a user view another user's following page when not logged in? Should redirect to login page"""
                
                with self.client as c:

                    testuser2 = User.signup(username="testuser2",
                                            email="test2@test.com",
                                            password="testuser",
                                            image_url=None)
                    
                    db.session.add(testuser2)
                    db.session.commit()

                    resp = c.get(f"/users/{testuser2.id}/following")
                    html = resp.get_data(as_text=True)

                    self.assertEqual(resp.status_code, 302)
                    self.assertIn('Redirecting', html)

    def test_user_add_like_message(self):
            """Can a user add a liked message?"""

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id

                testuser2 = User.signup(username="testuser2",
                                        email="test2@test.com",
                                        password="testuser",
                                        image_url=None)
                
                db.session.add(testuser2)
                db.session.commit()

                user2Message = Message(text="Test Test", timestamp=None, user_id=testuser2.id)

                db.session.add(user2Message)
                db.session.commit()

                resp = c.post(f"/users/add_like/{user2Message.id}")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(len(Likes.query.all()), 1)


    def test_user_delete_profile(self):
            """Can a user delete their profile"""

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id


                resp = c.post("/users/delete")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(len(User.query.all()), 0)


    def test_user_update_profile(self):
            """Can a user update their profile and see update profile form"""

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id

                
                resp = c.post("/users/profile", data = {'username': 'testUserUpdate', 
                'email': 'test@test.com', 
                'image_url': "image.com", 
                'header_img_url': 'headerimg.com', 
                'bio': "Test Bio", 
                'password': 'testuser'})

                resp2 = c.get('/users/profile')

                html = resp2.get_data(as_text=True)

                user = User.query.get(self.testuser.id)

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(user.username, 'testUserUpdate')
                self.assertIn('Edit Your Profile', html)
                
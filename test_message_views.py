"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

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

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_view_message(self):
        """Can a user view a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            msg = Message.query.one()

            resp2 = c.get(f"/messages/{msg.id}")
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn("Hello", html)


    def test_add_message_logged_out(self):
        """Make sure a user can't add a message when logged out."""

        with self.client as c:

            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            self.assertEqual(len(Message.query.all()), 0)


    def test_delete_message(self):
        """Can user delete a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            msg = Message.query.one()
            
            resp2 = c.post(f"/messages/{msg.id}/delete")

            self.assertEqual(resp2.status_code, 302)
            self.assertEqual(len(Message.query.all()), 0)


    # def test_delete_message_other_user(self):
    #     """User should not be able to delete another user's message when logged in."""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id

    #         resp = c.post("/messages/new", data={"text": "Hello"})

    #         msg = Message.query.one()

    #         testuser2 = User.signup(username="testuser2",
    #                                     email="test2@test.com",
    #                                     password="testuser",
    #                                     image_url=None)

    #         db.session.commit()

    #         with c.session_transaction() as sess:
    #             del sess[CURR_USER_KEY]
    #             sess[CURR_USER_KEY] = testuser2.id
            
    #         resp2 = c.post(f"/messages/{msg.id}/delete")

    #         self.assertEqual(resp2.status_code, 302)
    #         self.assertEqual(len(Message.query.all()), 1)


    def test_delete_message_logged_out(self):
        """Test to make sure a user can't delete a message when logged out"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            msg = Message.query.one()

            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]

            
            resp2 = c.post(f"/messages/{msg.id}/delete")

            self.assertEqual(resp2.status_code, 302)
            self.assertEqual(len(Message.query.all()), 1)


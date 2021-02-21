"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test User model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    # def tearDown(self):
    #     db.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_user_model_repr(self):
        """Does the representation method for a user work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        self.assertEqual(u.__repr__(), f"<User #{u.id}: {u.username}, {u.email}>")

    def test_user_model_follows(self):
        """Doe the methods that check if a user is following work?"""

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        follows = Follows(user_being_followed_id=u1.id, user_following_id=u2.id)

        db.session.add(follows)
        db.session.commit()

        # User should have no messages & no followers
        self.assertTrue(u2.is_following(u1), True)
        self.assertFalse(u1.is_following(u2), False)
        self.assertTrue(u1.is_followed_by(u2), True)
        self.assertFalse(u2.is_followed_by(u1), False)

    def test_user_signup(self):
        """Does the signup method for a user work?"""

        u = User.signup("testuser", "test@test.com","HASHED_PASSWORD", "test-image.com")
        # db.session.commit()
        self.assertIsInstance(u, User)


    def test_user_authenticate(self):
        """Does the authentication method for a user work?"""

        u = User.signup("testuser", "test@test.com","HASHED_PASSWORD", "test-image.com")

        db.session.commit()

        self.assertEqual(User.authenticate("testuser", "HASHED_PASSWORD"), u)
        self.assertFalse(User.authenticate("VVVVVVVVBBBBBB", "HASHED_PASSWORD"), False)
        self.assertFalse(User.authenticate("testuser", "WRONGWRONG"), False)

"""Message model tests."""

import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test Message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.user_id = u.id

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="test Message",
            timestamp=None,
            user_id=self.user_id
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.user.id, self.user_id)




    

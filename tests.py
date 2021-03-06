from unittest import TestCase

from app import app, db
from models import DEFAULT_IMAGE_URL, User, Post

# Let's configure our app to use a different database for tests
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly_test"

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        # As you add more models later in the exercise, you'll want to delete
        # all of their records before each test just as we're doing with the
        # User model below.
        Post.query.delete() #avoid orphan children
        User.query.delete()

        self.client = app.test_client()

        test_user = User(first_name="test_first",
                                    last_name="test_last",
                                    image_url=DEFAULT_IMAGE_URL)

        second_user = User(first_name="test_first_two", last_name="test_last_two",
                           image_url=DEFAULT_IMAGE_URL)



        # test_post = Post(title="test_title",
        #                             content="test_content",
        #                             user_id=test_user.id)

        db.session.add_all([test_user, second_user])
        db.session.commit()

        # We can hold onto our test_user's id by attaching it to self (which is
        # accessible throughout this test class). This way, we'll be able to
        # rely on this user in our tests without needing to know the numeric
        # value of their id, since it will change each time our tests are run.
        self.user_id = test_user.id



    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_show_users(self):
        """Tests get request on /users route"""
        with self.client as c:
            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test_first", html)
            self.assertIn("test_last", html)

    def test_list_users(self):
        """Tests redirect on root route"""
        #FIXME: see users, add more here.
        with self.client as c:
            resp = c.get("/")
            self.assertEqual(resp.status_code, 302)

    def test_new_user_form(self):
        """Tests get request on show new user route"""
        with self.client as c:
            resp = c.get("/users/new")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<h1>CREATE A USER", html)

    def test_add_new_user(self):
        """Tests post route to add user data."""
        with self.client as c:
            d = {"first_name": "test_first_name", "last_name": "test_last_name", "image_url": DEFAULT_IMAGE_URL }
            resp = c.post("/users/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn("test_first_name", html)
            self.assertIn("test_last_name", html)
            self.assertEqual(resp.status_code, 200)

    def test_delete_user(self):
        """Tests post route to delete user"""
        #TODO: Make sure post is not there as well. 
        with self.client as c:
            resp = c.post(f"/users/{self.user_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertNotIn(f"{self.user_id}", html)
            self.assertEqual(resp.status_code, 200)

    def test_add_post(self):
        """Tests post route to add post."""
        with self.client as c:
            d = {"title": "test_title", "content": "test_content"}
            resp = c.post(f"/users/{self.user_id}/posts/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn("test_title", html)
            self.assertEqual(resp.status_code, 200)



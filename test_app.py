import unittest
from app import app, db
from models import User, Course, UserCourse 
from flask_bcrypt import generate_password_hash

class LMSAppTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a clean database before each test."""
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up the database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # --- USER TESTS ---

    def test_user_registration_success(self):
        """Test successful user registration."""
        response = self.app.post('/register', json={
            "external_user_id": "12345",
            "name": "Lea Ferreira",
            "email": "leandra.ferreira.za@gmail.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("User registered successfully", response.get_json()["message"])

    def test_user_authentication_success(self):
        """Test successful user authentication."""
        self.app.post('/register', json={
            "external_user_id": "12345",
            "name": "Lea Ferreira",
            "email": "leandra.ferreira.za@gmail.com",
            "password": "password123"
        })
        response = self.app.post('/authenticate', json={
            "email": "leandra.ferreira.za@gmail.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Authentication successful", response.get_json()["message"])

    def test_user_authentication_invalid_password(self):
        """Test login with incorrect password."""
        self.app.post('/register', json={
            "external_user_id": "12345",
            "name": "Lea Ferreira",
            "email": "leandra.ferreira.za@gmail.com",
            "password": "password123"
        })
        response = self.app.post('/authenticate', json={
            "email": "leandra.ferreira.za@gmail.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.get_json()["message"])

    # --- COURSE TESTS ---

    def test_course_insertion_success(self):
        """Test inserting a new course."""
        response = self.app.post('/add_course', json={"course_name": "Biology"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("Course added successfully", response.get_json()["message"])

    def test_course_insertion_duplicate(self):
        """Test inserting a duplicate course (should be prevented)."""
        self.app.post('/add_course', json={"course_name": "Biology"})
        response = self.app.post('/add_course', json={"course_name": "Biology"})
        self.assertEqual(response.status_code, 400)  # Bad request
        self.assertIn("Course already exists", response.get_json()["message"])

    def test_course_assignment_success(self):
        """Test assigning a course to a user."""
        self.app.post('/register', json={
            "external_user_id": "12345",
            "name": "Lea Ferreira",
            "email": "leandra.ferreira.za@gmail.com",
            "password": "password123"
        })
        self.app.post('/add_course', json={"course_name": "Mathematics"})
        response = self.app.post('/assign_course', json={
            "external_user_id": "12345",
            "course_name": "Mathematics"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("assigned", response.get_json()["message"])


    def test_course_retrieval(self):
        """Test retrieving all available courses."""
        self.app.post('/add_course', json={"course_name": "History"})
        self.app.post('/add_course', json={"course_name": "Physics"})
        response = self.app.get('/courses')
        self.assertEqual(response.status_code, 200)
        courses = response.get_json()["courses"]
        self.assertEqual(len(courses), 2)
        self.assertIn("History", courses)
        self.assertIn("Physics", courses)

    # --- EDGE CASES ---


    def test_course_assignment_to_nonexistent_user(self):
        """Test assigning a course to a non-existing user."""
        self.app.post('/add_course', json={"course_name": "Physics"})
        response = self.app.post('/assign_course', json={
            "external_user_id": "99999",
            "course_name": "Physics"
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.get_json()["message"])

if __name__ == "__main__":
    unittest.main()

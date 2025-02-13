from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from models import db, User, Course, UserCourse 
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt = Bcrypt(app)

#@app.before_first_request
#def create_tables():
#According with the new release notes, the before_first_request is deprecated and will be removed from Flask 2.3:

# The following line will remove this handler, making it
# only run on the first request
with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        external_user_id=data['external_user_id'],
        name=data['name'],
        email=data['email'],
        password_hash=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully."}), 201

@app.route('/authenticate', methods=['POST'])
def authenticate_user():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({"message": "Authentication successful."})
    return jsonify({"message": "Invalid credentials."}), 401

@app.route('/assign_course', methods=['POST'])
def assign_course():
    data = request.get_json()
    user = User.query.filter_by(external_user_id=data['external_user_id']).first()
    course = Course.query.filter_by(course_name=data['course_name']).first()
    if not course:
        course = Course(course_name=data['course_name'])
        db.session.add(course)
    if user:
        user_course = UserCourse(user_id=user.id, course_id=course.id)
        db.session.add(user_course)
        db.session.commit()
        return jsonify({"message": f"Course '{course.course_name}' assigned to '{user.name}'."})
    return jsonify({"message": "User not found."}), 404


@app.route('/add_course', methods=['POST'])
def add_course():
    """Adds a new course to the system."""
    data = request.get_json()
    existing_course = Course.query.filter_by(course_name=data["course_name"]).first()
    if existing_course:
        return jsonify({"message": "Course already exists"}), 400
    new_course = Course(course_name=data["course_name"])
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"message": "Course added successfully"}), 201

@app.route('/courses', methods=['GET'])
def get_courses():
    """Retrieves all available courses."""
    courses = Course.query.all()
    return jsonify({"courses": [course.course_name for course in courses]}), 200



@app.route('/siyavula-get-token', methods=['POST'])
def siyavula_get_token():
    """
    Endpoint to get a Siyavula authentication token.
    """
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    region = data.get("region", "ZA")
    curriculum = data.get("curriculum", "CAPS")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    token_response = get_siyavula_token(username, password, region, curriculum) # type: ignore

    if token_response["status"] == "success":
        return jsonify(token_response), 200
    else:
        return jsonify(token_response), 401

@app.route('/siyavula-verify', methods=['POST'])
def siyavula_verify():
    """
    Endpoint to verify a Siyavula authentication token.
    """
    data = request.get_json()

    client_token = data.get("client_token")
    user_token = data.get("user_token")

    if not client_token or not user_token:
        return jsonify({"message": "Client and User tokens are required"}), 400

    verify_response = verify_siyavula_token(client_token, user_token)

    if verify_response["status"] == "success":
        return jsonify(verify_response), 200
    else:
        return jsonify(verify_response), 401


@app.route("/")
def home():
    return "Hello World! Lea First Flask & Python attempt", 200

if __name__ == '__main__':
    app.run(debug=True)

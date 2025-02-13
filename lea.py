from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from models import db, User, Course, UserCourse
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt = Bcrypt(app)

@app.route("/")
def home():
    return "Hello World! Lea First Flask & Python attempt"

if __name__ == '__main__':
    app.run(debug=True)


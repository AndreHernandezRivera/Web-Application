import boto3
import uuid

from flask import Flask, redirect, url_for, request, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy 


import os
from dotenv import load_dotenv



# Load environment variables from the .env file
load_dotenv()


# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png'}

# def allowed_file(filename):
    # return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    bucket = db.Column(db.String(100))
    region = db.Column(db.String(100))

def create_app():
    app = Flask(__name__)
    app.secret_key=os.urandom(24)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    
    db.init_app(app)
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            
            # Find the user by username
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password) and user.username == os.getenv("ME"):
                # Store the user's ID in the session
                session["user_id"] = user.id
                
                return redirect(url_for("index"))
            else:
                error = "Invalid username or password"
                return render_template("login.html", error=error)
        
        return render_template("login.html", error=None)


    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            hashed_password = generate_password_hash(password)
            
            # Create a new user
            user = User(username=username, password=hashed_password)
            db.session.add(user)
            
            try:
                db.session.commit()
            except Exception as e:
                error = "An error occurred while signing up"
                return render_template("login.html", error=error)
            
            return redirect(url_for("login"))
        
        return render_template("login.html", error=None)


    @app.route("/logout")
    def logout():
        # Clear the user's session data
        session.clear()
        return redirect(url_for("login"))


    @app.route("/", methods=["GET", "POST"])
    def index():
        if "user_id" not in session:
            return redirect(url_for("login"))
        if request.method == "POST":
            uploaded_file = request.files["file-to-save"]
            
            # if not allowed_file(uploaded_file.filename):
                # return "FILE NOT ALLOWED!"

            new_filename = uuid.uuid4().hex + '.' + uploaded_file.filename.rsplit('.', 1)[1].lower()

            bucket_name = "flaskfilebucket"
            s3 = boto3.resource(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION'),
            )
            
            
            s3.Bucket(bucket_name).upload_fileobj(uploaded_file, new_filename)

            file = File(original_filename=uploaded_file.filename, filename=new_filename,
                bucket=bucket_name, region=os.getenv('AWS_REGION'))

            db.session.add(file)
            db.session.commit()

            return redirect(url_for("index"))

        files = File.query.all()

        return render_template("index.html", files=files)

    @app.route("/delete/<int:file_id>", methods=["POST"])
    def delete_file(file_id):
        file = File.query.get(file_id)
        if file:
        
            s3 = boto3.resource(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION')
            )

            s3.Object(file.bucket, file.filename).delete()
        
        
            db.session.delete(file)
            db.session.commit()
        
        return redirect(url_for("index"))


    return app

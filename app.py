from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from PIL import Image, ImageChops
import os
import tensorflow as tf
import numpy as np

app = Flask(__name__)
app.secret_key = "your_secret_key" 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app) 

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


users = {"test@example.com": "1234"}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users and users[email] == password:
            session["user_id"] = email  # Set user_id in session
            session["username"] = email.split("@")[0]  # Or fetch real name if using DB
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))  
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if email in users:
            flash("Email already registered.", "error")
            return redirect(url_for("register"))
        else:
            users[email] = password
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        return render_template("dashboard.html", username=session["username"])
    else:
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/muscle-training")
def muscle_training():
    return render_template("muscle_training.html")

# Load your trained model once
level1_model = tf.keras.models.load_model('level1_model.h5')

def predict_image(img_path):
    img = Image.open(img_path).resize((128,128)).convert('RGB')
    arr = np.array(img) / 255.0
    arr = arr.reshape((1,128,128,3))
    pred = level1_model.predict(arr)[0][0]
    return pred

@app.route("/levels", methods=["GET", "POST"])
def levels():
    if "current_level" not in session:
        session["current_level"] = 1

    feedback = ""
    level_passed = False

    if request.method == "POST" and session["current_level"] == 1:
        uploaded_file = request.files.get("user_image")
        if uploaded_file:
            user_img_path = os.path.join("static", "user_upload.jpg")
            uploaded_file.save(user_img_path)
            pred = predict_image(user_img_path)
            if pred > 0.5:  # Adjust threshold as needed
                session["current_level"] = 2
                feedback = "Matched! Level 1 passed."
                level_passed = True
            else:
                feedback = "Not matched. Try again."

    # Handle "Next" button for Level 2
    if request.method == "POST" and session["current_level"] == 2 and request.form.get("next_level"):
        # You can add logic for Level 2 here
        feedback = "Welcome to Level 2!"

    return render_template("levels.html", current_level=session["current_level"], feedback=feedback, level_passed=level_passed)

@app.route("/reset_level")
def reset_level():
    session["current_level"] = 1
    return redirect(url_for("levels"))

@app.route("/weight-lifting")
def weight_lifting():
    return render_template("weight_lifting.html")

@app.route("/exercise-program")
def exercise_program():
    return render_template("exercise_program.html")

@app.route("/nutrition-plans")
def nutrition_plans():
    return render_template("nutrition_plans.html")

@app.route("/practice-time")
def practice_time():
    return render_template("practice_time.html")

@app.route("/diet-program", methods=["GET", "POST"])
def diet_program():
    result = None
    if request.method == "POST":
        weight = float(request.form.get("weight", 0))
        height = float(request.form.get("height", 0))
        protein = round(weight * 1.6, 1)
        fiber = 30
        carbs = round(weight * 4, 1)
        result = {
            "protein": protein,
            "fiber": fiber,
            "carbs": carbs
        }
    return render_template("diet.html", result=result)

@app.route("/diet", methods=["GET", "POST"])
def diet():
    result = None
    if request.method == "POST":
        weight = float(request.form.get("weight", 0))
        height = float(request.form.get("height", 0))
        # Example calculations (adjust as needed)
        protein = round(weight * 1.6, 1)  # grams per kg body weight
        fiber = 30  # general daily recommendation in grams
        carbs = round(weight * 4, 1)     # grams per kg body weight
        result = {
            "protein": protein,
            "fiber": fiber,
            "carbs": carbs
        }
    return render_template("diet.html", result=result)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
# Remove Jinja template code from Python file.
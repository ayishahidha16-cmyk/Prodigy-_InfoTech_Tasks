from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "my_secret_key"


# ---------------- CREATE DATABASE TABLE ----------------

def create_table():
    conn = sqlite3.connect("users.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return redirect("/login")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):

            # Create session
            session["user_id"] = user[0]
            session["user_name"] = user[1]

            # Go to dashboard
            return redirect("/dashboard")

        else:
            return "Invalid email or password!"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    # Check whether user is logged in
    if "user_id" not in session:
        return redirect("/login")

    name = session["user_name"]

    return render_template(
        "dashboard.html",
        name=name
    )


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Hash password before storing
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("users.db")

        try:

            conn.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
                """,
                (name, email, hashed_password)
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()
            return "Email already registered!"

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    # Remove session
    session.clear()

    return redirect("/login")


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    create_table()
    app.run(debug=True)
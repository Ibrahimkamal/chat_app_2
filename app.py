from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_socketio import SocketIO, emit, join_room

from database import User, db

app = Flask(__name__)
app.config["SECRET_KEY"] = "any-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("admin" if user.is_admin else "customer"))
        flash("Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def customer():
    if current_user.is_admin:
        return redirect(url_for("admin"))
    return render_template("customer.html")


@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for("customer"))
    return render_template("admin.html")


@socketio.on("send_message")
def handle_message(data):

    room = data["room"]
    message = data["message"]
    sender = data["sender"]
    emit("receive_message", {"message": message, "sender": sender}, room=room)


@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)


def create_user(username, password, is_admin):
    with app.app_context():
        # Check if user already exists
        if not User.query.filter_by(username=username).first():
            new_user = User()
            new_user.username = username
            new_user.set_password(password)
            new_user.is_admin = is_admin
            db.session.add(new_user)
            db.session.commit()
            print(f"User {username} created successfully")
        else:
            print(f"User {username} already exists")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    create_user("admin", "admin", True)
    create_user("customer", "customer", False)
    socketio.run(app, debug=True)


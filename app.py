from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"


# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    visits = db.relationship("PageVisit", backref="visitor", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PageVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(20), nullable=True)
    user_agent = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    username = db.Column(db.String(80), nullable=True)  # เพิ่มคอลัมน์ username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/home")
@login_required
def home():
    visit = PageVisit(
        page="home",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        user_id=current_user.id,
        username=current_user.username,  # เพิ่ม username
    )
    db.session.add(visit)
    db.session.commit()
    return render_template("home.html", debug=app.debug)


@app.route("/stats")
@login_required
def stats():
    if not current_user.username == "admin":
        flash("You don't have permission to view this page")
        return redirect(url_for("home"))

    # Get all page visits
    page_visits = PageVisit.query.order_by(PageVisit.timestamp.desc()).all()

    # Count visits per page
    page_counts = (
        db.session.query(PageVisit.page, db.func.count(PageVisit.id))
        .group_by(PageVisit.page)
        .all()
    )

    return render_template(
        "stats.html", page_counts=page_counts, page_visits=page_visits
    )


@app.route("/page<int:number>")
@login_required
def page(number):
    if 1 <= number <= 10:
        visit = PageVisit(
            page=f"page{number}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            user_id=current_user.id,
            username=current_user.username,  # เพิ่ม username
        )
        db.session.add(visit)
        db.session.commit()
        return render_template(f"page{number}.html", number=number)
    return redirect(url_for("home"))


# สร้างฐานข้อมูลเมื่อรันแอพ
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from extensions import db
from models import User, Post, Like, Comment, PageVisit


def init_routes(app):

    @app.route("/")
    def home():
        posts = Post.query.all()  # ดึงโพสต์ทั้งหมดจากฐานข้อมูล
        return render_template("home.html", posts=posts)

    @app.route("/create_post", methods=["POST"])
    @login_required
    def create_post():
        content = request.form.get("content")
        room_number = request.form.get("room_number")
        title = request.form.get("title")

        if not content or not room_number:
            flash("Content and room number are required", "danger")
            return redirect(url_for("home"))

        post = Post(
            content=content,
            user_id=current_user.id,
            room_number=int(room_number),
            title=title,
        )

        db.session.add(post)
        db.session.commit()

        # Redirect to the selected room
        return redirect(url_for("page", number=room_number))

    @app.route("/like_post/<int:post_id>", methods=["POST"])
    @login_required
    def like_post(post_id):
        post = Post.query.get_or_404(post_id)
        if current_user in post.likes:
            post.likes.remove(current_user)
        else:
            post.likes.append(current_user)
        db.session.commit()
        return redirect(url_for("home"))

    @app.route("/comment_post/<int:post_id>", methods=["POST"])
    @login_required
    def comment_post(post_id):
        content = request.form.get("content")
        if not content:
            flash("Comment content is required", "danger")
            return redirect(url_for("page", number=Post.query.get(post_id).room_number))

        comment = Comment(
            content=content,
            user_id=current_user.id,
            post_id=post_id,
        )

        db.session.add(comment)
        db.session.commit()
        flash("Comment added successfully", "success")
        return redirect(url_for("page", number=Post.query.get(post_id).room_number))

    @app.route("/page/<int:number>")
    @login_required
    def page(number):
        # Fetch all posts in this room
        room_posts = (
            Post.query.filter_by(room_number=number)
            .order_by(Post.timestamp.desc())
            .all()
        )

        data = {"title": f"Room {number}", "content": f"Welcome to Room {number}!"}

        return render_template("page.html", data=data, room_posts=room_posts)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out", "success")
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            print(f"Login attempt - Username: {username}")  # debug
            print(f"Password provided: {bool(password)}")  # debug

            user = User.query.filter_by(username=username).first()
            print(f"User found: {user is not None}")  # debug

            if user:
                print(f"Stored password hash: {user.password}")  # debug
                if user.check_password(password):
                    login_user(user)
                    flash("Logged in successfully", "success")
                    return redirect(url_for("home"))

            flash("Invalid username or password", "danger")
        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")

            if User.query.filter_by(username=username).first():
                flash("Username already exists", "danger")
                return redirect(url_for("register"))

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registered successfully", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

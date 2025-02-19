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

        if not content:
            flash("Post content cannot be empty")
            return redirect(url_for("home"))

        post = Post(
            content=content,
            user_id=current_user.id,
            room_number=room_number,
            title=title,
        )

        db.session.add(post)
        db.session.commit()

        return redirect(url_for("home"))

    @app.route("/like_post/<int:post_id>", methods=["POST"])
    @login_required
    def like_post(post_id):
        post = Post.query.get_or_404(post_id)
        like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

        if like:
            db.session.delete(like)
            post.like_count -= 1
        else:
            like = Like(user_id=current_user.id, post_id=post_id)
            db.session.add(like)
            post.like_count += 1

        db.session.commit()
        return redirect(url_for("home"))

    @app.route("/comment_post/<int:post_id>", methods=["POST"])
    @login_required
    def comment_post(post_id):
        content = request.form.get("content")
        if not content:
            flash("Comment cannot be empty")
            return redirect(url_for("home"))

        comment = Comment(content=content, user_id=current_user.id, post_id=post_id)

        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("home"))

    @app.route("/page/<int:number>")
    @login_required
    def page(number):
        post = Post.query.get_or_404(number)

        # เพิ่มจำนวนการดู
        post.view_count += 1
        db.session.commit()

        # บันทึกการเข้าชม
        visit = PageVisit(username=current_user.username, page=f"Page {number}")
        db.session.add(visit)
        db.session.commit()

        return render_template("page.html", number=number)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()  # ทำการออกจากระบบ
        return redirect(url_for("home"))  # เปลี่ยนเส้นทางไปยังหน้าแรก

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("home"))  # ถ้าผู้ใช้ล็อกอินอยู่แล้วก็ให้ไปที่หน้า home

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(
                password
            ):  # ตรวจสอบว่า username และ password ถูกต้อง
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Login failed. Check your username and/or password")
                return redirect(url_for("login"))

        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")  # Get the email from the form
            password = request.form.get("password")

            # ตรวจสอบว่าผู้ใช้มีอยู่แล้วหรือไม่
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("Username already exists. Please choose a different one.")
                return redirect(url_for("register"))

            # สร้างผู้ใช้ใหม่
            new_user = User(username=username, email=email)  # Set the email field
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! You can now login.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

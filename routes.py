from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from datetime import datetime
from extensions import db
from models import Post, Like, Comment, PageVisit


def init_routes(app):

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

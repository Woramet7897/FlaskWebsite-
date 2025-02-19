from datetime import datetime
from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    room_number = db.Column(db.Integer, nullable=False)

    # Optional: เพิ่มฟีเจอร์เพิ่มเติม
    title = db.Column(db.String(200))
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)

    # Relationships
    author = db.relationship("User", backref="posts")
    likes = db.relationship("Like", backref="post", lazy="dynamic")
    comments = db.relationship("Comment", backref="post", lazy="dynamic")


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)


# routes.py
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
        content=content, user_id=current_user.id, room_number=room_number, title=title
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


# ถ้าต้องการเก็บสถิติเพิ่มเติม
@app.route("/page/<int:number>")
@login_required
def page(number):
    post = Post.query.get_or_404(number)
    post.view_count += 1
    db.session.commit()

    # บันทึกการเข้าชมสำหรับสถิติ
    visit = PageVisit(
        username=current_user.username,
        page=f"Page {number}",
        timestamp=datetime.utcnow(),
    )
    db.session.add(visit)
    db.session.commit()

    return render_template("page.html", number=number)

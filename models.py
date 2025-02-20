from datetime import datetime
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    # ฟังก์ชันสำหรับตั้งรหัสผ่าน
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # ฟังก์ชันสำหรับตรวจสอบรหัสผ่าน
    def check_password(self, password):
        return check_password_hash(self.password, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    room_number = db.Column(db.Integer, nullable=False)

    title = db.Column(db.String(200))
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)

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


class PageVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    page = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

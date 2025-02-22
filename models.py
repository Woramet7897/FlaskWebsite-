from datetime import datetime
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}

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
        try:
            return check_password_hash(self.password, password)
        except TypeError as e:
            print(f"Error checking password: {e}")  # debug
            print(f"Stored password hash: {self.password}")  # debug
            print(f"Provided password: {password}")  # debug
            return False


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
    comments = db.relationship("Comment", backref="post", lazy=True)


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

    author = db.relationship("User", backref="comments")


class PageVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    page = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

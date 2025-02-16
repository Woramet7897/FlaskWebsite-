from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# สร้างโมเดลสำหรับเก็บข้อมูลการเข้าชม
class PageVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(20), nullable=True)
    user_agent = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"Visit('{self.page}', '{self.timestamp}')"


# สร้างฐานข้อมูลเมื่อรันแอพ
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    # บันทึกการเข้าชมหน้า home
    visit = PageVisit(
        page="home",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
    )
    db.session.add(visit)
    db.session.commit()

    return render_template("home.html")


# สร้าง route สำหรับแต่ละหน้าโดยใช้ฟังก์ชันที่แตกต่างกัน
def create_page_route(page_num):
    def page_view():
        # บันทึกการเข้าชม
        visit = PageVisit(
            page=f"page{page_num}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
        )
        db.session.add(visit)
        db.session.commit()

        return render_template(f"page{page_num}.html", number=page_num)

    # กำหนดชื่อฟังก์ชันแบบ dynamic
    page_view.__name__ = f"page_{page_num}"
    return page_view


# ลงทะเบียน route สำหรับแต่ละหน้า
for i in range(1, 11):
    app.add_url_rule(f"/page{i}", f"page_{i}", create_page_route(i))


# เพิ่ม route สำหรับดูสถิติ
@app.route("/stats")
def stats():
    # นับจำนวนการเข้าชมแต่ละหน้า
    page_counts = (
        db.session.query(PageVisit.page, db.func.count(PageVisit.id).label("count"))
        .group_by(PageVisit.page)
        .order_by(db.text("count DESC"))
        .all()
    )

    return render_template("stats.html", page_counts=page_counts)


if __name__ == "__main__":
    app.run(debug=True)

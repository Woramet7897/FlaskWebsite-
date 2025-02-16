from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


# แก้ปัญหาด้วยการใช้ lambda และ unique endpoint สำหรับแต่ละหน้า
for i in range(1, 11):
    app.route(f"/page{i}", endpoint=f"page_{i}")(
        lambda i=i: render_template(f"page{i}.html")
    )

if __name__ == "__main__":
    app.run(debug=True)

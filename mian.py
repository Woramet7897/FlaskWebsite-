from flask import Flask, render_template_string

app = Flask(__name__)

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
</head>
<body>
    <main class="container">
        <h1>Home</h1>
        <nav>
            {% for i in range(1, 11) %}
                <a href="/page{{ i }}" role="button">Page {{ i }}</a>
            {% endfor %}
        </nav>
    </main>
</body>
</html>
"""

PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page {{ number }}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
</head>
<body>
    <main class="container">
        <h1>Page {{ number }}</h1>
        <a href="/" role="button">Back to Home</a>
    </main>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HOME_TEMPLATE)


# แก้ปัญหาด้วยการใช้ lambda และ unique endpoint สำหรับแต่ละหน้า
for i in range(1, 11):
    app.route(f"/page{i}", endpoint=f"page_{i}")(
        lambda i=i: render_template_string(PAGE_TEMPLATE, number=i)
    )

if __name__ == "__main__":
    app.run(debug=True)

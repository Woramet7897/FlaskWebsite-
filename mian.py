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
        <a href="/page1" role="button">Go to Page 1</a>
    </main>
</body>
</html>
"""

PAGE1_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page 1</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
</head>
<body>
    <main class="container">
        <h1>Page 1</h1>
        <a href="/" role="button">Back to Home</a>  
    </main>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HOME_TEMPLATE)


@app.route("/page1")
def page1():
    return render_template_string(PAGE1_TEMPLATE)


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template as render, redirect, url_for

app = Flask(__name__)

@app.route('/')
def Home():
    return render("index.html")

if __name__ == "__main__":
    app.run(debug=True)
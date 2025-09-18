from flask import Flask, render_template as render, redirect, url_for
from flask_sqlalchemy import SQLAlchemy as sql

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biomatric.db'

db = sql(app)

@app.route('/')
def Home():
    return render("index.html")

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["ENV"] = "production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)
Migrate(app, db)


class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))


# @app.route("/")
# def home():
#     return "<h1>Bem-vindo!</h1>"


@app.route("/")
def home():
    tracks = Track.query.all()
    return render_template("index.html", tracks=tracks)

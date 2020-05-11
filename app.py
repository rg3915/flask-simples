from flask import Flask


app = Flask(__name__)
app.config["ENV"] = "production"


@app.route("/")
def home():
    return "<h1>Bem-vindo!</h1>"

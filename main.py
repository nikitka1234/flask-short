import random
import string

from flask import Flask, render_template, redirect, url_for

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


class URLForm(FlaskForm):
    url = StringField("Введите ссылку", validators=[DataRequired(message="Поле для ввода ссылки не моежт быть пустым")])
    submit = SubmitField("Сократить")


app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET_KEY"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"

db = SQLAlchemy(app)


class Urls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    short = db.Column(db.String(255), unique=True)
    visits = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow())


with app.app_context():
    db.create_all()


def shortener():
    while True:
        short_url = "".join(random.choices(string.ascii_letters + string.ascii_letters, k=6))

        if Urls.query.filter(Urls.short == short_url).first():
            continue

        return short_url


@app.route("/", methods=["GET", "POST"])
def index():
    form = URLForm()

    if form.validate_on_submit():
        urls_model = Urls()

        urls_model.url = form.url.data
        urls_model.short = shortener()

        db.session.add(urls_model)
        db.session.commit()

        return redirect(url_for("urls"))

    return render_template("index.html", form=form)


@app.route("/urls")
def urls():
    urls_list = Urls.query.order_by(Urls.date.desc()).all()

    return render_template("urls.html", urls_list=urls_list)


@app.route("/<string:shorts>")
def short(shorts):
    url = Urls.query.filter(Urls.short == shorts).first()

    if url:
        url.visits += 1

        db.session.add(url)
        db.session.commit()

    return redirect(url.url)

from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TimeField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy

rating_options = ['🤬', '😢😢', '😊😊😊', '😃😃😃😃', '🤩🤩🤩🤩🤩']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key_is_kept_in_my___'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cifi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    cafe_name = db.Column(db.String(250), nullable=False)
    opening_time = db.Column(db.Time)
    closing_time = db.Column(db.Time)
    coffee_rating = db.Column(db.Integer, nullable=False)
    wifi_rating = db.Column(db.Integer, nullable=False)
    toilet_rating = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(250))


db.create_all()


class CifiForm(FlaskForm):
    secret_key = PasswordField('Secret Key', validators=[DataRequired()])
    cafe_name = StringField("Cafe Name", validators=[DataRequired()])
    opening_time = TimeField('Opening Time')
    closing_time = TimeField('Closing Time')
    coffee_rating = SelectField('Coffee Rating', choices=rating_options, validators=[DataRequired()])
    wifi_rating = SelectField('Wifi Rating', choices=rating_options, validators=[DataRequired()])
    toilet_rating = SelectField('Toilet Rating', choices=rating_options, validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), URL()])
    submit = SubmitField('Add Cafe')


@app.route('/')
def home():
    cafe_list = db.session.query(Cafe).all()
    leng = len(cafe_list)
    return render_template('index.html', cafes=cafe_list, leng=leng, path="/")


@app.route('/insert-new-cafe', methods=["GET", "POST"])
def insert_new():
    form = CifiForm()
    if form.validate_on_submit():

        if form.secret_key.data == 'i9s19h8a1n14':
            new_cafe = Cafe(
                cafe_name=form.cafe_name.data, opening_time=form.opening_time.data,
                closing_time=form.closing_time.data, coffee_rating=form.coffee_rating.data,
                wifi_rating=form.wifi_rating.data, toilet_rating=form.toilet_rating.data,
                location=form.location.data
            )
            db.session.add(new_cafe)
            db.session.commit()

        return redirect(url_for('home'))
    return render_template('new-cafe.html', form=form, path='/insert-new-cafe')


@app.route('/cafe/<id>')
def cafe_details(id):
    cafe_to_show = Cafe.query.get(id)
    return render_template('cafe-details.html', cafe=cafe_to_show)


@app.route('/delete/<id>', methods=["POST"])
def delete_cafe(id):
    if request.method == 'POST':
        form_data = request.form
        if form_data['secret_key'] == 'i9s19h8a1n14':
            cafe_to_del = Cafe.query.get(id)
            db.session.delete(cafe_to_del)
            db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

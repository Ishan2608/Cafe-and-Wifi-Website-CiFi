from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TimeField, PasswordField, FileField, MultipleFileField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

rating_options = ['🤬', '😢😢', '😊😊😊', '😃😃😃😃', '🤩🤩🤩🤩🤩']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key_is_kept_in_my___'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cifi_cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    cafe_name = db.Column(db.String(250), nullable=False)
    opening_time = db.Column(db.Time)
    closing_time = db.Column(db.Time)
    coffee_rating = db.Column(db.Integer, nullable=False)
    wifi_rating = db.Column(db.Integer, nullable=False)
    toilet_rating = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(250))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))


db.create_all()

# Create the admin
admin = User(email="ishanrastogi26@gmail.com", password="i9s19h8a1n14")
db.session.add(admin)
db.session.commit()


class CifiForm(FlaskForm):
    cafe_name = StringField("Cafe Name", validators=[DataRequired()])
    opening_time = TimeField('Opening Time')
    closing_time = TimeField('Closing Time')
    coffee_rating = SelectField('Coffee Rating', choices=rating_options, validators=[DataRequired()])
    wifi_rating = SelectField('Wifi Rating', choices=rating_options, validators=[DataRequired()])
    toilet_rating = SelectField('Toilet Rating', choices=rating_options, validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])

    images = MultipleFileField('Upload Images', validators=[DataRequired()])
    submit = SubmitField('Add Cafe')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log Me In")


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    # Implement logic to load a user object using the user_id
    return User.query.get(user_id)  # Example assuming SQLAlchemy ORM


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif password != user.password:
            flash("Password Doesn't Match")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/')
def home():
    cafe_list = db.session.query(Cafe).all()
    leng = len(cafe_list)
    user_stat = "user"
    if current_user.is_authenticated:
        if (current_user.id == 1):
            user_stat = "admin"
    return render_template('index.html', cafes=cafe_list, leng=leng, path="/", user_stat=user_stat)


@app.route('/insert-new-cafe', methods=["GET", "POST"])
@admin_only
def insert_new():
    print("Inside Insert New")
    form = CifiForm()
    if form.validate_on_submit():
        print("Entered Form Validation")

        # uploaded_images = form.images.data
        # for image in uploaded_images:
        #     # Do something with each image (e.g., save to a folder, process, etc.)
        #     # image.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename)))
        #     print(image.filename)  # Example: printing the filenames

        new_cafe = Cafe(
            cafe_name=form.cafe_name.data, opening_time=form.opening_time.data,
            closing_time=form.closing_time.data, coffee_rating=form.coffee_rating.data,
            wifi_rating=form.wifi_rating.data, toilet_rating=form.toilet_rating.data,
            location=form.location.data
        )

        # print("Created Object Form Data")
        db.session.add(new_cafe)
        db.session.commit()
        # print("New Cafe Inserted")
        return redirect(url_for('home'))
    user_stat = "user"
    if current_user.is_authenticated:
        if (current_user.id == 1):
            user_stat = "admin"
    return render_template('new-cafe.html', form=form, path='/insert-new-cafe', user_stat=user_stat)


@app.route('/cafe/<id>')
def cafe_details(id):
    cafe_to_show = Cafe.query.get(id)
    return render_template('cafe-details.html', cafe=cafe_to_show)


@app.route('/delete/<id>', methods=["POST"])
@admin_only
def delete_cafe(id):
    if request.method == 'POST':
        cafe_to_del = Cafe.query.get(id)
        db.session.delete(cafe_to_del)
        db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

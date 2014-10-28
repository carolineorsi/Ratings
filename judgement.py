from flask import Flask, render_template, redirect, request, url_for, flash
from flask import session as flask_session
import jinja2
import model

app = Flask(__name__)
app.secret_key = 'blah'
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def create_user():
    user = model.User()
    user.email = request.form.get("email")
    user.password = request.form.get("password")
    user.age = request.form.get("age")
    user.zipcode = request.form.get("zipcode")
    user.gender = request.form.get("gender")
    model.session.add(user)
    model.session.commit()
    return redirect(url_for("show_login"))

@app.route("/login")
def show_login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def process_login():
    email = request.form.get("email")
    password = request.form.get("password")
    user = model.session.query(model.User).filter_by(email = email).first()
    if user == None:
        flash("User does not exist")
        return redirect(url_for("process_login"))
    elif password != user.password:
        flash("Wrong password.")
        return redirect(url_for("process_login"))
    else:
        flask_session['id'] = user.id
        flask_session['email'] = user.email
        flask_session['age'] = user.age
        flask_session['zipcode'] = user.zipcode
        flask_session['gender'] = user.gender
        return render_template("account.html", email=flask_session['email'], user_id=flask_session['id']) 

@app.route("/list_users")
def list_users():
    user_list = model.session.query(model.User).limit(5).all()
    return render_template("list.html", users=user_list)

@app.route("/list_ratings/<int:user_id>")
def list_ratings(user_id):
    user = model.session.query(model.User).get(user_id)
    ratings_list = user.ratings
    return render_template("ratings.html", user=user, ratings=ratings_list) 

@app.route("/all_movies")
def list_movies():
    all_movies = model.session.query(model.Movie).all()
    movie_title = []
    movie_url = []
    for i in range(len(all_movies)):
        movie_title.append(all_movies[i].movie_name)
        movie_url.append(all_movies[i].url)
    return render_template("all_movies.html", all_movies = all_movies)

@app.route("/view/<int:movie_id>")
def view_rating(movie_id):
    movie_info = model.session.query(model.Movie).get(movie_id)
    your_rating = None
    for rating in movie_info.ratings:
        if rating.user_id == flask_session['id']:
            your_rating = rating
            break

    return render_template("movie_detail.html", movie=movie_info, rating=your_rating)

@app.route("/update/<int:movie_id>", methods=['POST'])
def update_rating(movie_id):
    flag = False
    rating = request.form.get('newRating')
    this_user = model.session.query(model.User).get(flask_session['id'])
    for i in range(len(this_user.ratings)):
        if this_user.ratings[i].movie_id == movie_id:
            this_user.ratings[i].rating = rating
            model.session.add(this_user)
            model.session.commit()
            flag = True
            return str(this_user.ratings[i].rating)            

    if flag == False:
        newRating = model.Rating()
        newRating.movie_id = movie_id
        newRating.user_id = this_user.id
        newRating.rating = rating
        model.session.add(newRating)
        model.session.commit()
        return str(newRating.rating)


if __name__ == "__main__":
    app.run(debug = True)

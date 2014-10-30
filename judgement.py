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
    if email == "":
        flash("Invalid email address.")
        return redirect(url_for("process_login"))
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
        #        movie_title.append(all_movies[i].movie_name)
        # return render_template("account.html", email=flask_session['email'], user_id=flask_session['id'])
        return redirect(url_for("account_page"))

@app.route("/account")
def account_page():
    if 'email' in flask_session:
        return render_template("account.html", email=flask_session['email'], user_id=flask_session['id'])
    else:
        return render_template("account.html")

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
    avg_score = average_score(movie_info)
    for rating in movie_info.ratings:
        if 'id' in flask_session:
            if rating.user_id == flask_session['id']:
                your_rating = rating
                break

    user = model.session.query(model.User).get(flask_session['id'])
    prediction = None
    if not your_rating:
        prediction = user.predict_rating(movie_info)
        effective_rating = prediction
    else:
        effective_rating = your_rating.rating

    the_eye = model.session.query(model.User).filter_by(email="theeye@ofjudgement.com").first()
    eye_rating = model.session.query(model.Rating).filter_by(user_id=the_eye.id, movie_id=movie_info.id).first()

    if not eye_rating:
        eye_rating = the_eye.predict_rating(movie_info)
    else:
        eye_rating = eye_rating.rating

    difference = abs(eye_rating - effective_rating)

    messages = ["I suppose you don't have such bad taste after all.",
             "I regret every decision that I've ever made that has brought me to listen to your opinion.",
             "Words fail me, as your taste in movies has clearly failed you.",
             "That movie is great. For a clown to watch. Idiot."]

    beratement = messages[int(difference)-1]

    return render_template("movie_detail.html", 
                            movie=movie_info, 
                            rating=your_rating, 
                            avg_score = avg_score, 
                            prediction=prediction, beratement=beratement)

def average_score(movie_info):
    avg_score = 0
    for i in range(len(movie_info.ratings)):
        avg_score += movie_info.ratings[i].rating
    avg_score = float(avg_score)/float(i)
    return avg_score

@app.route("/update/<int:movie_id>", methods=['POST'])
def update_rating(movie_id):
    flag = False
    rating = request.form.get('newRating')
    this_user = model.session.query(model.User).get(flask_session['id'])
    movie = model.session.query(model.Movie).get(movie_id)

    # Update average score in movie detail page by passing average back to
    # javascript. Needs to be converted to JSON.
    # avg_score = average_score(movie)

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

@app.route("/logout")
def log_out():
    flask_session.clear()    
    return redirect(url_for("show_login"))



if __name__ == "__main__":
    app.run(debug = True)

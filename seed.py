import model
import csv
import datetime

def load_users(session):
    f = open("seed_data/u.user", "r")
    reader = csv.reader(f, delimiter="|")
    all_users = []
    for i, row in enumerate(reader):
        aUser = model.User()
        aUser.id = row[0]
        aUser.age = row[1]
        aUser.gender = row[2]
        aUser.zipcode = row[4]
        all_users.append(aUser)
        session.add(all_users[i])

def load_movies(session):
    f = open("seed_data/u.item", "r")
    reader = csv.reader(f, delimiter="|")
    all_movies = []
    i = 0
    for row in reader:
         aMovie = model.Movie()
         aMovie.id = row[0]
         aMovie.movie_name = row[1][0:-7]  # DEFINITELY DOCUMENT THIS OR MAKE IT SAFE
         aMovie.movie_name = aMovie.movie_name.decode("latin-1")
         try:
             aMovie.release_date = datetime.datetime.strptime(row[2], "%d-%b-%Y")
         except:
            print "HERE", row
            raw_input()
            aMovie.release_date = None 
         aMovie.url = row[4]
         all_movies.append(aMovie)
         session.add(all_movies[i])
         i += 1


def load_ratings(session):
    f = open("seed_data/u.data", "r")
    reader = csv.reader(f, delimiter="\t")
    all_ratings = []
    i = 0
    for row in reader:
        aRating = model.Rating()
        aRating.id = i + 1
        aRating.user_id = row[0]
        aRating.movie_id = row[1]
        aRating.rating = row[2]
        all_ratings.append(aRating)
        session.add(all_ratings[i])
        i += 1

def main(session):
    # You'll call each of the load_* functions with the session as an argument
    # load_users(session)
     load_movies(session)
    # load_ratings(session)
    # print vars(session.query(model.Movie).get(1))
    # print vars(session.query(model.User).get(1))
    # print vars(session.query(model.Rating).get(1))
    # session.commit()
    #pass

if __name__ == "__main__":
    s= model.connect()
    main(s)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, and_, or_
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.orm import scoped_session
from sqlalchemy import ForeignKey
import correlation


#magical shit that makes each session thread-safe
engine = create_engine("sqlite:///ratings.db", echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()


### Class declarations go here
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    email = Column(String(64), nullable = True)
    password = Column(String(64), nullable = True)
    age = Column(Integer, nullable = True)
    zipcode = Column(String(15), nullable = True)
    gender = Column(String(20), nullable = True)


    def similarity(self, other):
        u_movies = {}
        for rating in self.ratings:
            u_movies[rating.movie_id] = rating.rating
     
        rating_pairs = []
        for rating in other.ratings:
            u_rating = u_movies.get(rating.movie_id)
            if u_rating:
                rating_pairs.append((u_rating, rating.rating))

        if rating_pairs:
            return correlation.pearson(rating_pairs)
        else:
            return 0.0

    def predict_rating(self,movie):
        ratings = self.ratings
        other_ratings = movie.ratings
        other_users = [r.user for r in other_ratings]
        similarities = [(self.similarity(other_user), other_user) for other_user in other_users]
        similarities.sort(reverse = True)
        top_user = similarities[0]
        matched_rating = None
        for rating in other_ratings:
            if rating.user_id == top_user[1].id:
                matched_rating = rating
                break
        return matched_rating.rating * top_user[0]


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key = True)
    movie_name = Column(String(120), nullable = False)
    release_date = Column(Date)
    url = Column(String(150), nullable = True)

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key = True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    user_id  = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer, nullable = False)

    user = relationship("User", backref=backref("ratings", order_by=id))
    movie = relationship("Movie", backref=backref("ratings", order_by=id))


### End class declarations


def connect():
    global ENGINE
    global Session

    ENGINE = create_engine("sqlite:///ratings.db", echo=False)
    Session = sessionmaker(bind=ENGINE)
    return Session()


def main():
    pass
#    """In case we need this for something"""
#    session = connect()
    # results = session.query(Movie).filter(or_(Movie.movie_name.like('J%'),Movie.movie_name.like('Q%'))).all()
    # for result in results:
    #     print result.movie_name, result.release_date

    

if __name__ == "__main__":
    main()

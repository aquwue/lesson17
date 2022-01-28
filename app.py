# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    # description = fields.Str()
    # trailer = fields.Str()
    # year = fields.Int()
    # rating = fields.Float()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
genre_schema = GenreSchema()
dir_schema = DirectorSchema()


api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        res = Movie.query
        if director_id is not None:
            res = res.filter(Movie.director_id == director_id)
        if genre_id is not None:
            res = res.filter(Movie.genre_id == genre_id)
        if director_id is not None and genre_id is not None:
            res = res.filter(Movie.director_id == director_id, Movie.genre_id == genre_id)
        result = res.all()
        return movie_schema.dump(result, many=True)

    def post(self):
        r_json = request.json
        add_movie = Movie(**r_json)
        with db.session.begin():
            db.session.add(add_movie)
        return "", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid: int):
        try:
            movie = Movie.query.get(uid)
            return movie_schema.dump(movie), 200
        except Exception as e:
            return "Not founded", 404

    def delete(self, uid: int):
        movie = Movie.query.get(uid)
        if not movie:
            return 'Not founded', 404
        else:
            db.session.delete(movie)
            db.session.commit()
            return '', 204

    def put(self, uid: int):
        movie = Movie.query.get(uid)
        req_json = request.json
        if not movie:
            return 'Not founded', 404
        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.rating = req_json.get("rating")
        db.session.add(movie)
        db.session.commit()
        return "", 204

#-----------------------------------------------------------

@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = Director.query.all()
        return dir_schema.dump(all_directors, many=True), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return '', 201


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid: int):
        try:
            director = Director.query.get(uid)
            return dir_schema.dump(director), 200
        except Exception as e:
            return "Not founded", 404

    def delete(self, uid: int):
        director = Director.query.get(uid)
        if not director:
            return 'Not founded', 404
        else:
            db.session.delete(director)
            db.session.commit()
            return '', 204

    def put(self, uid: int):
        director = Director.query.get(uid)
        req_json = request.json
        if not director:
            return 'Not founded', 404
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

#----------------------------------------------------

@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = Genre.query.all()
        return genre_schema.dump(all_genres, many=True), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return '', 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid: int):
        try:
            genre = Genre.query.get(uid)
            return genre_schema.dump(genre), 200
        except Exception as e:
            return "Not founded", 404

    def delete(self, uid: int):
        genre = Genre.query.get(uid)
        if not genre:
            return 'Not founded', 404
        else:
            db.session.delete(genre)
            db.session.commit()
            return '', 204

    def put(self, uid: int):
        genre = Genre.query.get(uid)
        req_json = request.json
        if not genre:
            return 'Not founded', 404
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204



if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
#für create und insert: conn.execute (intern wird temporär cursor angelegt)
#für andere sql befehle und abfragen
#cur = conn.cursor
#cur.execute


conn = get_db_connection()
#DB Schema
conn.execute('''            
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    director TEXT NOT NULL,
    year INTEGER,
    genre TEXT,
    rating REAL,
    duration INTEGER
)
''')

conn.execute('''
INSERT INTO movies (title, director, year, genre, rating, duration)
VALUES ('Inception', 'Christopher Nolan', 2010, 'Sci-Fi', 8.8, 148)
''')

conn.execute('''
INSERT INTO movies (title, director, year, genre, rating, duration)
VALUES (?, ?, ?, ?, ?, ?)
''', ('The Matrix', 'Lana & Lilly Wachowski', 1999, 'Sci-Fi', 8.7, 136))

more_movies = [
    ('Interstellar', 'Christopher Nolan', 2014, 'Sci-Fi', 8.6, 169),
    ('Parasite', 'Bong Joon-ho', 2019, 'Thriller', 8.6, 132),
    ('The Godfather', 'Francis Ford Coppola', 1972, 'Crime', 9.2, 175),
    ('Pulp Fiction', 'Quentin Tarantino', 1994, 'Crime', 8.9, 154),
    ('The Dark Knight', 'Christopher Nolan', 2008, 'Action', 9.0, 152),
    ('Spirited Away', 'Hayao Miyazaki', 2001, 'Animation', 8.6, 125),
    ('The Shawshank Redemption', 'Frank Darabont', 1994, 'Drama', 9.3, 142),
    ('Whiplash', 'Damien Chazelle', 2014, 'Drama', 8.5, 107)
]
conn.executemany('''
INSERT INTO movies (title, director, year, genre, rating, duration)
VALUES (?, ?, ?, ?, ?, ?)
''', more_movies)

conn.commit()


@app.route('/movies', methods=['GET'])
def get_movies():
    movies = conn.execute('SELECT * FROM movies').fetchall()
    return jsonify([dict(row) for row in movies])

@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = conn.execute('SELECT * FROM movies WHERE id=?', (movie_id,)).fetchone()
    if movie is None:
        return jsonify({'error': 'Movie not found'}), 404
    return jsonify(dict(movie))

@app.route('/movies', methods=['POST'])
def add_movie():
    data = request.get_json()
    title = data.get('title')
    director = data.get('director')
    year = data.get('year')
    cur = conn.cursor()
    cur.execute('INSERT INTO movies (title, director, year) VALUES (?, ?, ?)', (title, director, year))
    conn.commit()
    return jsonify({'id': cur.lastrowid, 'title': title, 'director': director, 'year': year}), 201



#TODO lösche einen movie mit der id movie_id
#@app.route('/movies/<int:movie_id>', methods=['DELETE'])
#def del_movie(movie_id):



### Swagger UI Setup ###
SWAGGER_URL = '/swagger' 
API_URL = '/static/swagger.json'  

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Optional
        'app_name': "Movie API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True)
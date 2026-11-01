from flask import Flask, render_template, request, redirect, url_for, session, abort
import sqlite3

app = Flask(__name__)
app.secret_key = 'cinema_edit_secret_123'

def db_connection():
    conn = sqlite3.connect('cinema.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        genre TEXT,
        duration INTEGER,
        price INTEGER,
        description TEXT,
        image_url TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER,
        customer_name TEXT,
        seats INTEGER,
        show_date TEXT,
        selected_seats TEXT,
        FOREIGN KEY(movie_id) REFERENCES movies(id)
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/movies')
def movies():
    conn = db_connection()
    movies = conn.execute('SELECT * FROM movies ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('movies.html', movies=movies)

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if not session.get('edit_mode'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title')
        genre = request.form.get('genre')
        duration = request.form.get('duration')
        if duration:
            duration = int(duration)
        price = request.form.get('price')
        if price:
            price = int(float(price))
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        conn = db_connection()
        conn.execute('INSERT INTO movies (title, genre, duration, price, description, image_url) VALUES (?, ?, ?, ?, ?, ?)',
                     (title, genre, duration, price, description, image_url))
        conn.commit()
        conn.close()
        return redirect(url_for('movies'))
    return render_template('add_movie.html')


@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if not session.get('edit_mode'):
        return redirect(url_for('login'))
    conn = db_connection()
    conn.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('movies'))


@app.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    if not session.get('edit_mode'):
        return redirect(url_for('login'))
    conn = db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)).fetchone()
    if movie is None:
        conn.close()
        abort(404)
    if request.method == 'POST':
        title = request.form.get('title')
        genre = request.form.get('genre')
        duration = request.form.get('duration')
        if duration:
            duration = int(duration)
        price = request.form.get('price')
        if price:
            price = int(float(price))
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        conn.execute('UPDATE movies SET title=?, genre=?, duration=?, price=?, description=?, image_url=? WHERE id=?',
                     (title, genre, duration, price, description, image_url, movie_id))
        conn.commit()
        conn.close()
        return redirect(url_for('movies'))
    conn.close()
    return render_template('edit_movie.html', movie=movie)
@app.route('/buy_ticket/<int:movie_id>', methods=['GET', 'POST'])
def buy_ticket(movie_id):
    conn = db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)).fetchone()
    if movie is None:
        conn.close()
        abort(404)
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        seats = request.form.get('seats')
        show_date = request.form.get('show_date')
        selected_seats = request.form.get('selected_seats')
        conn.execute('INSERT INTO tickets (movie_id, customer_name, seats, show_date, selected_seats) VALUES (?, ?, ?, ?, ?)',
                     (movie_id, customer_name, seats, show_date, selected_seats))
        conn.commit()
        conn.close()
        return redirect(url_for('movies'))
    conn.close()
    return render_template('buy_ticket.html', movie=movie)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
            session['edit_mode'] = True
            return redirect(url_for('movies'))
        return render_template('login.html', error='Невірний пароль')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('edit_mode', None)
    return redirect(url_for('movies'))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

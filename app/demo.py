# imports
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
        abort, render_template, flash

# configuration
DATABASE = 'db/demo.db'
DEBUG = True
SECRET_KEY = 'correct horse battery staple'
USERNAME = 'admin'
PASSWORD = 'default'

# app code
app = Flask(__name__)
app.config.from_object(__name__)


# WRAPPERS

# Before each request, open a database connection.
@app.before_request
def before_request():
    g.db = connect_db()
    
# After each request, close the database connection.
@app.teardown_request
def teardown_request(exception):
    g.db.close()


# ROUTES

# Display index page.

@app.route("/")
def home():
    if session.get('logged_in'):
        return render_template('list_articles.jinja2')
    else:
        return render_template("home.jinja2")

@app.route('/articles')
def list_articles():
    cursor = g.db.execute('SELECT title, text FROM articles ORDER BY id DESC')
    articles = [{"title": row[0], "text": row[1]} for row in cursor.fetchall()]
    return render_template('list_articles.jinja2', articles=articles)

# TODO: create /article/<id> route

@app.route('/article/new', methods=['POST'])
def add_article():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('INSERT INTO articles (title, text) VALUES (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New article was successfully posted')
    return redirect(url_for('list_articles'))

@app.route('/home', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('list_articles'))
    return render_template('home.jinja2', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('list_articles'))


# UTILITY
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

if __name__ == '__main__':
    app.run()

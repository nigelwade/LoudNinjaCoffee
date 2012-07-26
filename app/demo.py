# imports
from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
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


# UTILITY

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

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
@app.route("/")
def home():
    if session.get('logged_in'):
        return redirect(url_for('list_articles'))
    else:
        return render_template("home.jinja2")

@app.route('/articles/')
def list_articles():
    cursor = g.db.execute('SELECT title, text FROM articles ORDER BY id DESC')
    articles = [{"title": row[0], "text": row[1]} for row in cursor.fetchall()]
    return render_template('list_articles.jinja2', articles=articles)
    

@app.route('/articles/<article_id>')
def show_article(article_id):
    # get a single article from the database, based on the id arguments
    cursor = g.db.execute('SELECT id, title, text FROM articles WHERE id = %d' % id)
    rows = cursor.fetchall()
    article = articles[0]
    article = {"id": row[0], "title": row[1], "text": row[2]}
    print "Showing article %s" % article["title"]
    return render_template('show_article.jinja2', article=article)


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

# shown as show entries
@app.route('/articles/new', methods=['GET'])
def add_article_form():
    if not session.get('logged_in'):
        abort(401)
    return render_template('add_article.jinja2')

@app.route('/articles/new', methods=['POST'])
def add_article():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('INSERT INTO articles (title, text) VALUES (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New article was successfully posted')
    return redirect(url_for('list_articles'))
    # TODO: show the new article instead

@app.route('/articles/edit', methods=['PUT'])
def edit_article_form():
    return render_template('add_article')




# TODO: handle article new GET request by showing article entry form


# TODO: handle /article/edit GET request by showing edit form

# TODO: handle /article/edit PUT request by updating article and showing it

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('list_articles'))

# TODO: create /article/<id> route



if __name__ == '__main__':
    app.run()
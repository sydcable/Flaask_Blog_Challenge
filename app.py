import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your seceret key'


# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn

#funtion to retrieve a post from the database
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()

    if post is None:
        abort(404)
    return post

# use the app.route() decorator to create a Flask view function called index()
@app.route('/')
def index():
    #get connection to db
    conn = get_db_connection()

    #execute query to read all post from post table in db
    posts = conn.execute('SELECT * FROM posts').fetchall() 
    #close connection
    conn.close()

    #send posts to index.html template
    return render_template('index.html', posts=posts)


# route to create a post
@app.route('/create/', methods=('GET', 'POST'))
def create():
    #determine if the page is being requested by POST or GET request
    if request.method == 'POST':
        #get the title and content that was submitted
        title = request.form['title']
        content = request.form['content']

        #display an error it title or content is not submitted
        if not title:
            flash("Title is required")
        elif not content:
            flash("Content is required")
        else:
            conn = get_db_connection()
            #insert data into database
            conn.execute('INSERT INTO posts (title, content) VALUES (?,?)', (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

#route to edit a post. Load page with get or post
#pass post id as url parameter
@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    #get the post from the database with a select query for the post with that id
    post = get_post(id)

    #determine if the page was requested with GET or POST
    #If POST, proccess the form data. Get the data and validate it. Update the post and redirect to the homepage
    if request.method == 'POST':
        #get the title and content
        title = request.form['title']
        content = request.form['content']

        #if no title or content flash an error message
        if not title:
            flash("Title is required")
        elif not content:
            flash("Content is required")
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    #If GET then display page
    return render_template('edit.html', post=post)

#create a route to delete a post
#delete route will only be proccessed with a POST method
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    #get the post
    post = get_post(id)

    #connect to the database
    conn = get_db_connection()

    #execute a delete query
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))

    #commit and close connection
    conn.commit()
    conn.close()

    #flash a success message
    flash('"{}" was successfully deleted!'.format(post['title']))
    
    #redirect to home page
    return redirect(url_for('index'))
    
app.run(port=5008)
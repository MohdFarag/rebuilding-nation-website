import os
from shutil import rmtree
from werkzeug.utils import secure_filename

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, json
)
from werkzeug.exceptions import abort

from auth import login_required
from db import mysql_connector, retrieve_tables
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import HTTPException

import pandas as pd
import math

from log import site_logger
from config import Config


#--------------------------------------------------------------------------#

bp_site = Blueprint('ahmedfrg', __name__)
UPLOAD_FOLDER = Config.UPLOAD_FOLDER

#--------------------------------------------------------------------------#

"""Constants"""
ALLOWED_EXTENSIONS_DOC = set(['pdf', 'doc', 'xlsx', 'png', 'jpg', 'jpeg'])

#--------------------------------------------------------------------------#

"""Functions"""
# Get Request
def argsGet(argName):
    if request.args.get(argName):
        field = request.args.get(argName)
    else:
        field = ""  
    return field

# Check Extension of file
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_DOC

# Save file
def saveFile(list, sn, fileName):

    if list and allowed_file(list.filename):
      filename = secure_filename(fileName + "." + list.filename.rsplit('.', 1)[1])
      path = app.config['UPLOAD_FOLDER'] + sn + "/" 
      os.makedirs(path, exist_ok=True)
      list.save(os.path.join(path, filename))
      return path + filename
    else:
      return ""

#--------------------------------------------------------------------------#

""" Routes of Pages """

# Home
@bp_site.route("/")
def Home():
  return redirect(url_for('ahmedfrg.home'))

# Dashboard
@bp_site.route("/home")
def home():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    number_of_books = 6
    myCursor.execute(f"SELECT `id`,`name`,LEFT(`description`,100), `img`, `link`, `created_at` FROM book Order by created_at DESC LIMIT {number_of_books}")
    books = myCursor.fetchall()
    
    number_of_articles = 3
    myCursor.execute(f"SELECT `id`,`name`,LEFT(`text`,250), `created_at` FROM article Order by created_at DESC LIMIT {number_of_articles}")
    articles = myCursor.fetchall()

    return render_template("index.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    books=books,
                    articles=articles,
                    title="الصفحة الرئيسية")

# Books Page
@bp_site.route("/books")
def books():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    myCursor.execute(f"SELECT `id`, `name`, LEFT(`description`,100), `img`, `link`, `created_at` FROM book Order by created_at DESC")
    books = myCursor.fetchall()

    return render_template("books.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    books=books,
                    title="كتبي")

# Book Page
@bp_site.route("/book")
def book():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    book_id = argsGet("id")
    myCursor.execute(f"SELECT * FROM book WHERE id={book_id}")
    bookData =myCursor.fetchone()
    
    paras = bookData[2].split('\n')
    return render_template("book.html",
                    title=bookData[1],
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    bookData=bookData,
                    paras=paras)


# Books Page
@bp_site.route("/articles")
def articles():
    _, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    myCursor.execute(f"SELECT `id`,`name`,LEFT(`text`,250), `created_at` FROM article Order by created_at DESC")
    articles = myCursor.fetchall()

    return render_template("articles.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    articles=articles,
                    title="مقالاتي")

# Article Page
@bp_site.route("/article")
def article():
    _, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    article_id = argsGet("id")
    myCursor.execute(f"SELECT * FROM article WHERE id={article_id}")
    articleData =myCursor.fetchone()
    
    title = articleData[1]
    articleText = articleData[2]

    articleText = articleText.split('\n')

    return render_template("article.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    title=title,
                    articleText=articleText)

#--------------------------------------------------------------------------#

#-----------Error Handler-----------#

# Error Handle exception
@bp_site.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

# Page 500
@bp_site.errorhandler(500)
def internal_server_error(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return render_template("500.html", e=e), 500

# Page 404
@bp_site.errorhandler(405)
@bp_site.errorhandler(404)
def page_not_found(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return render_template("404.html", e=e), 404

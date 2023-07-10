import os
from shutil import rmtree
from werkzeug.utils import secure_filename

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, json
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import mysql_connector, retrieve_tables
from werkzeug.exceptions import HTTPException

import pandas as pd
import math

from flaskr.log import site_logger
from flaskr.config import Config


#--------------------------------------------------------------------------#

bp_site = Blueprint('ahmedfrg', __name__)
UPLOAD_FOLDER = Config.UPLOAD_FOLDER

#--------------------------------------------------------------------------#

"""Functions"""
# Get Request
def argsGet(argName):
    if request.args.get(argName):
        field = request.args.get(argName)
    else:
        field = ""  
    return field
          
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


# Articles Page
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
    

# Videos Page
@bp_site.route("/videos")
def videos():
    _, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    myCursor.execute(f"SELECT `id`,`name`,LEFT(`text`,250), `created_at` FROM article Order by created_at DESC")
    videos = myCursor.fetchall()

    return render_template("videos.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    video=videos,
                    title="فيديوهات")

# Video Page
@bp_site.route("/video")
def video():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    video_id = argsGet("id")
    myCursor.execute(f"SELECT * FROM book WHERE id={video_id}")
    video =myCursor.fetchone()
    
    return render_template("book.html",
                    title=video[1],
                    name=settings[0][1],
                    video=video)


# Presentations Page
@bp_site.route("/presentations")
def presentations():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    myCursor.execute(f"SELECT `id`, `name`, LEFT(`description`,100), `img`, `link`, `created_at` FROM book Order by created_at DESC")
    presentations = myCursor.fetchall()

    return render_template("presentations.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    presentations=presentations,
                    title="العروض التقديمية")

# Book Page
@bp_site.route("/presentation")
def presentation():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    book_id = argsGet("id")
    myCursor.execute(f"SELECT * FROM book WHERE id={book_id}")
    presentation =myCursor.fetchone()
    
    paras = presentation[2].split('\n')
    return render_template("presentation.html",
                    title=presentation[1],
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    presentation=presentation,
                    paras=paras)

#--------------------------------------------------------------------------#

import os
from shutil import rmtree
from werkzeug.utils import secure_filename

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, json
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import mysql_connector, retrieve_tables, getWord
from werkzeug.exceptions import HTTPException

import numpy as np
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

COL_NAMES_1 = "`id`, `name`, LEFT(`description`,100), `img`, `link`, `category`, `created_at`"
COL_NAMES_2 = "`id`, `name`, `description`, `img`, `link`, `category`, `created_at`"
COL_NAMES_3 = "`id`, `name`, LEFT(`text`,250), `category`, `created_at`"
COL_NAMES_4 = "`id`, `name`, `text`, `category`, `created_at`"

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

    word = getWord(myCursor)
    number_of_books = 4
    myCursor.execute(f"SELECT {COL_NAMES_1} FROM book Order by created_at DESC LIMIT {number_of_books}")
    books = myCursor.fetchall()
    
    number_of_presentations = 4
    myCursor.execute(f"SELECT {COL_NAMES_1} FROM presentation Order by created_at DESC LIMIT {number_of_presentations}")
    presentations = myCursor.fetchall()

    number_of_videos = 4
    myCursor.execute(f"SELECT {COL_NAMES_1} FROM video Order by created_at DESC LIMIT {number_of_videos}")
    videos = myCursor.fetchall()

    number_of_articles = 3
    myCursor.execute(f"SELECT {COL_NAMES_3} FROM article Order by created_at DESC LIMIT {number_of_articles}")
    articles = myCursor.fetchall()

    return render_template("index.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    word=word,
                    books=books,
                    presentations=presentations,
                    videos=videos,
                    articles=articles,
                    title="الصفحة الرئيسية")

# Books Page
@bp_site.route("/books")
def books():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "settings", "book")
    settings = db_tables['settings']
    books = db_tables['book']

    word = getWord(myCursor)
    return render_template("books.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    word=word,
                    books=books,
                    title="كتبي")

# Book Page
@bp_site.route("/book")
def book():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    book_id = argsGet("id")
    myCursor.execute(f"SELECT {COL_NAMES_2} FROM book WHERE id={book_id}")
    bookData = myCursor.fetchone()
    
    word = getWord(myCursor)
    
    paras = bookData[2].split('\n')
    return render_template("book.html",
                    title=bookData[1],
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    word=word,
                    bookData=bookData,
                    paras=paras)

# Articles Page
@bp_site.route("/articles")
def articles():
    _, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "settings", "article")
    
    settings = db_tables['settings']
    articles = db_tables['article']
    
    word = getWord(myCursor)

    return render_template("articles.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    articles=articles,
                    word=word,
                    title="مقالاتي")

# Article Page
@bp_site.route("/article")
def article():
    _, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    article_id = argsGet("id")
    myCursor.execute(f"SELECT {COL_NAMES_4} FROM article WHERE id={article_id}")
    articleData = myCursor.fetchone()
    
    title = articleData[1]
    articleText = articleData[2]
    articleText = articleText.split('\n')

    word = getWord(myCursor)
    
    return render_template("article.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    title=title,
                    word=word,
                    articleText=articleText)
    

# Videos Page
@bp_site.route("/videos")
def videos():
    _, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "settings", "video")
    settings = db_tables['settings']
    videos = db_tables['video']

    word = getWord(myCursor)
    return render_template("videos.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    videos=videos,
                    word=word,
                    title="فيديوهات")

# Video Page
@bp_site.route("/video")
def video():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    video_id = argsGet("id")
    myCursor.execute(f"SELECT {COL_NAMES_2} FROM video WHERE id={video_id}")
    video = myCursor.fetchone()
    
    word = getWord(myCursor)
    
    return render_template("video.html",
                    title=video[1],
                    name=settings[0][1],
                    video=video,
                    word=word)

# Presentations Page
@bp_site.route("/presentations")
def presentations():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "settings", "presentation")
    settings = db_tables['settings']
    presentations = db_tables['presentation']

    word = getWord(myCursor)
    
    return render_template("presentations.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    presentations=presentations,
                    word=word,
                    title="العروض التقديمية")

# Presentation Page
@bp_site.route("/presentation")
def presentation():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    presentation_id = argsGet("id")
    myCursor.execute(f"SELECT {COL_NAMES_2} FROM presentation WHERE id={presentation_id}")
    presentation =myCursor.fetchone()
    
    word = getWord(myCursor)
    
    paras = presentation[2].split('\n')
    return render_template("presentation.html",
                    title=presentation[1],
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    presentation=presentation,
                    word=word,
                    paras=paras)

#--------------------------------------------------------------------------#

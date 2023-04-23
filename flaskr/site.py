import os
from shutil import rmtree
from werkzeug.utils import secure_filename

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, json
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import mysql_connector, retrieve_tables
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import HTTPException

import pandas as pd
import math

from flaskr.log import site_logger
from flaskr.config import Config


#--------------------------------------------------------------------------#

bp = Blueprint('ahmedfrg', __name__)
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
@bp.route("/")
def Home():
  return redirect(url_for('ahmedfrg.home'))

# Dashboard
@bp.route("/home")
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
@bp.route("/books")
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
@bp.route("/book")
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
@bp.route("/articles")
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
@bp.route("/article")
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

#--------------------------------------------------------------------------#

# Admin Page
@app.route("/admin", methods=['GET', 'POST'])
def admin():
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    if request.method == 'POST':
      name  = request.form['name']
      title  = request.form['title']
      username  = request.form['username']
      password  = request.form['password']

      myCursor.execute("""
      UPDATE settings
      SET title=%s, cover_text=%s, admin_username=%s, admin_password=%s
      WHERE id=1;
      """,(name,title,username,password))
      mydb.commit()

    return render_template("admin/index.html",
                  name=settings[0][1],
                  title="لوحة التحكم",
                  settings=settings[0])

# List of Books Page
@app.route("/admin/books")
def adminBooks():
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    myCursor.execute("SELECT `id`, `name`, LEFT(`description`,100), `img`, `link`, `created_at` FROM book Order by created_at DESC")
    books = myCursor.fetchall()

    return render_template("admin/books.html",
                  name=settings[0][1],
                  title="قائمة الكتب",
                  settings=settings[0],
                  books=books)

# Add Book Page
@app.route("/admin/addBook", methods=['GET', 'POST'])
def addBook():     
      db_tables = database.retrieve_tables(myCursor, "*")
      settings = db_tables['settings']
      status = -1
      
      if request.method == 'POST':
        name  = request.form['name']
        description  = request.form['description']
        image  = request.files['image']
        image_path = saveFile(image, name, "image") 
        link  = request.files['link']
        link_path = saveFile(link, name, "link") 
        createdAt = pd.to_datetime("today")
        createdAt = f"{createdAt.year}-{createdAt.month}-{createdAt.day}"
      
        myCursor.execute("""INSERT INTO Book(name, description, img, link, created_at) VALUES (%s,%s,%s,%s,%s)""",
                                            (name, description, image_path, link_path, createdAt))
        status = 1
        mydb.commit() # Work Is DONE

      return render_template("admin/addbook.html",
                    name=settings[0][1],
                    title="إضافة كتاب",
                    settings=settings[0],
                    status=status)

# Remove Book Page
@app.route("/admin/RemoveBook", methods=['GET', 'POST'])
def removeBook():
    id = argsGet("id")
    myCursor.execute("""DELETE FROM Book WHERE id=%s""",(id,))
    mydb.commit() # Work Is DONE

    return redirect(url_for('adminBooks'))

# Edit Book Page
@app.route("/admin/EditBook", methods=['GET', 'POST'])
def editBook():
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    id = argsGet("id")
    myCursor.execute(f"""SELECT * FROM Book WHERE id={id}""")
    book = myCursor.fetchone()

    if request.method == 'POST':
        name  = request.form['name']
        description  = request.form['description']
        image  = request.files['image']
        image_path = saveFile(image, name, "image")
        link  = request.files['link']
        link_path = saveFile(link, name, "link") 
        createdAt = pd.to_datetime("today")
        createdAt = f"{createdAt.year}-{createdAt.month}-{createdAt.day}"

        myCursor.execute(f"""UPDATE book SET name='{name}', description='{description}', img='{image_path}', link='{link_path}',created_at='{createdAt}' WHERE id={id}""")
        mydb.commit()

    return render_template("admin/editbook.html",
                name=settings[0][1],
                title="تعديل كتاب",
                settings=settings[0],
                book=book)

# List of Articles Page
@app.route("/admin/articles")
def adminArticles():
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    myCursor.execute("SELECT `id`, `name`, LEFT(`text`,100), `created_at` FROM article Order by created_at DESC")
    articles = myCursor.fetchall()

    return render_template("admin/articles.html",
                name=settings[0][1],
                title="قائمة المقالات",
                settings=settings[0],
                articles=articles)

# Add Book Page
@app.route("/admin/addArticle", methods=['GET', 'POST'])
def addArticle():     
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
    status = -1
    
    if request.method == 'POST':
      name  = request.form['name']
      text  = request.form['text']
      createdAt = pd.to_datetime("today")
      createdAt = f"{createdAt.year}-{createdAt.month}-{createdAt.day}"
    
      myCursor.execute("""INSERT INTO Article(name, text, created_at) VALUES (%s,%s,%s)""",
                                          (name, text, createdAt))
      status = 1
      mydb.commit() # Work Is DONE

    return render_template("admin/addArticle.html",
                  name=settings[0][1],
                  title="إضافة مقال",
                  settings=settings[0],
                  status=status)

# Remove Book Page
@app.route("/admin/RemoveArticle", methods=['GET', 'POST'])
def removeArticle():
    id = argsGet("id")
    myCursor.execute("""DELETE FROM Article WHERE id=%s""",(id,))
    mydb.commit() # Work Is DONE

    return redirect(url_for('adminArticles'))

# Edit Book Page
@app.route("/admin/EditArticle", methods=['GET', 'POST'])
def editArticle():
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    id = argsGet("id")
    myCursor.execute(f"""SELECT * FROM Article WHERE id={id}""")
    article = myCursor.fetchone()

    if request.method == 'POST':
      name  = request.form['name']
      text  = request.form['text']
      createdAt = pd.to_datetime("today")
      createdAt = f"{createdAt.year}-{createdAt.month}-{createdAt.day}"

      myCursor.execute(f"""UPDATE article SET name='{name}', text='{text}', created_at='{createdAt}' WHERE id={id}""")
      mydb.commit()

    return render_template("admin/editArticle.html",
                  name=settings[0][1],
                  title="تعديل كتاب",
                  settings=settings[0],
                  article=article)

#-----------Error Handler-----------#

# Error Handle exception
@bp.errorhandler(HTTPException)
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
@bp.errorhandler(500)
def internal_server_error(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return render_template("500.html", e=e), 500

# Page 404
@bp.errorhandler(405)
@bp.errorhandler(404)
def page_not_found(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return render_template("404.html", e=e), 404


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

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')
UPLOAD_FOLDER = Config.UPLOAD_FOLDER

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
def saveFile(list, id, fileName):

    if list and allowed_file(list.filename):
      filename = secure_filename(fileName + "." + list.filename.rsplit('.', 1)[1])
      path = UPLOAD_FOLDER + id + "/" 
      os.makedirs(path, exist_ok=True)
      list.save(os.path.join(path, filename))
      return path[7:] + filename
    else:
      return ""

#--------------------------------------------------------------------------#


# Home
@bp_admin.route("/")
def home():
  return redirect(url_for('admin.admin'))

# Admin | Admin Page
@bp_admin.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
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

# Admin | List of Books Page
@bp_admin.route("/books")
@login_required
def adminBooks():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    myCursor.execute("SELECT `id`, `name`, LEFT(`description`,100), `img`, `link`, `created_at` FROM book Order by created_at DESC")
    books = myCursor.fetchall()

    return render_template("admin/books.html",
                  name=settings[0][1],
                  title="قائمة الكتب",
                  settings=settings[0],
                  books=books)

# Admin | Add Book Page
@bp_admin.route("/addBook", methods=['GET', 'POST'])
@login_required
def addBook():     
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    status = False
    
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
        status = True
        mydb.commit() # Work Is DONE

    return render_template("admin/addbook.html",
                    name=settings[0][1],
                    title="إضافة كتاب",
                    settings=settings[0],
                    status=status)

# Admin | Remove Book Page
@bp_admin.route("/RemoveBook", methods=['GET', 'POST'])
@login_required
def removeBook():
    mydb, myCursor = mysql_connector()

    id = argsGet("id")
    myCursor.execute("""SELECT `name` FROM Book WHERE id=%s""",(id,))
    book_name = myCursor.fetchone()
    rmtree(UPLOAD_FOLDER + book_name[0] + "/")
    
    myCursor.execute("""DELETE FROM Book WHERE id=%s""",(id,))
    mydb.commit() # Work Is DONE

    return redirect(url_for('admin.adminBooks'))

# Admin | Edit Book Page
@bp_admin.route("/EditBook", methods=['GET', 'POST'])
@login_required
def editBook():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
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

# Admin | List of Articles Page
@bp_admin.route("/articles")
@login_required
def adminArticles():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    myCursor.execute("SELECT `id`, `name`, LEFT(`text`,100), `created_at` FROM article Order by created_at DESC")
    articles = myCursor.fetchall()

    return render_template("admin/articles.html",
                name=settings[0][1],
                title="قائمة المقالات",
                settings=settings[0],
                articles=articles)

# Admin | Add Book Page
@bp_admin.route("/addArticle", methods=['GET', 'POST'])
@login_required
def addArticle():     
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
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

    return render_template("admin/addarticle.html",
                  name=settings[0][1],
                  title="إضافة مقال",
                  settings=settings[0],
                  status=status)

# Admin | Remove Book Page
@bp_admin.route("/RemoveArticle", methods=['GET', 'POST'])
@login_required
def removeArticle():
    mydb, myCursor = mysql_connector()

    id = argsGet("id")
    myCursor.execute("""DELETE FROM Article WHERE id=%s""",(id,))
    mydb.commit() # Work Is DONE

    return redirect(url_for('Admin.adminArticles'))

# Admin | Edit Book Page
@bp_admin.route("/EditArticle", methods=['GET', 'POST'])
@login_required
def editArticle():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
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


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

from flaskr.messages import *
from flaskr.log import site_logger
from flaskr.config import Config

#--------------------------------------------------------------------------#
"""Blueprint"""
bp_admin = Blueprint('admin', __name__, url_prefix='/admin')
UPLOAD_FOLDER = Config.UPLOAD_FOLDER

"""Constants"""
ALLOWED_EXTENSIONS_DOC = set(['pdf'])
ALLOWED_EXTENSIONS_IMG = set(['png', 'jpg', 'jpeg'])
ALLOWED_EXTENSIONS_PP = set(['pptx','ppt'])
ALLOWED_EXTENSIONS_VID = set(['mp4','webm','mkv','flv'])

# ======================================================================== #

DOCUMENT   = "doc"
VIDEO      = "vid"
POWERPOINT = "pp"
IMAGE      = "img"

PAGES = ["book", "presentation", "video"]
SINGULAR_TITLES = ["الكتاب", "العرض التقديمي", "مقطع الفيديو"]
PLURAL_TITLES = ["قائمة الكتب", "قائمة العروض التقديمية", "قائمة مقاطع الفيديو"]
FILE_TYPES = [DOCUMENT, POWERPOINT, VIDEO, IMAGE]

# ======================================================================== #

"""Functions"""
# Get Request from arguments
def argsGet(argName):
    if request.args.get(argName):
        field = request.args.get(argName)
    else:
        field = ""  
    return field

# Get request from form
def get_request_from_form(input):
    text = request.form[input]
    if text == "": 
        raise Exception("بيانات غير مكتملة")

    return text

# Get request from form
def get_request_from_file(input):
    file = request.files[input]
    if not file: 
        raise Exception("بيانات غير مكتملة")

    return file

def set_title(input, singular):
    for i, page in zip(range(len(PAGES)),PAGES):
        if input == page:
            if singular:
                title = SINGULAR_TITLES[i]
            else:
                title = PLURAL_TITLES[i]
            
    return title


# Check Extension of file
def allowed_file(filename, type):
    if type == DOCUMENT:
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_DOC
    elif type == IMAGE:
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_IMG
    elif type == POWERPOINT:
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_PP
    elif type == VIDEO:
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_VID

# Save file
def saveFile(list, id, fileExt=DOCUMENT):

    if list and allowed_file(list.filename, fileExt):
        filename = secure_filename(fileExt + "." + list.filename.rsplit('.', 1)[1])
        if fileExt == DOCUMENT or fileExt == IMAGE:
            path = f"{UPLOAD_FOLDER}/Books/{id}/"
        elif fileExt == POWERPOINT:
            path = f"{UPLOAD_FOLDER}/Presentations/{id}/"
        elif fileExt == VIDEO:
            path = f"{UPLOAD_FOLDER}/Videos/{id}/"
        
        path = UPLOAD_FOLDER + id + "/" 
        os.makedirs(path, exist_ok=True)
        list.save(os.path.join(path, filename))
        return path[7:] + filename
    else:
      return ""

# ======================================================================== #

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
        try:
            name  = request.form['name']
            title  = request.form['title']
            username  = get_request_from_form('username')
            myCursor.execute("""
                UPDATE settings
                SET title=%s, cover_text=%s, admin_username=%s
                WHERE id=1;
            """,(name,title,username))
            mydb.commit()
            
            flash(settings_updated_success, "success")

        except Exception as err:
            flash(settings_updated_failed, "danger")
            flash(err, "reasons")

    return render_template("admin/index.html",
                  name=settings[0][1],
                  title="لوحة التحكم",
                  settings=settings[0])

@bp_admin.route("/changePassword", methods=['GET', 'POST'])
@login_required
def changePassword():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
    myCursor.execute('SELECT admin_password FROM settings WHERE id=1')
    admin_password = myCursor.fetchone()[0]
    
    show_old_password = True
    if admin_password == "":
        show_old_password = False

    if request.method == 'POST':
        try:
            myCursor.execute('SELECT admin_password FROM settings WHERE id=1')
            admin_password = myCursor.fetchone()[0]
            if show_old_password:
                old_password = get_request_from_form('old_password')
            else:
                old_password = request.form['old_password']
                
            if admin_password == "" or check_password_hash(admin_password, old_password):
                new_password  = get_request_from_form('new_password')
                myCursor.execute("""
                    UPDATE settings
                    SET admin_password=%s
                    WHERE id=1;
                """,(generate_password_hash(new_password),))
                
                mydb.commit()
                
                flash(password_updated_success, "success")
            else:
                raise Exception("كلمة المرور غير صحيحة")

        except Exception as err:
            flash(password_updated_failed, "danger")
            flash(err, "reasons")

    return render_template("admin/change-password.html",
                  name=settings[0][1],
                  title="تغيير كلمة المرور",
                  settings=settings[0],
                  show_old_password=show_old_password)

#--------------------------------------------------------------------------#

# Admin | List of item Page
@bp_admin.route("/listOfItems")
@login_required
def listOfItems():
    itemName = argsGet("name")
    title_main = set_title(itemName, 0)
    title = set_title(itemName, 1)
    
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    myCursor.execute(f"SELECT `id`, `name`, LEFT(`description`,100), `img`, `link`, category, `created_at` FROM {itemName} Order by created_at DESC")
    items = myCursor.fetchall()

    return render_template("admin/items.html",
                  name=settings[0][1],
                  itemName=itemName,
                  title=title,
                  settings=settings[0],
                  items=items)

# Admin | Add item Page
@bp_admin.route("/addItem", methods=['GET', 'POST'])
@login_required
def addItem():
    itemName = argsGet("name")
    title = set_title(itemName, 1)

    mydb, myCursor = mysql_connector() 
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
   
    if request.method == 'POST':
        try:
            name  = get_request_from_form('name')
            description  = get_request_from_form('description')
            image  = get_request_from_file('image')
            image_path = saveFile(image, name, IMAGE)
            link  = get_request_from_file('link')
            print(FILE_TYPES[PAGES.index(itemName)])
            link_path = saveFile(link, name, FILE_TYPES[PAGES.index(itemName)])
            category = get_request_from_form('category')
            createdAt = pd.to_datetime("today")
            createdAt = f"{createdAt.year}-{createdAt.month}-{createdAt.day}"        
            myCursor.execute(f"""INSERT INTO {itemName}(name, description, img, link, category, created_at) VALUES (%s,%s,%s,%s,%s,%s)""",
                                                (name, description, image_path, link_path, category, createdAt))

            mydb.commit() # Work Is DONE
            flash(item_added_success, "success")
            
        except Exception as err:
            print(err)
            flash(item_added_failed, "danger")
            flash(err, "reasons")

    return render_template("admin/add-item.html",
                    name=settings[0][1],
                    title=f"{title}",
                    settings=settings[0])

# Admin | Remove Item Page
@bp_admin.route("/RemoveItem", methods=['GET', 'POST'])
@login_required
def removeItem():
    mydb, myCursor = mysql_connector()

    id = argsGet("id")
    itemName = argsGet("name")

    try:
        myCursor.execute(f"""SELECT `name` FROM {itemName} WHERE id=%s""",(id,))
        item_name = myCursor.fetchone()
        rmtree(UPLOAD_FOLDER + item_name[0] + "/")
        flash(item_deleted_success, "success")
    except Exception as err:
        flash(item_deleted_failed, "danger")
        flash(err, "reasons")
    
    myCursor.execute(f"DELETE FROM {itemName} WHERE id={id}")
    mydb.commit() # Work Is DONE

    return redirect(f"listOfItems?name={itemName}")

# Admin | Edit Items Page
@bp_admin.route("/EditItem", methods=['GET', 'POST'])
@login_required
def editItem():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    itemName = argsGet("name")
    title = set_title(itemName, 1)
    
    id = argsGet("id")
    
    myCursor.execute(f"""SELECT name,description,category FROM {itemName} WHERE id={id}""")
    item = myCursor.fetchone()

    if request.method == 'POST':
        try:
            name  = get_request_from_form('name')
            description  = get_request_from_form('category')
            category  = get_request_from_form('description')

            myCursor.execute(f"""UPDATE {itemName} SET name='{name}', description='{description}, category='{category}' WHERE id={id}""")
            mydb.commit()
            
            flash(item_edited_success, "success")
            
        except Exception as err:
            flash(item_edited_failed, "danger")
            flash(err, "reasons")

    return render_template("admin/edit-item.html",
                name=settings[0][1],
                title=f"{title}",
                settings=settings[0],
                item=item)

# Admin | Edit Items Image
@bp_admin.route("/EditItemImage", methods=['GET', 'POST'])
@login_required
def editItemImage():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    id = argsGet("id")
    itemName = argsGet("name") 
    title = set_title(itemName, 1)
    
    myCursor.execute(f"""SELECT * FROM {itemName} WHERE id={id}""")
    item = myCursor.fetchone()

    if request.method == 'POST':
        try:           
            name = item[1]
            image  = get_request_from_file('image')
            image_path = saveFile(image, name, IMAGE)
            
            myCursor.execute(f"""UPDATE {itemName} SET img='{image_path}' WHERE id={id}""")
            mydb.commit()
            
            flash(item_edited_success, "success")
            
        except Exception as err:
            flash(item_edited_failed, "danger")
            flash(err, "reasons")
            
    print("x")

    return render_template("admin/edit-item-image.html",
                name=settings[0][1],
                title=f"{title}",
                settings=settings[0],
                item=item)

# Admin | Edit Item Page
@bp_admin.route("/EditItemLink", methods=['GET', 'POST'])
@login_required
def editItemLink():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    id = argsGet("id")
    itemName = argsGet("name")
    title = set_title(itemName,1)
        
    myCursor.execute(f"""SELECT * FROM {itemName} WHERE id={id}""")
    item = myCursor.fetchone()

    if request.method == 'POST':
        try:
            name = item[1]
            link  = get_request_from_file('link')
            link_path = saveFile(link, name, FILE_TYPES[PAGES.index(itemName)]) 
            
            myCursor.execute(f"""UPDATE {itemName} SET link='{link_path}' WHERE id={id}""")
            mydb.commit()
            
            flash(item_edited_success, "success")
            
        except Exception as err:
            flash(item_edited_failed, "danger")
            flash(err, "reasons")

    return render_template("admin/edit-item-link.html",
                name=settings[0][1],
                title=f"{title}",
                settings=settings[0],
                item=item)

# ======================================================================== #

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

# Admin | Add Article Page
@bp_admin.route("/addArticle", methods=['GET', 'POST'])
@login_required
def addArticle():     
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
       
    if request.method == 'POST':
        try:
            name  = get_request_from_form('name')
            text  = get_request_from_form('text')
            createdAt = pd.to_datetime("today")
            createdAt = f"{createdAt.year}-{createdAt.month}-{createdAt.day}"
            
            myCursor.execute("""INSERT INTO article(name, text, created_at) VALUES (%s,%s,%s)""",
                                                (name, text, createdAt))
            mydb.commit() # Work Is DONE

            flash(article_added_success, "success")
            
        except Exception as err:
            flash(article_added_failed, "danger")
            flash(err, "reasons")

    return render_template("admin/add-article.html",
                  name=settings[0][1],
                  title="إضافة مقال",
                  settings=settings[0])

# Admin | Remove Book Page
@bp_admin.route("/RemoveArticle", methods=['GET', 'POST'])
@login_required
def removeArticle():
    mydb, myCursor = mysql_connector()

    id = argsGet("id")
    myCursor.execute("""DELETE FROM article WHERE id=%s""",(id,))
    mydb.commit() # Work Is DONE

    return redirect(url_for('admin.adminArticles'))

# Admin | Edit Book Page
@bp_admin.route("/EditArticle", methods=['GET', 'POST'])
@login_required
def editArticle():
    mydb, myCursor = mysql_connector()
    
    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    id = argsGet("id")
    myCursor.execute(f"""SELECT * FROM article WHERE id={id}""")
    article = myCursor.fetchone()

    if request.method == 'POST':
        try:
            name  = get_request_from_form('name')
            text  = get_request_from_form('text')
            createdAt = pd.to_datetime("today")
            createdAt = f"{createdAt.year}-{createdAt.month}-{createdAt.day}"

            myCursor.execute(f"""UPDATE article SET name='{name}', text='{text}', created_at='{createdAt}' WHERE id={id}""")
            mydb.commit()

            flash(article_edited_success, "success")
        
        except Exception as err:
            flash(article_edited_failed, "danger")
            flash(err, "reasons")

    return render_template("admin/edit-article.html",
                  name=settings[0][1],
                  title="تعديل كتاب",
                  settings=settings[0],
                  article=article)

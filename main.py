# Imports
from flask import Flask, render_template, request, redirect, url_for, session
import database
from werkzeug.utils import secure_filename
import os
import pandas as pd

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

# Connecting with Database
mydb, myCursor = database.mysql_connector()

"""Retrieve Database Tables"""
db_tables = database.retrieve_tables(myCursor, "*")

#--------------------------------------------------------------------------#

"""Our app"""
app = Flask(__name__)
app.secret_key = 'hlzgzxpzlllkgzrn' # My Secret_Key
UPLOAD_FOLDER = "static/upload/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS_DOC = set(['pdf', 'doc', 'xlsx', 'png', 'jpg', 'jpeg'])

#--------------------------------------------------------------------------#

""" Routes of Pages """
# Home Page
@app.route("/")
def home():
    db_tables = database.retrieve_tables(myCursor, "*")
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
@app.route("/books")
def books():
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    myCursor.execute(f"SELECT `id`, `name`, LEFT(`description`,100), `img`, `link`, `created_at` FROM book Order by created_at DESC")
    books = myCursor.fetchall()

    return render_template("books.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    books=books,
                    title="كتبي")

# Book Page
@app.route("/book")
def book():
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    id = argsGet("id")
    myCursor.execute(f"SELECT * FROM book WHERE id={id}")
    bookData =myCursor.fetchone()
    
    paras = bookData[2].split('\n')
    return render_template("book.html",
                    title=bookData[1],
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    bookData=bookData,
                    paras=paras)


# Books Page
@app.route("/articles")
def articles():
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    myCursor.execute(f"SELECT `id`,`name`,LEFT(`text`,250), `created_at` FROM article Order by created_at DESC")
    articles = myCursor.fetchall()

    return render_template("articles.html",
                    name=settings[0][1],
                    coverTitle=settings[0][2],
                    articles=articles,
                    title="مقالاتي")

# Article Page
@app.route("/article")
def article():
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    id = argsGet("id")
    myCursor.execute(f"SELECT * FROM article WHERE id={id}")
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

# Admin Page
@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if 'loggedin' in session and session['loggedin'] == True:
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
    else:
      return redirect(url_for('login'))

# List of Books Page
@app.route("/admin/books")
def adminBooks():
    if 'loggedin' in session and session['loggedin'] == True:
      db_tables = database.retrieve_tables(myCursor, "*")
      settings = db_tables['settings']

      myCursor.execute("SELECT `id`, `name`, LEFT(`description`,100), `img`, `link`, `created_at` FROM book Order by created_at DESC")
      books = myCursor.fetchall()

      return render_template("admin/books.html",
                    name=settings[0][1],
                    title="قائمة الكتب",
                    settings=settings[0],
                    books=books)
    else:
      return redirect(url_for('login'))

# Add Book Page
@app.route("/admin/addBook", methods=['GET', 'POST'])
def addBook():
    if 'loggedin' in session and session['loggedin'] == True:
      
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
    else:
      return redirect(url_for('login'))

# Remove Book Page
@app.route("/admin/RemoveBook", methods=['GET', 'POST'])
def removeBook():
    if 'loggedin' in session and session['loggedin'] == True:
      id = argsGet("id")
      myCursor.execute("""DELETE FROM Book WHERE id=%s""",(id,))
      mydb.commit() # Work Is DONE

      return redirect(url_for('adminBooks'))
    else:
      return redirect(url_for('login'))

# Edit Book Page
@app.route("/admin/EditBook", methods=['GET', 'POST'])
def editBook():
    if 'loggedin' in session and session['loggedin'] == True:
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
    else:
      return redirect(url_for('login'))

#-----#

# List of Articles Page
@app.route("/admin/articles")
def adminArticles():
    if 'loggedin' in session and session['loggedin'] == True:
      db_tables = database.retrieve_tables(myCursor, "*")
      settings = db_tables['settings']

      myCursor.execute("SELECT `id`, `name`, LEFT(`text`,100), `created_at` FROM article Order by created_at DESC")
      articles = myCursor.fetchall()

      return render_template("admin/articles.html",
                    name=settings[0][1],
                    title="قائمة المقالات",
                    settings=settings[0],
                    articles=articles)
    else:
      return redirect(url_for('login'))

# Add Book Page
@app.route("/admin/addArticle", methods=['GET', 'POST'])
def addArticle():
    if 'loggedin' in session and session['loggedin'] == True:
      
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
    else:
      return redirect(url_for('login'))

# Remove Book Page
@app.route("/admin/RemoveArticle", methods=['GET', 'POST'])
def removeArticle():
    if 'loggedin' in session and session['loggedin'] == True:
      id = argsGet("id")
      myCursor.execute("""DELETE FROM Article WHERE id=%s""",(id,))
      mydb.commit() # Work Is DONE

      return redirect(url_for('adminArticles'))
    else:
      return redirect(url_for('login'))

# Edit Book Page
@app.route("/admin/EditArticle", methods=['GET', 'POST'])
def editArticle():
    if 'loggedin' in session and session['loggedin'] == True:
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
    else:
      return redirect(url_for('login'))

# Login in Admin Page
@app.route("/login", methods=['GET', 'POST'])
def login():
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    if 'loggedin' in session and session['loggedin'] == True:
      return redirect(url_for('home'))
    else:
      status = True
      if request.method == 'POST':
        username  = request.form['username']
        password  = request.form['password']

        # Check if account exists using MySQL
        myCursor.execute('SELECT * FROM settings WHERE `admin_username`=%s AND `admin_password`=%s', (username, password,))

        # Fetch one record and return result
        account = myCursor.fetchone()

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            status = True
            # Redirect to home page
            return redirect(url_for('admin'))
        else:
            # Account doesnt exist or username/password incorrect
            status = False

    return render_template("admin/login.html",
                    name=settings[0][1],
                    title="تسجيل الدخول",
                    status=status)

# Logout
@app.route("/admin/logout")
def logout():
  # Remove session data, this will log the user out
  session.pop('loggedin', None)
  session.pop('id', None)
  session.pop('username', None)
  # Redirect to login page
  return redirect(url_for('login'))

#--------------------------------------------------------------------------#

# Page 404
@app.errorhandler(404)
def page_not_found(e):
    db_tables = database.retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
  
    # note that we set the 404 status explicitly
    return render_template('404.html',name=settings[0][1],title="ERROR"), 404

# Run app
if __name__ == "__main__":  
  app.run(debug=True,port=9000)


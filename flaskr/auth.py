import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import mysql_connector, retrieve_tables
from flaskr.log import site_logger

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Login in Admin Page
@bp.route("/login", methods=['GET', 'POST'])
def login():
    _ , myCursor = mysql_connector()

    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']

    user = None
    if request.method == 'POST':
        username  = request.form['username']
        password  = request.form['password']

        # Check if account exists using MySQL
        myCursor.execute('SELECT * FROM settings WHERE `admin_username`=%s AND `admin_password`=%s', (username, password,))

        # Fetch one record and return result
        user = myCursor.fetchone()

    # If account exists in accounts table in out database
    if user:
        # Create session data, we can access this data in other routes
        session['loggedin'] = True
        session['id'] = user[0]
        session['username'] = user[1]
        
        # Redirect to home page
        return redirect(url_for('admin.home'))
    else:
        # Account doesn't exist or username/password incorrect
        flash("We didn't recognize the username / password you entered.", "error")

    return render_template("admin/login.html",
                    name=settings[0][1],
                    title="تسجيل الدخول")

# Load the logged in user details
@bp.before_app_request
def load_logged_in_user():
    admin_id = session.get('id')

    if admin_id is None:
        g.user = None
    else:
        _,myCursor = mysql_connector()
        myCursor.execute('SELECT * FROM settings WHERE id = %s', (admin_id,))
        g.user = myCursor.fetchone()

# Logout
@bp.route("/logout")
def logout():
  # Remove session data, this will log the user out
  username = session['username']
  session.clear()
  site_logger.info(f'admin {username} logged out succefully.')

  # Redirect to login page
  return redirect(url_for('auth.login'))

# Auth
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

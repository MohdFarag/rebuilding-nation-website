import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import mysql_connector, retrieve_tables
from flaskr.log import site_logger

from flaskr.messages import username_wrong, password_wrong

bp_auth = Blueprint('auth', __name__, url_prefix='/auth')

# Login in Admin Page
@bp_auth.route("/login", methods=['GET', 'POST'])
def login():
    _ , myCursor = mysql_connector()

    db_tables = retrieve_tables(myCursor, "*")
    settings = db_tables['settings']
   
    if request.method == 'POST':
        username  = request.form['username']
        password  = request.form['password']

        # Check if account exists using MySQL
        myCursor.execute('SELECT * FROM settings WHERE `admin_username`=%s', (username,))

        # Fetch one record and return result
        user = myCursor.fetchone()

        # If account exists in accounts table in out database
        if user:
            if user[4] == "":
                session['loggedin'] = True
                session['id'] = user[0]
                session['username'] = user[1]
                
                return redirect(url_for('admin.home'))
            elif check_password_hash(user[4], password):
                # Create session data, we can access this data in other routes
                session.clear()
                session['loggedin'] = True
                session['id'] = user[0]
                session['username'] = user[1]
                site_logger.info(f'admin {username} logged in successfully.')
                
                # Redirect to home page
                return redirect(url_for('admin.home'))
            else:
                # Account doesn't exist or password incorrect
                flash(password_wrong, "error")
        else:
            # Account doesn't exist or username incorrect
            flash(username_wrong, "error")
            
    return render_template("admin/login.html",
                        name=settings[0][1],
                        title="تسجيل الدخول")

# Load the logged in user details
@bp_auth.before_app_request
def load_logged_in_user():
    admin_id = session.get('id')

    if admin_id is None:
        g.user = None
    else:
        _,myCursor = mysql_connector()
        myCursor.execute('SELECT * FROM settings WHERE id = %s', (admin_id,))
        g.user = myCursor.fetchone()

# Logout
@bp_auth.route("/logout")
def logout():
  # Remove session data, this will log the user out
  username = session['username']
  session.clear()
  site_logger.info(f'admin {username} logged out successfully.')

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

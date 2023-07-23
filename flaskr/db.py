# Imports
import mysql.connector
from mysql.connector import errorcode
import click
from flask import current_app, g
from flaskr.log import site_logger
from flaskr.config import DB_CONFIG


# Connecting with Database
def mysql_connector():
    try:
        g.db = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            site_logger.exception("Something is wrong with your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            site_logger.exception("Database does not exist")
        else:
            print("Error: ", err)
            site_logger.exception(err)
        return
    else:
        # Initialize our cursor
        mycursor = g.db.cursor(buffered=True)
        return g.db, mycursor


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    _,mycursor = mysql_connector()

    with current_app.open_resource('schema.sql') as f:
        # Split the file content by semicolon and filter out empty lines
        sql_commands = [cmd.strip() for cmd in f.read().decode('utf8').split(';') if cmd.strip()]

        for cmd in sql_commands:
            mycursor.execute(cmd)

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# Registering with the Application
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

"""Retrive Database Tables"""
def getTableData(mycursor, tableName):

    'Retrieve all table data'
    mycursor.execute("SELECT * FROM "+ tableName)
    table = mycursor.fetchall()

    return table

# Retrieve all data in the database
def retrieve_tables(mycursor, *args) :

    ## TODO::AUTOMATIC select to tables
    AllTables = dict()
    if "*" in args:
        args = ["settings", "article", "book", "presentation"]

    for arg in args:
        AllTables[arg] = getTableData(mycursor, arg)

    return AllTables
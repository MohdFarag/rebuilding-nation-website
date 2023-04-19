import mysql.connector

# Connecting with Database
def mysql_connector():

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="01140345493",
        database="ahmedfarag"
    )
    print("Connected to database..")

    # Initialize our cursor
    mycursor = mydb.cursor(buffered=True)

    return mydb, mycursor


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
        args = ["settings", "article", "book"]

    for arg in args:
        AllTables[arg] = getTableData(mycursor, arg)

    return AllTables
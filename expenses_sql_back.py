import sqlite3


# Singleton class which allows only one connection to the database
class DBConnection:
    # class attribute which stores the object
    _connection = None

    # method that connects to database
    def open_connection(self):
        return sqlite3.connect("Expenses_db.db")

    # method that returns the connection if exists
    @staticmethod
    def get_connection():
        if DBConnection._connection == None:
            DBConnection()
        return DBConnection._connection

    # allow only one instance to be created
    def __init__(self):
        if DBConnection._connection != None:
            raise Exception("A connection was already made to the database")
        else:
            DBConnection._connection = self.open_connection()

db = DBConnection.get_connection()
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS expenses (
                Day INTEGER (2),
                Month VARCHAR(10),
                Year VARCHAR(4),
                Value FLOAT(20,2),
                [Expense Category] VARCHAR(40),
                Note VARCHAR(1000),
                ID INTEGER PRIMARY KEY AUTOINCREMENT);
                """)


# insert values to database
def insert(insertion_list):
    sql = """INSERT INTO expenses (Day, Month, Year, Value, [Expense Category], Note)
                        VALUES (?,?, ?, ?, ?, ?);"""
    values = insertion_list

    cursor.execute(sql, values)
    db.commit()


# shows data filtered by month and year
def db_show(month, year):
    sql = "SELECT * FROM expenses WHERE Month = ? AND Year = ? ORDER BY Day DESC, ID DESC"
    values = (month, year)

    cursor.execute(sql, values)
    query = cursor.fetchall()
    return query


# deletes records
def delete(id):
    sql = "DELETE FROM expenses WHERE id = ?"
    value = (id,)
    cursor.execute(sql, value)
    db.commit()


# modify table
def modify(modify_l):
    sql = """UPDATE expenses SET Value=?, [Expense Category]=?, Note=? WHERE ID=?"""
    values = modify_l
    cursor.execute(sql, values)
    db.commit()


# calculate statistics
def statistics(month, year):
    sql = """SELECT [Expense Category], SUM(Value) sum_value,
                       100.0 * SUM(Value) / SUM(SUM(Value)) OVER () percentage, SUM(SUM(Value)) OVER () total
                FROM expenses
                WHERE Month = ? AND Year = ?
                GROUP BY [Expense Category]
                ORDER BY SUM(Value) DESC;"""
    values = (month, year)
    cursor.execute(sql, values)
    query = cursor.fetchall()
    return query

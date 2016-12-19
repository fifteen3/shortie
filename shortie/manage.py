import os
import db
import sqlite3
from flask import Flask
from flask_script import Manager

app = Flask(__name__)
app.config.update( DATA = '../database/shortie.data.sql',
        DATABASE_SCHEMA = '../database/shortie.schema.sql'
        )
manager = Manager(app)

@manager.command
def create_db():
    execute_sql_byfile(app.config['DATABASE_SCHEMA'])
    return "Database created."

@manager.command
def delete_db():
    os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../database/shortie'))

@manager.command
def pop_db():
    execute_sql_byfile(app.config['DATA'])
    return "Database populated."

@manager.command
def clear_users():
    c = db.get_db()
    print "delete users"
    try:
        c.execute('DELETE from users')
    except Error:
        return 'delete error.'
    return 'cleared users table'

def execute_sql_byfile(file_name):
    c = db.get_db()
    try:
        with app.open_resource(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), file_name), mode='r') as f:
            c.cursor().executescript(f.read())
        c.commit()
    except sqlite3.IntegrityError as e:
        return e.message

if __name__ == "__main__":
    manager.run()
